from datetime import datetime
from typing import Optional


def format_currency(value: Optional[float]) -> str:
    if value is None:
        return "₹0"
    return f"₹{value:,.0f}"


def format_number(value: Optional[float]) -> str:
    if value is None:
        return "0"
    return f"{value:,.0f}"


def format_date(value: Optional[str], fmt: str = "%d %b %Y") -> str:
    if not value:
        return "—"
    try:
        # Handles both plain dates ("2026-07-24") and ISO timestamps.
        cleaned = value.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned).strftime(fmt)
    except (ValueError, TypeError):
        return value


def delta_label(value: Optional[float]) -> Optional[str]:
    if value is None:
        return None
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"
