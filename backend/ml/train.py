import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from xgboost import XGBClassifier

from backend.ml.data import load_or_generate_dataset
from backend.risk.scoring import risk_from_probability


def _model_dir() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root, os.getenv("MODEL_DIR", "saved_models"))


def _reports_dir() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root, os.getenv("REPORTS_DIR", "reports"))


def train_pipeline():
    os.makedirs(_model_dir(), exist_ok=True)
    os.makedirs(_reports_dir(), exist_ok=True)

    X, y, feature_names = load_or_generate_dataset()

    # Identify column types based on dtype
    categorical_cols = [c for c in X.columns if X[c].dtype == "object"]
    numeric_cols = [c for c in X.columns if c not in categorical_cols]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ],
        remainder="drop",
    )

    models = {
        "LogisticRegression": LogisticRegression(max_iter=2000),
        "DecisionTree": DecisionTreeClassifier(max_depth=10, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=300, random_state=42),
        "XGBoost": XGBClassifier(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42,
        ),
    }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    metrics_by_model = {}
    best_name = None
    best_auc = -1.0
    best_pipeline = None
    best_threshold = 0.5

    for name, clf in models.items():
        pipe = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", clf)])
        pipe.fit(X_train, y_train)

        proba = pipe.predict_proba(X_test)[:, 1]
        pred = (proba >= best_threshold).astype(int)

        metrics = {
            "accuracy": float(accuracy_score(y_test, pred)),
            "precision": float(precision_score(y_test, pred, zero_division=0)),
            "recall": float(recall_score(y_test, pred, zero_division=0)),
            "f1": float(f1_score(y_test, pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, proba)),
            "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
            "approval_threshold": best_threshold,
        }

        metrics_by_model[name] = metrics

        if metrics["roc_auc"] > best_auc:
            best_auc = metrics["roc_auc"]
            best_name = name
            best_pipeline = pipe

    # Persist best model
    bundle = {
        "model_name": best_name,
        "pipeline": best_pipeline,
        "feature_names": feature_names,
        "approval_threshold": best_threshold,
    }

    best_model_path = os.path.join(_model_dir(), "best_model.pkl")
    joblib.dump(bundle, best_model_path)

    # Persist metrics
    with open(os.path.join(_model_dir(), "model_metrics.json"), "w", encoding="utf-8") as f:
        json.dump({"best_model": best_name, "metrics_by_model": metrics_by_model, "selection_best_auc": best_auc}, f, indent=2)

    # Persist feature names for UI
    with open(os.path.join(_model_dir(), "feature_names.json"), "w", encoding="utf-8") as f:
        json.dump(feature_names, f, indent=2)

    print(f"Training complete. Best model: {best_name} (ROC AUC={best_auc:.4f})")

