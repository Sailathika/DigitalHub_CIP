import streamlit as st

from core.api_client import ApiError, get, get_file

st.title("Reports")
st.caption("Generate and export reports for your store.")

try:
    data = get("/vendor/reports")
except ApiError as exc:
    st.error(exc.message)
    st.stop()

mime_by_format = {"pdf": "application/pdf", "csv": "text/csv"}

for report in data["reports"]:
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"**{report['name']}**  \n<span class='dh-muted'>{report['description']}</span>", unsafe_allow_html=True)
        c1.caption(f"Format: {report['format'].upper()}")

        try:
            file_response = get_file(f"/vendor/reports/{report['id']}/download")
            c2.download_button(
                "Export",
                data=file_response.content,
                file_name=f"{report['id']}.{report['format']}",
                mime=mime_by_format.get(report["format"], "application/octet-stream"),
                icon=":material/download:",
                key=f"dl_{report['id']}",
            )
        except ApiError as exc:
            c2.error("Unavailable")
