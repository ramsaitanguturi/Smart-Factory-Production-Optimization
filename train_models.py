"""
Model Training & Evaluation Pipeline
Generates synthetic sensor & degradation dataset, trains:
1. XGBoost Failure Classification Model (predicts probability of failure)
2. Random Forest RUL Regressor (predicts remaining useful life in hours)
Saves evaluation metrics (Accuracy, ROC-AUC, F1, Confusion Matrix, Feature Importances)
and serializes models into `models/saved/`.
"""
import time
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report, mean_squared_error, r2_score
)
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb

from config import MODELS_DIR
from data_generator.telemetry_generator import TelemetryGenerator
from models.pdm_model import PredictiveMaintenanceModel


def train_pdm_models(n_samples: int = 8000, random_state: int = 42):
    print("=" * 70)
    print(" INDUSTRY 4.0 PREDICTIVE MAINTENANCE: MODEL TRAINING PIPELINE")
    print("=" * 70)

    # 1. Generate Synthetic Training Telemetry
    print(f"\n[1/4] Generating {n_samples} physics-grounded synthetic telemetry records...")
    generator = TelemetryGenerator(random_seed=random_state)
    df = generator.generate_training_dataset(n_samples=n_samples)
    print(f"      Dataset shape: {df.shape}")
    print(f"      Failure rate in dataset: {df['failure'].mean() * 100:.2f}%")
    print(f"      Failure mode distribution:\n{df['failure_mode'].value_counts().to_string()}")

    # 2. Features and Targets
    feature_cols = PredictiveMaintenanceModel.FEATURE_COLS
    X = df[feature_cols]
    y_fail = df["failure"]
    y_rul = df["rul_hours"]

    X_train, X_test, y_fail_train, y_fail_test, y_rul_train, y_rul_test = train_test_split(
        X, y_fail, y_rul, test_size=0.20, random_state=random_state, stratify=y_fail
    )

    # 3. Train XGBoost Classifier for Failure Probability
    print("\n[2/4] Training XGBoost Failure Classifier...")
    t0 = time.time()
    clf = xgb.XGBClassifier(
        n_estimators=140,
        max_depth=5,
        learning_rate=0.07,
        subsample=0.85,
        colsample_bytree=0.85,
        eval_metric="logloss",
        random_state=random_state
    )
    clf.fit(X_train, y_fail_train)
    clf_time = time.time() - t0

    # Predictions & Evaluation
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_fail_test, y_pred)
    prec = precision_score(y_fail_test, y_pred, zero_division=0)
    rec = recall_score(y_fail_test, y_pred, zero_division=0)
    f1 = f1_score(y_fail_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_fail_test, y_proba)
    cm = confusion_matrix(y_fail_test, y_pred).tolist()

    print(f"      Training completed in {clf_time:.2f}s")
    print(f"      Accuracy:  {acc * 100:.2f}%")
    print(f"      Precision: {prec * 100:.2f}%")
    print(f"      Recall:    {rec * 100:.2f}%")
    print(f"      F1 Score:  {f1 * 100:.2f}%")
    print(f"      ROC-AUC:   {auc:.4f}")

    # 4. Train Random Forest for RUL Regression
    print("\n[3/4] Training Random Forest RUL Regressor...")
    t1 = time.time()
    rf_rul = RandomForestRegressor(
        n_estimators=100,
        max_depth=9,
        min_samples_split=4,
        random_state=random_state,
        n_jobs=-1
    )
    rf_rul.fit(X_train, y_rul_train)
    rul_time = time.time() - t1

    y_rul_pred = rf_rul.predict(X_test)
    rmse = float(np.sqrt(mean_squared_error(y_rul_test, y_rul_pred)))
    r2 = float(r2_score(y_rul_test, y_rul_pred))
    print(f"      RUL Regressor trained in {rul_time:.2f}s")
    print(f"      RUL RMSE: {rmse:.2f} hours")
    print(f"      RUL R²:   {r2:.4f}")

    # 5. Extract Feature Importances
    importances = {col: round(float(imp), 4) for col, imp in zip(feature_cols, clf.feature_importances_)}
    sorted_importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))
    print("\n      Top Predictive Maintenance Features:")
    for feat, val in sorted_importances.items():
        bar = "#" * int(val * 40)
        print(f"        {feat:18s} {val:.4f} | {bar}")

    # 6. Save Artifacts to models/saved/
    print("\n[4/4] Serializing models and evaluation metadata...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    clf_file = MODELS_DIR / "pdm_classifier.joblib"
    rul_file = MODELS_DIR / "pdm_rul_regressor.joblib"
    metrics_file = MODELS_DIR / "pdm_metrics.joblib"

    joblib.dump(clf, clf_file)
    joblib.dump(rf_rul, rul_file)

    metrics_payload = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "confusion_matrix": cm,
        "rul_rmse": round(rmse, 2),
        "rul_r2": round(r2, 4),
        "feature_importances": sorted_importances,
        "training_samples": n_samples,
        "features": feature_cols,
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    joblib.dump(metrics_payload, metrics_file)

    print(f"      Saved classifier: {clf_file.name}")
    print(f"      Saved regressor:  {rul_file.name}")
    print(f"      Saved metrics:    {metrics_file.name}")
    print("=" * 70)
    print(" MODEL TRAINING COMPLETE & READY FOR PRODUCTION INFERENCE")
    print("=" * 70)
    return metrics_payload


if __name__ == "__main__":
    train_pdm_models()
