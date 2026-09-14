"""
Production Delay Prediction Model
Calculates the probability that a production order will miss its deadline.
Evaluates machine health risk, queue bottlenecks, deadline buffer slack, and priority urgency.
"""
import numpy as np
from typing import Dict, Any


class DelayPredictionModel:
    def __init__(self):
        pass

    def predict_delay_risk(
        self,
        processing_time_hrs: float,
        deadline_hrs: float,
        scheduled_start_hrs: float,
        machine_failure_prob: float,
        machine_health_score: float,
        priority: str = "Medium"
    ) -> Dict[str, Any]:
        """
        Calculates delay probability and estimated tardiness (hours past deadline).
        """
        scheduled_end = scheduled_start_hrs + processing_time_hrs
        slack_buffer = deadline_hrs - scheduled_end  # Positive = buffer, Negative = delayed already

        # Baseline delay probability from schedule buffer
        if slack_buffer <= 0:
            base_risk = 0.95
        elif slack_buffer < 2.0:
            base_risk = 0.65
        elif slack_buffer < 5.0:
            base_risk = 0.35
        elif slack_buffer < 10.0:
            base_risk = 0.15
        else:
            base_risk = 0.04

        # Machine unreliability penalty:
        # If machine failure probability is high, the machine might break down mid-operation,
        # triggering unplanned repair downtime (avg 6-12 hours) and thus causing delays!
        unplanned_downtime_exposure = machine_failure_prob * 8.0  # expected repair hours added
        adjusted_slack = slack_buffer - unplanned_downtime_exposure

        # Compound risk formula
        compound_risk = 1.0 / (1.0 + np.exp(adjusted_slack / 2.5))
        # Weight by machine health
        if machine_health_score < 40.0:
            compound_risk = max(compound_risk, 0.85)
        elif machine_health_score < 65.0:
            compound_risk = max(compound_risk, 0.48)

        final_prob = float(np.clip(compound_risk, 0.02, 0.99))
        is_delayed = int(final_prob > 0.50 or slack_buffer < 0.0)
        expected_tardiness = round(max(0.0, -slack_buffer + (machine_failure_prob * 6.0)), 1)

        # Risk category
        if final_prob > 0.70:
            risk_category = "CRITICAL DELAY RISK"
        elif final_prob > 0.35:
            risk_category = "MODERATE DELAY RISK"
        else:
            risk_category = "ON SCHEDULE"

        return {
            "delay_probability": round(final_prob, 3),
            "is_delayed": is_delayed,
            "slack_buffer_hrs": round(slack_buffer, 1),
            "expected_tardiness_hrs": expected_tardiness,
            "risk_category": risk_category,
            "scheduled_start_hrs": round(scheduled_start_hrs, 1),
            "scheduled_end_hrs": round(scheduled_end, 1)
        }
