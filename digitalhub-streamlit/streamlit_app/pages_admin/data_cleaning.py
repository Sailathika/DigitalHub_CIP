import streamlit as st

from core.api_client import ApiError, post
from core.auth import require_dataset
from core.theme import badge_html
from core.utils import format_number

st.title("Data Cleaning")
st.caption("Review and resolve data quality issues before analyzing your dataset.")

dataset = require_dataset()

with st.spinner("Running cleaning pipeline…"):
    try:
        result = post(f"/datasets/{dataset['id']}/clean")
    except ApiError as exc:
        st.error(exc.message)
        st.stop()

st.markdown(f"Flagged issues in **{dataset['name']}**")
st.caption(f"{format_number(result['rows_before'])} rows in → {format_number(result['rows_after'])} rows out")

st.markdown("")
if not result["issues"]:
    st.success("No data quality issues found.")
else:
    severity_variant = {"high": "danger", "medium": "warning", "low": "secondary"}
    for issue in result["issues"]:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(
                f"**{issue['issue']}**  \n"
                f"<span class='dh-muted'>{format_number(issue['affected_rows'])} rows affected · {issue['suggestion']}</span>",
                unsafe_allow_html=True,
            )
            c2.markdown(
                badge_html(issue["severity"].title(), severity_variant.get(issue["severity"], "default")),
                unsafe_allow_html=True,
            )
