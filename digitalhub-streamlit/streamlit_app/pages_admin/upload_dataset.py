import streamlit as st

from core.api_client import ApiError, get, post_form, post
from core.utils import format_date, format_number

st.title("Upload Dataset")
st.caption("Upload your marketplace data to unlock customer, sales, and reporting insights.")

dataset = st.session_state.get("active_dataset")

if dataset:
    st.success(
        f"**{dataset['name']}** — {format_number(dataset.get('rows'))} rows — status: `{dataset.get('status')}`",
        icon=":material/check_circle:",
    )
    cols = st.columns([1, 1, 4])
    if cols[0].button("Process another dataset"):
        st.session_state.active_dataset = None
        st.rerun()

    st.markdown("##### Continue with")
    next_steps = st.columns(4)
    next_steps[0].page_link("pages_admin/data_validation.py", label="Data Validation", icon=":material/fact_check:")
    next_steps[1].page_link("pages_admin/data_cleaning.py", label="Data Cleaning", icon=":material/cleaning_services:")
    next_steps[2].page_link("pages_admin/customer_analytics.py", label="Customer Analytics", icon=":material/people:")
    next_steps[3].page_link("pages_admin/sales_analytics.py", label="Sales Analytics", icon=":material/bar_chart:")

else:
    uploaded_file = st.file_uploader("Drag and drop your dataset here", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        with st.spinner("Uploading and processing your dataset — running ETL, this only takes a moment…"):
            try:
                content_type = (
                    "text/csv"
                    if uploaded_file.name.endswith(".csv")
                    else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), content_type)}
                result = post_form("/datasets/upload", files=files)
                dataset_id = result["id"]

                post(f"/datasets/{dataset_id}/etl")

                st.session_state.active_dataset = {
                    "id": dataset_id,
                    "name": result["original_filename"],
                    "rows": result.get("row_count"),
                    "status": "transformed",
                }
                st.rerun()
            except ApiError as exc:
                st.error(exc.message)

st.markdown("---")
st.markdown("##### Upload History")
try:
    history = get("/datasets/")
    datasets = history.get("datasets", [])
    if datasets:
        for d in datasets:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 2])
                c1.markdown(f"**{d['original_filename']}**")
                c2.markdown(f"{format_number(d.get('row_count'))} rows")
                c3.markdown(f"`{d['status']}` · {format_date(d['uploaded_at'])}")
    else:
        st.caption("No datasets uploaded yet.")
except ApiError as exc:
    st.error(exc.message)
