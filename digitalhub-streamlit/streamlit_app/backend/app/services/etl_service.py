import uuid
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.dataset import DatasetStatus
from app.models.etl_log import ETLLog, ETLStage, ETLStatus
from app.models.order import Order
from app.models.product import Product
from app.models.user import User, UserRole
from app.preprocessing.cleaners import clean_dataset
from app.preprocessing.feature_engineering import engineer_features
from app.repository.customer_repository import CustomerRepository, OrderRepository, ProductRepository
from app.repository.dataset_repository import DatasetRepository
from app.schemas.dataset import ETLRunResponse, ETLStageResult
from app.utils.file_utils import read_dataset, write_cleaned_dataset
from app.utils.logger import get_logger
from app.utils.response_utils import get_dataset_or_404

logger = get_logger(__name__)


class ETLService:
    def __init__(self, db: Session):
        self.db = db
        self.datasets = DatasetRepository(db)
        self.customers = CustomerRepository(db)
        self.orders = OrderRepository(db)
        self.products = ProductRepository(db)

    def _log_stage(self, dataset_id: uuid.UUID, stage: ETLStage, status_: ETLStatus, message: str,
                   rows_before: int = None, rows_after: int = None) -> ETLLog:
        entry = ETLLog(
            dataset_id=dataset_id,
            stage=stage,
            status=status_,
            message=message,
            rows_before=rows_before,
            rows_after=rows_after,
            completed_at=datetime.now(timezone.utc),
        )
        self.db.add(entry)
        self.db.commit()
        return entry

    def run(self, dataset_id: uuid.UUID) -> ETLRunResponse:
        dataset = get_dataset_or_404(self.db, dataset_id)
        stages: list[ETLStageResult] = []

        # --- EXTRACT ---
        try:
            df = read_dataset(dataset.file_path, dataset.file_type)
            self._log_stage(dataset_id, ETLStage.EXTRACT, ETLStatus.SUCCESS, f"Read {len(df)} rows", rows_after=len(df))
            stages.append(ETLStageResult(stage="extract", status="success", message=f"Read {len(df)} rows", rows_after=len(df)))
        except Exception as exc:  # noqa: BLE001
            self._log_stage(dataset_id, ETLStage.EXTRACT, ETLStatus.FAILED, str(exc))
            raise

        # --- TRANSFORM (clean + feature engineer) ---
        rows_before = len(df)
        cleaned_df, issues = clean_dataset(df)
        rows_after = len(cleaned_df)
        write_cleaned_dataset(cleaned_df, dataset_id)
        transform_status = ETLStatus.SUCCESS if not issues else ETLStatus.WARNING
        transform_message = f"Cleaned {rows_before} -> {rows_after} rows ({len(issues)} issue types resolved)"
        self._log_stage(dataset_id, ETLStage.TRANSFORM, transform_status, transform_message, rows_before, rows_after)
        stages.append(
            ETLStageResult(stage="transform", status=transform_status.value, message=transform_message,
                            rows_before=rows_before, rows_after=rows_after)
        )

        features = engineer_features(cleaned_df)
        customers_df = features["customers"]
        products_df = features["products"]
        orders_df = features["orders"]

        # --- LOAD ---
        # Clear any previous load for this dataset so re-running ETL is idempotent.
        self.orders.delete_by_dataset(dataset_id)
        self.products.delete_by_dataset(dataset_id)
        self.customers.delete_by_dataset(dataset_id)

        customer_id_map = {}
        customer_rows = []
        for _, row in customers_df.iterrows():
            customer = Customer(
                dataset_id=dataset_id,
                customer_ref=str(row["customer_ref"]),
                name=str(row.get("name") or row["customer_ref"]),
                email=row.get("email"),
                first_purchase_date=row["first_purchase_date"],
                last_purchase_date=row["last_purchase_date"],
                total_orders=int(row["total_orders"]),
                total_spent=float(row["total_spent"]),
                avg_order_value=float(row["avg_order_value"]),
            )
            customer_rows.append(customer)
        self.customers.bulk_create(customer_rows)
        for customer in customer_rows:
            customer_id_map[customer.customer_ref] = customer.id

        product_id_map = {}
        product_rows = []

        # Best-effort vendor attribution: if the dataset carries a vendor
        # column, match it (case-insensitive) against registered vendors'
        # business names so Vendor Details can show real product/order/
        # revenue figures. Datasets without a vendor column simply load
        # with vendor_id = NULL, which the vendor endpoints handle gracefully.
        vendor_lookup = {
            (v.business_name or "").strip().lower(): v.id
            for v in self.db.query(User).filter(User.role == UserRole.VENDOR).all()
            if v.business_name
        }

        for _, row in products_df.iterrows():
            vendor_ref = row.get("vendor_ref")
            vendor_id = None
            if pd.notna(vendor_ref):
                vendor_id = vendor_lookup.get(str(vendor_ref).strip().lower())

            stock_value = row.get("stock_quantity")
            product = Product(
                dataset_id=dataset_id,
                vendor_id=vendor_id,
                product_ref=str(row["product_ref"]),
                name=str(row.get("name") or row["product_ref"]),
                category=row.get("category") or "Uncategorized",
                total_units_sold=int(row["total_units_sold"]),
                total_revenue=float(row["total_revenue"]),
                stock_quantity=int(stock_value) if pd.notna(stock_value) else None,
            )
            product_rows.append(product)
        self.products.bulk_create(product_rows)
        for product in product_rows:
            product_id_map[product.product_ref] = product.id

        order_rows = []
        for _, row in orders_df.iterrows():
            customer_ref = str(row["customer_ref"])
            if customer_ref not in customer_id_map:
                continue
            product_ref = row.get("product_ref")
            order_rows.append(
                Order(
                    dataset_id=dataset_id,
                    customer_id=customer_id_map[customer_ref],
                    product_id=product_id_map.get(str(product_ref)) if pd.notna(product_ref) else None,
                    order_ref=str(row.get("order_ref")) if pd.notna(row.get("order_ref")) else None,
                    order_date=row["order_date"],
                    quantity=int(row["quantity"]) if pd.notna(row["quantity"]) else 1,
                    amount=float(row["amount"]),
                )
            )
        self.orders.bulk_create(order_rows)

        load_message = (
            f"Loaded {len(customer_rows)} customers, {len(product_rows)} products, {len(order_rows)} orders"
        )
        self._log_stage(dataset_id, ETLStage.LOAD, ETLStatus.SUCCESS, load_message)
        stages.append(ETLStageResult(stage="load", status="success", message=load_message))

        self.datasets.update(dataset, status=DatasetStatus.TRANSFORMED)

        return ETLRunResponse(
            dataset_id=dataset_id,
            status="success",
            stages=stages,
            customers_loaded=len(customer_rows),
            orders_loaded=len(order_rows),
            products_loaded=len(product_rows),
        )
