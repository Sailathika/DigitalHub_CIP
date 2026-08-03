import streamlit as st

from core.api_client import ApiError, get, post
from core.theme import badge_html

st.title("Vendor Management")
st.caption("Search, filter, and manage every vendor on DigitalHub_CIP.")

with st.expander("Add Vendor", icon=":material/add:"):
    with st.form("add_vendor_form"):
        c1, c2 = st.columns(2)
        business_name = c1.text_input("Business Name")
        owner_name = c2.text_input("Owner Name")

        c3, c4 = st.columns(2)
        email = c3.text_input("Email")
        phone = c4.text_input("Phone Number")

        address = st.text_input("Address")

        c5, c6, c7 = st.columns(3)
        category = c5.text_input("Category", placeholder="e.g. Smartphones")
        gst_number = c6.text_input("GST Number (optional)")
        commission = c7.number_input(
            "Commission %",
            min_value=0.0,
            max_value=100.0,
            value=10.0,
            step=0.5,
        )

        password = st.text_input("Temporary Password", type="password")

        submitted = st.form_submit_button("Add Vendor", type="primary")

        if submitted:
            if not all([business_name, owner_name, email, phone, address, password]):
                st.error("Please fill in all required fields.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                try:
                    post(
                        "/vendors/",
                        json={
                            "business_name": business_name,
                            "owner_name": owner_name,
                            "email": email,
                            "phone": phone,
                            "address": address,
                            "category": category or None,
                            "gst_number": gst_number or None,
                            "commission_percent": commission,
                            "password": password,
                        },
                    )
                    st.success(f"Vendor '{business_name}' created.")
                    st.rerun()

                except ApiError as exc:
                    st.error(exc.message)

st.markdown("---")

# ---------------- Filters ---------------- #

try:
    initial = get("/vendors/")
except ApiError as exc:
    st.error(exc.message)
    st.stop()

f1, f2, f3 = st.columns([2, 1, 1])

search = f1.text_input(
    "Search by business name, owner, or email",
    key="vendor_search",
)

status_filter = f2.selectbox(
    "Status",
    ["all"] + initial["statuses"],
    format_func=str.title,
)

category_filter = f3.selectbox(
    "Category",
    ["all"] + initial["categories"],
)

try:
    params = {}

    if search:
        params["search"] = search

    if status_filter != "all":
        params["status_filter"] = status_filter

    if category_filter != "all":
        params["category"] = category_filter

    data = get("/vendors/", params=params)

except ApiError as exc:
    st.error(exc.message)
    st.stop()

vendors = data["vendors"]

st.caption(f"Showing {len(vendors)} vendors")

status_variant = {
    "active": "success",
    "pending": "warning",
    "suspended": "danger",
}

if vendors:

    h1, h2, h3, h4, h5 = st.columns([3, 1.5, 1, 1, 2])

    h1.markdown(
        "<span class='dh-muted' style='font-weight:600;'>VENDOR</span>",
        unsafe_allow_html=True,
    )

    h2.markdown(
        "<span class='dh-muted' style='font-weight:600;'>CATEGORY</span>",
        unsafe_allow_html=True,
    )

    h3.markdown(
        "<span class='dh-muted' style='font-weight:600;'>COMMISSION</span>",
        unsafe_allow_html=True,
    )

    h4.markdown(
        "<span class='dh-muted' style='font-weight:600;'>STATUS</span>",
        unsafe_allow_html=True,
    )

    h5.markdown(
        "<span class='dh-muted' style='font-weight:600;'>ACTIONS</span>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<hr style='margin:0.4rem 0 0.8rem 0;border-color:#E2E8F0;'>",
        unsafe_allow_html=True,
    )

for vendor in vendors:

    with st.container(border=True):

        c1, c2, c3, c4, c5 = st.columns([3, 1.5, 1, 1, 2])

        c1.markdown(
            f"**{vendor['business_name']}**  \n"
            f"<span class='dh-muted'>{vendor['full_name']} · {vendor['email']}</span>",
            unsafe_allow_html=True,
        )

        c2.markdown(vendor.get("category") or "—")

        c3.markdown(f"{vendor['commission_percent']}%")

        c4.markdown(
            badge_html(
                vendor["vendor_status"].title(),
                status_variant.get(vendor["vendor_status"], "default"),
            ),
            unsafe_allow_html=True,
        )

        with c5:

            btn_cols = st.columns(3)

            if btn_cols[0].button(
                "View",
                key=f"view_{str(vendor['id'])}",
            ):
                st.session_state.selected_vendor_id = vendor["id"]
                st.switch_page("pages_admin/vendor_details.py")

            if vendor["vendor_status"] == "pending":

                if btn_cols[1].button(
                    "Approve",
                    key=f"approve_{str(vendor['id'])}",
                ):
                    try:
                        post(f"/vendors/{vendor['id']}/approve")
                        st.rerun()
                    except ApiError as exc:
                        st.error(exc.message)

            elif vendor["vendor_status"] == "suspended":

                if btn_cols[1].button(
                    "Activate",
                    key=f"activate_{str(vendor['id'])}",
                ):
                    try:
                        post(f"/vendors/{vendor['id']}/activate")
                        st.rerun()
                    except ApiError as exc:
                        st.error(exc.message)

            else:

                if btn_cols[1].button(
                    "Suspend",
                    key=f"suspend_{str(vendor['id'])}",
                ):
                    try:
                        post(f"/vendors/{vendor['id']}/suspend")
                        st.rerun()
                    except ApiError as exc:
                        st.error(exc.message)

if not vendors:
    st.info("No vendors match your search or filters.")