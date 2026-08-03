"""
Product recommendation engine.

Three strategies, all derived from the orders/products data already loaded
for a dataset — no external catalog or embeddings required:

- Frequently Bought Together: market-basket co-occurrence within the same
  order.
- Similar Products: content-based similarity (category + scaled sales
  features) using scikit-learn's cosine similarity.
- Personalized: category affinity from a customer's own purchase history,
  ranked by how well other products in those categories are selling.
"""
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


def frequently_bought_together(orders: pd.DataFrame, product_ref: str, top_n: int = 5) -> List[Dict]:
    if "order_ref" not in orders.columns or "product_ref" not in orders.columns:
        return []

    baskets = orders.dropna(subset=["order_ref", "product_ref"]).groupby("order_ref")["product_ref"].apply(set)
    baskets_with_product = baskets[baskets.apply(lambda basket: product_ref in basket)]

    co_occurrence: Dict[str, int] = {}
    for basket in baskets_with_product:
        for other_product in basket:
            if other_product == product_ref:
                continue
            co_occurrence[other_product] = co_occurrence.get(other_product, 0) + 1

    ranked = sorted(co_occurrence.items(), key=lambda item: item[1], reverse=True)[:top_n]
    max_count = ranked[0][1] if ranked else 1
    return [{"product_ref": ref, "score": round(count / max_count, 4)} for ref, count in ranked]


def similar_products(products: pd.DataFrame, product_ref: str, top_n: int = 5) -> List[Dict]:
    if products.empty or product_ref not in products["product_ref"].values:
        return []

    features = products[["total_units_sold", "total_revenue"]].fillna(0).values
    if len(products) < 2:
        return []

    scaled = StandardScaler().fit_transform(features)
    similarity_matrix = cosine_similarity(scaled)

    target_idx = products.index[products["product_ref"] == product_ref][0]
    target_category = products.loc[target_idx, "category"]

    scores = pd.Series(similarity_matrix[products.index.get_loc(target_idx)], index=products.index)
    scores = scores.drop(index=target_idx)

    # Prefer same-category matches, but don't exclude cross-category ones
    same_category_bonus = (products["category"] == target_category).astype(float) * 0.25
    scores = scores + same_category_bonus.drop(index=target_idx, errors="ignore")

    ranked_idx = scores.sort_values(ascending=False).head(top_n).index
    results = []
    for idx in ranked_idx:
        row = products.loc[idx]
        results.append({"product_ref": row["product_ref"], "score": round(float(scores[idx]), 4)})
    return results


def personalized_recommendations(
    orders: pd.DataFrame, products: pd.DataFrame, customer_ref: str, top_n: int = 5
) -> List[Dict]:
    if orders.empty or products.empty:
        return []

    customer_orders = orders[orders["customer_ref"] == customer_ref]
    purchased_products = set(customer_orders["product_ref"].dropna().unique())
    if not purchased_products:
        # Cold start — fall back to overall best sellers.
        top = products.sort_values("total_revenue", ascending=False).head(top_n)
        return [
            {"product_ref": row["product_ref"], "score": 1.0}
            for _, row in top.iterrows()
        ]

    purchased_categories = set(
        products[products["product_ref"].isin(purchased_products)]["category"].dropna().unique()
    )

    candidates = products[
        products["category"].isin(purchased_categories) & ~products["product_ref"].isin(purchased_products)
    ].copy()

    if candidates.empty:
        candidates = products[~products["product_ref"].isin(purchased_products)].copy()

    max_revenue = candidates["total_revenue"].max() or 1
    candidates["score"] = (candidates["total_revenue"] / max_revenue).round(4)
    candidates = candidates.sort_values("score", ascending=False).head(top_n)

    return [
        {"product_ref": row["product_ref"], "score": float(row["score"])}
        for _, row in candidates.iterrows()
    ]
