import uuid
from typing import List

from pydantic import BaseModel


class KPI(BaseModel):
    id: str
    label: str
    value: float
    format: str  # "currency" | "number"
    delta: float
    trend: List[float]


class CustomerOverviewResponse(BaseModel):
    dataset_id: uuid.UUID
    kpis: List[KPI]
    total_customers: int
    returning_customers: int
    active_customers: int
    average_order_value: float
    average_basket_size: float
    purchase_frequency: float


class SegmentSlice(BaseModel):
    name: str
    value: int


class RetentionPoint(BaseModel):
    month: str
    retention: float


class TopCustomer(BaseModel):
    id: str
    name: str
    orders: int
    lifetime_value: float


class CustomerAnalyticsResponse(BaseModel):
    dataset_id: uuid.UUID
    segments: List[SegmentSlice]
    retention_trend: List[RetentionPoint]
    top_customers: List[TopCustomer]


class SalesTrendPoint(BaseModel):
    month: str
    revenue: float


class CategoryRevenue(BaseModel):
    category: str
    revenue: float


class SalesAnalyticsResponse(BaseModel):
    dataset_id: uuid.UUID
    sales_trend: List[SalesTrendPoint]
    sales_by_category: List[CategoryRevenue]
