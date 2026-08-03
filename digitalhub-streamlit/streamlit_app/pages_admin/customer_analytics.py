import pandas as pd
import plotly.express as px
import streamlit as st

from core.api_client import ApiError, get
from core.auth import require_dataset
from core.utils import format_currency, format_number

st.title("Customer Analytics")
st.caption("Understand customer segments, retention, and lifetime value.")

dataset = require_dataset()

try:
    data = get(f"/analytics/{dataset['id']}/customers")
except ApiError as exc:
    st.error(exc.message)
    st.stop()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Customer Retention")
    st.caption("Percentage of customers retained month over month")
    trend = data["retention_trend"]
    if trend:
        df = pd.DataFrame(trend)
        fig = px.area(df, x="month", y="retention", markers=True)
        fig.update_traces(line_color="#22C55E", fillcolor="rgba(34,197,94,0.15)")
        fig.update_layout(
            height=320, margin=dict(l=0, r=0, t=10, b=0),
            yaxis_title="Retention %", xaxis_title=None,
            plot_bgcolor="white", paper_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough order history yet to compute retention.")

with col_right:
    st.subheader("Customer Segments")
    st.caption("Distribution by lifecycle stage")
    segments = data["segments"]
    if segments:
        df = pd.DataFrame(segments)
        fig = px.pie(df, names="name", values="value", hole=0.55, color_discrete_sequence=px.colors.sequential.Purples_r)
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No segment data yet.")

st.subheader("Top Customers")
st.caption("Ranked by lifetime value")
top_customers = data["top_customers"]
if top_customers:
    df = pd.DataFrame(top_customers).rename(
        columns={"name": "Customer", "id": "Customer ID", "orders": "Orders", "lifetime_value": "Lifetime Value"}
    )
    df["Lifetime Value"] = df["Lifetime Value"].apply(format_currency)
    st.dataframe(df[["Customer", "Customer ID", "Orders", "Lifetime Value"]], use_container_width=True, hide_index=True)
else:
    st.info("No customer data yet.")
