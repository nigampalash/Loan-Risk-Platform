import os
import pytest
from backend.ml.data import load_or_generate_dataset
from backend.ml.train import train_pipeline
from backend.ml.infer import predict_one_with_shap, ensure_model_loaded


def test_data_generation():
    # Set env vars to run synthetic generation quickly
    os.environ["DATASET_MODE"] = "synthetic"
    os.environ["DATASET_ROWS"] = "100"

    X, y, feature_names = load_or_generate_dataset()

    assert len(X) == 100
    assert len(y) == 100
    assert len(feature_names) == 13
    assert "Monthly Income" in X.columns
    assert "Credit History" in X.columns


def test_ml_pipeline_and_inference():
    os.environ["DATASET_MODE"] = "synthetic"
    os.environ["DATASET_ROWS"] = "150"  # Small number of rows for fast test execution
    os.environ["MODEL_DIR"] = "saved_models_test"
    os.environ["REPORTS_DIR"] = "reports_test"

    try:
        # Run training pipeline
        train_pipeline()

        # Check model files created
        assert os.path.exists("saved_models_test/best_model.pkl")
        assert os.path.exists("saved_models_test/model_metrics.json")

        # Test inference pipeline
        sample = {
            "Gender": "Male",
            "Age": 30,
            "Married": "Yes",
            "Dependents": 1,
            "Education": "Graduate",
            "Employment Type": "Salaried",
            "Monthly Income": 5000.0,
            "CoApplicant Income": 1500.0,
            "Loan Amount": 100000.0,
            "Loan Term": 360,
            "Credit History": 1.0,
            "Existing Debt": 2000.0,
            "Property Area": "Urban",
        }

        # Override model load config
        from backend.ml import infer
        infer.model_path = lambda: "saved_models_test/best_model.pkl"
        infer._MODEL_BUNDLE = None  # Force reload

        res = predict_one_with_shap(sample)

        assert "approval_probability" in res
        assert "approval_status" in res
        assert "risk_score" in res
        assert "risk_category" in res
        assert "shap_feature_importance" in res
        assert 0.0 <= res["approval_probability"] <= 1.0
        assert 0.0 <= res["risk_score"] <= 100.0
        assert res["approval_status"] in ("approved", "rejected")
        assert res["risk_category"] in ("Low Risk", "Medium Risk", "High Risk")

    finally:
        # Cleanup
        import shutil
        if os.path.exists("saved_models_test"):
            shutil.rmtree("saved_models_test")
        if os.path.exists("reports_test"):
            shutil.rmtree("reports_test")
