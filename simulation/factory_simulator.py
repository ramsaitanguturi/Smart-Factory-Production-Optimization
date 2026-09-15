"""
Factory Simulator Engine
Simulates dynamic shop floor operations, sensor telemetry streams,
machine degradation state machine, in-flight order processing,
and real-time anomaly injection for What-If scenarios.
"""
import time
import random
from typing import Dict, Any, List, Optional
import pandas as pd

from config import (
    MACHINES, STATUS_NORMAL, STATUS_WARNING, STATUS_CRITICAL,
    STATUS_MAINTENANCE, STATUS_FAILED, PRODUCTS
)
from database.db_manager import DatabaseManager
from data_generator.telemetry_generator import TelemetryGenerator
from models.pdm_model import PredictiveMaintenanceModel
from models.energy_model import EnergyPredictionModel


class FactorySimulator:
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or DatabaseManager()
        self.generator = TelemetryGenerator()
        self.pdm_model = PredictiveMaintenanceModel()
        self.energy_model = EnergyPredictionModel()
        
        # Runtime in-memory state tracking
        self.simulation_time_hrs = 0.0
        self.anomaly_states: Dict[str, Dict[str, Any]] = {}
        self.latest_telemetry: Dict[str, Dict[str, Any]] = {}
        
        # Initialize machine memory buffers
        self._initialize_runtime_state()

    def reset(self):
        """Completely resets simulator clock, clears all anomalies, and re-seeds baseline."""
        self.simulation_time_hrs = 0.0
        self.anomaly_states.clear()
        self.latest_telemetry.clear()
        self._initialize_runtime_state()

    def _initialize_runtime_state(self):
        """Initializes internal tracking for machines and fills initial telemetry if empty."""
        db_machines = self.db.get_machines()
        for m in db_machines:
            mid = m["machine_id"]
            self.anomaly_states[mid] = {
                "active": False,
                "type": None,
                "factor": 0.0,
                "temp_boost": 0.0,
                "vib_boost": 0.0,
                "pres_drop": 0.0
            }
            # Record initial baseline telemetry reading
            reading = self.generator.generate_single_reading(
                machine_id=mid,
                current_status=m["status"],
                operating_hours=m["operating_hours"],
                load_factor=0.75,
                anomaly_factor=0.0
            )
            # Pass through ML model
            ml_out = self.pdm_model.predict_risk(
                temperature=reading["temperature"],
                vibration=reading["vibration"],
                rpm=reading["rpm"],
                pressure=reading["pressure"],
                power_kw=reading["power_kw"],
                operating_hours=m["operating_hours"],
                load_factor=0.75
            )
            reading["health_score"] = ml_out["health_score"]
            reading["failure_prob"] = ml_out["failure_probability"]
            reading["primary_cause"] = ml_out["primary_cause"]
            reading["recommendation"] = ml_out["recommendation"]
            reading["rul_hours"] = ml_out["rul_hours"]
            self.latest_telemetry[mid] = reading

    def step(self, time_delta_hrs: float = 0.25) -> Dict[str, Any]:
        """
        Advances the factory simulation by time_delta_hrs.
        Generates new sensor readings, updates ML predictions, records to DB,
        and advances order execution progress.
        """
        self.simulation_time_hrs += time_delta_hrs
        machines = self.db.get_machines()
        updates = []
        telemetry_batch = []

        for m in machines:
            mid = m["machine_id"]
            anom = self.anomaly_states.get(mid, {"active": False, "factor": 0.0})
            
            current_status = m["status"]
            current_hours = m["operating_hours"] + time_delta_hrs

            if current_status == STATUS_MAINTENANCE:
                # Machine undergoing maintenance
                reading = self.generator.generate_single_reading(
                    machine_id=mid,
                    current_status=STATUS_MAINTENANCE,
                    operating_hours=current_hours
                )
                fail_prob = 0.005
                health = 98.0
                rul = 720.0
                cause = "Maintenance in Progress"
                recom = "Inspection / servicing ongoing."
                new_status = STATUS_MAINTENANCE
            elif current_status == STATUS_FAILED or anom.get("type") == "CATASTROPHIC_FAILURE":
                reading = self.generator.generate_single_reading(
                    machine_id=mid,
                    current_status=STATUS_FAILED,
                    operating_hours=current_hours
                )
                fail_prob = 0.99
                health = 5.0
                rul = 0.0
                cause = "CRITICAL BREAKDOWN - Spindle Seized"
                recom = "Emergency repair crew dispatched."
                new_status = STATUS_FAILED
            else:
                # Active operation with possible anomaly factor
                eff_factor = anom.get("factor", 0.0) if anom.get("active") else 0.0
                reading = self.generator.generate_single_reading(
                    machine_id=mid,
                    current_status=current_status,
                    operating_hours=current_hours,
                    load_factor=0.82,
                    anomaly_factor=eff_factor
                )

                # Inject anomaly specific boosts if active
                if anom.get("active"):
                    reading["temperature"] += anom.get("temp_boost", 0.0)
                    reading["vibration"] += anom.get("vib_boost", 0.0)
                    reading["pressure"] = max(15.0, reading["pressure"] - anom.get("pres_drop", 0.0))

                # Pass through ML Model
                ml_out = self.pdm_model.predict_risk(
                    temperature=reading["temperature"],
                    vibration=reading["vibration"],
                    rpm=reading["rpm"],
                    pressure=reading["pressure"],
                    power_kw=reading["power_kw"],
                    operating_hours=current_hours,
                    load_factor=0.82
                )
                fail_prob = ml_out["failure_probability"]
                health = ml_out["health_score"]
                rul = ml_out["rul_hours"]
                cause = ml_out["primary_cause"]
                recom = ml_out["recommendation"]

                # Determine new machine status from ML predictions
                if fail_prob > 0.65 or health < 35.0:
                    new_status = STATUS_CRITICAL
                elif fail_prob > 0.25 or health < 65.0:
                    new_status = STATUS_WARNING
                else:
                    new_status = STATUS_NORMAL

            # Update DB & in-memory buffer
            reading["health_score"] = health
            reading["failure_prob"] = fail_prob
            reading["primary_cause"] = cause
            reading["recommendation"] = recom
            reading["rul_hours"] = rul
            reading["status"] = new_status
            self.latest_telemetry[mid] = reading

            self.db.update_machine_state(
                machine_id=mid,
                status=new_status,
                health_score=health,
                failure_prob=fail_prob,
                operating_hours=round(current_hours, 1)
            )
            telemetry_batch.append((
                mid, reading["temperature"], reading["vibration"],
                reading["rpm"], reading["pressure"], reading["power_kw"],
                health, fail_prob, new_status
            ))
            updates.append({"machine_id": mid, "telemetry": reading})

        # Batch write telemetry in a single ACID transaction (BUG-03)
        if telemetry_batch:
            self.db.record_telemetry_batch(telemetry_batch)

        # Advance in-flight production orders with single-machine concurrency enforcement (BUG-01 & BUG-11)
        active_orders = self.db.get_orders(status="Scheduled") + self.db.get_orders(status="In-Progress")
        
        # Group orders by assigned machine
        orders_by_machine: Dict[str, List[Dict[str, Any]]] = {}
        for order in active_orders:
            assigned_mid = order.get("assigned_machine_id")
            if assigned_mid:
                orders_by_machine.setdefault(assigned_mid, []).append(order)

        for assigned_mid, m_orders in orders_by_machine.items():
            m_info = self.db.get_machine(assigned_mid)
            # Only advance execution if assigned machine is operational
            if not m_info or m_info["status"] not in (STATUS_NORMAL, STATUS_WARNING):
                continue

            # Prioritize order already In-Progress on this machine
            in_prog = [o for o in m_orders if o["status"] == "In-Progress"]
            if in_prog:
                in_prog.sort(key=lambda o: float(o.get("scheduled_start_hrs", 0.0)))
                current_order = in_prog[0]
            else:
                # Find scheduled order whose start time has arrived, or earliest scheduled order in queue
                sched = [o for o in m_orders if o["status"] == "Scheduled"]
                sched.sort(key=lambda o: (float(o.get("scheduled_start_hrs", 0.0)), float(o.get("deadline_hrs", 999.0))))
                eligible = [o for o in sched if float(o.get("scheduled_start_hrs", 0.0)) <= self.simulation_time_hrs]
                current_order = eligible[0] if eligible else sched[0] if sched else None

            if not current_order:
                continue

            rem_time = max(0.0, float(current_order["processing_time_hrs"]) - time_delta_hrs)
            if rem_time <= 0.001:
                self.db.update_order_status(current_order["order_id"], "Completed")
                with self.db.get_connection() as conn:
                    conn.execute(
                        "UPDATE production_orders SET processing_time_hrs = 0.0 WHERE order_id = ?",
                        (current_order["order_id"],)
                    )
                    conn.execute(
                        "UPDATE machines SET total_cycles = total_cycles + 1 WHERE machine_id = ?",
                        (assigned_mid,)
                    )
                    conn.commit()
            else:
                with self.db.get_connection() as conn:
                    conn.execute(
                        "UPDATE production_orders SET processing_time_hrs = ?, status = 'In-Progress' WHERE order_id = ?",
                        (round(rem_time, 2), current_order["order_id"])
                    )
                    conn.commit()

        return {
            "simulation_time_hrs": round(self.simulation_time_hrs, 2),
            "updates": updates
        }

    def inject_anomaly(self, machine_id: str, anomaly_type: str):
        """
        Injects real-time anomalies for What-If scenario evaluation:
        - "BEARING_WEAR": Severe vibration spike & friction power increase
        - "COOLANT_FAILURE": Rapid overheating & hydraulic pressure loss
        - "MOTOR_MISALIGN": RPM fluctuation & erratic current draw
        - "CATASTROPHIC_FAILURE": Instant machine halt & failure
        """
        if anomaly_type == "BEARING_WEAR":
            self.anomaly_states[machine_id] = {
                "active": True,
                "type": anomaly_type,
                "factor": 0.85,
                "temp_boost": 16.0,
                "vib_boost": 4.1,
                "pres_drop": 5.0
            }
        elif anomaly_type == "COOLANT_FAILURE":
            self.anomaly_states[machine_id] = {
                "active": True,
                "type": anomaly_type,
                "factor": 0.92,
                "temp_boost": 32.0,
                "vib_boost": 1.2,
                "pres_drop": 38.0
            }
        elif anomaly_type == "MOTOR_MISALIGN":
            self.anomaly_states[machine_id] = {
                "active": True,
                "type": anomaly_type,
                "factor": 0.75,
                "temp_boost": 18.0,
                "vib_boost": 3.2,
                "pres_drop": 10.0
            }
        elif anomaly_type == "CATASTROPHIC_FAILURE":
            self.anomaly_states[machine_id] = {
                "active": True,
                "type": anomaly_type,
                "factor": 1.0,
                "temp_boost": 35.0,
                "vib_boost": 5.5,
                "pres_drop": 50.0
            }
        # Run one step immediately to propagate sensor spike
        self.step(time_delta_hrs=0.05)

    def clear_anomaly(self, machine_id: str):
        """Clears anomalies and restores machine to nominal operating parameters."""
        self.anomaly_states[machine_id] = {
            "active": False,
            "type": None,
            "factor": 0.0,
            "temp_boost": 0.0,
            "vib_boost": 0.0,
            "pres_drop": 0.0
        }
        self.step(time_delta_hrs=0.05)

    def perform_maintenance(self, machine_id: str, event_type: str = "Preventive Overhaul"):
        """Performs maintenance, replacing worn components and restoring health."""
        cost = 450.0 if "Overhaul" in event_type else 180.0
        duration = 2.5
        self.clear_anomaly(machine_id)
        self.db.log_maintenance(
            machine_id=machine_id,
            event_type=event_type,
            description=f"Replaced bearings, inspected coolant pumps and calibrated sensors on {machine_id}.",
            duration_hrs=duration,
            cost=cost,
            health_restored_to=98.5
        )
        self.step(time_delta_hrs=0.05)

    def inject_rush_orders(self, count: int = 3):
        """Injects urgent high-priority customer orders to stress the schedule."""
        prod_choices = PRODUCTS
        existing_orders = self.db.get_orders()
        max_id_num = 400
        for o in existing_orders:
            try:
                num = int(o["order_id"].split("-")[-1])
                if num > max_id_num:
                    max_id_num = num
            except Exception:
                pass

        for i in range(count):
            p = random.choice(prod_choices)
            new_id = f"ORD-{max_id_num + i + 1}"
            qty = random.choice([25, 50, 75])
            ptime = p["base_time_hrs"] + round(random.uniform(-0.5, 1.0), 1)
            deadline = round(random.uniform(7.0, 16.0), 1)
            self.db.add_order(
                order_id=new_id,
                product_code=p["code"],
                product_name=p["name"],
                quantity=qty,
                processing_time_hrs=ptime,
                required_machine_type=p["machine_type"],
                priority="Urgent",
                deadline_hrs=deadline
            )
