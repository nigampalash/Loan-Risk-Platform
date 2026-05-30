import streamlit as st
import requests
import os

API_BASE = "http://localhost:5000"


def render(st_module):
    st_module.markdown("# Reports")

    r = requests.get(f"{API_BASE}/reports", timeout=30)
    if r.status_code != 200:
        st_module.error("Unable to load reports")
        return

    reports = r.json()

    if not reports:
        st_module.info("No reports generated yet.")
        return

    for rep in reports:
        st_module.write(rep)
        path = rep.get("pdf_path")
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                st_module.download_button(
                    label=f"Download {os.path.basename(path)}",
                    data=f,
                    file_name=os.path.basename(path),
                    mime="application/pdf",
                )

