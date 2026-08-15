import streamlit as st

from core.api_client import ApiError
from core.auth import init_session_state, is_authenticated, login, logout, register_vendor, current_role
from core.theme import inject_global_css, LOGO_SVG

st.set_page_config(
    page_title="DigitalHub_CIP",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#x26A1;</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
inject_global_css()

def hide_auth_navigation():
    st.markdown(
        """
        <style>
        /* Hide sidebar completely on authentication page */
        section[data-testid="stSidebar"] {
            display: none !important;
        }

        /* Hide Streamlit navigation */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* Remove sidebar spacing */
        [data-testid="stAppViewContainer"] {
            margin-left: 0 !important;
        }

        /* Full-width authentication page */
        .main .block-container {
            max-width: 100% !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
# ── Auth page ──────────────────────────────────────────────────────────────────
def render_login_form():
    col_left, col_right = st.columns([1, 1.2])

    # ── Left branding panel ──
    with col_left:
        st.markdown(
            f"""
            <div class="auth-left-panel">
                <div>
                    <div class="auth-logo">
                        <div class="auth-logo-badge">{LOGO_SVG}</div>
                        <span class="auth-brand-name">DigitalHub_CIP</span>
                    </div>
                    <div class="auth-headline">
                        Customers Insights Platform
                    </div>
                    <div class="auth-subtext">
                        Enterprise analytics, vendor management,
                        and marketplace insights — all in one place.
                    </div>
                </div>
                <div class="auth-footer">
                    Electronics marketplace &nbsp;&middot;&nbsp; Customers Insights Platform
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Right form panel ──
    with col_right:
        st.markdown('<div class="auth-right-panel">', unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            with st.form("login_form", border=False):
                st.markdown(
                    "<p style='font-size:1.05rem;font-weight:700;color:#0F172A;"
                    "margin-bottom:1rem;'>Welcome back</p>",
                    unsafe_allow_html=True,
                )
                role = st.radio(
                    "Sign in as",
                    ["admin", "vendor"],
                    horizontal=True,
                    format_func=str.title,
                )
                email = st.text_input("Email address", placeholder="you@company.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button(
                    "Sign In", type="primary", use_container_width=True
                )
                if submitted:
                    if not email or not password:
                        st.error("Please enter your email and password.")
                    else:
                        try:
                            login(email, password, role)
                            st.rerun()
                        except ApiError as exc:
                            st.error(exc.message)

           

        with tab_register:
            with st.form("register_form", border=False):
                st.markdown(
                    "<p style='font-size:1.05rem;font-weight:700;color:#0F172A;"
                    "margin-bottom:1rem;'>Create a vendor account</p>",
                    unsafe_allow_html=True,
                )
                business_name = st.text_input("Business Name")
                owner_name = st.text_input("Owner Name")
                email_r = st.text_input("Email", key="reg_email")
                phone = st.text_input("Phone Number")
                address = st.text_input("Business Address")
                password_r = st.text_input("Password", type="password", key="reg_password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted_r = st.form_submit_button(
                    "Create Account", type="primary", use_container_width=True
                )
                if submitted_r:
                    if not all([business_name, owner_name, email_r, phone, address, password_r]):
                        st.error("Please fill in every field.")
                    elif password_r != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(password_r) < 8:
                        st.error("Password must be at least 8 characters.")
                    else:
                        try:
                            register_vendor(
                                business_name, owner_name, email_r, phone, address, password_r
                            )
                            st.rerun()
                        except ApiError as exc:
                            st.error(exc.message)

        st.markdown("</div>", unsafe_allow_html=True)


# ── Navigation ─────────────────────────────────────────────────────────────────
def build_navigation():
    role = current_role()

    if role == "admin":
        return st.navigation(
            {
                "Overview": [
                    st.Page("pages_admin/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True),
                ],
                "Data Management": [
                    st.Page("pages_admin/upload_dataset.py",  title="Upload Dataset",  icon=":material/upload:"),
                    st.Page("pages_admin/data_validation.py", title="Data Validation", icon=":material/fact_check:"),
                    st.Page("pages_admin/data_cleaning.py",   title="Data Cleaning",   icon=":material/cleaning_services:"),
                ],
                "Insights": [
                    st.Page("pages_admin/customer_analytics.py", title="Customer Analytics", icon=":material/people:"),
                    st.Page("pages_admin/clv_prediction.py",     title="CLV Prediction",     icon=":material/auto_graph:"),
                    st.Page("pages_admin/churn_prediction.py",   title="Churn Prediction",   icon=":material/trending_down:"),
                    st.Page("pages_admin/sales_analytics.py",    title="Sales Analytics",    icon=":material/bar_chart:"),
                ],
                "Marketplace": [
                    st.Page("pages_admin/vendor_management.py", title="Vendor Management", icon=":material/storefront:"),
                    st.Page("pages_admin/vendor_details.py",    title="Vendor Details",    icon=":material/manage_search:"),
                ],
                "System": [
                    st.Page("pages_admin/reports.py",  title="Reports",  icon=":material/description:"),
                    st.Page("pages_admin/settings.py", title="Settings", icon=":material/settings:"),
                ],
            }
        )

    return st.navigation(
        {
            "Overview": [
                st.Page("pages_vendor/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True),
            ],
            "Store": [
                st.Page("pages_vendor/my_products.py", title="My Products", icon=":material/inventory_2:"),
                st.Page("pages_vendor/orders.py",      title="Orders",      icon=":material/receipt_long:"),
                st.Page("pages_vendor/inventory.py",   title="Inventory",   icon=":material/warehouse:"),
            ],
            "Insights": [
                st.Page("pages_vendor/sales_analytics.py", title="Sales Analytics", icon=":material/bar_chart:"),
                st.Page("pages_vendor/reports.py",         title="Reports",         icon=":material/description:"),
            ],
            "Account": [
                st.Page("pages_vendor/profile.py", title="Profile", icon=":material/person:"),
            ],
        }
    )


# ── Guard ──────────────────────────────────────────────────────────────────────
if not is_authenticated():
    hide_auth_navigation()
    render_login_form()
    st.stop()

# ── Sidebar Brand (Forces to Top via CSS order: -100) ─────────────────────────
with st.sidebar:
    role_label = current_role().upper()
    st.markdown(
        f"""
        <div class="dh-brand-wrapper">
            <div class="dh-brand">
                <div class="dh-brand-logo">{LOGO_SVG}</div>
                <div>
                    <div class="dh-brand-name">DigitalHub_CIP</div>
                    <div class="dh-brand-role">{role_label} PORTAL</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

pg = build_navigation()

# ── Sidebar User Block & Logout Button (Forces to Bottom via CSS order: 100) ──
with st.sidebar:
    user = st.session_state.user
    st.markdown(
        f"""
        <div class="dh-user-wrapper">
            <hr class="dh-sidebar-divider" />
            <div class="dh-user-block">
                <div class="dh-user-name">{user['name']}</div>
                <div class="dh-user-email">{user['email']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Sign Out", use_container_width=True, key="sidebar_logout_btn"):
        logout()
        st.rerun()

pg.run()
