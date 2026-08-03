import uuid
from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from app.ml.rfm import compute_rfm
from app.repository.customer_repository import CustomerRepository, OrderRepository, ProductRepository
from app.repository.prediction_repository import SegmentationRepository
from app.schemas.customer import (
    CategoryRevenue,
    CustomerAnalyticsResponse,
    CustomerOverviewResponse,
    KPI,
    RetentionPoint,
    SalesAnalyticsResponse,
    SalesTrendPoint,
    SegmentSlice,
    TopCustomer,
)
from app.utils.response_utils import clean_number, get_dataset_or_404


def _customers_to_frame(customers) -> pd.DataFrame:
    if not customers:
        return pd.DataFrame(
            columns=["id", "customer_ref", "name", "total_orders", "total_spent", "avg_order_value",
                     "first_purchase_date", "last_purchase_date"]
        )
    return pd.DataFrame(
        [
            {
                "id": c.id,
                "customer_ref": c.customer_ref,
                "name": c.name,
                "total_orders": c.total_orders,
                "total_spent": c.total_spent,
                "avg_order_value": c.avg_order_value,
                "first_purchase_date": c.first_purchase_date,
                "last_purchase_date": c.last_purchase_date,
            }
            for c in customers
        ]
    )


def build_rfm_feature_frame(customers_df: pd.DataFrame) -> pd.DataFrame:
    if customers_df.empty:
        return customers_df
    snapshot = customers_df["last_purchase_date"].max() + pd.Timedelta(days=1)
    df = customers_df.copy()
    df["recency_days"] = (snapshot - df["last_purchase_date"]).dt.days
    df["frequency"] = df["total_orders"]
    df["monetary"] = df["total_spent"]
    return df


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.order_repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)
        self.segment_repo = SegmentationRepository(db)

    def customer_overview(self, dataset_id: uuid.UUID) -> CustomerOverviewResponse:
        get_dataset_or_404(self.db, dataset_id)
        customers = self.customer_repo.list_by_dataset(dataset_id)
        df = _customers_to_frame(customers)

        total_customers = len(df)
        returning_customers = int((df["total_orders"] > 1).sum()) if not df.empty else 0

        active_customers = 0
        if not df.empty:
            snapshot = df["last_purchase_date"].max()
            active_customers = int((df["last_purchase_date"] >= snapshot - pd.Timedelta(days=90)).sum())

        avg_order_value = clean_number(df["avg_order_value"].mean()) if not df.empty else 0.0
        purchase_frequency = clean_number(df["total_orders"].mean()) if not df.empty else 0.0

        orders = self.order_repo.list_by_dataset(dataset_id)
        avg_basket_size = 0.0
        if orders:
            avg_basket_size = clean_number(sum(o.quantity for o in orders) / len(orders))

        monthly = self._monthly_customer_counts(dataset_id)
        kpis = self._build_kpis(total_customers, returning_customers, active_customers, avg_order_value, monthly)

        return CustomerOverviewResponse(
            dataset_id=dataset_id,
            kpis=kpis,
            total_customers=total_customers,
            returning_customers=returning_customers,
            active_customers=active_customers,
            average_order_value=round(avg_order_value, 2),
            average_basket_size=round(avg_basket_size, 2),
            purchase_frequency=round(purchase_frequency, 2),
        )

    def _monthly_customer_counts(self, dataset_id: uuid.UUID) -> pd.Series:
        orders = self.order_repo.list_by_dataset(dataset_id)
        if not orders:
            return pd.Series(dtype=float)
        df = pd.DataFrame([{"customer_id": o.customer_id, "order_date": o.order_date} for o in orders])
        df["month"] = pd.to_datetime(df["order_date"]).dt.to_period("M")
        return df.groupby("month")["customer_id"].nunique().sort_index()

    def _build_kpis(self, total, returning, active, aov, monthly_series: pd.Series) -> List[KPI]:
        trend = [float(v) for v in monthly_series.tail(12).values] or [float(active or 1)]
        delta = 0.0
        if len(trend) >= 2 and trend[-2] != 0:
            delta = round(((trend[-1] - trend[-2]) / trend[-2]) * 100, 1)

        return [
            KPI(id="total_customers", label="Total Customers", value=total, format="number", delta=delta, trend=trend),
            KPI(id="returning_customers", label="Returning Customers", value=returning, format="number", delta=delta, trend=trend),
            KPI(id="active_customers", label="Active Customers", value=active, format="number", delta=delta, trend=trend),
            KPI(id="avg_order_value", label="Average Order Value", value=round(aov, 2), format="currency", delta=delta, trend=trend),
        ]

    def customer_analytics(self, dataset_id: uuid.UUID) -> CustomerAnalyticsResponse:
        get_dataset_or_404(self.db, dataset_id)
        customers = self.customer_repo.list_by_dataset(dataset_id)
        df = _customers_to_frame(customers)

        # Prefer persisted segments; fall back to computing RFM on the fly.
        stored_segments = self.segment_repo.list_by_dataset(dataset_id)
        if stored_segments:
            segment_counts = pd.Series([s.segment_label for s in stored_segments]).value_counts()
        elif not df.empty:
            rfm_df = compute_rfm(build_rfm_feature_frame(df))
            segment_counts = rfm_df["segment_label"].value_counts()
        else:
            segment_counts = pd.Series(dtype=int)

        segments = [SegmentSlice(name=name, value=int(count)) for name, count in segment_counts.items()]

        retention_trend = self._retention_trend(dataset_id)

        top_customers_df = df.sort_values("total_spent", ascending=False).head(5) if not df.empty else df
        top_customers = [
            TopCustomer(
                id=row["customer_ref"],
                name=row["name"] or row["customer_ref"],
                orders=int(row["total_orders"]),
                lifetime_value=clean_number(row["total_spent"]),
            )
            for _, row in top_customers_df.iterrows()
        ]

        return CustomerAnalyticsResponse(
            dataset_id=dataset_id, segments=segments, retention_trend=retention_trend, top_customers=top_customers
        )

    def _retention_trend(self, dataset_id: uuid.UUID) -> List[RetentionPoint]:
        orders = self.order_repo.list_by_dataset(dataset_id)
        if not orders:
            return []
        df = pd.DataFrame([{"customer_id": o.customer_id, "order_date": o.order_date} for o in orders])
        df["month"] = pd.to_datetime(df["order_date"]).dt.to_period("M")
        months = sorted(df["month"].unique())

        seen_before = set()
        points: List[RetentionPoint] = []
        for month in months:
            active_this_month = set(df.loc[df["month"] == month, "customer_id"])
            returning = active_this_month & seen_before
            rate = (len(returning) / len(active_this_month) * 100) if active_this_month else 0.0
            points.append(RetentionPoint(month=month.strftime("%b"), retention=round(rate, 1)))
            seen_before |= active_this_month
        return points[-12:]

    def sales_analytics(self, dataset_id: uuid.UUID) -> SalesAnalyticsResponse:
        get_dataset_or_404(self.db, dataset_id)
        orders = self.order_repo.list_by_dataset(dataset_id)
        products = self.product_repo.list_by_dataset(dataset_id)

        sales_trend: List[SalesTrendPoint] = []
        if orders:
            df = pd.DataFrame([{"order_date": o.order_date, "amount": o.amount} for o in orders])
            df["month"] = pd.to_datetime(df["order_date"]).dt.to_period("M")
            grouped = df.groupby("month")["amount"].sum().sort_index().tail(12)
            sales_trend = [
                SalesTrendPoint(month=month.strftime("%b"), revenue=round(float(value), 2))
                for month, value in grouped.items()
            ]

        category_totals: dict = {}
        for product in products:
            category_totals[product.category or "Uncategorized"] = (
                category_totals.get(product.category or "Uncategorized", 0.0) + product.total_revenue
            )
        sales_by_category = [
            CategoryRevenue(category=category, revenue=round(revenue, 2))
            for category, revenue in sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
        ]

        return SalesAnalyticsResponse(dataset_id=dataset_id, sales_trend=sales_trend, sales_by_category=sales_by_category)
