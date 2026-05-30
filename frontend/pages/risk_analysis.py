import streamlit as st
import requests
import plotly.express as px

API_BASE = "http://localhost:5000"


def render(st_module):
    st_module.markdown("# Risk Analysis")

    r = requests.get(f"{API_BASE}/analytics", timeout=30)
    if r.status_code != 200:
        st_module.error("Unable to load analytics")
        return

    data = r.json()
    categories = data.get("risk_categories", {})

    if categories:
        labels = list(categories.keys())
        values = list(categories.values())
        fig = px.pie(values=values, names=labels, title="Risk Category Distribution")
        st_module.plotly_chart(fig, use_container_width=True)

    st_module.markdown("---")
    st_module.subheader("Heatmap & Trends")
    heat = data.get("heatmap", None)
    if heat and isinstance(heat, dict):
        fig2 = px.imshow(
            z=heat.get("z"),
            x=heat.get("x"),
            y=heat.get("y"),
            labels=dict(x="Loan Amount", y="Credit History", color="Count"),
        )
        st_module.plotly_chart(fig2, use_container_width=True)

    trends = data.get("trends", None)
    if trends and isinstance(trends, dict):
        fig3 = px.line(trends, x="x", y="y")
        st_module.plotly_chart(fig3, use_container_width=True)

