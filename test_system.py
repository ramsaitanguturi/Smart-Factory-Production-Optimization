"""
Automated Verification Suite for Smart Factory Production Optimization
Tests:
- Database connectivity, tables, and CRUD operations
- Telemetry generation and physics logic
- Predictive maintenance ML model inference and RUL
- Factory simulator step progression and fault injection
- Google OR-Tools CP-SAT optimization and Before vs. After calculation
"""
import sys
import os
import unittest
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from config import MACHINES, STATUS_NORMAL, STATUS_CRITICAL, STATUS_WARNING
from database.db_manager import DatabaseManager
from data_generator.telemetry_generator import TelemetryGenerator
from models.pdm_model import PredictiveMaintenanceModel
from models.energy_model import EnergyPredictionModel
from models.delay_model import DelayPredictionModel
from simulation.factory_simulator import FactorySimulator
from optimization.scheduler import ProductionScheduler


class TestSmartFactorySystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseManager()
        cls.db.reset_to_defaults()
        cls.generator = TelemetryGenerator(random_seed=123)
        cls.pdm = PredictiveMaintenanceModel()
        cls.energy = EnergyPredictionModel()
        cls.delay = DelayPredictionModel()
        cls.simulator = FactorySimulator(db=cls.db)
        cls.simulator.reset()
        cls.scheduler = ProductionScheduler(db=cls.db)

    def test_01_database_seeded(self):
        """Verify machines and initial production orders are seeded."""
        machines = self.db.get_machines()
        self.assertEqual(len(machines), 6, "Expected 6 industrial machines")
        orders = self.db.get_orders()
        self.assertGreaterEqual(len(orders), 10, "Expected at least 10 seeded production orders")
        print(f" [PASS] DB seeded with {len(machines)} machines and {len(orders)} orders.")

    def test_02_telemetry_generation(self):
        """Verify physics-based telemetry is realistic."""
        reading = self.generator.generate_single_reading(
            machine_id="M1-CNC-01",
            current_status=STATUS_NORMAL,
            operating_hours=1200.0,
            load_factor=0.8
        )
        self.assertIn("temperature", reading)
        self.assertIn("vibration", reading)
        self.assertIn("pressure", reading)
        self.assertIn("power_kw", reading)
        self.assertTrue(40.0 <= reading["temperature"] <= 120.0)
        self.assertTrue(0.5 <= reading["vibration"] <= 10.0)
        print(f" [PASS] Telemetry sample: Temp={reading['temperature']}C, Vib={reading['vibration']}mm/s, Pwr={reading['power_kw']}kW")

    def test_03_pdm_model_inference(self):
        """Verify ML model accurately differentiates healthy vs severe degraded states."""
        # Healthy telemetry
        healthy_res = self.pdm.predict_risk(
            temperature=63.0,
            vibration=1.2,
            rpm=11900,
            pressure=110.0,
            power_kw=15.0,
            operating_hours=600.0,
            load_factor=0.75
        )
        self.assertLess(healthy_res["failure_probability"], 0.30)
        self.assertGreaterEqual(healthy_res["health_score"], 70.0)

        # Critical degraded telemetry (thermal runaway + high vibration)
        degraded_res = self.pdm.predict_risk(
            temperature=108.0,
            vibration=5.8,
            rpm=8500,
            pressure=55.0,
            power_kw=38.0,
            operating_hours=4200.0,
            load_factor=1.0
        )
        self.assertGreater(degraded_res["failure_probability"], 0.70)
        self.assertLess(degraded_res["health_score"], 40.0)
        print(f" [PASS] PdM Model: Healthy FailProb={healthy_res['failure_probability']:.3f} | Degraded FailProb={degraded_res['failure_probability']:.3f}")

    def test_04_simulator_fault_injection(self):
        """Verify anomaly injection causes failure probability to spike."""
        target_machine = "M1-CNC-01"
        self.simulator.inject_anomaly(target_machine, "COOLANT_FAILURE")
        m = self.db.get_machine(target_machine)
        self.assertIn(m["status"], [STATUS_WARNING, STATUS_CRITICAL])
        self.assertGreater(m["failure_prob"], 0.30)
        print(f" [PASS] Fault injection: {target_machine} status={m['status']}, fail_prob={m['failure_prob']:.3f}")
        # Clean up
        self.simulator.perform_maintenance(target_machine)
        m_after = self.db.get_machine(target_machine)
        self.assertEqual(m_after["status"], STATUS_NORMAL)
        print(f" [PASS] Maintenance recovery: {target_machine} status={m_after['status']}, health={m_after['health_score']}%")

    def test_05_ortools_optimizer(self):
        """Verify OR-Tools CP-SAT scheduler solves successfully and computes improvements."""
        res = self.scheduler.optimize_schedule(max_solve_time_sec=3.0, commit_to_db=True)
        self.assertIn(res["solver_status"], ["OPTIMAL", "FEASIBLE"])
        self.assertIn("improvements", res)
        print(f" [PASS] OR-Tools Solver: status={res['solver_status']} in {res['solve_time_ms']}ms")
        print(f"        Improvements: Delay Saved={res['improvements']['delay_saved_hrs']}h, High Risk Avoided={res['improvements']['high_risk_jobs_avoided']}")

    def test_06_order_progression(self):
        """BUG-01: Verify step() decrements order processing time and completes finished jobs."""
        test_oid = "ORD-TEST-PROG"
        target_mid = "M1-CNC-01"
        try:
            with self.db.get_connection() as conn:
                conn.execute("DELETE FROM production_orders WHERE order_id = ?", (test_oid,))
                # Clean isolation for target machine (BUG-11 single-machine concurrency)
                conn.execute("UPDATE production_orders SET assigned_machine_id = NULL WHERE assigned_machine_id = ?", (target_mid,))
                conn.commit()

            self.db.add_order(
                order_id=test_oid,
                product_code="PRD-AERO-01",
                product_name="Test Turbine Blade",
                quantity=10,
                processing_time_hrs=1.0,
                required_machine_type="CNC_MILL",
                priority="High",
                deadline_hrs=12.0
            )
            self.db.update_order_assignment(
                order_id=test_oid,
                machine_id="M1-CNC-01",
                start_hrs=0.0,
                end_hrs=1.0,
                delay_risk=0.05,
                is_delayed=0,
                energy_kwh=25.0
            )
            # Advance by 0.5 hours
            self.simulator.step(time_delta_hrs=0.5)
            orders = {o["order_id"]: o for o in self.db.get_orders()}
            self.assertEqual(orders[test_oid]["status"], "In-Progress")
            self.assertAlmostEqual(orders[test_oid]["processing_time_hrs"], 0.5, places=2)

            # Advance by 0.6 hours -> should complete
            self.simulator.step(time_delta_hrs=0.6)
            orders = {o["order_id"]: o for o in self.db.get_orders()}
            self.assertEqual(orders[test_oid]["status"], "Completed")
            self.assertAlmostEqual(orders[test_oid]["processing_time_hrs"], 0.0, places=2)
            print(f" [PASS] BUG-01: Order progression advanced and transitioned to Completed correctly.")
        finally:
            with self.db.get_connection() as conn:
                conn.execute("DELETE FROM production_orders WHERE order_id = ?", (test_oid,))
                conn.commit()

    def test_07_energy_continuous_peak_overlap(self):
        """BUG-02: Verify continuous interval overlap calculus in peak tariff calculation."""
        # Case 1: Job starts at 13.5 and runs for 1.0 hr (ends at 14.5).
        # Overlap with [14.0, 19.0] must be exactly 0.5h, so peak_ratio = 0.5 / 1.0 = 0.50
        res1 = self.energy.predict_job_energy("M1-CNC-01", processing_time_hrs=1.0, start_hour_of_day=13.5)
        self.assertAlmostEqual(res1["peak_ratio"], 0.50, places=2)

        # Case 2: Job starts at 10.0 and runs for 2.0 hr (ends at 12.0) -> zero overlap
        res2 = self.energy.predict_job_energy("M1-CNC-01", processing_time_hrs=2.0, start_hour_of_day=10.0)
        self.assertAlmostEqual(res2["peak_ratio"], 0.0, places=2)

        # Case 3: Job entirely within peak window: 14.0 to 19.0 (5.0 hrs) -> 100% peak
        res3 = self.energy.predict_job_energy("M1-CNC-01", processing_time_hrs=5.0, start_hour_of_day=14.0)
        self.assertAlmostEqual(res3["peak_ratio"], 1.0, places=2)
        print(f" [PASS] BUG-02: Continuous interval overlap verified (0.5h overlap -> peak_ratio={res1['peak_ratio']}).")

    def test_08_sqlite_foreign_keys_and_batch_telemetry(self):
        """BUG-03: Verify foreign key enforcement and batch telemetry recording."""
        import sqlite3
        # Foreign key violation test
        with self.assertRaises(sqlite3.IntegrityError):
            with self.db.get_connection() as conn:
                conn.execute("""
                    INSERT INTO telemetry (
                        machine_id, temperature, vibration, rpm, pressure,
                        power_kw, health_score, failure_prob, status
                    ) VALUES ('NON-EXISTENT-MACHINE', 65.0, 1.2, 10000, 100.0, 20.0, 95.0, 0.02, 'NORMAL')
                """)

        # Batch telemetry insertion test
        batch_rows = [
            ("M1-CNC-01", 60.0, 1.0, 12000, 100.0, 15.0, 98.0, 0.01, "NORMAL"),
            ("M2-CNC-02", 62.0, 1.1, 11800, 98.0, 16.0, 97.0, 0.01, "NORMAL"),
        ]
        self.db.record_telemetry_batch(batch_rows)
        df = self.db.get_recent_telemetry(limit=2)
        self.assertGreaterEqual(len(df), 2)
        print(" [PASS] BUG-03: Foreign key PRAGMA enforced and batch telemetry written in single transaction.")

    def test_09_all_failed_machine_resilience(self):
        """BUG-04: Verify scheduler handles all-failed machines without deadlock or dropping orders."""
        try:
            # Fail both CNC machines
            with self.db.get_connection() as conn:
                conn.execute("UPDATE machines SET status = 'FAILED' WHERE type = 'CNC_MILL'")
                conn.commit()

            # Optimizer should still assign all orders (including CNC orders with heavy penalty) without dropping any
            res = self.scheduler.optimize_schedule(max_solve_time_sec=4.0, commit_to_db=False)
            self.assertIn(res["solver_status"], ["OPTIMAL", "FEASIBLE"])
            # Verify order count matches active orders (excluding completed)
            orders = [o for o in self.db.get_orders() if o.get("status") != "Completed"]
            self.assertEqual(len(res["optimized"]["scheduled_orders"]), len(orders), "No orders should be dropped")
            print(f" [PASS] BUG-04: Optimizer handled all-failed cell with 0 orders dropped ({len(res['optimized']['scheduled_orders'])} orders scheduled).")
        finally:
            # Restore machines
            with self.db.get_connection() as conn:
                conn.execute("UPDATE machines SET status = 'NORMAL' WHERE type = 'CNC_MILL'")
                conn.commit()

    def test_10_simulator_reset(self):
        """BUG-05: Verify simulator.reset() resets clock, anomalies, and latest telemetry."""
        self.simulator.simulation_time_hrs = 15.5
        self.simulator.inject_anomaly("M3-ROB-01", "BEARING_WEAR")
        self.assertTrue(self.simulator.anomaly_states["M3-ROB-01"]["active"])

        # Execute reset
        self.simulator.reset()
        self.assertEqual(self.simulator.simulation_time_hrs, 0.0)
        self.assertFalse(self.simulator.anomaly_states["M3-ROB-01"]["active"])
        self.assertIn("M3-ROB-01", self.simulator.latest_telemetry)
        print(" [PASS] BUG-05: Simulator reset() properly restored clock to 0.0 and cleared anomalies.")

    def test_11_delay_model_semantics(self):
        """BUG-06: Verify separation between actual lateness and unreliability risk."""
        # Job with ample 15-hour buffer slack on a degraded machine
        res = self.delay.predict_delay_risk(
            processing_time_hrs=3.0,
            deadline_hrs=25.0,
            scheduled_start_hrs=7.0,  # ends at 10.0, slack = 15.0h
            machine_failure_prob=0.85,
            machine_health_score=25.0,
            priority="High"
        )
        self.assertEqual(res["is_delayed"], 0, "Order with 15h positive slack must NOT be flagged as delayed/late")
        self.assertEqual(res["is_at_risk"], 1, "Degraded machine should correctly flag order as at risk")
        print(f" [PASS] BUG-06: Lateness and delay risk disentangled: is_delayed={res['is_delayed']}, is_at_risk={res['is_at_risk']}.")

    def test_12_unique_order_insertion(self):
        """BUG-08: Verify get_next_order_id generates unique IDs and add_order handles collisions."""
        next_id = self.db.get_next_order_id()
        self.assertTrue(next_id.startswith("ORD-"))
        try:
            success1 = self.db.add_order(
                order_id=next_id,
                product_code="PRD-AERO-01",
                product_name="Aero Turbine",
                quantity=10,
                processing_time_hrs=2.0,
                required_machine_type="CNC_MILL",
                priority="Medium",
                deadline_hrs=18.0
            )
            self.assertTrue(success1)

            # Attempt duplicate insertion
            success2 = self.db.add_order(
                order_id=next_id,
                product_code="PRD-AERO-01",
                product_name="Aero Turbine Duplicate",
                quantity=10,
                processing_time_hrs=2.0,
                required_machine_type="CNC_MILL",
                priority="Medium",
                deadline_hrs=18.0
            )
            self.assertFalse(success2, "Duplicate order ID must return False")
            print(f" [PASS] BUG-08: Sequential ID {next_id} generated and collision rejected properly.")
        finally:
            with self.db.get_connection() as conn:
                conn.execute("DELETE FROM production_orders WHERE order_id = ?", (next_id,))
                conn.commit()

    def test_13_no_joblib_deprecation_warning(self):
        """BUG-10: Verify loading PdM models produces zero deprecation warnings."""
        with warnings.catch_warnings(record=True) as recorded_warnings:
            warnings.simplefilter("always")
            new_pdm = PredictiveMaintenanceModel()
            self.assertTrue(new_pdm.load_models())
            dep_warnings = [w for w in recorded_warnings if issubclass(w.category, DeprecationWarning)]
            self.assertEqual(len(dep_warnings), 0, "No deprecation warnings should be emitted on model loading")
            print(" [PASS] BUG-10: PdM model loads cleanly with 0 deprecation warnings.")

    def test_14_bug11_machine_concurrency(self):
        """BUG-11: Verify machine concurrency enforcement prevents parallel execution on single machine."""
        oid1 = "ORD-TEST-C1"
        oid2 = "ORD-TEST-C2"
        target_mid = "M6-INJ-02"
        try:
            # Temporarily unassign any prior orders from target machine for clean test isolation
            with self.db.get_connection() as conn:
                conn.execute("UPDATE production_orders SET assigned_machine_id = NULL WHERE assigned_machine_id = ?", (target_mid,))
                conn.commit()

            self.db.add_order(oid1, "PRD-POLY-03", "Polymer 1", 5, 2.0, "INJECTION_MOLD", "High", 20.0)
            self.db.add_order(oid2, "PRD-POLY-03", "Polymer 2", 5, 2.0, "INJECTION_MOLD", "Medium", 25.0)
            self.db.update_order_assignment(oid1, target_mid, 0.0, 2.0, 0.05, 0, 40.0)
            self.db.update_order_assignment(oid2, target_mid, 2.0, 4.0, 0.05, 0, 40.0)

            # Advance by 1.0 hour
            self.simulator.step(time_delta_hrs=1.0)
            orders = {o["order_id"]: o for o in self.db.get_orders()}

            # Job 1 must have progressed to In-Progress with 1.0 hr left
            self.assertEqual(orders[oid1]["status"], "In-Progress")
            self.assertAlmostEqual(orders[oid1]["processing_time_hrs"], 1.0, places=2)

            # Job 2 must remain Scheduled with full 2.0 hrs (NOT progressed concurrently!)
            self.assertEqual(orders[oid2]["status"], "Scheduled")
            self.assertAlmostEqual(orders[oid2]["processing_time_hrs"], 2.0, places=2)
            print(" [PASS] BUG-11: Single-machine concurrency strictly enforced (Job 2 queued while Job 1 runs).")
        finally:
            with self.db.get_connection() as conn:
                conn.execute("DELETE FROM production_orders WHERE order_id IN (?, ?)", (oid1, oid2))
                conn.commit()

    def test_15_bug12_completed_orders_excluded(self):
        """BUG-12: Verify completed orders with 0 duration are excluded from optimization."""
        oid_done = "ORD-TEST-DONE"
        try:
            self.db.add_order(oid_done, "PRD-AUTO-02", "Done Chassis", 10, 0.0, "ROBOTIC_ARM", "Low", 5.0)
            self.db.update_order_status(oid_done, "Completed")

            res = self.scheduler.optimize_schedule(max_solve_time_sec=2.0, commit_to_db=False)
            base_ids = [o["order_id"] for o in res["baseline"]["scheduled_orders"]]
            opt_ids = [o["order_id"] for o in res["optimized"]["scheduled_orders"]]

            self.assertNotIn(oid_done, base_ids, "Completed orders must not appear in baseline schedule")
            self.assertNotIn(oid_done, opt_ids, "Completed orders must not appear in optimized schedule")
            print(" [PASS] BUG-12: Completed orders cleanly excluded from CP-SAT optimization.")
        finally:
            with self.db.get_connection() as conn:
                conn.execute("DELETE FROM production_orders WHERE order_id = ?", (oid_done,))
                conn.commit()

    def test_16_bug13_whatif_reset_state(self):
        """BUG-13: Verify simulator reset restores clock to 0.0 and purges anomaly states."""
        self.simulator.simulation_time_hrs = 14.5
        self.simulator.inject_anomaly("M1-CNC-01", "COOLANT_FAILURE")
        self.assertTrue(self.simulator.anomaly_states["M1-CNC-01"]["active"])
        self.assertGreater(self.simulator.simulation_time_hrs, 0.0)

        self.simulator.reset()
        self.assertEqual(self.simulator.simulation_time_hrs, 0.0)
        self.assertFalse(self.simulator.anomaly_states["M1-CNC-01"]["active"])
        print(" [PASS] BUG-13: Simulator reset cleanly restores clock to 0.0 and clears anomaly buffers.")

    def test_17_bug14_risk_metric_consistency(self):
        """BUG-14: Verify is_machine_high_risk accurately flags critical/failed/degraded status."""
        healthy_m = {"status": "NORMAL", "failure_prob": 0.02, "health_score": 98.0}
        critical_m = {"status": "CRITICAL", "failure_prob": 0.20, "health_score": 75.0}
        failed_m = {"status": "FAILED", "failure_prob": 0.10, "health_score": 80.0}
        prob_m = {"status": "NORMAL", "failure_prob": 0.45, "health_score": 85.0}
        health_m = {"status": "NORMAL", "failure_prob": 0.15, "health_score": 55.0}

        self.assertFalse(self.scheduler.is_machine_high_risk(healthy_m))
        self.assertTrue(self.scheduler.is_machine_high_risk(critical_m))
        self.assertTrue(self.scheduler.is_machine_high_risk(failed_m))
        self.assertTrue(self.scheduler.is_machine_high_risk(prob_m))
        self.assertTrue(self.scheduler.is_machine_high_risk(health_m))
        print(" [PASS] BUG-14: Machine risk evaluation standardized across baseline and CP-SAT.")

    def test_18_bug15_rul_continuous_physics(self):
        """BUG-15: Verify synthetic RUL is grounded in continuous degradation physics."""
        df = self.generator.generate_training_dataset(n_samples=500)
        # Healthy low-hour machines should have high RUL (> 400h)
        healthy_low_hours = df[(df["failure"] == 0) & (df["operating_hours"] < 1500) & (df["temperature"] < 72.0) & (df["vibration"] < 1.8)]
        self.assertGreater(len(healthy_low_hours), 0)
        self.assertGreater(healthy_low_hours["rul_hours"].mean(), 400.0)

        # Failed machines must have low RUL (<= 35h)
        failed_machines = df[df["failure"] == 1]
        self.assertGreater(len(failed_machines), 0)
        self.assertLessEqual(failed_machines["rul_hours"].max(), 35.0)
        print(" [PASS] BUG-15: Synthetic RUL continuously coupled to degradation physics.")


if __name__ == "__main__":
    unittest.main()

