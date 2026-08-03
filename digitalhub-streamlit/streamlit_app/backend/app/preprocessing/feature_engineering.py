"""
Feature engineering.

Takes a cleaned, column-resolved dataframe and derives the normalized
customer/product-level aggregates the ETL "load" stage persists, plus the
raw features (recency/frequency/monetary) consumed downstream by
segmentation, CLV, and churn.
"""
from typing import Dict

import pandas as pd

from app.preprocessing.validators import resolve_column_map


def engineer_features(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    column_map = resolve_column_map(df)
    order_col = column_map["order_id"]
    customer_col = column_map["customer_id"]
    date_col = column_map["order_date"]
    amount_col = column_map["amount"]
    qty_col = column_map.get("quantity")
    product_col = column_map.get("product_id")
    product_name_col = column_map.get("product_name")
    category_col = column_map.get("category")
    name_col = column_map.get("customer_name")
    email_col = column_map.get("customer_email")
    vendor_col = column_map.get("vendor")
    stock_col = column_map.get("stock_quantity")

    working = df.copy()
    working[date_col] = pd.to_datetime(working[date_col])
    working[amount_col] = pd.to_numeric(working[amount_col])
    if qty_col:
        working[qty_col] = pd.to_numeric(working[qty_col]).fillna(1)
    else:
        qty_col = "__quantity__"
        working[qty_col] = 1

    snapshot_date = working[date_col].max() + pd.Timedelta(days=1)

    # --- Customer-level aggregates (also the raw RFM feature set) ---
    customer_group = working.groupby(customer_col)
    customers = customer_group.agg(
        total_orders=(order_col, "nunique") if order_col else (amount_col, "count"),
        total_spent=(amount_col, "sum"),
        first_purchase_date=(date_col, "min"),
        last_purchase_date=(date_col, "max"),
    ).reset_index()
    customers = customers.rename(columns={customer_col: "customer_ref"})
    customers["avg_order_value"] = (customers["total_spent"] / customers["total_orders"]).round(2)
    customers["recency_days"] = (snapshot_date - customers["last_purchase_date"]).dt.days
    customers["frequency"] = customers["total_orders"]
    customers["monetary"] = customers["total_spent"]

    if name_col:
        first_name = customer_group[name_col].first().reset_index().rename(columns={customer_col: "customer_ref", name_col: "name"})
        customers = customers.merge(first_name, on="customer_ref", how="left")
    else:
        customers["name"] = customers["customer_ref"].astype(str)

    if email_col:
        first_email = customer_group[email_col].first().reset_index().rename(columns={customer_col: "customer_ref", email_col: "email"})
        customers = customers.merge(first_email, on="customer_ref", how="left")
    else:
        customers["email"] = None

    # --- Product-level aggregates ---
    if product_col:
        product_group = working.groupby(product_col)
        products = product_group.agg(
            total_units_sold=(qty_col, "sum"),
            total_revenue=(amount_col, "sum"),
        ).reset_index()
        products = products.rename(columns={product_col: "product_ref"})
        if product_name_col:
            first_pname = product_group[product_name_col].first().reset_index().rename(
                columns={product_col: "product_ref", product_name_col: "name"}
            )
            products = products.merge(first_pname, on="product_ref", how="left")
        else:
            products["name"] = products["product_ref"].astype(str)
        if category_col:
            first_cat = product_group[category_col].first().reset_index().rename(
                columns={product_col: "product_ref", category_col: "category"}
            )
            products = products.merge(first_cat, on="product_ref", how="left")
        else:
            products["category"] = "Uncategorized"

        if vendor_col:
            first_vendor = product_group[vendor_col].first().reset_index().rename(
                columns={product_col: "product_ref", vendor_col: "vendor_ref"}
            )
            products = products.merge(first_vendor, on="product_ref", how="left")
        else:
            products["vendor_ref"] = None

        if stock_col:
            # Latest reported stock figure for the product, if the dataset
            # includes one — used for the "low stock" dashboard widget.
            last_stock = product_group[stock_col].last().reset_index().rename(
                columns={product_col: "product_ref", stock_col: "stock_quantity"}
            )
            products = products.merge(last_stock, on="product_ref", how="left")
            products["stock_quantity"] = pd.to_numeric(products["stock_quantity"], errors="coerce")
        else:
            products["stock_quantity"] = None
    else:
        products = pd.DataFrame(
            columns=["product_ref", "total_units_sold", "total_revenue", "name", "category", "vendor_ref", "stock_quantity"]
        )

    # --- Order-level (normalized) rows for the Orders table ---
    orders = working[[customer_col, date_col, amount_col, qty_col]].copy()
    orders = orders.rename(
        columns={customer_col: "customer_ref", date_col: "order_date", amount_col: "amount", qty_col: "quantity"}
    )
    orders["order_ref"] = working[order_col].astype(str) if order_col else None
    orders["product_ref"] = working[product_col].astype(str) if product_col else None

    return {"customers": customers, "products": products, "orders": orders, "column_map": column_map}


def monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    column_map = resolve_column_map(df)
    date_col = column_map["order_date"]
    amount_col = column_map["amount"]
    working = df.copy()
    working[date_col] = pd.to_datetime(working[date_col])
    working["_month"] = working[date_col].dt.to_period("M")
    trend = working.groupby("_month")[amount_col].sum().reset_index()
    trend["month"] = trend["_month"].dt.strftime("%b")
    trend["revenue"] = trend[amount_col].round(2)
    return trend[["month", "revenue"]]


def category_revenue(df: pd.DataFrame) -> pd.DataFrame:
    column_map = resolve_column_map(df)
    category_col = column_map.get("category")
    amount_col = column_map["amount"]
    if not category_col:
        return pd.DataFrame(columns=["category", "revenue"])
    working = df.copy()
    grouped = working.groupby(category_col)[amount_col].sum().reset_index()
    grouped = grouped.rename(columns={category_col: "category", amount_col: "revenue"})
    return grouped.sort_values("revenue", ascending=False)
