import streamlit as st

from core.api_client import ApiError, post
from core.auth import require_dataset
from core.theme import badge_html

st.title("Data Validation")
st.caption("Verify schema and data quality before running analytics.")

dataset = require_dataset()

with st.spinner("Running validation checks…"):
    try:
        result = post(f"/datasets/{dataset['id']}/validate")
    except ApiError as exc:
        st.error(exc.message)
        st.stop()

passed = result["passed"]
total = result["total"]
variant = "success" if passed == total else "warning"
st.markdown(
    f"Results for **{dataset['name']}** &nbsp; {badge_html(f'{passed} of {total} checks passed', variant)}",
    unsafe_allow_html=True,
)

st.markdown("")
for check in result["checks"]:
    status = check["status"]
    variant = {"Passed": "success", "Warning": "warning", "Failed": "danger"}.get(status, "default")
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"**{check['check']}**  \n<span class='dh-muted'>{check['detail']}</span>", unsafe_allow_html=True)
        c2.markdown(badge_html(status, variant), unsafe_allow_html=True)
