import os
import json
import joblib
import numpy as np

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


def _build_explainer(pipeline, X_background):
    # Use model's predicted probabilities.
    # For linear/logistic we could use LinearExplainer, but for generic we use KernelExplainer fallback.
    # However KernelExplainer is too slow. Prefer TreeExplainer when possible.
    classifier = pipeline.named_steps.get("classifier")
    pre = pipeline.named_steps.get("preprocessor")

    X_bg = pre.transform(X_background)

    try:
        if "XGB" in classifier.__class__.__name__ or hasattr(classifier, "predict_proba"):
            explainer = shap.TreeExplainer(classifier)
            return explainer, pre
    except Exception:
        pass

    # Fallback to shap.Explainer with model wrapper
    f = lambda X: classifier.predict_proba(X)[:, 1]
    explainer = shap.Explainer(f, X_bg)
    return explainer, pre


def predict_one_with_shap(applicant: dict):
    ensure_model_loaded()
    bundle = _MODEL_BUNDLE
    pipeline = bundle["pipeline"]

    # Keep feature order by building df
    import pandas as pd

    X = pd.DataFrame([applicant])

    proba = pipeline.predict_proba(X)[:, 1][0]
    risk_score, risk_category = risk_from_probability(proba)

    approval_threshold = float(bundle.get("approval_threshold", 0.5))
    approval_status = "approved" if proba >= approval_threshold else "rejected"

    # SHAP artifacts: compute explainer on small background sample.
    # For speed, generate background from synthetic split from saved dataset.
    reports_dir = _reports_dir()
    os.makedirs(reports_dir, exist_ok=True)

    background_path = os.path.join(os.path.dirname(_model_dir()), os.getenv("DATA_DIR", "datasets"), "loan_synthetic.csv")
    try:
        df_bg = pd.read_csv(background_path)
        X_bg = df_bg.drop(columns=[c for c in df_bg.columns if c.lower() == "loan_status" or c.lower() == "loan status"], errors="ignore").head(200)
    except Exception:
        X_bg = pd.DataFrame([applicant])

    shap_artifacts = {}
    try:
        # Preprocess for shap
        classifier = pipeline.named_steps["classifier"]
        preprocessor = pipeline.named_steps["preprocessor"]

        X_bg_trans = preprocessor.transform(X_bg)
        X_trans = preprocessor.transform(X)

        # TreeExplainer for tree-based estimators
        if classifier.__class__.__name__.lower().find("xgb") >= 0 or classifier.__class__.__name__.lower().find("randomforest") >= 0 or classifier.__class__.__name__.lower().find("decisiontree") >= 0:
            explainer = shap.TreeExplainer(classifier)
            shap_values = explainer.shap_values(X_trans)

            # Summary plot
            summary_path = os.path.join(reports_dir, f"shap_summary_{int(np.random.randint(1e9))}.png")
            shap.summary_plot(shap_values, features=X_trans, show=False)
            plt.tight_layout()
            plt.savefig(summary_path, dpi=200, bbox_inches="tight")
            plt.close()

            # Bar/importance plot
            importance_path = os.path.join(reports_dir, f"shap_importance_{int(np.random.randint(1e9))}.png")
            shap.summary_plot(shap_values, features=X_trans, plot_type="bar", show=False)
            plt.tight_layout()
            plt.savefig(importance_path, dpi=200, bbox_inches="tight")
            plt.close()

            shap_artifacts["shap_summary_path"] = summary_path
            shap_artifacts["shap_importance_path"] = importance_path

            # Individual explanation: top features by absolute shap
            sv = shap_values
            if isinstance(sv, list):
                sv = sv[0]
            abs_vals = np.abs(sv[0])
            top_idx = np.argsort(-abs_vals)[:6]
            feature_importance = []

            try:
                feature_names_out = preprocessor.get_feature_names_out().tolist()
            except Exception:
                feature_names_out = [f"f{i}" for i in range(len(abs_vals))]

            for i in top_idx:
                feature_importance.append(
                    {
                        "feature": feature_names_out[i],
                        "shap_value": float(sv[0][i]),
                        "direction": "increases approval" if sv[0][i] > 0 else "decreases approval",
                    }
                )

        else:
            shap_artifacts["shap_summary_path"] = None
            shap_artifacts["shap_importance_path"] = None
            feature_importance = []

    except Exception:
        shap_artifacts["shap_summary_path"] = None
        shap_artifacts["shap_importance_path"] = None
        feature_importance = []

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

