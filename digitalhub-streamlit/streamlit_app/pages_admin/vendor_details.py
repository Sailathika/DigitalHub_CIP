import pandas as pd
import plotly.express as px
import streamlit as st

from core.api_client import ApiError, get
from core.theme import badge_html
from core.utils import format_currency, format_date, format_number

st.title("Vendor Details")

vendor_id = st.session_state.get("selected_vendor_id")

if not vendor_id:
    st.caption("Pick a vendor to view their full profile and performance.")

    try:
        vendor_list = get("/vendors/")["vendors"]
    except ApiError as exc:
        st.error(exc.message)
        st.stop()

    if not vendor_list:
        st.info("No vendors yet.")
        st.stop()

    options = {
        v["id"]: f"{v['business_name']} ({v['full_name']})"
        for v in vendor_list
    }

    picked = st.selectbox(
        "Vendor",
        options.keys(),
        format_func=lambda vid: options[vid],
    )

    if st.button("View Vendor", type="primary"):
        st.session_state.selected_vendor_id = picked
        st.rerun()

    st.stop()

if st.button("Back to Vendor Management", icon=":material/arrow_back:"):
    st.session_state.selected_vendor_id = None
    st.switch_page("pages_admin/vendor_management.py")

try:
    data = get(f"/vendors/{vendor_id}")
except ApiError as exc:
    st.error(exc.message)
    st.stop()

vendor = data["vendor"]

status_variant = {
    "active": "success",
    "pending": "warning",
    "suspended": "danger",
}

st.markdown(
    f"## {vendor['business_name']} &nbsp; "
    f"{badge_html(vendor['vendor_status'].title(), status_variant.get(vendor['vendor_status'], 'default'))}",
    unsafe_allow_html=True,
)

st.caption(str(vendor["id"]))

st.markdown("##### Business Information")

with st.container(border=True):

    c1, c2, c3 = st.columns(3)

    c1.markdown(f"**Owner**  \n{vendor['full_name']}")
    c1.markdown(f"**Category**  \n{vendor.get('category') or '—'}")

    c2.markdown(f"**Email**  \n{vendor['email']}")
    c2.markdown(f"**Phone**  \n{vendor.get('phone') or '—'}")

    c3.markdown(f"**GST Number**  \n{vendor.get('gst_number') or 'Not provided'}")
    c3.markdown(f"**Joined**  \n{format_date(vendor.get('created_at'))}")

    st.markdown(f"**Address**  \n{vendor.get('address') or '—'}")

    c4, c5 = st.columns(2)

    c4.markdown(f"**Commission**  \n{vendor['commission_percent']}%")

    rating = vendor.get("rating", 0)

    c5.markdown(
        f"**Rating**  \n{f'{rating:.1f} / 5.0' if rating > 0 else 'Not yet rated'}"
    )

st.markdown("##### Performance Metrics")

m1, m2, m3 = st.columns(3)

m1.metric("Revenue", format_currency(data["total_revenue"]))
m2.metric("Orders", format_number(data["total_orders"]))
m3.metric("Products", format_number(data["total_products"]))

col_left, col_right = st.columns([2, 1])

with col_left:

    st.markdown("##### Sales Trend")

    trend = data["sales_trend"]

    if trend:

        df = pd.DataFrame(trend)

        fig = px.area(
            df,
            x="month",
            y="revenue",
            markers=True,
        )

        fig.update_traces(
            line_color="#3B82F6",
            fillcolor="rgba(59,130,246,0.12)",
        )

        fig.update_layout(
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis_title=None,
            xaxis_title=None,
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No sales data yet for this vendor.")

with col_right:

    st.markdown("##### Top Products")

    top_products = data["top_products"]

    if top_products:

        for i, p in enumerate(top_products, start=1):

            st.markdown(
                f"**{i}. {p['name']}**  \n"
                f"<span class='dh-muted'>{format_number(p['unitsSold'])} units</span> · "
                f"<span style='font-family:monospace'>{format_currency(p['revenue'])}</span>",
                unsafe_allow_html=True,
            )

    else:
        st.caption("No products yet.")

st.markdown("##### Recent Orders")

recent_orders = data["recent_orders"]

if recent_orders:

    df = pd.DataFrame(recent_orders).rename(
        columns={
            "id": "Order",
            "customer": "Customer",
            "quantity": "Quantity",
            "amount": "Amount",
            "date": "Date",
        }
    )

    df["Order"] = df["Order"].astype(str).str[:8]
    df["Amount"] = df["Amount"].apply(format_currency)
    df["Customer"] = df["Customer"].fillna("—")

    st.dataframe(
        df[
            [
                "Order",
                "Customer",
                "Quantity",
                "Amount",
                "Date",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info("No orders yet for this vendor.")