import uuid
from typing import Dict, List

from pydantic import BaseModel


class RFMRecord(BaseModel):
    customer_id: uuid.UUID
    customer_ref: str
    name: str
    recency_days: int
    frequency: int
    monetary: float
    r_score: int
    f_score: int
    m_score: int
    rfm_score: str
    segment_label: str


class SegmentDistribution(BaseModel):
    segment_label: str
    customer_count: int
    total_monetary: float


class RFMResponse(BaseModel):
    dataset_id: uuid.UUID
    records: List[RFMRecord]
    distribution: List[SegmentDistribution]


class CLVTrainResponse(BaseModel):
    dataset_id: uuid.UUID
    model_version: str
    mlflow_run_id: str
    r2_score: float
    mae: float
    trained_on_customers: int


class CLVPredictionRecord(BaseModel):
    customer_id: uuid.UUID
    customer_ref: str
    name: str
    predicted_clv: float


class CLVPredictResponse(BaseModel):
    dataset_id: uuid.UUID
    model_version: str
    predictions: List[CLVPredictionRecord]


class ChurnTrainResponse(BaseModel):
    dataset_id: uuid.UUID
    model_version: str
    mlflow_run_id: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    feature_importance: Dict[str, float]
    trained_on_customers: int


class ChurnPredictionRecord(BaseModel):
    customer_id: uuid.UUID
    customer_ref: str
    name: str
    churn_probability: float
    risk_level: str


class ChurnPredictResponse(BaseModel):
    dataset_id: uuid.UUID
    model_version: str
    predictions: List[ChurnPredictionRecord]
    feature_importance: Dict[str, float]
