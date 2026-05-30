import os
import sys
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

# Allow `python backend/app.py` execution by fixing import root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import get_engine
from backend.auth import AuthService
from backend.ml.infer import ensure_model_loaded, predict_one_with_shap
from backend.ml.analytics import compute_analytics
from backend.reports.report_service import list_reports, generate_pdf_for_prediction
from backend.storage.artifacts import load_model_metrics



def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev_secret")

    ensure_model_loaded()

    auth_service = AuthService()

    @app.post("/register")
    def register():
        payload = request.get_json(force=True, silent=True) or {}
        username = payload.get("username")
        password = payload.get("password")
        if not username or not password:
            return jsonify({"error": "username and password are required"}), 400
        try:
            auth_service.register(username=username, password=password)
            return jsonify({"status": "ok"}), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.post("/login")
    def login():
        payload = request.get_json(force=True, silent=True) or {}
        username = payload.get("username")
        password = payload.get("password")
        if not username or not password:
            return jsonify({"error": "username and password are required"}), 400
        try:
            token = auth_service.login(username=username, password=password)
            return jsonify({"token": token}), 200
        except PermissionError as e:
            return jsonify({"error": str(e)}), 401

    @app.post("/logout")
    def logout():
        # Stateless token approach: client discards token.
        return jsonify({"status": "ok"}), 200

    def _require_user():
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:]
        if not token:
            return None
        return auth_service.verify_token(token)

    @app.post("/predict")
    def predict():
        user = _require_user()
        if user is None:
            return jsonify({"error": "Unauthorized"}), 401

        payload = request.get_json(force=True, silent=True) or {}
        required_fields = [
            "Gender",
            "Age",
            "Married",
            "Dependents",
            "Education",
            "Employment Type",
            "Monthly Income",
            "CoApplicant Income",
            "Loan Amount",
            "Loan Term",
            "Credit History",
            "Existing Debt",
            "Property Area",
        ]
        missing = [f for f in required_fields if f not in payload]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        try:
            result = predict_one_with_shap(payload)
            # Optionally persist artifacts in DB
            approval_status = "approved" if result["approval_probability"] >= result["approval_threshold"] else "rejected"
            persisted = auth_service.persist_prediction(
                user_id=user["id"],
                applicant_json=payload,
                approval_probability=result["approval_probability"],
                approval_status=approval_status,
                model_name=result["model_name"],
                approval_threshold=result["approval_threshold"],
                risk_score=result["risk_score"],
                risk_category=result["risk_category"],
                shap_summary_path=result.get("shap_summary_path"),
                shap_importance_path=result.get("shap_importance_path"),
            )

            # Generate PDF report
            pdf_path = generate_pdf_for_prediction(
                user_id=user["id"],
                prediction_id=persisted["prediction_id"],
                applicant_json=payload,
                predict_result=result,
            )

            result["pdf_report_path"] = pdf_path
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.get("/analytics")
    def analytics():
        # Requires auth in a real system; for demo keep open.
        stats = compute_analytics()
        return jsonify(stats), 200

    @app.get("/reports")
    def reports():
        return jsonify(list_reports()), 200

    @app.get("/model-metrics")
    def model_metrics():
        return jsonify(load_model_metrics()), 200

    @app.get("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    # Minimal Swagger/OpenAPI via raw JSON (no runtime deps)
    @app.get("/swagger")
    def swagger_spec():
        spec = {
            "openapi": "3.0.0",
            "info": {"title": "Loan Risk Analytics API", "version": "1.0.0"},
            "paths": {
                "/register": {
                    "post": {
                        "summary": "Register user",
                        "requestBody": {"required": True},
                        "responses": {"201": {"description": "Created"}},
                    }
                },
                "/login": {"post": {"summary": "Login user", "responses": {"200": {"description": "OK"}}}},
                "/predict": {
                    "post": {
                        "summary": "Predict loan approval and compute risk",
                        "responses": {"200": {"description": "OK"}, "400": {"description": "Bad request"}},
                    }
                },
                "/analytics": {"get": {"responses": {"200": {"description": "OK"}}}},
                "/reports": {"get": {"responses": {"200": {"description": "OK"}}}},
                "/model-metrics": {"get": {"responses": {"200": {"description": "OK"}}}},
            },
        }
        return jsonify(spec), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=os.getenv("FLASK_ENV") == "development")

