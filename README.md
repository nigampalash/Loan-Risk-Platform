# Loan Approval Prediction & Risk Analytics Platform with Explainable AI

Industry-grade final-year project: loan approval prediction, risk scoring (0-100), analytics dashboards, explainable AI (SHAP), MySQL persistence, PDF reports, and deployment-ready Docker setup.

---

## Project layout

- `frontend/` - Streamlit UI (multi-page)
- `backend/` - Flask API (auth, prediction, analytics, reports)
- `database/` - SQL schema + SQLAlchemy integration
- `models/` - SQLAlchemy ORM models
- `saved_models/` - trained ML artifacts
- `reports/` - generated SHAP/PDF artifacts
- `datasets/` - dataset used for training and analytics
- `tests/` - pytest suite
- `docs/` - architecture, workflow, diagrams, interview/viva

Top-level files:
- `app.py` - Streamlit entrypoint
- `train_model.py` - training pipeline entrypoint
- `predict.py` - inference + SHAP explanation utility
- `requirements.txt`
- `docker-compose.yml`
- `Dockerfile`

---

## Quick start (local)

### 1) Prerequisites
- Python 3.10+ recommended
- MySQL 8+

### 2) Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Configure environment
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

### 5) Create database schema
```bash
python backend/scripts/init_db.py
```

### 6) Train & persist model + SHAP artifacts
```bash
python train_model.py
```

### 7) Run backend (Flask)
```bash
python backend/app.py
```

### 8) Run dashboard (Streamlit)
```bash
streamlit run app.py
```

---

## Docker start (recommended)
```bash
docker compose up --build
```

- Backend: `http://localhost:5000`
- Streamlit: `http://localhost:8501`
- Swagger UI: `http://localhost:5000/swagger`

---

## Notes
- SHAP plots and PDF reports are generated under `reports/`.
- The first run trains a model if a saved model is not found.


