import pytest
from fastapi.testclient import TestClient
from models.user import User


def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}


def test_auth_registration_and_login(client):
    # Register user
    reg_payload = {"username": "testanalyst", "password": "password123"}
    res = client.post("/register", json=reg_payload)
    assert res.status_code == 201
    assert res.json()["status"] == "ok"

    # Register duplicate
    res = client.post("/register", json=reg_payload)
    assert res.status_code == 400
    assert "exists" in res.json()["detail"].lower()

    # Login user
    login_payload = {"username": "testanalyst", "password": "password123"}
    res = client.post("/login", json=login_payload)
    assert res.status_code == 200
    token_data = res.json()
    assert "token" in token_data
    assert token_data["username"] == "testanalyst"
    assert token_data["role"] in ("admin", "user")

    # Login invalid
    res = client.post("/login", json={"username": "testanalyst", "password": "wrongpassword"})
    assert res.status_code == 401


def test_authenticated_prediction_and_dashboard(client):
    # Setup test model if not loaded
    import os
    os.environ["DATASET_MODE"] = "synthetic"
    os.environ["DATASET_ROWS"] = "100"
    from backend.ml.infer import ensure_model_loaded
    ensure_model_loaded()

    # Register & Login first user (becomes admin)
    client.post("/register", json={"username": "admin_user", "password": "password123"})
    res = client.post("/login", json={"username": "admin_user", "password": "password123"})
    token = res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Prediction Payload
    predict_payload = {
        "gender": "Female",
        "age": 29,
        "married": "No",
        "dependents": 0,
        "education": "Graduate",
        "employment_type": "Salaried",
        "monthly_income": 6000.0,
        "coapplicant_income": 0.0,
        "loan_amount": 100000.0,
        "loan_term": 180,
        "credit_history": 1.0,
        "existing_debt": 5000.0,
        "property_area": "Semiurban"
    }

    # Test unauthorized prediction
    res = client.post("/predict", json=predict_payload)
    assert res.status_code == 401

    # Test authorized prediction
    res = client.post("/predict", json=predict_payload, headers=headers)
    assert res.status_code == 200
    pred_res = res.json()
    assert "approval_probability" in pred_res
    assert "risk_score" in pred_res
    assert pred_res["approval_status"] in ("approved", "rejected")
    assert pred_res["pdf_report_path"] is not None

    # Test Dashboard Data endpoint
    res = client.get("/dashboard-data", headers=headers)
    assert res.status_code == 200
    dash_res = res.json()
    assert "kpis" in dash_res
    assert "risk_categories" in dash_res
    assert dash_res["kpis"]["total_predictions"] >= 1

    # Test Model Metrics endpoint
    res = client.get("/model-metrics", headers=headers)
    assert res.status_code == 200
    assert "best_model" in res.json()

    # Test Borrower List endpoint
    res = client.get("/api/v1/borrowers", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1
    assert res.json()[0]["age"] == 29

    # Test Audit Logs (requires Admin role)
    res = client.get("/api/v1/audit-logs", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) >= 1
