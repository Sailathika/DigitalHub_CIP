import uuid

from sqlalchemy.orm import Session

from app.repository.vendor_product_repository import VendorProductRepository
from app.services.vendor_sales_service import VendorSalesService


class VendorDashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.products = VendorProductRepository(db)
        self.sales = VendorSalesService(db)

    def get_overview(self, vendor_id: uuid.UUID) -> dict:
        analytics = self.sales.get_sales_analytics(vendor_id)
        catalog = self.products.list_by_vendor(vendor_id)

        low_stock_threshold = 15
        low_stock_count = sum(1 for p in catalog if 0 < p.stock <= low_stock_threshold)

        return {
            "total_revenue": analytics["total_revenue"],
            "total_orders": analytics["total_orders"],
            "average_order_value": analytics["average_order_value"],
            "total_products": len(catalog),
            "low_stock_count": low_stock_count,
            "sales_trend": analytics["sales_trend"],
            "top_products": analytics["top_products"][:5],
        }
