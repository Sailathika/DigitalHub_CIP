"""
MLflow tracking helpers.

Centralizes experiment setup so every training routine (CLV, churn) logs to
the same experiment with a consistent naming/tagging convention.
"""
from contextlib import contextmanager
from typing import Dict, Iterator

import mlflow

from app.config import settings

_initialized = False


def init_mlflow() -> None:
    global _initialized
    if _initialized:
        return
    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)
    _initialized = True


@contextmanager
def start_run(run_name: str, tags: Dict[str, str] = None) -> Iterator["mlflow.ActiveRun"]:
    init_mlflow()
    with mlflow.start_run(run_name=run_name, tags=tags or {}) as run:
        yield run


def log_training_run(params: Dict, metrics: Dict[str, float]) -> None:
    for key, value in params.items():
        mlflow.log_param(key, value)
    for key, value in metrics.items():
        mlflow.log_metric(key, value)
