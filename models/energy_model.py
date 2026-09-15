"""
Energy Consumption Prediction Model
Estimates power demand (kW), total energy usage (kWh), and costs for
assigned jobs based on machine physics, workload, and mechanical wear.
"""
from typing import Dict, Any, List
from config import MACHINES, ENERGY_PEAK_TARIFF, ENERGY_OFFPEAK_TARIFF


class EnergyPredictionModel:
    def __init__(self):
        pass

    def predict_job_energy(
        self,
        machine_id: str,
        processing_time_hrs: float,
        load_factor: float = 0.85,
        health_score: float = 95.0,
        start_hour_of_day: float = 10.0
    ) -> Dict[str, Any]:
        """
        Calculates expected energy metrics for a scheduled order.
        Worn machines (lower health_score) suffer increased friction and thermal dissipation losses,
        consuming 5% to 25% more electricity.
        """
        m_cfg = MACHINES.get(machine_id, MACHINES["M1-CNC-01"])
        nominal_kw = m_cfg["nominal_power_kw"]
        idle_kw = m_cfg["idle_power_kw"]

        # Friction / degradation multiplier
        wear_overhead = max(0.0, (100.0 - health_score) / 100.0) * 0.22  # up to +22% power
        effective_power_kw = (idle_kw + (nominal_kw - idle_kw) * (0.35 + 0.65 * load_factor)) * (1.0 + wear_overhead)
        
        total_kwh = effective_power_kw * processing_time_hrs

        # Calculate exact continuous overlap hours with peak window [14.0, 19.0]
        total_peak_hours = 0.0
        cur_start = start_hour_of_day
        rem_duration = processing_time_hrs

        while rem_duration > 0:
            day_start = cur_start % 24.0
            chunk_duration = min(rem_duration, 24.0 - day_start)
            day_end = day_start + chunk_duration
            # Overlap between [day_start, day_end] and [14.0, 19.0]
            overlap = max(0.0, min(day_end, 19.0) - max(day_start, 14.0))
            total_peak_hours += overlap
            cur_start += chunk_duration
            rem_duration -= chunk_duration

        peak_ratio = total_peak_hours / max(0.01, processing_time_hrs)
        peak_ratio = min(1.0, max(0.0, peak_ratio))
        
        effective_tariff = (peak_ratio * ENERGY_PEAK_TARIFF) + ((1.0 - peak_ratio) * ENERGY_OFFPEAK_TARIFF)
        estimated_cost_usd = total_kwh * effective_tariff

        return {
            "machine_id": machine_id,
            "avg_power_kw": round(effective_power_kw, 2),
            "total_kwh": round(total_kwh, 2),
            "estimated_cost_usd": round(estimated_cost_usd, 2),
            "wear_penalty_pct": round(wear_overhead * 100.0, 1),
            "peak_ratio": round(peak_ratio, 2)
        }

    def predict_factory_power(self, active_machines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates instantaneous power and projected 24-hr energy profile for all machines."""
        total_current_kw = sum(m.get("power_kw", 0.0) for m in active_machines)
        peak_capacity_kw = sum(MACHINES[m["machine_id"]]["nominal_power_kw"] for m in active_machines if m["machine_id"] in MACHINES)
        
        load_pct = (total_current_kw / peak_capacity_kw * 100.0) if peak_capacity_kw > 0 else 0.0
        projected_daily_kwh = total_current_kw * 24.0

        return {
            "current_total_kw": round(total_current_kw, 2),
            "peak_capacity_kw": round(peak_capacity_kw, 2),
            "factory_load_pct": round(load_pct, 1),
            "projected_daily_kwh": round(projected_daily_kwh, 1)
        }
