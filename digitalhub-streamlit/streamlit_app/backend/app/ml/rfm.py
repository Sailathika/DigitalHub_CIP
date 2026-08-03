"""
RFM (Recency, Frequency, Monetary) customer segmentation.

Scores each customer 1-5 on each dimension via quintile binning, then maps
the combined score to a human-readable segment label using standard RFM
segment heuristics.
"""
import pandas as pd


def _safe_qcut(series: pd.Series, ascending: bool) -> pd.Series:
    """Quintile-bin a series into 1-5 (5 = best), tolerating too few unique
    values. `ascending` controls the rank direction: pass False when a
    *lower* raw value should score *higher* (e.g. recency_days)."""
    ranks = series.rank(method="first", ascending=ascending)
    try:
        return pd.qcut(ranks, 5, labels=[1, 2, 3, 4, 5]).astype(int)
    except ValueError:
        # Not enough distinct values for 5 bins — fall back to fewer bins.
        n_bins = max(1, series.nunique())
        labels = list(range(1, n_bins + 1))
        return pd.qcut(ranks, n_bins, labels=labels, duplicates="drop").astype(int)


def label_segment(r: int, f: int, m: int) -> str:
    score = r + f + m
    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal Customers"
    if r >= 4 and f <= 2:
        return "New Customers"
    if r <= 2 and f >= 3 and m >= 3:
        return "At Risk"
    if r <= 2 and f <= 2 and m <= 2:
        return "Lost"
    if score >= 10:
        return "Potential Loyalist"
    return "Needs Attention"


def compute_rfm(customers: pd.DataFrame) -> pd.DataFrame:
    """
    Expects columns: recency_days, frequency, monetary.
    Lower recency is better (more recent), so it's ranked ascending on
    recency_days but scored so that a *lower* recency_days yields a
    *higher* r_score.
    """
    df = customers.copy()
    df["r_score"] = _safe_qcut(df["recency_days"], ascending=False)
    df["f_score"] = _safe_qcut(df["frequency"], ascending=True)
    df["m_score"] = _safe_qcut(df["monetary"], ascending=True)
    df["rfm_score"] = df["r_score"].astype(str) + df["f_score"].astype(str) + df["m_score"].astype(str)
    df["segment_label"] = df.apply(lambda row: label_segment(row["r_score"], row["f_score"], row["m_score"]), axis=1)
    return df
