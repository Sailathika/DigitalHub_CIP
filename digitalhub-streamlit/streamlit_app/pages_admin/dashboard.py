import pandas as pd
import plotly.express as px
import streamlit as st

from core.api_client import ApiError, get
from core.utils import format_currency, format_number

st.title("Marketplace Overview")
st.caption("A real-time snapshot of revenue, orders, and vendor performance across DigitalHub_CIP.")

try:
    data = get("/dashboard/overview")
except ApiError as exc:
    st.error(exc.message)
    st.stop()

# --- KPI row ---
row1 = st.columns(4)
row1[0].metric("Total Revenue", format_currency(data["total_revenue"]))
row1[1].metric("Total Orders", format_number(data["total_orders"]))
row1[2].metric("Total Customers", format_number(data["total_customers"]))
row1[3].metric("Total Products", format_number(data["total_products"]))

row2 = st.columns(4)
row2[0].metric("Total Vendors", format_number(data["total_vendors"]))
row2[1].metric("Active Vendors", format_number(data["active_vendors"]))
row2[2].metric("Pending Vendors", format_number(data["pending_vendors"]))
row2[3].metric("Low Stock Products", format_number(len(data["low_stock_products"])))

st.markdown("")

# --- Sales trend + Top vendors ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Sales Trend")
    st.caption("Monthly revenue across the marketplace")
    trend = data["sales_trend"]
    if trend:
        df = pd.DataFrame(trend)
        fig = px.area(df, x="month", y="revenue", markers=True)
        fig.update_traces(line_color="#3B82F6", fillcolor="rgba(59,130,246,0.12)")
        fig.update_layout(
            height=320, margin=dict(l=0, r=0, t=10, b=0),
            yaxis_title=None, xaxis_title=None,
            plot_bgcolor="white", paper_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No orders yet — upload and process a dataset to see revenue trends.")

with col_right:
    st.subheader("Top Vendors")
    st.caption("Ranked by attributed revenue")
    top_vendors = data["top_vendors"]
    if top_vendors:
        df = pd.DataFrame(top_vendors).sort_values("revenue")
        fig = px.bar(df, x="revenue", y="business_name", orientation="h")
        fig.update_traces(marker_color="#3B82F6")
        fig.update_layout(
            height=320, margin=dict(l=0, r=0, t=10, b=0),
            yaxis_title=None, xaxis_title=None,
            plot_bgcolor="white", paper_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No vendor revenue data yet.")

# --- Customer growth + Top products ---
col_left2, col_right2 = st.columns([2, 1])

with col_left2:
    st.subheader("Customer Growth")
    st.caption("New customers acquired per month")
    growth = data["customer_growth"]
    if growth:
        df = pd.DataFrame(growth)
        fig = px.line(df, x="month", y="customers", markers=True)
        fig.update_traces(line_color="#10B981")
        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            yaxis_title=None, xaxis_title=None,
            plot_bgcolor="white", paper_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No customer data yet.")

with col_right2:
    st.subheader("Top Products")
    top_products = data["top_products"]
    if top_products:
        for i, product in enumerate(top_products, start=1):
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{i}. {product['name']}**  \n<span class='dh-muted'>{format_number(product['units_sold'])} units sold</span>", unsafe_allow_html=True)
            c2.markdown(f"<div style='text-align:right;font-family:monospace;'>{format_currency(product['revenue'])}</div>", unsafe_allow_html=True)
    else:
        st.info("No product sales data yet.")

# --- Low stock ---
st.subheader("Low Stock Products")
st.caption("Products below the low-stock threshold, across all vendors")
low_stock = data["low_stock_products"]
if low_stock:
    df = pd.DataFrame(low_stock).rename(
        columns={"name": "Product", "category": "Category", "stock_quantity": "Stock Left", "product_ref": "SKU"}
    )
    st.dataframe(df[["Product", "Category", "Stock Left"]], use_container_width=True, hide_index=True)
else:
    st.success("No low-stock products right now.")
