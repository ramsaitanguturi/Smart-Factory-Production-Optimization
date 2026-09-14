"""
Telemetry & Sensor Data Generator
Physics-informed synthetic data generator that models realistic machine degradation,
bearing vibration harmonics, thermal dissipation issues, hydraulic pressure drops,
and power consumption variations.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from config import MACHINES, SENSOR_SPECS, STATUS_NORMAL, STATUS_WARNING, STATUS_CRITICAL, STATUS_MAINTENANCE, STATUS_FAILED


class TelemetryGenerator:
    def __init__(self, random_seed: int = 42):
        self.rng = np.random.default_rng(random_seed)

    def generate_single_reading(
        self,
        machine_id: str,
        current_status: str = STATUS_NORMAL,
        operating_hours: float = 1200.0,
        load_factor: float = 0.8,
        anomaly_factor: float = 0.0  # 0.0 = completely healthy, 1.0 = near failure
    ) -> Dict[str, Any]:
        """
        Generates realistic sensor telemetry for a machine given its operating conditions.
        """
        m_cfg = MACHINES.get(machine_id, MACHINES["M1-CNC-01"])
        m_type = m_cfg["type"]
        nominal_kw = m_cfg["nominal_power_kw"]
        idle_kw = m_cfg["idle_power_kw"]
        base_rpm = m_cfg["max_rpm"]

        # Base noise
        noise_temp = self.rng.normal(0.0, 0.8)
        noise_vib = self.rng.normal(0.0, 0.08)
        noise_rpm = self.rng.normal(0.0, base_rpm * 0.008)
        noise_pres = self.rng.normal(0.0, 1.2)
        noise_pwr = self.rng.normal(0.0, 0.3)

        # Baseline values
        base_temp = 62.0 + (load_factor * 8.0)
        base_vib = 1.35 + (load_factor * 0.35)
        base_pres = 105.0 - (load_factor * 3.0)
        active_kw = idle_kw + (nominal_kw - idle_kw) * (0.3 + 0.7 * load_factor)

        # Operating hours wear penalty (gradual baseline drift)
        wear_hours_factor = min(1.0, operating_hours / 4000.0)
        wear_vib_drift = wear_hours_factor * 0.6
        wear_temp_drift = wear_hours_factor * 4.0

        # State / Anomaly escalation
        if current_status == STATUS_NORMAL:
            eff_anomaly = anomaly_factor
        elif current_status == STATUS_WARNING:
            eff_anomaly = max(0.45, anomaly_factor)
        elif current_status == STATUS_CRITICAL:
            eff_anomaly = max(0.85, anomaly_factor)
        elif current_status == STATUS_MAINTENANCE:
            # Idling or offline during maintenance
            return {
                "temperature": round(28.0 + self.rng.normal(0, 0.5), 2),
                "vibration": round(0.05 + abs(self.rng.normal(0, 0.02)), 3),
                "rpm": 0.0,
                "pressure": round(15.0 + self.rng.normal(0, 0.5), 1),
                "power_kw": round(0.4, 2),
                "health_score": 98.0,
                "failure_prob": 0.005,
                "status": STATUS_MAINTENANCE
            }
        elif current_status == STATUS_FAILED:
            return {
                "temperature": round(95.0 + self.rng.normal(0, 2.0), 2),
                "vibration": round(6.5 + abs(self.rng.normal(0, 0.5)), 3),
                "rpm": 0.0,
                "pressure": round(25.0 + self.rng.normal(0, 2.0), 1),
                "power_kw": round(0.5, 2),
                "health_score": 5.0,
                "failure_prob": 0.98,
                "status": STATUS_FAILED
            }
        else:
            eff_anomaly = anomaly_factor

        # Escalations based on anomaly
        temp = base_temp + wear_temp_drift + (eff_anomaly ** 1.6) * 45.0 + noise_temp
        vib = base_vib + wear_vib_drift + (eff_anomaly ** 1.8) * 4.8 + noise_vib
        pres = base_pres - (eff_anomaly ** 1.3) * 45.0 + noise_pres
        
        # RPM instability under high vibration & bearing resistance
        rpm_drop_ratio = (eff_anomaly ** 2.0) * 0.28
        rpm = (base_rpm * (1.0 - rpm_drop_ratio)) + noise_rpm
        
        # Power increases under mechanical strain
        power_friction = (eff_anomaly ** 1.4) * (nominal_kw * 0.35)
        pwr = active_kw + power_friction + noise_pwr

        # Bounding to physical limits
        temp = max(35.0, float(temp))
        vib = max(0.1, float(vib))
        rpm = max(0.0, float(rpm))
        pres = max(10.0, float(pres))
        pwr = max(idle_kw, float(pwr))

        # Health score calculation (100 = brand new, 0 = broken)
        health = 100.0 - (
            (max(0, temp - 70.0) / 40.0) * 35.0 +
            (max(0, vib - 2.0) / 4.0) * 40.0 +
            (max(0, 95.0 - pres) / 50.0) * 15.0 +
            wear_hours_factor * 10.0
        )
        health = max(2.0, min(100.0, health))

        # Failure probability (ground truth proxy)
        fail_prob = 1.0 / (1.0 + np.exp((health - 42.0) / 9.0))
        fail_prob = float(np.clip(fail_prob, 0.005, 0.99))

        # Compute status tag
        if fail_prob > 0.60 or health < 35.0:
            calc_status = STATUS_CRITICAL
        elif fail_prob > 0.22 or health < 65.0:
            calc_status = STATUS_WARNING
        else:
            calc_status = STATUS_NORMAL

        return {
            "temperature": round(temp, 2),
            "vibration": round(vib, 3),
            "rpm": round(rpm, 1),
            "pressure": round(pres, 1),
            "power_kw": round(pwr, 2),
            "health_score": round(health, 1),
            "failure_prob": round(fail_prob, 4),
            "status": calc_status
        }

    def generate_training_dataset(self, n_samples: int = 8000) -> pd.DataFrame:
        """
        Generates a rich, balanced training dataset reflecting realistic Industry 4.0
        physics and machine degradation modes:
        - Heat dissipation failure (HDF): High temp + high load + low pressure
        - Power failure / overload (PWF): High power + high torque/rpm drop
        - Tool wear / Bearing wear (TWF): High vibration + high operating hours
        - Random overstrain failure (OSF): Spikes in power + temperature
        """
        rows = []
        machine_keys = list(MACHINES.keys())

        for _ in range(n_samples):
            mid = self.rng.choice(machine_keys)
            m_cfg = MACHINES[mid]
            nominal_kw = m_cfg["nominal_power_kw"]
            idle_kw = m_cfg["idle_power_kw"]
            base_rpm = m_cfg["max_rpm"]

            # Sample operating hours
            hours = self.rng.uniform(50.0, 5000.0)
            load = self.rng.uniform(0.3, 1.1)

            # Assign synthetic health state (70% healthy, 18% degrading, 12% critical failure)
            state_rand = self.rng.uniform(0.0, 1.0)
            if state_rand < 0.70:
                anomaly = self.rng.uniform(0.0, 0.25)
                fail_mode = "None"
            elif state_rand < 0.88:
                anomaly = self.rng.uniform(0.30, 0.65)
                fail_mode = self.rng.choice(["Heat Warning", "Vibration Warning", "Pressure Drift"])
            else:
                anomaly = self.rng.uniform(0.70, 1.0)
                fail_mode = self.rng.choice(["Heat Dissipation Failure", "Bearing Failure", "Tool Wear Failure", "Overstrain Failure"])

            # Specific failure mode physics injection
            temp_boost = 0.0
            vib_boost = 0.0
            pres_drop = 0.0
            power_boost = 0.0

            if fail_mode == "Heat Dissipation Failure":
                temp_boost = self.rng.uniform(28.0, 45.0)
                pres_drop = self.rng.uniform(25.0, 45.0)
            elif fail_mode == "Bearing Failure":
                vib_boost = self.rng.uniform(2.8, 5.0)
                power_boost = self.rng.uniform(0.2, 0.4) * nominal_kw
            elif fail_mode == "Tool Wear Failure":
                vib_boost = self.rng.uniform(2.0, 4.0)
                hours += self.rng.uniform(1500.0, 3000.0)
            elif fail_mode == "Overstrain Failure":
                power_boost = self.rng.uniform(0.3, 0.6) * nominal_kw
                temp_boost = self.rng.uniform(15.0, 30.0)

            # Compute sensors
            wear_factor = min(1.0, hours / 4500.0)
            temp = 60.0 + (load * 8.0) + (wear_factor * 4.0) + (anomaly * 25.0) + temp_boost + self.rng.normal(0, 1.0)
            vib = 1.3 + (load * 0.3) + (wear_factor * 0.8) + (anomaly * 2.8) + vib_boost + self.rng.normal(0, 0.1)
            pres = 105.0 - (load * 3.0) - (anomaly * 30.0) - pres_drop + self.rng.normal(0, 1.5)
            
            rpm_penalty = (anomaly ** 1.8) * 0.25
            rpm = (base_rpm * (1.0 - rpm_penalty)) + self.rng.normal(0, base_rpm * 0.01)

            active_kw = idle_kw + (nominal_kw - idle_kw) * (0.3 + 0.7 * load)
            power = active_kw + (anomaly * nominal_kw * 0.25) + power_boost + self.rng.normal(0, 0.3)

            # Target failure classification
            # Failure occurs if severe physical degradation conditions are met
            is_failure = int(
                (temp >= 88.0 and pres <= 75.0) or
                (vib >= 4.0) or
                (temp >= 96.0) or
                (power >= nominal_kw * 1.35) or
                (hours > 4200.0 and vib >= 3.4) or
                (anomaly >= 0.78)
            )

            # RUL calculation in hours
            if is_failure:
                rul_hrs = self.rng.uniform(1.0, 35.0)
            elif anomaly > 0.45:
                rul_hrs = self.rng.uniform(40.0, 180.0)
            else:
                rul_hrs = self.rng.uniform(220.0, 800.0)

            rows.append({
                "machine_id": mid,
                "machine_type": m_cfg["type"],
                "temperature": round(max(30.0, temp), 2),
                "vibration": round(max(0.1, vib), 3),
                "rpm": round(max(0.0, rpm), 1),
                "pressure": round(max(10.0, pres), 1),
                "power_kw": round(max(idle_kw, power), 2),
                "operating_hours": round(hours, 1),
                "load_factor": round(load, 2),
                "failure": is_failure,
                "failure_mode": fail_mode,
                "rul_hours": round(rul_hrs, 1)
            })

        df = pd.DataFrame(rows)
        return df
