"""
Benchmark Experiments for Smart Factory Production Optimization
Evaluates Baseline vs CP-SAT Solver across multiple deterministic scenarios:
1. Nominal Workload (12 orders, healthy fleet)
2. Single Machine Degradation (M1-CNC-01 Coolant Failure)
3. Heavy Stress Workload (15 orders, multiple degraded machines)
4. Dispatching Rule Comparison (FIFO vs EDF vs CP-SAT)
"""
import sys
import time
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from database.db_manager import DatabaseManager
from optimization.scheduler import ProductionScheduler
from simulation.factory_simulator import FactorySimulator
from config import STATUS_NORMAL, STATUS_CRITICAL, STATUS_WARNING

def run_benchmarks():
    db = DatabaseManager()
    scheduler = ProductionScheduler(db=db)
    simulator = FactorySimulator(db=db)
    results = {}

    # ---------------------------------------------------------
    # Scenario 1: Nominal Workload (12 Orders, All Healthy)
    # ---------------------------------------------------------
    db.reset_to_defaults()
    simulator.reset()
    s1_res = scheduler.optimize_schedule(commit_to_db=False)
    
    results["scenario_1_nominal"] = {
        "description": "12 initial orders across 6 healthy machines (100% nominal state)",
        "baseline": {
            "makespan_hrs": s1_res["baseline"]["makespan_hrs"],
            "tardiness_hrs": s1_res["baseline"]["total_tardiness_weighted"],
            "delayed_orders": s1_res["baseline"]["delayed_orders_count"],
            "high_risk_assignments": s1_res["baseline"]["high_risk_assignments"],
            "energy_kwh": s1_res["baseline"]["total_energy_kwh"]
        },
        "optimized": {
            "makespan_hrs": s1_res["optimized"]["makespan_hrs"],
            "tardiness_hrs": s1_res["optimized"]["total_tardiness_weighted"],
            "delayed_orders": s1_res["optimized"]["delayed_orders_count"],
            "high_risk_assignments": s1_res["optimized"]["high_risk_assignments"],
            "energy_kwh": s1_res["optimized"]["total_energy_kwh"]
        },
        "improvements": s1_res["improvements"],
        "solve_time_ms": s1_res["solve_time_ms"],
        "solver_status": s1_res["solver_status"]
    }

    # ---------------------------------------------------------
    # Scenario 2: Single Degradation (M1-CNC-01 Coolant Failure)
    # ---------------------------------------------------------
    db.reset_to_defaults()
    simulator.reset()
    simulator.inject_anomaly("M1-CNC-01", "COOLANT_FAILURE")
    simulator.step(time_delta_hrs=0.5)  # Evolve anomaly to trigger PdM failure classification
    
    s2_res = scheduler.optimize_schedule(commit_to_db=False)
    results["scenario_2_coolant_failure"] = {
        "description": "M1-CNC-01 experiences Coolant Failure (health drops, failure prob spikes > 0.95)",
        "baseline": {
            "makespan_hrs": s2_res["baseline"]["makespan_hrs"],
            "tardiness_hrs": s2_res["baseline"]["total_tardiness_weighted"],
            "delayed_orders": s2_res["baseline"]["delayed_orders_count"],
            "high_risk_assignments": s2_res["baseline"]["high_risk_assignments"],
            "energy_kwh": s2_res["baseline"]["total_energy_kwh"]
        },
        "optimized": {
            "makespan_hrs": s2_res["optimized"]["makespan_hrs"],
            "tardiness_hrs": s2_res["optimized"]["total_tardiness_weighted"],
            "delayed_orders": s2_res["optimized"]["delayed_orders_count"],
            "high_risk_assignments": s2_res["optimized"]["high_risk_assignments"],
            "energy_kwh": s2_res["optimized"]["total_energy_kwh"]
        },
        "improvements": s2_res["improvements"],
        "solve_time_ms": s2_res["solve_time_ms"],
        "solver_status": s2_res["solver_status"]
    }

    # ---------------------------------------------------------
    # Scenario 3: Heavy Stress Workload (15 Orders + 2 Degraded Machines)
    # ---------------------------------------------------------
    db.reset_to_defaults()
    simulator.reset()
    simulator.inject_anomaly("M1-CNC-01", "COOLANT_FAILURE")
    simulator.inject_anomaly("M3-ROB-01", "BEARING_WEAR")
    simulator.step(time_delta_hrs=0.5)

    # Inject 3 urgent surge orders
    db.add_order("ORD-SURGE-01", "PRD-AERO-01", "Aero Titanium Blisk", 10, 4.0, "CNC_MILL", "Urgent", 12.0)
    db.add_order("ORD-SURGE-02", "PRD-AUTO-02", "Automotive Arm Joint", 25, 3.0, "ROBOTIC_ARM", "Urgent", 10.0)
    db.add_order("ORD-SURGE-03", "PRD-POLY-03", "Medical Polymer Shell", 50, 2.5, "INJECTION_MOLD", "Urgent", 8.0)

    s3_res = scheduler.optimize_schedule(commit_to_db=False)
    results["scenario_3_heavy_stress"] = {
        "description": "15 orders (including 3 surge urgent orders) with M1 Coolant Failure & M3 Bearing Wear",
        "baseline": {
            "makespan_hrs": s3_res["baseline"]["makespan_hrs"],
            "tardiness_hrs": s3_res["baseline"]["total_tardiness_weighted"],
            "delayed_orders": s3_res["baseline"]["delayed_orders_count"],
            "high_risk_assignments": s3_res["baseline"]["high_risk_assignments"],
            "energy_kwh": s3_res["baseline"]["total_energy_kwh"]
        },
        "optimized": {
            "makespan_hrs": s3_res["optimized"]["makespan_hrs"],
            "tardiness_hrs": s3_res["optimized"]["total_tardiness_weighted"],
            "delayed_orders": s3_res["optimized"]["delayed_orders_count"],
            "high_risk_assignments": s3_res["optimized"]["high_risk_assignments"],
            "energy_kwh": s3_res["optimized"]["total_energy_kwh"]
        },
        "improvements": s3_res["improvements"],
        "solve_time_ms": s3_res["solve_time_ms"],
        "solver_status": s3_res["solver_status"]
    }

    # ---------------------------------------------------------
    # Scenario 4: Dispatching Rule Baseline Comparison (FIFO vs EDF vs CP-SAT)
    # ---------------------------------------------------------
    db.reset_to_defaults()
    simulator.reset()
    orders = db.get_orders()
    machines = db.get_machines()

    # FIFO dispatching: sorted by order_id
    fifo_orders = sorted(orders, key=lambda x: x["order_id"])
    fifo_res = scheduler.build_naive_baseline_schedule(fifo_orders, machines)

    # Earliest Deadline First (EDF) dispatching: sorted by deadline_hrs
    edf_orders = sorted(orders, key=lambda x: float(x.get("deadline_hrs", 999.0)))
    edf_res = scheduler.build_naive_baseline_schedule(edf_orders, machines)

    # CP-SAT multi-objective optimization
    cpsat_res = scheduler.optimize_schedule(orders=orders, machines=machines, commit_to_db=False)

    results["scenario_4_dispatching_rules"] = {
        "description": "Comparison of classical heuristics (FIFO, EDF) vs CP-SAT Multi-Objective Optimization",
        "FIFO": {
            "makespan_hrs": fifo_res["makespan_hrs"],
            "tardiness_hrs": fifo_res["total_tardiness_weighted"],
            "delayed_orders": fifo_res["delayed_orders_count"],
            "high_risk_assignments": fifo_res["high_risk_assignments"],
            "energy_kwh": fifo_res["total_energy_kwh"]
        },
        "EDF": {
            "makespan_hrs": edf_res["makespan_hrs"],
            "tardiness_hrs": edf_res["total_tardiness_weighted"],
            "delayed_orders": edf_res["delayed_orders_count"],
            "high_risk_assignments": edf_res["high_risk_assignments"],
            "energy_kwh": edf_res["total_energy_kwh"]
        },
        "CP_SAT": {
            "makespan_hrs": cpsat_res["optimized"]["makespan_hrs"],
            "tardiness_hrs": cpsat_res["optimized"]["total_tardiness_weighted"],
            "delayed_orders": cpsat_res["optimized"]["delayed_orders_count"],
            "high_risk_assignments": cpsat_res["optimized"]["high_risk_assignments"],
            "energy_kwh": cpsat_res["optimized"]["total_energy_kwh"],
            "solve_time_ms": cpsat_res["solve_time_ms"]
        }
    }

    # Reset DB cleanly after experiment
    db.reset_to_defaults()
    simulator.reset()

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_benchmarks()
