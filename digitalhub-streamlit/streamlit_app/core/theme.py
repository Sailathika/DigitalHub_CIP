"""
Visual polish layer — DigitalHub_CIP premium enterprise theme.
Injects a Midnight Blue design system: sidebar, KPI cards, tables,
forms, typography, and layout tokens that make the app feel like a
production SaaS product rather than a default Streamlit demo.
"""
import streamlit as st

# ── Design tokens ──────────────────────────────────────────────────────────────
SIDEBAR_BG   = "#111827"   # Midnight Blue
PRIMARY      = "#3B82F6"   # Enterprise Blue
PRIMARY_DARK = "#2563EB"
PRIMARY_MUTED= "#EFF6FF"   # Very light blue tint
SURFACE      = "#FFFFFF"
SURFACE_2    = "#F8FAFC"
BORDER       = "#E2E8F0"
DARK         = "#0F172A"
MUTED        = "#64748B"
SUCCESS      = "#10B981"
WARNING      = "#F59E0B"
DANGER       = "#EF4444"

BADGE_COLORS = {
    "default":   (PRIMARY_MUTED, PRIMARY),
    "success":   ("#ECFDF5", SUCCESS),
    "warning":   ("#FFFBEB", WARNING),
    "danger":    ("#FEF2F2", DANGER),
    "secondary": ("#F1F5F9", MUTED),
}


def inject_global_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* ── Base typography ─────────────────────────────────────────────── */
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
            color: {DARK};
            font-size: 14px;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}

        /* ── Main content area ───────────────────────────────────────────── */
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1340px;
            background-color: {SURFACE};
        }}
        [data-testid="stAppViewContainer"] {{
            background-color: {SURFACE_2};
        }}
        [data-testid="stHeader"] {{
            background-color: {SURFACE};
            border-bottom: 1px solid {BORDER};
        }}

        /* ── Page headings ───────────────────────────────────────────────── */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Inter', sans-serif;
            color: {DARK};
            letter-spacing: -0.02em;
        }}
        h1 {{ font-size: 1.625rem; font-weight: 700; }}
        h2 {{ font-size: 1.25rem;  font-weight: 600; }}
        h3 {{ font-size: 1.05rem;  font-weight: 600; }}

        /* ── KPI / Metric cards ──────────────────────────────────────────── */
        div[data-testid="stMetric"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-top: 3px solid {PRIMARY};
            border-radius: 0.625rem;
            padding: 1.1rem 1.25rem 1rem 1.25rem;
            box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.04);
            transition: box-shadow 0.15s ease;
        }}
        div[data-testid="stMetric"]:hover {{
            box-shadow: 0 4px 12px rgba(59,130,246,0.10);
        }}
        div[data-testid="stMetricLabel"] {{
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: {MUTED};
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {DARK};
            line-height: 1.2;
            letter-spacing: -0.03em;
        }}
        div[data-testid="stMetricDelta"] {{
            font-size: 0.8rem;
            font-weight: 500;
        }}

        /* ── Sidebar — Midnight Blue ─────────────────────────────────────── */
        section[data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG} !important;
            border-right: none !important;
            width: 250px !important;
        }}
        
        /* Flexbox structure to force Brand to Top and Logout to Bottom */
        section[data-testid="stSidebar"] > div,
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
        section[data-testid="stSidebar"] .st-emotion-cache-1cypcdb {{
            display: flex !important;
            flex-direction: column !important;
            background-color: transparent !important;
        }}

        /* Remove default white card containers inside sidebar */
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"],
        section[data-testid="stSidebar"] div[data-testid="stElementContainer"],
        section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        /* Order elements: Brand top (-100), Nav middle (0), User bottom (100) */
        .dh-brand-wrapper,
        section[data-testid="stSidebar"] div:has(> .dh-brand-wrapper) {{
            order: -100 !important;
        }}
        section[data-testid="stSidebarNav"] {{
            order: 0 !important;
        }}
        .dh-user-wrapper,
        section[data-testid="stSidebar"] div:has(> .dh-user-wrapper),
        section[data-testid="stSidebar"] div:has(> button[key="sidebar_logout_btn"]) {{
            order: 100 !important;
        }}

        /* All sidebar text defaults to soft grey on dark bg */
        section[data-testid="stSidebar"] *,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div {{
            color: #CBD5E1;
        }}

        /* Nav section labels */
        section[data-testid="stSidebarNav"] p {{
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #475569 !important;
            padding: 0.9rem 1rem 0.25rem 1rem;
        }}
        /* Nav link items */
        section[data-testid="stSidebarNav"] a,
        section[data-testid="stSidebar"] nav a {{
            color: #94A3B8 !important;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            font-weight: 500;
            padding: 0.45rem 0.75rem;
            text-decoration: none !important;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: background 0.12s, color 0.12s;
            margin: 1px 0.5rem;
        }}
        section[data-testid="stSidebarNav"] a:hover,
        section[data-testid="stSidebar"] nav a:hover {{
            background-color: rgba(255,255,255,0.07) !important;
            color: #E2E8F0 !important;
        }}
        /* Active page */
        section[data-testid="stSidebarNav"] a[aria-current="page"],
        section[data-testid="stSidebar"] [aria-current="page"],
        section[data-testid="stSidebar"] nav a[aria-current="page"] {{
            background-color: rgba(59,130,246,0.18) !important;
            color: #93C5FD !important;
            font-weight: 600;
            border-radius: 0.375rem;
        }}
        section[data-testid="stSidebarNav"] a[aria-current="page"] *,
        section[data-testid="stSidebar"] nav a[aria-current="page"] span,
        section[data-testid="stSidebar"] nav a[aria-current="page"] p {{
            color: #93C5FD !important;
        }}

        /* Sidebar logout button */
        section[data-testid="stSidebar"] .stButton button {{
            background-color: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            color: #94A3B8 !important;
            border-radius: 0.375rem;
            font-size: 0.8rem;
            font-weight: 500;
            padding: 0.45rem 0.75rem;
            margin: 0.25rem 0.75rem 1rem 0.75rem;
            transition: background 0.15s, border-color 0.15s;
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{
            background-color: rgba(239,68,68,0.15) !important;
            border-color: rgba(239,68,68,0.35) !important;
            color: #FCA5A5 !important;
        }}

        /* ── Brand block ─────────────────────────────────────────────────── */
        .dh-brand-wrapper {{
            padding: 1.25rem 1rem 1rem 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 0.5rem;
        }}
        .dh-brand {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .dh-brand-logo {{
            width: 34px; height: 34px;
            background: {PRIMARY};
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }}
        .dh-brand-logo svg {{
            width: 18px; height: 18px; fill: white;
        }}
        .dh-brand-name {{
            font-size: 0.95rem;
            font-weight: 700;
            color: #F8FAFC !important;
            letter-spacing: -0.01em;
            line-height: 1.2;
        }}
        .dh-brand-role {{
            font-size: 0.65rem;
            color: #94A3B8 !important;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-top: 0.1rem;
        }}

        /* ── User block at bottom of sidebar ─────────────────────────────── */
        .dh-user-wrapper {{
            padding: 0.75rem 1rem 0.25rem 1rem;
            margin-top: auto;
        }}
        .dh-user-block {{
            display: flex;
            flex-direction: column;
            gap: 0.1rem;
        }}
        .dh-user-name {{
            font-size: 0.85rem;
            font-weight: 600;
            color: #F8FAFC !important;
        }}
        .dh-user-email {{
            font-size: 0.75rem;
            color: #94A3B8 !important;
        }}
        .dh-sidebar-divider {{
            border-color: rgba(255,255,255,0.08) !important;
            margin: 0.5rem 0 0.75rem 0 !important;
        }}

        /* ── Buttons ─────────────────────────────────────────────────────── */
        .stButton > button[kind="primary"],
        button[data-testid="baseButton-primary"] {{
            background: {PRIMARY};
            border: none;
            border-radius: 0.375rem;
            color: white !important;
            font-size: 0.875rem;
            font-weight: 600;
            padding: 0.5rem 1.25rem;
            transition: background 0.15s, box-shadow 0.15s;
            box-shadow: 0 1px 2px rgba(59,130,246,0.3);
        }}
        .stButton > button[kind="primary"]:hover,
        button[data-testid="baseButton-primary"]:hover {{
            background: {PRIMARY_DARK};
            box-shadow: 0 4px 12px rgba(59,130,246,0.35);
        }}
        .stButton > button[kind="secondary"],
        button[data-testid="baseButton-secondary"] {{
            background: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 0.375rem;
            color: {DARK} !important;
            font-size: 0.875rem;
            font-weight: 500;
            transition: border-color 0.15s, box-shadow 0.15s;
        }}
        .stButton > button[kind="secondary"]:hover {{
            border-color: {PRIMARY};
            box-shadow: 0 0 0 3px rgba(59,130,246,0.08);
        }}

        /* ── Inputs & Text areas ─────────────────────────────────────────── */
        input[type="text"], input[type="email"], input[type="password"],
        input[type="number"], textarea, select,
        div[data-baseweb="input"], div[data-baseweb="textarea"] {{
            border-radius: 0.375rem !important;
            border: 1px solid {BORDER} !important;
            background: {SURFACE} !important;
            font-size: 0.875rem !important;
            color: {DARK} !important;
            transition: border-color 0.15s, box-shadow 0.15s;
        }}
        input[type="text"]:focus, input[type="email"]:focus,
        input[type="password"]:focus, textarea:focus {{
            border-color: {PRIMARY} !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
            outline: none !important;
        }}
        label {{
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            color: {DARK} !important;
            letter-spacing: 0.01em;
        }}

        /* ── Forms ───────────────────────────────────────────────────────── */
        div[data-testid="stForm"] {{
            border: 1px solid {BORDER};
            border-radius: 0.625rem;
            padding: 1.5rem;
            background: {SURFACE};
            box-shadow: 0 1px 3px rgba(15,23,42,0.05);
        }}

        /* ── Tabs ────────────────────────────────────────────────────────── */
        button[data-baseweb="tab"] {{
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            color: {MUTED} !important;
            padding: 0.6rem 1rem;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {DARK} !important;
            font-weight: 600 !important;
        }}
        div[data-baseweb="tab-highlight"] {{
            background-color: {PRIMARY} !important;
            height: 2px !important;
        }}
        div[data-baseweb="tab-border"] {{
            background-color: {BORDER} !important;
        }}

        /* ── Dataframes / Tables ─────────────────────────────────────────── */
        div[data-testid="stDataFrame"] {{
            border: 1px solid {BORDER};
            border-radius: 0.5rem;
            overflow: hidden;
        }}
        div[data-testid="stDataFrame"] th {{
            background: {SURFACE_2} !important;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: {MUTED} !important;
            border-bottom: 1px solid {BORDER};
            padding: 0.6rem 0.75rem;
        }}
        div[data-testid="stDataFrame"] td {{
            font-size: 0.875rem;
            color: {DARK};
            padding: 0.55rem 0.75rem;
            border-bottom: 1px solid #F1F5F9;
        }}
        div[data-testid="stDataFrame"] tr:hover td {{
            background: {SURFACE_2};
        }}

        /* ── Expanders ───────────────────────────────────────────────────── */
        details[data-testid="stExpander"] {{
            border: 1px solid {BORDER} !important;
            border-radius: 0.5rem !important;
            background: {SURFACE};
        }}
        details[data-testid="stExpander"] summary {{
            font-weight: 600;
            font-size: 0.875rem;
            color: {DARK};
            padding: 0.75rem 1rem;
        }}

        /* ── Alerts / Info / Success ─────────────────────────────────────── */
        div[data-testid="stAlert"] {{
            border-radius: 0.5rem;
            font-size: 0.875rem;
        }}

        /* ── Selectbox / Radio ───────────────────────────────────────────── */
        div[data-baseweb="select"] {{
            border-radius: 0.375rem !important;
        }}
        div[role="radiogroup"] label span {{
            color: {DARK} !important;
            font-size: 0.875rem !important;
        }}

        /* ── Custom card components ──────────────────────────────────────── */
        .dh-badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.03em;
        }}
        .dh-card {{
            border: 1px solid {BORDER};
            border-radius: 0.625rem;
            padding: 1.25rem 1.5rem;
            background: {SURFACE};
            margin-bottom: 0.75rem;
            box-shadow: 0 1px 3px rgba(15,23,42,0.04);
        }}
        .dh-muted {{
            color: {MUTED};
            font-size: 0.83rem;
        }}
        .dh-section-label {{
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {MUTED};
            margin-bottom: 0.5rem;
        }}

        /* ── Page title block ────────────────────────────────────────────── */
        .dh-page-header {{
            padding-bottom: 1.25rem;
            border-bottom: 1px solid {BORDER};
            margin-bottom: 1.5rem;
        }}
        .dh-page-title {{
            font-size: 1.375rem;
            font-weight: 700;
            color: {DARK};
            letter-spacing: -0.02em;
        }}
        .dh-page-subtitle {{
            font-size: 0.83rem;
            color: {MUTED};
            margin-top: 0.15rem;
        }}

        /* ── Auth page ───────────────────────────────────────────────────── */
        .auth-left-panel {{
            background: linear-gradient(160deg, {SIDEBAR_BG} 0%, #1E3A5F 100%);
            border-radius: 1rem 0 0 1rem;
            padding: 3rem 2.5rem;
            min-height: 520px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .auth-right-panel {{
            background: {SURFACE};
            border-radius: 0 1rem 1rem 0;
            padding: 2.5rem;
        }}
        .auth-logo {{
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 2rem;
        }}
        .auth-logo-badge {{
            width: 38px; height: 38px;
            background: {PRIMARY};
            border-radius: 9px;
            display: flex; align-items: center; justify-content: center;
        }}
        .auth-logo-badge svg {{
            width: 20px; height: 20px; fill: white;
        }}
        .auth-brand-name {{
            font-size: 1.1rem;
            font-weight: 700;
            color: #F1F5F9;
            letter-spacing: -0.01em;
        }}
        .auth-headline {{
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            line-height: 1.3;
            letter-spacing: -0.02em;
            margin-bottom: 0.75rem;
        }}
        .auth-subtext {{
            font-size: 0.875rem;
            color: #64748B;
            line-height: 1.6;
        }}
        .auth-footer {{
            font-size: 0.75rem;
            color: #334155;
        }}

        /* ── Links ───────────────────────────────────────────────────────── */
        a, a:visited, a:hover, a:active {{
            color: {PRIMARY} !important;
            text-decoration: none;
        }}
        a:hover {{ text-decoration: underline; }}
        div[data-testid="stPageLink"] p,
        div[data-testid="stPageLink"] a {{
            color: {PRIMARY} !important;
        }}

        /* ── Markdown text ───────────────────────────────────────────────── */
        .stMarkdown p,
        .stMarkdown li,
        .stMarkdown span {{
            color: {DARK};
            font-size: 0.875rem;
        }}

        /* ── Main content containers (NOT sidebar) ───────────────────────── */
        .block-container div[data-testid="stVerticalBlockBorderWrapper"] {{
            border: 1px solid {BORDER} !important;
            border-radius: 0.5rem !important;
            background: {SURFACE};
        }}

        /* ── Dividers ────────────────────────────────────────────────────── */
        hr {{
            border-color: {BORDER} !important;
            margin: 1.25rem 0 !important;
        }}

        /* ── Caption / helper text ───────────────────────────────────────── */
        .stCaption p {{
            font-size: 0.78rem !important;
            color: {MUTED} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def badge_html(label: str, variant: str = "default") -> str:
    bg, fg = BADGE_COLORS.get(variant, BADGE_COLORS["default"])
    return f'<span class="dh-badge" style="background:{bg};color:{fg};">{label}</span>'


def badge(label: str, variant: str = "default") -> None:
    st.markdown(badge_html(label, variant), unsafe_allow_html=True)


def status_variant(status: str) -> str:
    mapping = {
        "active":    "success",
        "pending":   "warning",
        "suspended": "danger",
        "passed":    "success",
        "warning":   "warning",
        "failed":    "danger",
        "low":       "success",
        "medium":    "warning",
        "high":      "danger",
        "draft":     "warning",
        "inactive":  "secondary",
    }
    return mapping.get((status or "").lower(), "default")


# ── SVG icon helper (inline, no emoji) ────────────────────────────────────────
LOGO_SVG = """<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
</svg>"""
