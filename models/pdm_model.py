"""
Predictive Maintenance (PdM) Machine Learning Model
Uses XGBoost Classifier & Random Forest Regressor to predict:
1. Machine failure probability (0.0 to 1.0)
2. Machine Health Index (0 to 100%)
3. Estimated Remaining Useful Life (RUL in hours)
4. Primary Risk Factor / Degradation Cause
"""
import joblib
import warnings
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd

# Suppress NumPy 2.x array shape mutation deprecation warning from joblib unpickling
warnings.filterwarnings("ignore", category=DeprecationWarning)

from config import MODELS_DIR


class PredictiveMaintenanceModel:
    FEATURE_COLS = [
        "temperature", "vibration", "rpm", "pressure",
        "power_kw", "operating_hours", "load_factor"
    ]

    def __init__(self, model_dir: Path = MODELS_DIR):
        self.model_dir = model_dir
        self.clf_path = self.model_dir / "pdm_classifier.joblib"
        self.rul_path = self.model_dir / "pdm_rul_regressor.joblib"
        self.metrics_path = self.model_dir / "pdm_metrics.joblib"
        
        self.classifier = None
        self.rul_regressor = None
        self.evaluation_metrics = {}
        self.load_models()

    def load_models(self) -> bool:
        """Loads serialized models from disk if available."""
        if self.clf_path.exists() and self.rul_path.exists():
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.classifier = joblib.load(self.clf_path)
                    self.rul_regressor = joblib.load(self.rul_path)
                    if self.metrics_path.exists():
                        self.evaluation_metrics = joblib.load(self.metrics_path)
                return True
            except Exception as e:
                print(f"Error loading PdM models: {e}")
                return False
        return False

    def predict_risk(
        self,
        temperature: float,
        vibration: float,
        rpm: float,
        pressure: float,
        power_kw: float,
        operating_hours: float = 1500.0,
        load_factor: float = 0.8
    ) -> Dict[str, Any]:
        """
        Runs inference on live sensor telemetry to predict failure probability,
        health index, RUL, and primary root cause.
        """
        features_df = pd.DataFrame([{
            "temperature": temperature,
            "vibration": vibration,
            "rpm": rpm,
            "pressure": pressure,
            "power_kw": power_kw,
            "operating_hours": operating_hours,
            "load_factor": load_factor
        }])[self.FEATURE_COLS]

        if self.classifier is not None and self.rul_regressor is not None:
            proba = float(self.classifier.predict_proba(features_df)[0][1])
            rul = float(max(1.0, self.rul_regressor.predict(features_df)[0]))
        else:
            # Calibrated analytical fallback in case model file has not yet been generated
            health_penalty = (
                (max(0.0, temperature - 72.0) / 35.0) * 35.0 +
                (max(0.0, vibration - 2.0) / 4.0) * 40.0 +
                (max(0.0, 95.0 - pressure) / 45.0) * 15.0 +
                (min(1.0, operating_hours / 4000.0) * 10.0)
            )
            calc_health = max(5.0, min(100.0, 100.0 - health_penalty))
            proba = float(np.clip(1.0 / (1.0 + np.exp((calc_health - 45.0) / 9.0)), 0.01, 0.99))
            rul = float(np.clip(calc_health * 7.5, 5.0, 750.0))

        # Health index derived from failure probability & sensor degradation
        health_score = round(float(np.clip((1.0 - proba) * 95.0 + 5.0, 1.0, 100.0)), 1)
        rul_hours = round(rul, 1)

        # Root Cause Analysis
        causes = []
        if temperature > 85.0:
            causes.append(f"High Temp ({temperature:.1f}°C)")
        if vibration > 3.5:
            causes.append(f"Excessive Vibration ({vibration:.2f} mm/s)")
        if pressure < 80.0:
            causes.append(f"Low Hydraulic Pressure ({pressure:.1f} bar)")
        if power_kw > 35.0:
            causes.append(f"Motor Overload ({power_kw:.1f} kW)")
        if operating_hours > 3500.0:
            causes.append(f"High Operating Hours ({operating_hours:.0f} hrs)")

        primary_cause = ", ".join(causes) if causes else "Normal Operating Conditions"

        # Maintenance recommendation
        if proba >= 0.65:
            recommendation = "CRITICAL: Immediate shutdown & overhaul required to prevent catastrophic failure."
            action_code = "SHUTDOWN_IMMEDIATE"
        elif proba >= 0.30:
            recommendation = "WARNING: Schedule inspection & lubrication within next 8-12 operating hours."
            action_code = "INSPECT_SOON"
        else:
            recommendation = "NOMINAL: Machine operating within healthy tolerances."
            action_code = "NORMAL"

        return {
            "failure_probability": round(proba, 4),
            "health_score": health_score,
            "rul_hours": rul_hours,
            "primary_cause": primary_cause,
            "recommendation": recommendation,
            "action_code": action_code,
        }

    def get_feature_importances(self) -> Dict[str, float]:
        """Returns feature importances from trained model or representative defaults."""
        if self.classifier is not None and hasattr(self.classifier, "feature_importances_"):
            importances = self.classifier.feature_importances_
            return {col: round(float(imp), 4) for col, imp in zip(self.FEATURE_COLS, importances)}
        return {
            "vibration": 0.32,
            "temperature": 0.28,
            "pressure": 0.16,
            "power_kw": 0.12,
            "operating_hours": 0.08,
            "rpm": 0.03,
            "load_factor": 0.01,
        }
