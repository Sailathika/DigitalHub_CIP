"""
Dataset validation.

Uploaded files won't share one exact schema, so we resolve flexible column
aliases first, then run a battery of checks (required columns, dtypes,
duplicates, missing values, referential sanity) that mirror what the
frontend's Data Validation screen expects to render.
"""
from typing import Dict, List, Optional

import pandas as pd

# Canonical field -> accepted column-name aliases (case-insensitive).
COLUMN_ALIASES: Dict[str, List[str]] = {
    "order_id": ["order_id", "order_ref", "orderid", "invoice_no", "invoice_id"],
    "customer_id": ["customer_id", "customer_ref", "customerid", "client_id"],
    "customer_name": ["customer_name", "customer", "client_name", "name"],
    "customer_email": ["customer_email", "email"],
    "product_id": ["product_id", "sku", "product_ref", "productid"],
    "product_name": ["product_name", "product", "item_name", "description"],
    "category": ["category", "product_category", "department"],
    "order_date": ["order_date", "date", "invoice_date", "purchase_date", "created_at"],
    "quantity": ["quantity", "qty", "units"],
    "amount": ["amount", "total", "sales", "revenue", "price", "total_amount"],
    "vendor": ["vendor", "vendor_name", "seller", "seller_name", "store", "store_name"],
    "stock_quantity": ["stock", "stock_quantity", "inventory", "quantity_available", "units_in_stock"],
}

REQUIRED_FIELDS = ["order_id", "customer_id", "order_date", "amount"]


def resolve_column_map(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """Map each canonical field to the actual column name found in `df`."""
    lower_cols = {col.lower().strip(): col for col in df.columns}
    resolved: Dict[str, Optional[str]] = {}
    for field, aliases in COLUMN_ALIASES.items():
        found = None
        for alias in aliases:
            if alias in lower_cols:
                found = lower_cols[alias]
                break
        resolved[field] = found
    return resolved


def validate_dataset(df: pd.DataFrame) -> List[dict]:
    """Run schema/quality checks, returning results shaped for the API."""
    checks: List[dict] = []
    column_map = resolve_column_map(df)
    check_id = 1

    # 1. Required columns present
    missing_required = [f for f in REQUIRED_FIELDS if column_map.get(f) is None]
    checks.append(
        {
            "id": check_id,
            "check": "Required columns present",
            "detail": (
                "order_id, customer_id, order_date, amount all found"
                if not missing_required
                else f"Missing required fields: {', '.join(missing_required)}"
            ),
            "status": "Passed" if not missing_required else "Failed",
        }
    )
    check_id += 1

    # 2. Column data types
    dtype_issues = []
    amount_col = column_map.get("amount")
    date_col = column_map.get("order_date")
    if amount_col:
        numeric_amount = pd.to_numeric(df[amount_col], errors="coerce")
        bad_amount = int(numeric_amount.isna().sum())
        if bad_amount:
            dtype_issues.append(f"{bad_amount} non-numeric values in '{amount_col}'")
    if date_col:
        parsed_date = pd.to_datetime(df[date_col], errors="coerce")
        bad_date = int(parsed_date.isna().sum())
        if bad_date:
            dtype_issues.append(f"{bad_date} unparsable dates in '{date_col}'")

    checks.append(
        {
            "id": check_id,
            "check": "Column data types",
            "detail": "; ".join(dtype_issues) if dtype_issues else "amount parses as numeric, order_date parses as date",
            "status": "Passed" if not dtype_issues else "Warning",
        }
    )
    check_id += 1

    # 3. Duplicate rows
    order_col = column_map.get("order_id")
    duplicate_count = 0
    if order_col:
        duplicate_count = int(df.duplicated(subset=[order_col]).sum())
    else:
        duplicate_count = int(df.duplicated().sum())
    checks.append(
        {
            "id": check_id,
            "check": "Duplicate rows",
            "detail": f"{duplicate_count} duplicate order records found" if duplicate_count else "No duplicate order records found",
            "status": "Passed" if duplicate_count == 0 else "Warning",
        }
    )
    check_id += 1

    # 4. Missing values in key optional fields
    email_col = column_map.get("customer_email")
    missing_email = int(df[email_col].isna().sum()) if email_col else 0
    checks.append(
        {
            "id": check_id,
            "check": "Missing values",
            "detail": (
                f"customer email is empty in {missing_email} rows"
                if email_col
                else "No customer email column found — skipped"
            ),
            "status": "Passed" if missing_email == 0 else "Warning",
        }
    )
    check_id += 1

    # 5. Referential integrity — customer_id populated for every row
    customer_col = column_map.get("customer_id")
    missing_customer = int(df[customer_col].isna().sum()) if customer_col else len(df)
    checks.append(
        {
            "id": check_id,
            "check": "Referential integrity",
            "detail": (
                "All rows have a customer_id"
                if missing_customer == 0
                else f"{missing_customer} rows are missing a customer_id"
            ),
            "status": "Passed" if missing_customer == 0 else "Failed",
        }
    )
    check_id += 1

    # 6. Negative or zero amounts
    negative_amounts = 0
    if amount_col:
        numeric_amount = pd.to_numeric(df[amount_col], errors="coerce")
        negative_amounts = int((numeric_amount < 0).sum())
    checks.append(
        {
            "id": check_id,
            "check": "Amount sanity",
            "detail": (
                f"{negative_amounts} rows have a negative amount (likely refunds)"
                if negative_amounts
                else "All amounts are non-negative"
            ),
            "status": "Passed" if negative_amounts == 0 else "Warning",
        }
    )

    return checks
