import uuid

import pandas as pd
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.product import Product
from app.utils.response_utils import clean_number


class VendorSalesService:
    def __init__(self, db: Session):
        self.db = db

    def get_sales_analytics(self, vendor_id: uuid.UUID) -> dict:
        products = self.db.query(Product).filter(Product.vendor_id == vendor_id).all()
        product_ids = [p.id for p in products]
        orders = self.db.query(Order).filter(Order.product_id.in_(product_ids)).all() if product_ids else []

        total_revenue = sum(o.amount for o in orders)
        total_orders = len(orders)
        avg_order_value = clean_number(total_revenue / total_orders) if total_orders else 0.0

        sales_trend = []
        if orders:
            df = pd.DataFrame([{"order_date": o.order_date, "amount": o.amount} for o in orders])
            df["month"] = pd.to_datetime(df["order_date"]).dt.to_period("M")
            grouped = df.groupby("month")["amount"].sum().sort_index().tail(12)
            sales_trend = [{"month": m.strftime("%b"), "revenue": round(float(v), 2)} for m, v in grouped.items()]

        category_totals: dict = {}
        for product in products:
            category = product.category or "Uncategorized"
            category_totals[category] = category_totals.get(category, 0.0) + (product.total_revenue or 0)
        sales_by_category = [
            {"category": category, "revenue": round(revenue, 2)}
            for category, revenue in sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
        ]

        top_products = sorted(
            [
                {
                    "product_ref": p.product_ref,
                    "name": p.name,
                    "unitsSold": p.total_units_sold or 0,
                    "revenue": round(clean_number(p.total_revenue), 2),
                }
                for p in products
            ],
            key=lambda item: item["revenue"],
            reverse=True,
        )[:10]

        return {
            "total_revenue": round(clean_number(total_revenue), 2),
            "total_orders": total_orders,
            "average_order_value": round(avg_order_value, 2),
            "sales_trend": sales_trend,
            "sales_by_category": sales_by_category,
            "top_products": top_products,
        }
