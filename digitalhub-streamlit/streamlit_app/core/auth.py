"""
Session/auth helpers. Streamlit re-runs the whole script on every
interaction, so `st.session_state` is our equivalent of the React app's
AuthContext — it persists for the browser tab's session.
"""
import streamlit as st

from core.api_client import post, put


def init_session_state() -> None:
    defaults = {
        "token": None,
        "user": None,
        "active_dataset": None,  # {"id", "name", "rows", "status"} once uploaded
        "selected_vendor_id": None,  # used when navigating list -> detail views
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _to_frontend_user(user_out: dict) -> dict:
    full_name = user_out.get("full_name") or ""
    initials = "".join(part[0].upper() for part in full_name.split()[:2]) or "U"
    return {
        "id": user_out.get("id"),
        "name": full_name,
        "email": user_out.get("email"),
        "role": user_out.get("role"),
        "business_name": user_out.get("business_name"),
        "phone": user_out.get("phone"),
        "address": user_out.get("address"),
        "initials": initials,
    }


def login(email: str, password: str, role: str) -> dict:
    data = post("/auth/login", json={"email": email, "password": password, "role": role})
    st.session_state.token = data["access_token"]
    st.session_state.user = _to_frontend_user(data["user"])
    return st.session_state.user


def register_vendor(business_name, owner_name, email, phone, address, password) -> dict:
    data = post(
        "/auth/register",
        json={
            "business_name": business_name,
            "owner_name": owner_name,
            "email": email,
            "phone": phone,
            "address": address,
            "password": password,
        },
    )
    st.session_state.token = data["access_token"]
    st.session_state.user = _to_frontend_user(data["user"])
    return st.session_state.user


def update_profile(full_name, phone, address, business_name=None) -> dict:
    data = put(
        "/auth/me",
        json={"full_name": full_name, "phone": phone, "address": address, "business_name": business_name},
    )
    st.session_state.user = _to_frontend_user(data)
    return st.session_state.user


def logout() -> None:
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.active_dataset = None
    st.session_state.selected_vendor_id = None


def is_authenticated() -> bool:
    return bool(st.session_state.get("token") and st.session_state.get("user"))


def current_role() -> str:
    user = st.session_state.get("user")
    return user["role"] if user else ""


def require_dataset():
    """Call at the top of any page that needs an active, processed dataset.
    Returns the dataset dict, or renders a notice and stops the page."""
    dataset = st.session_state.get("active_dataset")
    if not dataset or dataset.get("status") != "transformed":
        st.info("Upload a dataset to start analyzing your business.", icon=":material/folder_open:")
        st.page_link("pages_admin/upload_dataset.py", label="Go to Upload Dataset", icon=":material/upload:")
        st.stop()
    return dataset
