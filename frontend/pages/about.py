import streamlit as st


def render(st_module):
    st_module.markdown("# About")
    st_module.write("""
Loan Approval Prediction & Risk Analytics Platform with Explainable AI (SHAP).

Built with:
- Flask backend
- Streamlit frontend
- MySQL + SQLAlchemy
- ML models: Logistic Regression, Decision Tree, Random Forest, XGBoost
- Explainable AI: SHAP
- PDF reporting
- Docker-ready deployment
    """)

