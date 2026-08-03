import uuid
from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from app.ml.recommendation_engine import (
    frequently_bought_together,
    personalized_recommendations,
    similar_products,
)
from app.repository.customer_repository import CustomerRepository, OrderRepository, ProductRepository
from app.schemas.recommendation import (
    FrequentlyBoughtTogetherResponse,
    PersonalizedRecommendationResponse,
    RecommendedProduct,
    SimilarProductsResponse,
)
from app.utils.response_utils import get_dataset_or_404


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)
        self.customer_repo = CustomerRepository(db)

    def _orders_frame(self, dataset_id: uuid.UUID) -> pd.DataFrame:
        orders = self.order_repo.list_by_dataset(dataset_id)
        if not orders:
            return pd.DataFrame(columns=["order_ref", "product_ref", "customer_ref"])
        return pd.DataFrame(
            [
                {
                    "order_ref": o.order_ref,
                    "product_ref": o.product.product_ref if o.product else None,
                    "customer_ref": o.customer.customer_ref if o.customer else None,
                }
                for o in orders
            ]
        )

    def _products_frame(self, dataset_id: uuid.UUID) -> pd.DataFrame:
        products = self.product_repo.list_by_dataset(dataset_id)
        if not products:
            return pd.DataFrame(columns=["product_ref", "name", "category", "total_units_sold", "total_revenue"])
        return pd.DataFrame(
            [
                {
                    "id": p.id,
                    "product_ref": p.product_ref,
                    "name": p.name,
                    "category": p.category,
                    "total_units_sold": p.total_units_sold,
                    "total_revenue": p.total_revenue,
                }
                for p in products
            ]
        )

    def _to_recommended_products(self, results: List[dict], products_df: pd.DataFrame) -> List[RecommendedProduct]:
        indexed = products_df.set_index("product_ref") if not products_df.empty else products_df
        output = []
        for item in results:
            ref = item["product_ref"]
            if ref not in indexed.index:
                continue
            row = indexed.loc[ref]
            output.append(
                RecommendedProduct(
                    product_id=row["id"],
                    product_ref=ref,
                    name=row["name"] or ref,
                    category=row["category"] or "Uncategorized",
                    score=item["score"],
                )
            )
        return output

    def frequently_bought_together(self, dataset_id: uuid.UUID, product_id: uuid.UUID) -> FrequentlyBoughtTogetherResponse:
        get_dataset_or_404(self.db, dataset_id)
        product = self.product_repo.get(product_id)
        if product is None:
            raise ValueError("Product not found")

        orders_df = self._orders_frame(dataset_id)
        products_df = self._products_frame(dataset_id)
        results = frequently_bought_together(orders_df, product.product_ref)
        return FrequentlyBoughtTogetherResponse(
            dataset_id=dataset_id, product_id=product_id, recommendations=self._to_recommended_products(results, products_df)
        )

    def similar_products(self, dataset_id: uuid.UUID, product_id: uuid.UUID) -> SimilarProductsResponse:
        get_dataset_or_404(self.db, dataset_id)
        product = self.product_repo.get(product_id)
        if product is None:
            raise ValueError("Product not found")

        products_df = self._products_frame(dataset_id)
        results = similar_products(products_df, product.product_ref)
        return SimilarProductsResponse(
            dataset_id=dataset_id, product_id=product_id, recommendations=self._to_recommended_products(results, products_df)
        )

    def personalized(self, dataset_id: uuid.UUID, customer_id: uuid.UUID) -> PersonalizedRecommendationResponse:
        get_dataset_or_404(self.db, dataset_id)
        customer = self.customer_repo.get(customer_id)
        if customer is None:
            raise ValueError("Customer not found")

        orders_df = self._orders_frame(dataset_id)
        products_df = self._products_frame(dataset_id)
        results = personalized_recommendations(orders_df, products_df, customer.customer_ref)
        return PersonalizedRecommendationResponse(
            dataset_id=dataset_id,
            customer_id=customer_id,
            recommendations=self._to_recommended_products(results, products_df),
        )
