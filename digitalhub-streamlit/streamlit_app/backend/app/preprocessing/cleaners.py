"""
Data cleaning.

Applies deterministic fixes to a raw uploaded dataframe and returns both the
cleaned dataframe and a structured list of what was found/fixed, shaped for
the frontend's Data Cleaning screen.
"""
from typing import List, Tuple

import numpy as np
import pandas as pd

from app.preprocessing.validators import resolve_column_map


def clean_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[dict]]:
    issues: List[dict] = []
    issue_id = 1
    column_map = resolve_column_map(df)
    cleaned = df.copy()

    order_col = column_map.get("order_id")
    amount_col = column_map.get("amount")
    date_col = column_map.get("order_date")
    email_col = column_map.get("customer_email")
    customer_col = column_map.get("customer_id")
    qty_col = column_map.get("quantity")

    # 1. Duplicate order records — keep the most recent occurrence
    if order_col:
        dup_mask = cleaned.duplicated(subset=[order_col], keep="last")
        dup_count = int(dup_mask.sum())
        if dup_count:
            issues.append(
                {
                    "id": issue_id,
                    "issue": "Duplicate order records",
                    "affected_rows": dup_count,
                    "suggestion": "Kept the most recent record for each duplicated order_id",
                    "severity": "medium",
                }
            )
            issue_id += 1
        cleaned = cleaned[~dup_mask]

    # 2. Missing customer email — backfill placeholder
    if email_col:
        missing_email_mask = cleaned[email_col].isna()
        missing_email_count = int(missing_email_mask.sum())
        if missing_email_count:
            issues.append(
                {
                    "id": issue_id,
                    "issue": "Missing customer email",
                    "affected_rows": missing_email_count,
                    "suggestion": "Filled with a placeholder derived from customer_id",
                    "severity": "low",
                }
            )
            issue_id += 1
            fallback = cleaned[customer_col].astype(str) if customer_col else "unknown"
            cleaned.loc[missing_email_mask, email_col] = "unknown+" + fallback[missing_email_mask].astype(str) + "@shopsense.local"

    # 3. Negative order amounts — flag, don't silently drop
    if amount_col:
        numeric_amount = pd.to_numeric(cleaned[amount_col], errors="coerce")
        negative_mask = numeric_amount < 0
        negative_count = int(negative_mask.sum())
        if negative_count:
            issues.append(
                {
                    "id": issue_id,
                    "issue": "Negative order amounts",
                    "affected_rows": negative_count,
                    "suggestion": "Flagged as likely refunds; excluded from revenue aggregates",
                    "severity": "high",
                }
            )
            issue_id += 1
        cleaned[amount_col] = numeric_amount
        cleaned = cleaned[~cleaned[amount_col].isna()]

    # 4. Inconsistent / unparsable date formats
    if date_col:
        parsed_dates = pd.to_datetime(cleaned[date_col], errors="coerce")
        bad_dates_mask = parsed_dates.isna()
        bad_dates_count = int(bad_dates_mask.sum())
        if bad_dates_count:
            issues.append(
                {
                    "id": issue_id,
                    "issue": "Inconsistent or unparsable date formats",
                    "affected_rows": bad_dates_count,
                    "suggestion": "Rows with unparsable dates were dropped; remaining dates normalized to ISO 8601",
                    "severity": "medium",
                }
            )
            issue_id += 1
        cleaned[date_col] = parsed_dates
        cleaned = cleaned[~cleaned[date_col].isna()]

    # 5. Missing quantity — default to 1 unit
    if qty_col:
        missing_qty_mask = cleaned[qty_col].isna()
        missing_qty_count = int(missing_qty_mask.sum())
        if missing_qty_count:
            issues.append(
                {
                    "id": issue_id,
                    "issue": "Missing order quantity",
                    "affected_rows": missing_qty_count,
                    "suggestion": "Defaulted missing quantities to 1 unit",
                    "severity": "low",
                }
            )
            issue_id += 1
        cleaned[qty_col] = pd.to_numeric(cleaned[qty_col], errors="coerce").fillna(1).astype(int)

    # 6. Rows missing a customer_id entirely can't be attributed — drop them
    if customer_col:
        missing_customer_mask = cleaned[customer_col].isna()
        missing_customer_count = int(missing_customer_mask.sum())
        if missing_customer_count:
            issues.append(
                {
                    "id": issue_id,
                    "issue": "Rows missing customer_id",
                    "affected_rows": missing_customer_count,
                    "suggestion": "Dropped — cannot attribute an order to a customer without an ID",
                    "severity": "high",
                }
            )
            issue_id += 1
        cleaned = cleaned[~missing_customer_mask]

    cleaned = cleaned.replace({np.nan: None})
    return cleaned.reset_index(drop=True), issues
