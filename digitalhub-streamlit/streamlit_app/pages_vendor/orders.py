import pandas as pd
import streamlit as st

from core.theme import badge_html
from core.utils import format_currency, format_number


st.title("Orders")
st.caption("View and track orders placed for your products.")


# ---------------------------------------------------------
# Demo Order Data
# ---------------------------------------------------------

orders = [
    {"order_ref":"ORD1001","customer":"Rahul Sharma","product":"Samsung Galaxy S25","category":"Smartphones","quantity":1,"amount":79999,"status":"Delivered","date":"2026-08-02"},
    {"order_ref":"ORD1002","customer":"Priya Nair","product":"Sony WH-1000XM6","category":"Audio","quantity":2,"amount":59998,"status":"Shipped","date":"2026-08-02"},
    {"order_ref":"ORD1003","customer":"Arjun Kumar","product":"Logitech MX Master 3S","category":"Accessories","quantity":1,"amount":8995,"status":"Processing","date":"2026-08-01"},
    {"order_ref":"ORD1004","customer":"Sneha Patel","product":"Apple Watch Series 10","category":"Wearables","quantity":1,"amount":49900,"status":"Pending","date":"2026-07-31"},
    {"order_ref":"ORD1005","customer":"Vikram Singh","product":"Dell XPS 15","category":"Laptops","quantity":1,"amount":168990,"status":"Delivered","date":"2026-07-30"},
    {"order_ref":"ORD1006","customer":"Ananya Roy","product":"iPhone 17 Pro","category":"Smartphones","quantity":1,"amount":134900,"status":"Delivered","date":"2026-07-30"},
    {"order_ref":"ORD1007","customer":"Karan Mehta","product":"JBL Flip 7","category":"Audio","quantity":2,"amount":25998,"status":"Cancelled","date":"2026-07-29"},
    {"order_ref":"ORD1008","customer":"Neha Verma","product":"Canon EOS R10","category":"Cameras","quantity":1,"amount":87999,"status":"Shipped","date":"2026-07-28"},
    {"order_ref":"ORD1009","customer":"Amit Joshi","product":"Samsung Smart Monitor","category":"Monitors","quantity":1,"amount":24999,"status":"Delivered","date":"2026-07-28"},
    {"order_ref":"ORD1010","customer":"Pooja Das","product":"Boat Airdopes 311","category":"Audio","quantity":3,"amount":4497,"status":"Delivered","date":"2026-07-27"},
    {"order_ref":"ORD1011","customer":"Rohan Gupta","product":"HP Victus Gaming Laptop","category":"Laptops","quantity":1,"amount":78999,"status":"Pending","date":"2026-07-27"},
    {"order_ref":"ORD1012","customer":"Meera Iyer","product":"OnePlus Pad 3","category":"Tablets","quantity":1,"amount":42999,"status":"Delivered","date":"2026-07-26"},
    {"order_ref":"ORD1013","customer":"Sanjay Rao","product":"AirPods Pro","category":"Audio","quantity":2,"amount":49998,"status":"Processing","date":"2026-07-25"},
    {"order_ref":"ORD1014","customer":"Deepika Sen","product":"LG OLED 55 TV","category":"Television","quantity":1,"amount":129999,"status":"Delivered","date":"2026-07-25"},
    {"order_ref":"ORD1015","customer":"Harish Kumar","product":"Acer Predator Helios","category":"Laptops","quantity":1,"amount":149999,"status":"Delivered","date":"2026-07-24"},
    {"order_ref":"ORD1016","customer":"Ishita Jain","product":"Samsung Galaxy Buds 3","category":"Audio","quantity":1,"amount":9999,"status":"Shipped","date":"2026-07-24"},
    {"order_ref":"ORD1017","customer":"Varun Nair","product":"ROG Phone 10","category":"Smartphones","quantity":1,"amount":89999,"status":"Pending","date":"2026-07-23"},
    {"order_ref":"ORD1018","customer":"Divya Kapoor","product":"Fitbit Charge 7","category":"Wearables","quantity":2,"amount":31998,"status":"Delivered","date":"2026-07-23"},
    {"order_ref":"ORD1019","customer":"Nikhil Shah","product":"Lenovo Legion 5","category":"Laptops","quantity":1,"amount":118999,"status":"Processing","date":"2026-07-22"},
    {"order_ref":"ORD1020","customer":"Asha Reddy","product":"Kindle Paperwhite","category":"Tablets","quantity":1,"amount":14999,"status":"Delivered","date":"2026-07-21"},
    {"order_ref":"ORD1021","customer":"Kishore Babu","product":"Galaxy Tab S10","category":"Tablets","quantity":1,"amount":68999,"status":"Delivered","date":"2026-07-20"},
    {"order_ref":"ORD1022","customer":"Lavanya S","product":"Nothing Phone 4","category":"Smartphones","quantity":1,"amount":45999,"status":"Shipped","date":"2026-07-19"},
    {"order_ref":"ORD1023","customer":"Akash Menon","product":"GoPro Hero 14","category":"Cameras","quantity":1,"amount":54999,"status":"Delivered","date":"2026-07-18"},
    {"order_ref":"ORD1024","customer":"Sowmya K","product":"Xiaomi Smart Band 10","category":"Wearables","quantity":2,"amount":8998,"status":"Cancelled","date":"2026-07-18"},
    {"order_ref":"ORD1025","customer":"Manoj Pillai","product":"BenQ 27 Monitor","category":"Monitors","quantity":1,"amount":38999,"status":"Delivered","date":"2026-07-17"},
]


df = pd.DataFrame(orders)
df["date"] = pd.to_datetime(df["date"])


# ---------------------------------------------------------
# Filters
# ---------------------------------------------------------

f1, f2, f3 = st.columns([2,1,1])

search = f1.text_input(
    "Search Orders",
    placeholder="Customer, product or order ID..."
)

status_filter = f2.selectbox(
    "Status",
    ["All","Pending","Processing","Shipped","Delivered","Cancelled"]
)

sort_by = f3.selectbox(
    "Sort By",
    ["Newest","Oldest","Highest Amount","Lowest Amount"]
)


filtered = df.copy()


if search:
    text = search.lower()

    filtered = filtered[
        filtered["customer"].str.lower().str.contains(text)
        |
        filtered["product"].str.lower().str.contains(text)
        |
        filtered["order_ref"].str.lower().str.contains(text)
    ]


if status_filter != "All":
    filtered = filtered[
        filtered["status"] == status_filter
    ]


if sort_by == "Newest":
    filtered = filtered.sort_values(
        "date",
        ascending=False
    )

elif sort_by == "Oldest":
    filtered = filtered.sort_values("date")

elif sort_by == "Highest Amount":
    filtered = filtered.sort_values(
        "amount",
        ascending=False
    )

else:
    filtered = filtered.sort_values("amount")


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Total Orders",
    format_number(len(df))
)

c2.metric(
    "Revenue",
    format_currency(df["amount"].sum())
)

c3.metric(
    "Average Order",
    format_currency(df["amount"].mean())
)

pending = len(
    df[
        df["status"].isin(
            ["Pending","Processing"]
        )
    ]
)

c4.metric(
    "Pending",
    format_number(pending)
)

st.markdown("")

# ---------------------------------------------------------
# Orders Table / Cards
# ---------------------------------------------------------

STATUS_VARIANT = {
    "Pending": "warning",
    "Processing": "default",
    "Shipped": "default",
    "Delivered": "success",
    "Cancelled": "danger",
}


st.markdown("### Order History")


if filtered.empty:
    st.info("No orders match your search or selected filter.")
    st.stop()


# Header row

headers = st.columns(
    [1.5, 2, 3, 1, 1.5, 1.5]
)

labels = [
    "ORDER",
    "CUSTOMER",
    "PRODUCT",
    "QTY",
    "AMOUNT",
    "STATUS"
]


for col, label in zip(headers, labels):
    col.markdown(
        f"""
        <span class="dh-muted"
        style="font-weight:600;">
        {label}
        </span>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    "<hr style='margin:0.5rem 0 1rem 0;'>",
    unsafe_allow_html=True
)



# ---------------------------------------------------------
# Order Cards
# ---------------------------------------------------------

for _, row in filtered.iterrows():

    with st.container(border=True):

        c1, c2, c3, c4, c5, c6 = st.columns(
            [1.5, 2, 3, 1, 1.5, 1.5]
        )


        # Order ID

        c1.markdown(
            f"""
            <span style="
            color:#3B82F6;
            font-weight:700;
            font-family:monospace;">
            #{row["order_ref"]}
            </span>
            """,
            unsafe_allow_html=True
        )


        # Customer

        c2.markdown(
            f"""
            **{row["customer"]}**
            """
        )


        # Product

        c3.markdown(
            f"""
            **{row["product"]}**

            <span class="dh-muted">
            {row["category"]}
            </span>
            """,
            unsafe_allow_html=True
        )


        # Quantity

        c4.markdown(
            str(row["quantity"])
        )


        # Amount

        c5.markdown(
            f"""
            <span style="
            font-weight:700;
            font-family:monospace;">
            {format_currency(row["amount"])}
            </span>
            """,
            unsafe_allow_html=True
        )


        # Status

        c6.markdown(
            badge_html(
                row["status"],
                STATUS_VARIANT.get(
                    row["status"],
                    "default"
                )
            ),
            unsafe_allow_html=True
        )



        # -------------------------------------------------
        # Details
        # -------------------------------------------------

        with st.expander(
            "View Order Details"
        ):

            left, right = st.columns(2)


            with left:

                st.markdown(
                    "#### Order Information"
                )

                st.write(
                    f"**Order ID:** {row['order_ref']}"
                )

                st.write(
                    f"**Customer:** {row['customer']}"
                )

                st.write(
                    f"**Order Date:** {row['date'].strftime('%d %b %Y')}"
                )

                st.write(
                    f"**Status:** {row['status']}"
                )



            with right:

                st.markdown(
                    "#### Product Information"
                )

                st.write(
                    f"**Product:** {row['product']}"
                )

                st.write(
                    f"**Category:** {row['category']}"
                )

                st.write(
                    f"**Quantity:** {row['quantity']}"
                )

                st.write(
                    f"**Total Amount:** {format_currency(row['amount'])}"
                )



            st.markdown("---")


            # Order status message

            if row["status"] == "Delivered":

                st.success(
                    "✓ Order delivered successfully."
                )

            elif row["status"] == "Shipped":

                st.info(
                    "🚚 Order has been shipped and is in transit."
                )

            elif row["status"] == "Processing":

                st.warning(
                    "⏳ Order is being prepared."
                )

            elif row["status"] == "Pending":

                st.warning(
                    "Waiting for order confirmation."
                )

            else:

                st.error(
                    "This order has been cancelled."
                )



st.markdown("")


st.caption(
    f"Showing {len(filtered)} of {len(df)} total orders"
)