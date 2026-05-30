import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_BASE = "http://localhost:5000"


def render(st_module):
    st_module.markdown("# Analytics")

    r = requests.get(f"{API_BASE}/analytics", timeout=30)
    if r.status_code != 200:
        st_module.error("Unable to load analytics")
        return

    data = r.json()

    kpis = data.get("kpis", {})
    c1, c2, c3, c4 = st_module.columns(4)
    c1.metric("Total Predictions", kpis.get("total_predictions", 0))
    c2.metric("Approval Rate", f"{kpis.get('approval_rate', 0):.2f}%")
    c3.metric("Avg Risk", f"{kpis.get('avg_risk', 0):.1f}")
    c4.metric("Users", kpis.get("users", 0))

    # Histogram
    hist = data.get("histogram", None)
    if hist:
        df = pd.DataFrame({"risk": hist.get("values", [])})
        fig = px.histogram(df, x="risk", nbins=30, title="Risk Score Distribution")
        st_module.plotly_chart(fig, use_container_width=True)

    # Bar chart approvals by category
    bar = data.get("bar", None)
    if bar:
        fig2 = px.bar(bar, x="risk_category", y="count", title="Predictions by Risk Category")
        st_module.plotly_chart(fig2, use_container_width=True)

