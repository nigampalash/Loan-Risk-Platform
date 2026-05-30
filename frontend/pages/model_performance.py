import streamlit as st
import requests
import plotly.graph_objects as go

API_BASE = "http://localhost:5000"


def render(st_module):
    st_module.markdown("# Model Performance")

    r = requests.get(f"{API_BASE}/model-metrics", timeout=30)
    if r.status_code != 200:
        st_module.error("Unable to load model metrics")
        return

    m = r.json()

    c1, c2, c3, c4 = st_module.columns(4)
    c1.metric("Accuracy", f"{m.get('accuracy', 0):.3f}")
    c2.metric("Precision", f"{m.get('precision', 0):.3f}")
    c3.metric("Recall", f"{m.get('recall', 0):.3f}")
    c4.metric("ROC AUC", f"{m.get('roc_auc', 0):.3f}")

    threshold = m.get("approval_threshold", 0.5)
    fig = go.Figure()
    fig.add_trace(go.Indicator(mode="gauge+number", value=float(m.get("roc_auc", 0)), title={"text": "ROC AUC"}))
    fig.update_layout(height=240)
    st_module.plotly_chart(fig, use_container_width=True)

    st_module.subheader("Confusion Matrix")
    cm = m.get("confusion_matrix", None)
    if cm:
        st_module.json(cm)

