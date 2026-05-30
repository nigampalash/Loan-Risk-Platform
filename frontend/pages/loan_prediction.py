import streamlit as st
import requests
import pandas as pd


# Streamlit secrets are optional; fall back to local backend.
try:
    API_BASE = st.secrets.get("API_BASE", "http://localhost:5000")
except Exception:
    API_BASE = "http://localhost:5000"




def _get_token():
    return st.session_state.get("token")


def _ensure_login_ui():
    with st.expander("Authentication", expanded=False):
        username = st.text_input("Username", key="lp_username")
        password = st.text_input("Password", type="password", key="lp_password")
        colA, colB = st.columns(2)
        if colA.button("Login"):
            r = requests.post(f"{API_BASE}/login", json={"username": username, "password": password}, timeout=15)
            if r.status_code == 200:
                st.session_state.token = r.json()["token"]
                st.success("Logged in")
            else:
                st.error(r.json().get("error", "Login failed"))


def render(st_module):
    st_module.markdown("# Loan Prediction")

    if "token" not in st_module.session_state:
        _ensure_login_ui()

    with st_module.form("prediction_form", clear_on_submit=False):
        Gender = st_module.selectbox("Gender", ["Male", "Female"])
        Age = st_module.number_input("Age", min_value=18, max_value=100, value=30)
        Married = st_module.selectbox("Married", ["Yes", "No"])
        Dependents = st_module.selectbox("Dependents", [0, 1, 2, 3, 4])
        Education = st_module.selectbox("Education", ["Graduate", "Not Graduate"])
        Employment_Type = st_module.selectbox("Employment Type", ["Salaried", "Self employed"])
        Monthly_Income = st_module.number_input("Monthly Income", min_value=0, value=5000)
        CoApplicant_Income = st_module.number_input("CoApplicant Income", min_value=0, value=0)
        Loan_Amount = st_module.number_input("Loan Amount", min_value=0, value=120000)
        Loan_Term = st_module.selectbox("Loan Term", [36, 180, 360, 480, 600])
        Credit_History = st_module.selectbox("Credit History", [1.0, 0.0])
        Existing_Debt = st_module.number_input("Existing Debt", min_value=0, value=10000)
        Property_Area = st_module.selectbox("Property Area", ["Urban", "Rural", "Semiurban"])

        submitted = st_module.form_submit_button("Predict")

    if submitted:
        token = _get_token()
        if not token:
            st_module.error("Login required. Use Authentication expander.")
            return

        payload = {
            "Gender": Gender,
            "Age": int(Age),
            "Married": Married,
            "Dependents": int(Dependents),
            "Education": Education,
            "Employment Type": Employment_Type,
            "Monthly Income": float(Monthly_Income),
            "CoApplicant Income": float(CoApplicant_Income),
            "Loan Amount": float(Loan_Amount),
            "Loan Term": int(Loan_Term),
            "Credit History": float(Credit_History),
            "Existing Debt": float(Existing_Debt),
            "Property Area": Property_Area,
        }

        r = requests.post(
            f"{API_BASE}/predict",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        if r.status_code == 200:
            data = r.json()
            st_module.success("Prediction complete")
            st_module.write(data)
            if data.get("pdf_report_path"):
                st_module.info(f"PDF report generated: {data['pdf_report_path']}")
        else:
            try:
                st_module.error(r.json().get("error", "Prediction failed"))
            except Exception:
                st_module.error("Prediction failed")

