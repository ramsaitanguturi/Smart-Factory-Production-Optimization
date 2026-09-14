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
        cls.generator = TelemetryGenerator(random_seed=123)
        cls.pdm = PredictiveMaintenanceModel()
        cls.energy = EnergyPredictionModel()
        cls.delay = DelayPredictionModel()
        cls.simulator = FactorySimulator(db=cls.db)
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


if __name__ == "__main__":
    unittest.main()
