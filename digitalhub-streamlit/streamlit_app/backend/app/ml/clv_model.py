"""
Customer Lifetime Value (CLV) prediction.

Trains a Gradient Boosting regressor on RFM-derived features to predict
total historical monetary value as a proxy for future CLV. Tracked in
MLflow; the fitted model is persisted with joblib for later inference.
"""
import uuid
from pathlib import Path
from typing import Dict, Tuple

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from app.config import settings
from app.ml.mlflow_utils import start_run

FEATURE_COLUMNS = ["recency_days", "frequency", "avg_order_value"]
TARGET_COLUMN = "monetary"


def train_clv_model(customers: pd.DataFrame, dataset_id: uuid.UUID) -> Tuple[object, Dict[str, float], str, Path]:
    df = customers.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN])
    if len(df) < 10:
        raise ValueError("Need at least 10 customers with complete data to train a CLV model")

    X = df[FEATURE_COLUMNS].values
    y = df[TARGET_COLUMN].values

    test_size = 0.2 if len(df) >= 20 else max(1 / len(df), 0.1)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    r2 = float(r2_score(y_test, y_pred)) if len(y_test) > 1 else 0.0
    mae = float(mean_absolute_error(y_test, y_pred))

    model_version = f"clv-{dataset_id}-{pd.Timestamp.utcnow().strftime('%Y%m%dT%H%M%S')}"
    artifact_path = settings.MODELS_DIR / f"{model_version}.joblib"
    joblib.dump(model, artifact_path)

    with start_run(run_name=model_version, tags={"dataset_id": str(dataset_id), "model": "clv"}) as run:
        mlflow.log_params(
            {
                "n_estimators": 200,
                "learning_rate": 0.05,
                "max_depth": 3,
                "features": ",".join(FEATURE_COLUMNS),
                "n_samples": len(df),
            }
        )
        mlflow.log_metrics({"r2_score": r2, "mae": mae})
        mlflow.sklearn.log_model(model, artifact_path="model")
        run_id = run.info.run_id

    metrics = {"r2_score": round(r2, 4), "mae": round(mae, 2)}
    return model, metrics, run_id, artifact_path


def predict_clv(model, customers: pd.DataFrame) -> np.ndarray:
    df = customers.copy()
    for col in FEATURE_COLUMNS:
        df[col] = df[col].fillna(df[col].median() if df[col].notna().any() else 0)
    predictions = model.predict(df[FEATURE_COLUMNS].values)
    return np.clip(predictions, a_min=0, a_max=None)


def load_clv_model(artifact_path: Path):
    return joblib.load(artifact_path)
