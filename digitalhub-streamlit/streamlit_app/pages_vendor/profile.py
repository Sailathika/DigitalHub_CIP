import streamlit as st

from core.api_client import ApiError, get, put

st.title("Profile")
st.caption("Manage your store's business information.")

try:
    profile = get("/vendor/profile")
except ApiError as exc:
    st.error(exc.message)
    st.stop()

with st.form("vendor_profile_form", border=True):
    c1, c2 = st.columns(2)
    business_name = c1.text_input("Business Name", value=profile.get("business_name") or "")
    owner_name = c2.text_input("Owner Name", value=profile["owner_name"])

    c3, c4 = st.columns(2)
    c3.text_input("Email", value=profile["email"], disabled=True, help="Email is your login ID and can't be changed here.")
    phone = c4.text_input("Phone Number", value=profile.get("phone") or "")

    gst_number = st.text_input("GST Number", value=profile.get("gst_number") or "", placeholder="22AAAAA0000A1Z5")
    address = st.text_input("Business Address", value=profile.get("address") or "")

    c5, c6 = st.columns(2)
    city = c5.text_input("City", value=profile.get("city") or "")
    state = c6.text_input("State", value=profile.get("state") or "")

    submitted = st.form_submit_button("Save Changes", type="primary")

    if submitted:
        if not all([business_name, owner_name, phone, address, city, state]):
            st.error("Please fill in all required fields (GST Number is optional).")
        else:
            try:
                put(
                    "/vendor/profile",
                    json={
                        "business_name": business_name,
                        "owner_name": owner_name,
                        "phone": phone,
                        "gst_number": gst_number or None,
                        "address": address,
                        "city": city,
                        "state": state,
                    },
                )
                st.success("Profile updated.")
                st.rerun()
            except ApiError as exc:
                st.error(exc.message)
