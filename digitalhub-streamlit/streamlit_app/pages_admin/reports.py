import streamlit as st

from core.api_client import ApiError, get, get_file, post
from core.auth import require_dataset
from core.utils import format_date

st.title("Reports")
st.caption("Generate and export reports built from your marketplace data.")

dataset = require_dataset()

try:
    existing = get("/reports/", params={"dataset_id": dataset["id"]})
    reports = existing.get("reports", [])
except ApiError as exc:
    st.error(exc.message)
    reports = []

if not reports:
    st.info("No report generated yet for this dataset.")
    if st.button("Generate Full Analytics Report", type="primary"):
        with st.spinner("Generating report — this runs segmentation, CLV, and churn if not already trained…"):
            try:
                post(f"/reports/{dataset['id']}/generate", json={})
                st.rerun()
            except ApiError as exc:
                st.error(exc.message)
else:
    for report in reports:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"**{report['name']}**  \n<span class='dh-muted'>{report['description']}</span>", unsafe_allow_html=True)
            c1.caption(f"Generated {format_date(report['generated_at'])}")
            try:
                file_response = get_file(f"/reports/{report['id']}/download")
                c2.download_button(
                    "Download PDF",
                    data=file_response.content,
                    file_name=f"{report['name']}.pdf",
                    mime="application/pdf",
                    icon=":material/download:",
                    key=f"dl_{report['id']}",
                )
            except ApiError as exc:
                c2.error("Unavailable")

st.markdown("---")
st.markdown("##### CSV Export")
st.caption("Customer-level data with segment, CLV, and churn results, if computed.")
try:
    csv_response = get_file(f"/reports/{dataset['id']}/export-csv")
    st.download_button(
        "Download Customers CSV",
        data=csv_response.content,
        file_name=f"customers_{dataset['id']}.csv",
        mime="text/csv",
        icon=":material/download:",
    )
except ApiError as exc:
    st.warning(f"CSV export not available yet: {exc.message}")
