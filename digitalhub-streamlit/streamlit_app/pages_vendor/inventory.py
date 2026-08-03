import pandas as pd
import plotly.express as px
import streamlit as st

from core.api_client import ApiError, get
from core.theme import badge_html
from core.utils import format_currency, format_number

st.title("Inventory")
st.caption("Track stock levels across your product catalog.")

try:
    data = get("/vendor/products/inventory")
except ApiError as exc:
    st.error(exc.message)
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Products", format_number(data["total_products"]))
c2.metric("In Stock", format_number(data["in_stock"]))
c3.metric("Low Stock", format_number(data["low_stock"]))
c4.metric("Out of Stock", format_number(data["out_of_stock"]))

st.metric("Total Inventory Value", format_currency(data["total_inventory_value"]))

st.markdown("##### Stock Levels")
st.caption(f"Products below {data['low_stock_threshold']} units are flagged as low stock")

products = data["products"]
if not products:
    st.info("No products yet. Add products from the My Products page.")
else:
    status_variant = {"active": "success", "inactive": "secondary", "draft": "warning"}

    h1, h2, h3, h4, h5 = st.columns([3, 1.5, 1, 1, 1])
    h1.markdown("<span class='dh-muted' style='font-weight:600;'>PRODUCT</span>", unsafe_allow_html=True)
    h2.markdown("<span class='dh-muted' style='font-weight:600;'>CATEGORY</span>", unsafe_allow_html=True)
    h3.markdown("<span class='dh-muted' style='font-weight:600;'>PRICE</span>", unsafe_allow_html=True)
    h4.markdown("<span class='dh-muted' style='font-weight:600;'>STOCK</span>", unsafe_allow_html=True)
    h5.markdown("<span class='dh-muted' style='font-weight:600;'>STATUS</span>", unsafe_allow_html=True)
    st.markdown("<hr style='margin:0.4rem 0 0.8rem 0;border-color:#E2E8F0;'>", unsafe_allow_html=True)

    for product in products:
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([3, 1.5, 1, 1, 1])
            c1.markdown(f"**{product['name']}**  \n<span class='dh-muted'>{product.get('sku')}</span>", unsafe_allow_html=True)
            c2.markdown(product.get("category") or "—")
            c3.markdown(f"₹{product['price']:,.0f}")
            stock_color = (
                "#EF4444" if product["stock"] <= 0
                else "#F59E0B" if product["stock"] <= data["low_stock_threshold"]
                else "#1E293B"
            )
            c4.markdown(f"<span style='color:{stock_color};font-weight:600;'>{product['stock']}</span>", unsafe_allow_html=True)
            c5.markdown(badge_html(product["status"].title(), status_variant.get(product["status"], "default")), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### Stock by Category")
    df = pd.DataFrame(products)
    if not df.empty and "category" in df.columns:
        by_category = df.groupby(df["category"].fillna("Uncategorized"))["stock"].sum().reset_index()
        by_category = by_category.sort_values("stock")
        fig = px.bar(by_category, x="stock", y="category", orientation="h")
        fig.update_traces(marker_color="#3B82F6")
        fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), yaxis_title=None, xaxis_title=None,
                           plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)
