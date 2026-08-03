import pandas as pd
import plotly.express as px
import streamlit as st

from core.api_client import ApiError, get
from core.utils import format_currency, format_number

st.title(f"Welcome back, {st.session_state.user.get('business_name') or st.session_state.user['name']}")
st.caption("Here's how your store is performing.")

try:
    data = get("/vendor/dashboard/overview")
except ApiError as exc:
    st.error(exc.message)
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Revenue", format_currency(data["total_revenue"]))
c2.metric("Orders", format_number(data["total_orders"]))
c3.metric("Products Listed", format_number(data["total_products"]))
c4.metric("Low Stock", format_number(data["low_stock_count"]))

st.markdown("")
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Monthly Sales")
    st.caption("Your store revenue over the past 12 months")
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

with col_right:
    st.subheader("Top Selling Products")
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
        st.info("No sales yet.")
st.markdown("---")
st.subheader("Recommendations")

try:
    recs = get("/vendor/recommendations")
except ApiError:
    recs = {}

if not recs or not recs.get("anchor_product"):

    st.caption("Business recommendations based on your store performance.")

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            st.markdown("#### 📦 Restock Popular Products")
            st.write("Keep your best-selling products in stock.")
            st.caption(
                "Products with consistent sales should be restocked before inventory runs low."
            )

    with c2:
        with st.container(border=True):
            st.markdown("#### 💰 Increase Average Order Value")
            st.write("Bundle related products together.")
            st.caption(
                "Create offers such as Laptop + Mouse or Smartphone + Charger to encourage larger purchases."
            )

    st.markdown("")

    c3, c4 = st.columns(2)

    with c3:
        with st.container(border=True):
            st.markdown("#### 📈 Promote Trending Categories")
            st.write("Highlight fast-moving categories.")
            st.caption(
                "Feature your most popular products on the homepage or in promotional campaigns."
            )

    with c4:
        with st.container(border=True):
            st.markdown("#### ⭐ Reward Repeat Customers")
            st.write("Offer loyalty discounts.")
            st.caption(
                "Returning customers are more likely to purchase again when offered exclusive discounts."
            )

else:

    st.caption(
        f"Recommendations based on your best-selling product: **{recs['anchor_product']['name']}**"
    )

    rc1, rc2 = st.columns(2)

    with rc1:
        with st.container(border=True):
            st.markdown("#### Frequently Bought Together")

            if recs["frequently_bought_together"]:
                for item in recs["frequently_bought_together"]:
                    st.markdown(
                        f"""
**{item['name']}**

Category: {item['category']}

Confidence: **{round(item['score']*100)}%**
"""
                    )
            else:
                st.caption("No purchase pattern available.")

    with rc2:
        with st.container(border=True):
            st.markdown("#### Similar Products")

            if recs["similar_products"]:
                for item in recs["similar_products"]:
                    st.markdown(
                        f"""
**{item['name']}**

Category: {item['category']}

Similarity: **{round(item['score']*100)}%**
"""
                    )
            else:
                st.caption("No similar products found.")