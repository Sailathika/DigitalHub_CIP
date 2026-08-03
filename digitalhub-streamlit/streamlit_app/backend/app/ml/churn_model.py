"""
Customer churn prediction.

Most uploaded transaction datasets don't carry an explicit "churned" label,
so we derive one: a customer is treated as churned if their recency is
beyond 1.5x the dataset's median recency (a common practical heuristic).
A Random Forest classifier is then trained to predict that label from
RFM-style features, so the model captures *why* a customer looks churned
(feature importances) rather than just thresholding recency directly.
"""
import uuid
from pathlib import Path
from typing import Dict, Tuple

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from app.config import settings
from app.ml.mlflow_utils import start_run

FEATURE_COLUMNS = ["recency_days", "frequency", "monetary", "avg_order_value"]


def derive_churn_label(customers: pd.DataFrame) -> pd.Series:
    median_recency = customers["recency_days"].median()
    threshold = median_recency * 1.5
    return (customers["recency_days"] > threshold).astype(int)


def train_churn_model(customers: pd.DataFrame, dataset_id: uuid.UUID) -> Tuple[object, Dict, str, Path]:
    df = customers.dropna(subset=FEATURE_COLUMNS).copy()
    if len(df) < 10:
        raise ValueError("Need at least 10 customers with complete data to train a churn model")

    df["churned"] = derive_churn_label(df)
    if df["churned"].nunique() < 2:
        # Degenerate case (all same label) — force at least one minority
        # example so the classifier has both classes to learn from.
        flip_idx = df["recency_days"].idxmax()
        df.loc[flip_idx, "churned"] = 1 - df["churned"].iloc[0]

    X = df[FEATURE_COLUMNS].values
    y = df["churned"].values

    test_size = 0.2 if len(df) >= 20 else max(1 / len(df), 0.1)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y if df["churned"].nunique() > 1 else None
    )

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=6,
        min_samples_leaf=2,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, zero_division=0))
    recall = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))

    feature_importance = {
        feature: round(float(importance), 4)
        for feature, importance in zip(FEATURE_COLUMNS, model.feature_importances_)
    }

    model_version = f"churn-{dataset_id}-{pd.Timestamp.utcnow().strftime('%Y%m%dT%H%M%S')}"
    artifact_path = settings.MODELS_DIR / f"{model_version}.joblib"
    joblib.dump(model, artifact_path)

    with start_run(run_name=model_version, tags={"dataset_id": str(dataset_id), "model": "churn"}) as run:
        mlflow.log_params(
            {
                "n_estimators": 300,
                "max_depth": 6,
                "min_samples_leaf": 2,
                "features": ",".join(FEATURE_COLUMNS),
                "n_samples": len(df),
            }
        )
        mlflow.log_metrics(
            {"accuracy": accuracy, "precision": precision, "recall": recall, "f1_score": f1}
        )
        for feature, importance in feature_importance.items():
            mlflow.log_metric(f"importance_{feature}", importance)
        mlflow.sklearn.log_model(model, artifact_path="model")
        run_id = run.info.run_id

    metrics = {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "feature_importance": feature_importance,
    }
    return model, metrics, run_id, artifact_path


def predict_churn(model, customers: pd.DataFrame) -> np.ndarray:
    df = customers.copy()
    for col in FEATURE_COLUMNS:
        df[col] = df[col].fillna(df[col].median() if df[col].notna().any() else 0)
    return model.predict_proba(df[FEATURE_COLUMNS].values)[:, 1]


def risk_level(probability: float) -> str:
    if probability < 0.33:
        return "Low"
    if probability < 0.66:
        return "Medium"
    return "High"


def load_churn_model(artifact_path: Path):
    return joblib.load(artifact_path)
