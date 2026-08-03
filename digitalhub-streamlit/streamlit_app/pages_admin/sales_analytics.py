import pandas as pd
import plotly.express as px
import streamlit as st

from core.api_client import ApiError, get
from core.auth import require_dataset

st.title("Sales Analytics")
st.caption("Revenue trends and category performance across the marketplace.")

dataset = require_dataset()

try:
    data = get(f"/analytics/{dataset['id']}/sales")
except ApiError as exc:
    st.error(exc.message)
    st.stop()

st.subheader("Revenue Trend")
st.caption("Monthly revenue across the marketplace")
trend = data["sales_trend"]
if trend:
    df = pd.DataFrame(trend)
    fig = px.area(df, x="month", y="revenue", markers=True)
    fig.update_traces(line_color="#3B82F6", fillcolor="rgba(59,130,246,0.12)")
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), yaxis_title=None, xaxis_title=None,
                       plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No sales data yet.")

st.subheader("Revenue by Category")
st.caption("Which product categories drive the most revenue")
by_category = data["sales_by_category"]
if by_category:
    df = pd.DataFrame(by_category).sort_values("revenue")
    fig = px.bar(df, x="revenue", y="category", orientation="h")
    fig.update_traces(marker_color="#3B82F6")
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), yaxis_title=None, xaxis_title=None,
                       plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No category data yet.")
