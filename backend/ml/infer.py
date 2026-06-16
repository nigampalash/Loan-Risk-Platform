import os
import json
import joblib
import numpy as np
import pandas as pd
import shap
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend.risk.scoring import risk_from_probability
from backend.storage.artifacts import load_model_bundle, model_path

_MODEL_BUNDLE = None


def _model_dir() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root, os.getenv("MODEL_DIR", "saved_models"))


def _reports_dir() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root, os.getenv("REPORTS_DIR", "reports"))


def ensure_model_loaded():
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is not None:
        return
    if not os.path.exists(model_path()):
        from backend.ml.train import train_pipeline
        train_pipeline()
    _MODEL_BUNDLE = load_model_bundle()


def predict_one_with_shap(applicant: dict):
    ensure_model_loaded()
    bundle = _MODEL_BUNDLE
    pipeline = bundle["pipeline"]

    # Build single-row DataFrame for inference
    X = pd.DataFrame([applicant])

    # Predict approval probability
    proba = float(pipeline.predict_proba(X)[:, 1][0])
    risk_score, risk_category = risk_from_probability(proba)

    approval_threshold = float(bundle.get("approval_threshold", 0.5))
    approval_status = "approved" if proba >= approval_threshold else "rejected"

    reports_dir = _reports_dir()
    os.makedirs(reports_dir, exist_ok=True)

    # Load background dataset for SHAP if available
    background_path = os.path.join(
        os.path.dirname(_model_dir()),
        os.getenv("DATA_DIR", "datasets"),
        "loan_synthetic.csv"
    )
    try:
        df_bg = pd.read_csv(background_path)
        X_bg = df_bg.drop(
            columns=[c for c in df_bg.columns if c.lower() in ("loan_status", "loan status")],
            errors="ignore"
        ).head(100)
    except Exception:
        X_bg = pd.DataFrame([applicant])

    shap_artifacts = {}
    feature_importance = []

    try:
        classifier = pipeline.named_steps["preprocessor"]  # wait, preprocessor is first
        classifier = pipeline.named_steps["classifier"]
        preprocessor = pipeline.named_steps["preprocessor"]

        # Transform data to match classifier input shape
        X_bg_trans = preprocessor.transform(X_bg)
        X_trans = preprocessor.transform(X)

        # Convert to dense if sparse (e.g. from OneHotEncoder)
        if hasattr(X_trans, "toarray"):
            X_trans = X_trans.toarray()
            X_bg_trans = X_bg_trans.toarray() if hasattr(X_bg_trans, "toarray") else X_bg_trans

        # Determine feature names after preprocessing
        try:
            feature_names_out = preprocessor.get_feature_names_out().tolist()
        except Exception:
            feature_names_out = [f"f{i}" for i in range(X_trans.shape[1])]

        clf_name = classifier.__class__.__name__.lower()
        explainer = None

        # Build explainer based on classifier type
        if "xgb" in clf_name or "randomforest" in clf_name or "decisiontree" in clf_name or "lgbm" in clf_name or "lightgbm" in clf_name:
            explainer = shap.TreeExplainer(classifier)
            # TreeExplainer returns list for multiclass or 2D array for binary.
            # Handle array structure.
            shap_values = explainer.shap_values(X_trans)
            if isinstance(shap_values, list):
                # For binary classification, index 1 corresponds to class 1 (approved/positive class)
                sv = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            else:
                # If 3D (e.g. multiclass/binary with dimensions) or 2D
                if len(shap_values.shape) == 3:
                    sv = shap_values[:, :, 1]
                else:
                    sv = shap_values
        elif "logistic" in clf_name:
            explainer = shap.LinearExplainer(classifier, X_bg_trans)
            sv = explainer.shap_values(X_trans)
        else:
            # Fallback
            explainer = shap.Explainer(classifier.predict, X_bg_trans)
            sv = explainer(X_trans).values

        # Ensure sv is 2D
        if len(sv.shape) > 1:
            sv_single = sv[0]
        else:
            sv_single = sv

        # Plot summary
        summary_path = os.path.join(reports_dir, f"shap_summary_{int(np.random.randint(1e9))}.png")
        plt.figure(figsize=(8, 4))
        shap.summary_plot(sv, features=X_trans, feature_names=feature_names_out, show=False)
        plt.tight_layout()
        plt.savefig(summary_path, dpi=150, bbox_inches="tight")
        plt.close()

        # Plot importance bar
        importance_path = os.path.join(reports_dir, f"shap_importance_{int(np.random.randint(1e9))}.png")
        plt.figure(figsize=(8, 4))
        shap.summary_plot(sv, features=X_trans, feature_names=feature_names_out, plot_type="bar", show=False)
        plt.tight_layout()
        plt.savefig(importance_path, dpi=150, bbox_inches="tight")
        plt.close()

        shap_artifacts["shap_summary_path"] = summary_path
        shap_artifacts["shap_importance_path"] = importance_path

        # Get top features contributing to decision
        abs_vals = np.abs(sv_single)
        top_idx = np.argsort(-abs_vals)[:6]

        for i in top_idx:
            val = float(sv_single[i])
            feature_importance.append(
                {
                    "feature": feature_names_out[i],
                    "shap_value": val,
                    "direction": "increases approval" if val > 0 else "decreases approval",
                }
            )
    except Exception as e:
        # Fallback gracefully so predictions never fail due to SHAP compilation
        print(f"SHAP explanation failed: {e}")
        shap_artifacts["shap_summary_path"] = None
        shap_artifacts["shap_importance_path"] = None

    return {
        "approval_probability": float(proba),
        "approval_status": approval_status,
        "approval_threshold": approval_threshold,
        "model_name": bundle.get("model_name"),
        "risk_score": float(risk_score),
        "risk_category": risk_category,
        **shap_artifacts,
        "shap_feature_importance": feature_importance,
    }
