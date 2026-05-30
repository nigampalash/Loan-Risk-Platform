import os
import streamlit as st

st.set_page_config(
    page_title="Loan Risk Analytics Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark theme
st.markdown(
    """
<style>
    .reportview-container { background: #0e1117; }
    .sidebar .sidebar-content { background: #0b0f14; }
    section[data-testid="stSidebar"] { background: #0b0f14; }
    h1, h2, h3 { color: #e6edf3; }
    .stMarkdown, .css-1544g2w { color: #c9d1d9; }
    .stTextInput input { background-color: #111827; color: #e5e7eb; }
    .stButton>button { background-color: #1f2937; color: #e5e7eb; }
</style>
""",
    unsafe_allow_html=True,
)

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Loan Prediction", "Risk Analysis", "Analytics", "Model Performance", "Reports", "About"],
)

if page == "Home":
    from frontend.pages.home import render

    render(st)

elif page == "Loan Prediction":
    from frontend.pages.loan_prediction import render

    render(st)

elif page == "Risk Analysis":
    from frontend.pages.risk_analysis import render

    render(st)

elif page == "Analytics":
    from frontend.pages.analytics import render

    render(st)

elif page == "Model Performance":
    from frontend.pages.model_performance import render

    render(st)

elif page == "Reports":
    from frontend.pages.reports import render

    render(st)

elif page == "About":
    from frontend.pages.about import render

    render(st)

