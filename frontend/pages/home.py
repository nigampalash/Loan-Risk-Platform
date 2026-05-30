import streamlit as st
import plotly.graph_objects as go


def render(st_module):
    st_module.markdown("# Loan Approval Prediction & Risk Analytics")
    st_module.write(
        "A fintech AI platform that predicts loan approval, computes risk scores (0-100), and provides explainable insights via SHAP."
    )

    c1, c2, c3, c4 = st_module.columns(4)
    c1.metric("Model", "XGBoost (Best)")
    c2.metric("Risk Scale", "0-100")
    c3.metric("Explainability", "SHAP")
    c4.metric("Reports", "PDF Export")

    fig = go.Figure()
    fig.add_trace(go.Indicator(mode="gauge+number", value=72, title={"text": "System Readiness"}))
    fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st_module.plotly_chart(fig, use_container_width=True)

    st_module.markdown("---")
    st_module.subheader("How it works")
    st_module.markdown(
        """
1. Train ML models with automated preprocessing.
2. Select best model by ROC-AUC.
3. Generate SHAP artifacts for feature importance.
4. Persist predictions and risk scores to MySQL.
5. Create PDF reports with plots and explanation.
        """
    )

