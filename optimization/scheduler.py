"""
AI Production Scheduling Optimization Engine
Uses Google OR-Tools CP-SAT Solver for multi-objective constrained scheduling:
1. Minimizes Weighted Order Tardiness (Prioritizing High/Urgent Orders before Deadlines)
2. Minimizes Machine Failure Risk Exposure (Penalizing assigning orders to unhealthy machines)
3. Minimizes Energy Consumption & Peak Load Costs
4. Enforces Machine Capability and Non-Overlapping Job Intervals

Also provides Naive FIFO Baseline scheduling to evaluate Before vs. After Optimization metrics.
"""
import time
from typing import List, Dict, Any, Tuple, Optional
from ortools.sat.python import cp_model
import pandas as pd

from config import (
    MACHINES, PRIORITY_WEIGHTS, STATUS_NORMAL,
    STATUS_WARNING, STATUS_CRITICAL, STATUS_FAILED
)
from database.db_manager import DatabaseManager
from models.energy_model import EnergyPredictionModel
from models.delay_model import DelayPredictionModel


class ProductionScheduler:
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or DatabaseManager()
        self.energy_model = EnergyPredictionModel()
        self.delay_model = DelayPredictionModel()

    def get_eligible_machines(self, machine_type: str, machines_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filters machines capable of executing the requested machine type."""
        return [m for m in machines_list if m["type"] == machine_type]

    @staticmethod
    def is_machine_high_risk(m_info: Dict[str, Any]) -> bool:
        """Standardized check: returns True if machine is degraded, failing, or high failure probability (BUG-14)."""
        return (
            m_info.get("failure_prob", 0.0) > 0.35
            or m_info.get("health_score", 100.0) < 60.0
            or m_info.get("status") in (STATUS_CRITICAL, STATUS_FAILED)
        )

    def build_naive_baseline_schedule(
        self,
        orders: List[Dict[str, Any]],
        machines: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Computes a naive, unoptimized baseline schedule (FIFO order, round-robin assignment
        ignoring machine health, failure risk, and energy costs).
        Used for Before vs. After comparison.
        """
        # Exclude completed orders from baseline scheduling (BUG-12)
        orders = [o for o in orders if o.get("status") != "Completed"]
        machine_lookup = {m["machine_id"]: m for m in machines}
        machine_timelines: Dict[str, float] = {m["machine_id"]: 0.0 for m in machines}
        
        scheduled_orders = []
        total_tardiness = 0.0
        total_energy_kwh = 0.0
        high_risk_assignments = 0
        delayed_orders_count = 0

        # Group eligible machines by type
        type_to_machines: Dict[str, List[str]] = {}
        for m in machines:
            type_to_machines.setdefault(m["type"], []).append(m["machine_id"])

        round_robin_idx: Dict[str, int] = {t: 0 for t in type_to_machines}

        for order in orders:
            req_type = order["required_machine_type"]
            eligible = type_to_machines.get(req_type, [])
            if not eligible:
                continue

            # Naively pick next machine in round-robin without checking health or risk
            idx = round_robin_idx[req_type] % len(eligible)
            assigned_mid = eligible[idx]
            round_robin_idx[req_type] += 1

            m_info = machine_lookup[assigned_mid]
            proc_time = float(order["processing_time_hrs"])
            deadline = float(order["deadline_hrs"])
            
            start_time = machine_timelines[assigned_mid]
            end_time = start_time + proc_time
            machine_timelines[assigned_mid] = end_time

            # Check tardiness
            tardiness = max(0.0, end_time - deadline)
            total_tardiness += tardiness * PRIORITY_WEIGHTS.get(order["priority"], 2)

            # Check if machine was high risk (BUG-14)
            if self.is_machine_high_risk(m_info):
                high_risk_assignments += 1

            # Energy calculation
            energy_out = self.energy_model.predict_job_energy(
                machine_id=assigned_mid,
                processing_time_hrs=proc_time,
                health_score=m_info["health_score"],
                start_hour_of_day=start_time
            )
            total_energy_kwh += energy_out["total_kwh"]

            # Delay model prediction
            delay_out = self.delay_model.predict_delay_risk(
                processing_time_hrs=proc_time,
                deadline_hrs=deadline,
                scheduled_start_hrs=start_time,
                machine_failure_prob=m_info["failure_prob"],
                machine_health_score=m_info["health_score"],
                priority=order["priority"]
            )
            if delay_out["is_delayed"]:
                delayed_orders_count += 1

            scheduled_orders.append({
                **order,
                "assigned_machine_id": assigned_mid,
                "scheduled_start_hrs": round(start_time, 2),
                "scheduled_end_hrs": round(end_time, 2),
                "delay_risk_prob": delay_out["delay_probability"],
                "is_delayed": delay_out["is_delayed"],
                "energy_kwh": energy_out["total_kwh"],
                "cost_usd": energy_out["estimated_cost_usd"],
                "machine_health": m_info["health_score"],
                "machine_failure_prob": m_info["failure_prob"]
            })

        makespan = max(machine_timelines.values()) if machine_timelines else 0.0

        return {
            "scheduled_orders": scheduled_orders,
            "total_tardiness_weighted": round(total_tardiness, 2),
            "delayed_orders_count": delayed_orders_count,
            "high_risk_assignments": high_risk_assignments,
            "total_energy_kwh": round(total_energy_kwh, 2),
            "makespan_hrs": round(makespan, 2)
        }

    def optimize_schedule(
        self,
        orders: Optional[List[Dict[str, Any]]] = None,
        machines: Optional[List[Dict[str, Any]]] = None,
        max_solve_time_sec: float = 4.0,
        commit_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Runs OR-Tools CP-SAT multi-objective optimization to assign orders
        to the best machines and sequence them.
        """
        t0 = time.time()
        if orders is None:
            orders = self.db.get_orders()
        # Exclude completed orders from CP-SAT optimization (BUG-12)
        orders = [o for o in orders if o.get("status") != "Completed"]
        if machines is None:
            machines = self.db.get_machines()

        machine_lookup = {m["machine_id"]: m for m in machines}
        
        # Calculate Naive Baseline first
        baseline = self.build_naive_baseline_schedule(orders, machines)

        # Build OR-Tools CP-SAT Model
        model = cp_model.CpModel()
        
        # Scale float hours to integer time units (e.g. 1 hour = 10 units = 6 minute resolution)
        TIME_SCALE = 10
        HORIZON_HRS = 120  # 5-day scheduling horizon
        HORIZON_UNITS = HORIZON_HRS * TIME_SCALE

        all_machines_by_type: Dict[str, List[str]] = {}
        for m in machines:
            all_machines_by_type.setdefault(m["type"], []).append(m["machine_id"])

        # Decision variables:
        # x[(order_id, machine_id)] = BoolVar indicating order is assigned to machine
        # start[(order_id, machine_id)] = IntVar start time
        # end[(order_id, machine_id)] = IntVar end time
        # interval[(order_id, machine_id)] = OptionalIntervalVar
        
        x = {}
        starts = {}
        ends = {}
        intervals = {}
        tardiness_vars = {}

        machine_intervals: Dict[str, List[Any]] = {m["machine_id"]: [] for m in machines}

        for order in orders:
            oid = order["order_id"]
            req_type = order["required_machine_type"]
            eligible_mids = all_machines_by_type.get(req_type, [])
            p_time_units = int(round(float(order["processing_time_hrs"]) * TIME_SCALE))
            deadline_units = int(round(float(order["deadline_hrs"]) * TIME_SCALE))
            prio_weight = PRIORITY_WEIGHTS.get(order["priority"], 2)

            tardiness = model.NewIntVar(0, HORIZON_UNITS, f"tardiness_{oid}")
            tardiness_vars[oid] = tardiness

            assigned_bools = []
            for mid in eligible_mids:
                m_info = machine_lookup[mid]

                b = model.NewBoolVar(f"x_{oid}_{mid}")
                s = model.NewIntVar(0, HORIZON_UNITS, f"s_{oid}_{mid}")
                e = model.NewIntVar(0, HORIZON_UNITS, f"e_{oid}_{mid}")
                itv = model.NewOptionalIntervalVar(s, p_time_units, e, b, f"itv_{oid}_{mid}")

                x[(oid, mid)] = b
                starts[(oid, mid)] = s
                ends[(oid, mid)] = e
                intervals[(oid, mid)] = itv
                assigned_bools.append(b)
                machine_intervals[mid].append(itv)

                # Link tardiness: tardiness >= end - deadline when assigned to this machine
                model.Add(tardiness >= e - deadline_units).OnlyEnforceIf(b)

            # Each order must be assigned to exactly ONE eligible machine
            if assigned_bools:
                model.Add(sum(assigned_bools) == 1)
            else:
                model.Add(tardiness >= 0)

        # Machine non-overlapping intervals constraint
        for mid, itvs in machine_intervals.items():
            if itvs:
                model.AddNoOverlap(itvs)

        # Multi-Objective Function:
        # 1. Minimize Weighted Tardiness (Delays)
        # 2. Minimize Machine Failure Risk Penalties (High penalty if assigning to degraded machine)
        # 3. Minimize Energy & Machine Cost
        # 4. Minimize Makespan
        
        objective_terms = []

        # Objective Term 1: Tardiness
        for order in orders:
            oid = order["order_id"]
            if oid in tardiness_vars:
                weight = PRIORITY_WEIGHTS.get(order["priority"], 2) * 50
                objective_terms.append(tardiness_vars[oid] * weight)

        # Objective Term 2 & 3: Risk Penalties and Machine Energy Costs
        for (oid, mid), b in x.items():
            m_info = machine_lookup[mid]
            m_fail_prob = m_info["failure_prob"]
            m_health = m_info["health_score"]

            # Risk penalty: insurmountable penalty if machine is failed, steep quadratic if critical
            if m_info["status"] == STATUS_FAILED:
                risk_penalty = 50000  # Insurmountable penalty: only assigned if no alternative machine
            elif m_info["status"] == STATUS_CRITICAL or m_fail_prob > 0.50:
                risk_penalty = 8000  # Extreme disincentive
            elif m_info["status"] == STATUS_WARNING or m_fail_prob > 0.25 or m_health < 70.0:
                risk_penalty = int(m_fail_prob * 3000)
            else:
                risk_penalty = 0

            # Energy efficiency term: CNC/Inj power differences
            power_cost = int(m_info["nominal_power_kw"] * 5)
            
            total_assignment_penalty = risk_penalty + power_cost
            if total_assignment_penalty > 0:
                objective_terms.append(b * total_assignment_penalty)

        # Makespan term
        makespan = model.NewIntVar(0, HORIZON_UNITS, "makespan")
        for (oid, mid), e in ends.items():
            model.Add(makespan >= e).OnlyEnforceIf(x[(oid, mid)])
        objective_terms.append(makespan * 5)

        model.Minimize(sum(objective_terms))

        # Solve with CP-SAT
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max_solve_time_sec
        solver.parameters.num_workers = 4
        solver_status_code = solver.Solve(model)
        solve_duration_ms = (time.time() - t0) * 1000.0

        status_str = solver.StatusName(solver_status_code)
        
        # If solver succeeded (OPTIMAL or FEASIBLE)
        if solver_status_code in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            optimized_orders = []
            opt_total_tardiness = 0.0
            opt_total_energy = 0.0
            opt_high_risk_count = 0
            opt_delayed_count = 0
            opt_makespan = float(solver.Value(makespan)) / TIME_SCALE

            for order in orders:
                oid = order["order_id"]
                assigned_mid = None
                start_hrs = 0.0
                end_hrs = 0.0

                for (o, mid), b in x.items():
                    if o == oid and solver.Value(b) == 1:
                        assigned_mid = mid
                        start_hrs = float(solver.Value(starts[(o, mid)])) / TIME_SCALE
                        end_hrs = float(solver.Value(ends[(o, mid)])) / TIME_SCALE
                        break

                if assigned_mid is None:
                    continue

                m_info = machine_lookup[assigned_mid]
                proc_time = float(order["processing_time_hrs"])
                deadline = float(order["deadline_hrs"])

                tardiness = max(0.0, end_hrs - deadline)
                opt_total_tardiness += tardiness * PRIORITY_WEIGHTS.get(order["priority"], 2)

                # Check if machine was high risk (BUG-14)
                if self.is_machine_high_risk(m_info):
                    opt_high_risk_count += 1

                # Predict Energy
                energy_out = self.energy_model.predict_job_energy(
                    machine_id=assigned_mid,
                    processing_time_hrs=proc_time,
                    health_score=m_info["health_score"],
                    start_hour_of_day=start_hrs
                )
                opt_total_energy += energy_out["total_kwh"]

                # Predict Delay Risk
                delay_out = self.delay_model.predict_delay_risk(
                    processing_time_hrs=proc_time,
                    deadline_hrs=deadline,
                    scheduled_start_hrs=start_hrs,
                    machine_failure_prob=m_info["failure_prob"],
                    machine_health_score=m_info["health_score"],
                    priority=order["priority"]
                )
                if delay_out["is_delayed"]:
                    opt_delayed_count += 1

                opt_record = {
                    **order,
                    "assigned_machine_id": assigned_mid,
                    "scheduled_start_hrs": round(start_hrs, 2),
                    "scheduled_end_hrs": round(end_hrs, 2),
                    "delay_risk_prob": delay_out["delay_probability"],
                    "is_delayed": delay_out["is_delayed"],
                    "energy_kwh": energy_out["total_kwh"],
                    "cost_usd": energy_out["estimated_cost_usd"],
                    "machine_health": m_info["health_score"],
                    "machine_failure_prob": m_info["failure_prob"]
                }
                optimized_orders.append(opt_record)

                if commit_to_db:
                    self.db.update_order_assignment(
                        order_id=oid,
                        machine_id=assigned_mid,
                        start_hrs=round(start_hrs, 2),
                        end_hrs=round(end_hrs, 2),
                        delay_risk=delay_out["delay_probability"],
                        is_delayed=delay_out["is_delayed"],
                        energy_kwh=energy_out["total_kwh"]
                    )

            opt_results = {
                "scheduled_orders": optimized_orders,
                "total_tardiness_weighted": round(opt_total_tardiness, 2),
                "delayed_orders_count": opt_delayed_count,
                "high_risk_assignments": opt_high_risk_count,
                "total_energy_kwh": round(opt_total_energy, 2),
                "makespan_hrs": round(opt_makespan, 2)
            }
        else:
            # Fallback to naive baseline if solver couldn't find feasible
            status_str = f"FAILED ({status_str}) - Baseline retained"
            opt_results = baseline

        # Calculate Improvement Deltas
        delay_saved_hrs = round(max(0.0, baseline["total_tardiness_weighted"] - opt_results["total_tardiness_weighted"]), 1)
        energy_saved_kwh = round(max(0.0, baseline["total_energy_kwh"] - opt_results["total_energy_kwh"]), 1)
        risk_reduction = baseline["high_risk_assignments"] - opt_results["high_risk_assignments"]
        delayed_orders_prevented = baseline["delayed_orders_count"] - opt_results["delayed_orders_count"]

        # Record to DB history
        if commit_to_db:
            self.db.record_optimization_run(
                total_orders=len(orders),
                solver_status=status_str,
                solve_time_ms=round(solve_duration_ms, 1),
                tardiness_before=baseline["total_tardiness_weighted"],
                tardiness_after=opt_results["total_tardiness_weighted"],
                energy_before=baseline["total_energy_kwh"],
                energy_after=opt_results["total_energy_kwh"],
                risk_before=float(baseline["high_risk_assignments"]),
                risk_after=float(opt_results["high_risk_assignments"]),
                notes=f"CP-SAT: saved {delay_saved_hrs}h delay & avoided {risk_reduction} high-risk jobs"
            )

        return {
            "solver_status": status_str,
            "solve_time_ms": round(solve_duration_ms, 1),
            "baseline": baseline,
            "optimized": opt_results,
            "improvements": {
                "delay_saved_hrs": delay_saved_hrs,
                "delayed_orders_prevented": delayed_orders_prevented,
                "energy_saved_kwh": energy_saved_kwh,
                "high_risk_jobs_avoided": max(0, risk_reduction),
                "efficiency_gain_pct": round(min(100.0, (delay_saved_hrs / max(1.0, baseline['total_tardiness_weighted'] + 10.0)) * 100.0), 1)
            }
        }
