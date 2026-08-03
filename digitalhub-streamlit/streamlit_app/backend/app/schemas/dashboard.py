from typing import List

from pydantic import BaseModel


class DashboardSalesPoint(BaseModel):
    month: str
    revenue: float


class DashboardGrowthPoint(BaseModel):
    month: str
    customers: int


class DashboardVendorRanking(BaseModel):
    vendor_id: str
    business_name: str
    revenue: float


class DashboardProductRanking(BaseModel):
    product_ref: str
    name: str
    revenue: float
    units_sold: int


class DashboardLowStockItem(BaseModel):
    product_ref: str
    name: str
    category: str
    stock_quantity: int


class DashboardOverviewResponse(BaseModel):
    total_revenue: float
    total_orders: int
    total_customers: int
    total_products: int
    total_vendors: int
    active_vendors: int
    pending_vendors: int
    low_stock_products: List[DashboardLowStockItem]
    sales_trend: List[DashboardSalesPoint]
    customer_growth: List[DashboardGrowthPoint]
    top_vendors: List[DashboardVendorRanking]
    top_products: List[DashboardProductRanking]
