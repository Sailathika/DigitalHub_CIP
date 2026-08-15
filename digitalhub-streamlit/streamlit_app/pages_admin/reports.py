import streamlit as st

from core.api_client import ApiError, get, get_file, post
from core.auth import require_dataset

st.title("📄 Reports")
st.caption("Generate and export analytics reports from your marketplace data.")

dataset = require_dataset()

# ---------- Custom Styling ----------
st.markdown(
    """
    <style>
    .report-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 24px;
        height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .report-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .report-desc {
        color: #6b7280;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Fetch Reports ----------
try:
    existing = get("/reports/", params={"dataset_id": dataset["id"]})
    reports = existing.get("reports", [])
except ApiError as exc:
    st.error(exc.message)
    reports = []

# ---------- Generate Report ----------
if not reports:
    st.info("No analytics report has been generated yet.")

    if st.button("Generate Analytics Report", type="primary"):
        with st.spinner(
            "Generating report, segmentation, CLV, churn and recommendations..."
        ):
            try:
                post(f"/reports/{dataset['id']}/generate", json={})
                st.rerun()
            except ApiError as exc:
                st.error(exc.message)

else:
    report = reports[0]

    col1, col2 = st.columns(2)

    # PDF REPORT CARD
    with col1:
        st.markdown(
            """
            <div class="report-card">
                <div>
                    <div class="report-title">📄 Analytics Report</div>
                    <div class="report-desc">
                        Complete marketplace analytics including customer
                        segmentation, CLV analysis, churn prediction,
                        recommendations and business insights.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            file_response = get_file(f"/reports/{report['id']}/download")

            st.download_button(
                "⬇ Download PDF Report",
                data=file_response.content,
                file_name="DigitalHub_Analytics_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except ApiError:
            st.error("PDF report unavailable")

    # CSV EXPORT CARD
    with col2:
        st.markdown(
            """
            <div class="report-card">
                <div>
                    <div class="report-title">📊 Customer Data Export</div>
                    <div class="report-desc">
                        Export customer-level analytics data including
                        segments, CLV values, churn scores and related
                        customer insights.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            csv_response = get_file(
                f"/reports/{dataset['id']}/export-csv"
            )

            st.download_button(
                "⬇ Download CSV Export",
                data=csv_response.content,
                file_name=f"customers_{dataset['id']}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        except ApiError as exc:
            st.warning("CSV export unavailable")