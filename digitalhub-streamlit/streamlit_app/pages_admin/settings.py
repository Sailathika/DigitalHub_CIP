import streamlit as st

from core.api_client import ApiError, get, post
from core.auth import update_profile

st.title("Settings")
st.caption("Manage your admin profile, security, and view system information.")

user = st.session_state.user

st.markdown("##### Admin Profile")
with st.form("profile_form", border=True):
    c1, c2 = st.columns(2)
    full_name = c1.text_input("Full Name", value=user["name"])
    c2.text_input("Email", value=user["email"], disabled=True, help="Email is your login ID and can't be changed here.")
    c3, c4 = st.columns(2)
    phone = c3.text_input("Phone Number", value=user.get("phone") or "")
    address = c4.text_input("Address", value=user.get("address") or "")
    save_profile = st.form_submit_button("Save Changes", type="primary")

    if save_profile:
        try:
            update_profile(full_name, phone, address)
            st.success("Profile updated.")
        except ApiError as exc:
            st.error(exc.message)

st.markdown("##### Change Password")
with st.form("password_form", border=True):
    current_password = st.text_input("Current Password", type="password")
    c1, c2 = st.columns(2)
    new_password = c1.text_input("New Password", type="password")
    confirm_password = c2.text_input("Confirm New Password", type="password")
    save_password = st.form_submit_button("Update Password", type="primary")

    if save_password:
        if len(new_password) < 8:
            st.error("New password must be at least 8 characters.")
        elif new_password != confirm_password:
            st.error("New passwords do not match.")
        else:
            try:
                post(
                    "/auth/change-password",
                    json={"current_password": current_password, "new_password": new_password},
                )
                st.success("Password updated.")
            except ApiError as exc:
                st.error(exc.message)

st.markdown("##### System Information")
try:
    info = get("/system/info")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**Application**  \n{info['app_name']}")
        c2.markdown(f"**Version**  \n{info['app_version']}")
        c3.markdown(f"**Environment**  \n{info['environment'].title()}")
        c1.markdown(f"**Database Engine**  \n{info['database_engine']}")
        c2.markdown(f"**Total Users**  \n{info['total_users']}")
        c3.markdown(f"**Admins / Vendors**  \n{info['total_admins']} / {info['total_vendors']}")
        c1.markdown(f"**Datasets Processed**  \n{info['total_datasets']}")
        st.markdown(f"**MLflow Tracking URI**  \n`{info['mlflow_tracking_uri']}`")
except ApiError as exc:
    st.error(exc.message)
