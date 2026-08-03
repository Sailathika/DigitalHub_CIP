import pandas as pd
import plotly.express as px
import streamlit as st

from core.api_client import ApiError, get
from core.utils import format_currency, format_number

st.title("Sales Analytics")
st.caption("Analyze your store's sales performance.")

try:
    data = get("/vendor/sales-analytics")
except ApiError as exc:
    st.error(exc.message)
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Total Revenue", format_currency(data["total_revenue"]))
c2.metric("Total Orders", format_number(data["total_orders"]))
c3.metric("Avg. Order Value", format_currency(data["average_order_value"]))

st.subheader("Revenue Trend")
st.caption("Monthly revenue for your store")
trend = data["sales_trend"]
if trend:
    df = pd.DataFrame(trend)
    fig = px.area(df, x="month", y="revenue", markers=True)
    fig.update_traces(line_color="#3B82F6", fillcolor="rgba(59,130,246,0.12)")
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), yaxis_title=None, xaxis_title=None,
                       plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No sales yet.")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Revenue by Category")
    by_category = data["sales_by_category"]
    if by_category:
        df = pd.DataFrame(by_category).sort_values("revenue")
        fig = px.bar(df, x="revenue", y="category", orientation="h")
        fig.update_traces(marker_color="#3B82F6")
        fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), yaxis_title=None, xaxis_title=None,
                           plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data yet.")

with col_right:
    st.subheader("Top Products")
    top_products = data["top_products"]
    if top_products:
        for i, p in enumerate(top_products, start=1):
            st.markdown(
                f"**{i}. {p['name']}**  \n"
                f"<span class='dh-muted'>{format_number(p['unitsSold'])} units sold</span> · "
                f"<span style='font-family:monospace'>{format_currency(p['revenue'])}</span>",
                unsafe_allow_html=True,
            )
    else:
        st.info("No product sales yet.")
