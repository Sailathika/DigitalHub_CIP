import pandas as pd
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order
from app.models.product import Product
from app.models.user import User, UserRole, VendorStatus
from app.schemas.dashboard import (
    DashboardGrowthPoint,
    DashboardLowStockItem,
    DashboardOverviewResponse,
    DashboardProductRanking,
    DashboardSalesPoint,
    DashboardVendorRanking,
)
from app.utils.response_utils import clean_number

LOW_STOCK_THRESHOLD = 20


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> DashboardOverviewResponse:
        orders = self.db.query(Order).all()
        customers = self.db.query(Customer).all()
        products = self.db.query(Product).all()
        vendors = self.db.query(User).filter(User.role == UserRole.VENDOR).all()

        total_revenue = sum(o.amount for o in orders)
        total_orders = len(orders)
        total_customers = len(customers)
        total_products = len(products)
        total_vendors = len(vendors)
        active_vendors = sum(1 for v in vendors if v.vendor_status == VendorStatus.ACTIVE)
        pending_vendors = sum(1 for v in vendors if v.vendor_status == VendorStatus.PENDING)

        low_stock_products = [
            DashboardLowStockItem(
                product_ref=p.product_ref,
                name=p.name or p.product_ref,
                category=p.category or "Uncategorized",
                stock_quantity=int(p.stock_quantity),
            )
            for p in products
            if p.stock_quantity is not None and p.stock_quantity < LOW_STOCK_THRESHOLD
        ]
        low_stock_products = sorted(low_stock_products, key=lambda item: item.stock_quantity)[:10]

        sales_trend = []
        customer_growth = []
        if orders:
            orders_df = pd.DataFrame([{"order_date": o.order_date, "amount": o.amount} for o in orders])
            orders_df["month"] = pd.to_datetime(orders_df["order_date"]).dt.to_period("M")
            revenue_by_month = orders_df.groupby("month")["amount"].sum().sort_index().tail(12)
            sales_trend = [
                DashboardSalesPoint(month=m.strftime("%b"), revenue=round(float(v), 2))
                for m, v in revenue_by_month.items()
            ]

        if customers:
            customers_df = pd.DataFrame([{"first_purchase_date": c.first_purchase_date} for c in customers])
            customers_df["month"] = pd.to_datetime(customers_df["first_purchase_date"]).dt.to_period("M")
            new_customers_by_month = customers_df.groupby("month").size().sort_index().tail(12)
            customer_growth = [
                DashboardGrowthPoint(month=m.strftime("%b"), customers=int(v))
                for m, v in new_customers_by_month.items()
            ]

        vendor_revenue: dict = {}
        for product in products:
            if product.vendor_id is None:
                continue
            vendor_revenue[product.vendor_id] = vendor_revenue.get(product.vendor_id, 0.0) + (product.total_revenue or 0)
        vendor_by_id = {v.id: v for v in vendors}
        top_vendors = sorted(
            [
                DashboardVendorRanking(
                    vendor_id=str(vendor_id),
                    business_name=(vendor_by_id[vendor_id].business_name or vendor_by_id[vendor_id].full_name)
                    if vendor_id in vendor_by_id else "Unknown Vendor",
                    revenue=round(clean_number(revenue), 2),
                )
                for vendor_id, revenue in vendor_revenue.items()
                if vendor_id in vendor_by_id
            ],
            key=lambda item: item.revenue,
            reverse=True,
        )[:5]

        top_products = sorted(
            [
                DashboardProductRanking(
                    product_ref=p.product_ref,
                    name=p.name or p.product_ref,
                    revenue=round(clean_number(p.total_revenue), 2),
                    units_sold=p.total_units_sold or 0,
                )
                for p in products
            ],
            key=lambda item: item.revenue,
            reverse=True,
        )[:5]

        return DashboardOverviewResponse(
            total_revenue=round(clean_number(total_revenue), 2),
            total_orders=total_orders,
            total_customers=total_customers,
            total_products=total_products,
            total_vendors=total_vendors,
            active_vendors=active_vendors,
            pending_vendors=pending_vendors,
            low_stock_products=low_stock_products,
            sales_trend=sales_trend,
            customer_growth=customer_growth,
            top_vendors=top_vendors,
            top_products=top_products,
        )
