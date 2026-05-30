import json
import os
import joblib


def _default_dir(name: str) -> str:
    base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    # backend/storage -> backend -> project root
    return os.path.join(base, name)


MODEL_DIR = os.getenv("MODEL_DIR", "saved_models")
REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")


def model_path() -> str:
    return os.path.join(_default_dir(MODEL_DIR), "best_model.pkl")


def load_model_metrics() -> dict:
    metrics_path = os.path.join(_default_dir(MODEL_DIR), "model_metrics.json")
    if not os.path.exists(metrics_path):
        return {}
    with open(metrics_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_model_bundle():
    path = model_path()
    bundle = joblib.load(path)
    return bundle

