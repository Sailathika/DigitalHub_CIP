import pandas as pd
import streamlit as st

from core.api_client import ApiError, get
from core.theme import badge_html
from core.utils import format_currency, format_number


# ---------------------------------------------------------
# Page Header
# ---------------------------------------------------------

st.title("Orders")
st.caption("View and track orders placed for your products.")


# ---------------------------------------------------------
# Load Orders
# ---------------------------------------------------------

@st.cache_data(ttl=30)
def load_orders(search="", status_filter="All"):
    params = {}

    if search:
        params["search"] = search

    if status_filter and status_filter != "All":
        params["status_filter"] = status_filter.lower()

    return get("/vendor/orders/", params=params)


try:
    # We need search/status values before loading,
    # so filters are created first.
    f1, f2 = st.columns([3, 1])

    search = f1.text_input(
        "Search Orders",
        placeholder="Customer, product or order ID...",
    )

    status_filter = f2.selectbox(
        "Status",
        [
            "All",
            "Pending",
            "Processing",
            "Shipped",
            "Delivered",
            "Cancelled",
        ],
    )

    response = load_orders(search, status_filter)

except ApiError as exc:
    st.error(f"Unable to load orders: {exc.message}")
    st.stop()


# ---------------------------------------------------------
# Convert API Response
# ---------------------------------------------------------

orders = response.get("orders", [])
total = response.get("total", 0)


if not orders:
    st.info("No orders match your search or selected filter.")
    st.stop()


# ---------------------------------------------------------
# Data Preparation
# ---------------------------------------------------------

rows = []

for order in orders:

    customer = order.get("customer") or {}
    product = order.get("product") or {}

    rows.append(
        {
            "id": order.get("id"),
            "order_ref": order.get("order_ref") or "N/A",
            "customer": customer.get("name") or "Unknown Customer",
            "email": customer.get("email") or "N/A",
            "product": product.get("name") or "Unknown Product",
            "category": product.get("category") or "N/A",
            "product_ref": product.get("product_ref") or "N/A",
            "quantity": order.get("quantity", 0),
            "amount": order.get("amount", 0),
            "status": order.get("status", "pending"),
            "date": order.get("order_date"),
        }
    )


df = pd.DataFrame(rows)

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce",
)


# ---------------------------------------------------------
# Sort
# ---------------------------------------------------------

sort_by = st.selectbox(
    "Sort By",
    [
        "Newest",
        "Oldest",
        "Highest Amount",
        "Lowest Amount",
    ],
)


if sort_by == "Newest":

    df = df.sort_values(
        "date",
        ascending=False,
    )

elif sort_by == "Oldest":

    df = df.sort_values(
        "date",
        ascending=True,
    )

elif sort_by == "Highest Amount":

    df = df.sort_values(
        "amount",
        ascending=False,
    )

else:

    df = df.sort_values(
        "amount",
        ascending=True,
    )


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Orders",
    format_number(total),
)

c2.metric(
    "Revenue",
    format_currency(df["amount"].sum()),
)

c3.metric(
    "Average Order",
    format_currency(df["amount"].mean()),
)

pending_count = len(
    df[
        df["status"].str.lower().isin(
            ["pending", "processing"]
        )
    ]
)

c4.metric(
    "Pending",
    format_number(pending_count),
)


st.markdown("")


# ---------------------------------------------------------
# Status Styling
# ---------------------------------------------------------

STATUS_VARIANT = {
    "pending": "warning",
    "processing": "default",
    "shipped": "default",
    "delivered": "success",
    "cancelled": "danger",
}


def display_status(status_value):
    status_text = str(status_value).replace(
        "_",
        " ",
    ).title()

    variant = STATUS_VARIANT.get(
        str(status_value).lower(),
        "default",
    )

    return badge_html(
        status_text,
        variant,
    )


# ---------------------------------------------------------
# Order History
# ---------------------------------------------------------

st.markdown("### Order History")


# Header

headers = st.columns(
    [1.5, 2, 3, 0.8, 1.5, 1.5]
)

labels = [
    "ORDER",
    "CUSTOMER",
    "PRODUCT",
    "QTY",
    "AMOUNT",
    "STATUS",
]


for col, label in zip(headers, labels):

    col.markdown(
        f"""
        <span class="dh-muted"
        style="font-weight:600;">
            {label}
        </span>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    "<hr style='margin:0.5rem 0 1rem 0;'>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Order Cards
# ---------------------------------------------------------

for _, row in df.iterrows():

    with st.container(border=True):

        c1, c2, c3, c4, c5, c6 = st.columns(
            [1.5, 2, 3, 0.8, 1.5, 1.5]
        )

        # ---------------------------------------------
        # Order ID
        # ---------------------------------------------

        c1.markdown(
            f"""
            <span style="
                color:#3B82F6;
                font-weight:700;
                font-family:monospace;
            ">
                #{row["order_ref"]}
            </span>
            """,
            unsafe_allow_html=True,
        )

        # ---------------------------------------------
        # Customer
        # ---------------------------------------------

        c2.markdown(
            f"**{row['customer']}**"
        )

        # ---------------------------------------------
        # Product
        # ---------------------------------------------

        c3.markdown(
            f"""
            **{row["product"]}**

            <span class="dh-muted">
                {row["category"]}
            </span>
            """,
            unsafe_allow_html=True,
        )

        # ---------------------------------------------
        # Quantity
        # ---------------------------------------------

        c4.markdown(
            str(row["quantity"])
        )

        # ---------------------------------------------
        # Amount
        # ---------------------------------------------

        c5.markdown(
            f"""
            <span style="
                font-weight:700;
                font-family:monospace;
            ">
                {format_currency(row["amount"])}
            </span>
            """,
            unsafe_allow_html=True,
        )

        # ---------------------------------------------
        # Status
        # ---------------------------------------------

        c6.markdown(
            display_status(row["status"]),
            unsafe_allow_html=True,
        )


        # ---------------------------------------------
        # Order Details
        # ---------------------------------------------

        with st.expander("View Order Details"):

            # We already have all details from the list
            # endpoint, so no extra API request is necessary.

            left, right = st.columns(2)

            # -----------------------------------------
            # Order Information
            # -----------------------------------------

            with left:

                st.markdown(
                    "#### Order Information"
                )

                st.write(
                    f"**Order ID:** {row['order_ref']}"
                )

                st.write(
                    f"**Order Date:** "
                    f"{row['date'].strftime('%d %b %Y, %I:%M %p')}"
                    if pd.notna(row["date"])
                    else "**Order Date:** N/A"
                )

                st.write(
                    f"**Status:** "
                    f"{str(row['status']).title()}"
                )

                st.write(
                    f"**Quantity:** {row['quantity']}"
                )

                st.write(
                    f"**Total Amount:** "
                    f"{format_currency(row['amount'])}"
                )

            # -----------------------------------------
            # Customer Information
            # -----------------------------------------

            with right:

                st.markdown(
                    "#### Customer Information"
                )

                st.write(
                    f"**Customer:** {row['customer']}"
                )

                st.write(
                    f"**Email:** {row['email']}"
                )

            st.markdown("---")

            # -----------------------------------------
            # Product Information
            # -----------------------------------------

            st.markdown(
                "#### Product Information"
            )

            p1, p2, p3 = st.columns(3)

            p1.write(
                f"**Product:** {row['product']}"
            )

            p2.write(
                f"**Category:** {row['category']}"
            )

            p3.write(
                f"**Product Ref:** {row['product_ref']}"
            )

            st.markdown("---")

            # -----------------------------------------
            # Status Message
            # -----------------------------------------

            current_status = str(
                row["status"]
            ).lower()

            if current_status == "delivered":

                st.success(
                    "✓ Order delivered successfully."
                )

            elif current_status == "shipped":

                st.info(
                    "🚚 Order has been shipped and is in transit."
                )

            elif current_status == "processing":

                st.warning(
                    "⏳ Order is currently being prepared."
                )

            elif current_status == "pending":

                st.warning(
                    "Waiting for order confirmation."
                )

            elif current_status == "cancelled":

                st.error(
                    "This order has been cancelled."
                )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.markdown("")

st.caption(
    f"Showing {len(df)} of {total} total orders"
)