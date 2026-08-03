import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DatasetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    original_filename: str
    file_type: str
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    status: str
    uploaded_at: datetime


class DatasetListResponse(BaseModel):
    datasets: List[DatasetOut]


class ValidationCheck(BaseModel):
    id: int
    check: str
    detail: str
    status: str  # Passed | Warning | Failed


class ValidationResponse(BaseModel):
    dataset_id: uuid.UUID
    checks: List[ValidationCheck]
    passed: int
    total: int


class CleaningIssue(BaseModel):
    id: int
    issue: str
    affected_rows: int
    suggestion: str
    severity: str  # low | medium | high


class CleaningResponse(BaseModel):
    dataset_id: uuid.UUID
    issues: List[CleaningIssue]
    rows_before: int
    rows_after: int


class ETLStageResult(BaseModel):
    stage: str
    status: str
    message: str
    rows_before: Optional[int] = None
    rows_after: Optional[int] = None


class ETLRunResponse(BaseModel):
    dataset_id: uuid.UUID
    status: str
    stages: List[ETLStageResult]
    customers_loaded: int
    orders_loaded: int
    products_loaded: int
