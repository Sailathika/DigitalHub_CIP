import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    name: str
    description: str
    report_type: str
    generated_at: datetime


class ReportListResponse(BaseModel):
    reports: List[ReportOut]


class ReportGenerateRequest(BaseModel):
    include_segmentation: bool = True
    include_clv: bool = True
    include_churn: bool = True
    include_recommendations: bool = True


class ReportGenerateResponse(BaseModel):
    report: ReportOut
    download_url: str
