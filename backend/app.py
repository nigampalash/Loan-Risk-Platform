import os
import sys
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any

# Ensure project imports work when executing directly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import get_db, engine
from backend.auth import AuthService
from backend.ml.infer import ensure_model_loaded, predict_one_with_shap
from backend.ml.analytics import compute_analytics
from backend.reports.report_service import list_reports, generate_pdf_for_prediction
from backend.storage.artifacts import load_model_metrics
from backend.schemas import (
    UserRegister,
    UserLogin,
    Token,
    PredictionRequest,
    PredictionResponse,
    DashboardDataResponse,
    BorrowerResponse,
    AuditLogResponse,
)
from backend.middleware import StructuredLoggingMiddleware, RateLimitingMiddleware
from models.base import Base
from models.user import User
from models.borrower import Borrower
from models.prediction import Prediction
from models.model_metric import ModelMetric
from models.audit_log import AuditLog

# Create DB tables on startup (if SQLite or if PG is running)
try:
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")
except Exception as e:
    print(f"Failed to initialize database tables: {e}")

# Pre-train/Load ML Models
try:
    ensure_model_loaded()
except Exception as e:
    print(f"Failed to load or train ML models: {e}")

# Initialize FastAPI App
app = FastAPI(
    title="Loan Risk Analytics Platform API",
    description="Production-ready FastAPI backend for credit risk assessment, explainable AI, and analytics",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares
app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(RateLimitingMiddleware, requests_limit=100, window_seconds=60)

# Setup directories
os.makedirs("reports", exist_ok=True)
os.makedirs("saved_models", exist_ok=True)

# Mount reports folder to serve generated PDFs and SHAP plots statically
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# Initialize Services
auth_service = AuthService()


# JWT dependency
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Dict[str, Any]:
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:]

    if not token:
        # Fallback to query parameter for report downloading
        token = request.query_params.get("token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid",
        )

    user = auth_service.verify_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token",
        )
    return user


# Swagger redirect
@app.get("/swagger", include_in_schema=False)
def swagger_redirect():
    return RedirectResponse(url="/docs")


@app.get("/", include_in_schema=False)
def root_redirect():
    frontend_dist = os.path.join(PROJECT_ROOT, "frontend", "dist")
    if os.path.exists(frontend_dist):
        from fastapi.responses import FileResponse
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    return RedirectResponse(url="/docs")


# ---------------- API ENDPOINTS ----------------

# Health Check
@app.get("/health", response_model=Dict[str, str])
@app.get("/api/v1/health", response_model=Dict[str, str], tags=["System"])
def health_check():
    return {"status": "healthy"}


# Register
@app.post("/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
@app.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(payload: UserRegister, db: Session = Depends(get_db)):
    try:
        auth_service.register(db, username=payload.username, password=payload.password)
        return {"status": "ok", "message": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Login
@app.post("/login", response_model=Token, tags=["Auth"])
@app.post("/api/v1/auth/login", response_model=Token, tags=["Auth"])
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    try:
        token = auth_service.login(db, username=payload.username, password=payload.password, ip_address=client_ip)
        user = db.query(User).filter(User.username == payload.username).first()
        return Token(token=token, username=user.username, role=user.role)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


# Predict Risk
@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
@app.post("/api/v1/predict", response_model=PredictionResponse, tags=["Predictions"])
def predict(
    payload: PredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        # Convert Pydantic model back to regular dict for inference pipeline
        input_data = payload.model_dump()
        # Ensure correct dictionary key formatting matching what model expects
        applicant = {
            "Gender": input_data["gender"],
            "Age": input_data["age"],
            "Married": input_data["married"],
            "Dependents": input_data["dependents"],
            "Education": input_data["education"],
            "Employment Type": input_data["employment_type"],
            "Monthly Income": input_data["monthly_income"],
            "CoApplicant Income": input_data["coapplicant_income"],
            "Loan Amount": input_data["loan_amount"],
            "Loan Term": input_data["loan_term"],
            "Credit History": input_data["credit_history"],
            "Existing Debt": input_data["existing_debt"],
            "Property Area": input_data["property_area"],
        }

        # Run inference and SHAP explainability
        result = predict_one_with_shap(applicant)

        # Save results in DB
        persisted = auth_service.persist_prediction(
            db=db,
            user_id=current_user["id"],
            applicant_json=applicant,
            approval_probability=result["approval_probability"],
            approval_status=result["approval_status"],
            model_name=result["model_name"],
            approval_threshold=result["approval_threshold"],
            risk_score=result["risk_score"],
            risk_category=result["risk_category"],
            shap_summary_path=result.get("shap_summary_path"),
            shap_importance_path=result.get("shap_importance_path"),
        )

        # Generate PDF Report
        pdf_path = generate_pdf_for_prediction(
            user_id=current_user["id"],
            prediction_id=persisted.id,
            applicant_json=applicant,
            predict_result=result,
        )

        # Update prediction with PDF report path
        # Normalize report path to make it downloadable statically (e.g. /reports/filename.pdf)
        pdf_filename = os.path.basename(pdf_path)
        persisted.pdf_report_path = f"/reports/{pdf_filename}"
        db.commit()
        db.refresh(persisted)

        # Build response
        response_data = PredictionResponse(
            id=persisted.id,
            borrower_id=persisted.borrower_id,
            approval_probability=persisted.approval_probability,
            approval_status=persisted.approval_status,
            approval_threshold=persisted.approval_threshold,
            risk_score=persisted.risk_score,
            risk_category=persisted.risk_category,
            shap_summary_path=f"/reports/{os.path.basename(result.get('shap_summary_path'))}" if result.get('shap_summary_path') else None,
            shap_importance_path=f"/reports/{os.path.basename(result.get('shap_importance_path'))}" if result.get('shap_importance_path') else None,
            pdf_report_path=persisted.pdf_report_path,
            shap_feature_importance=result.get("shap_feature_importance"),
            created_at=persisted.created_at,
        )

        return response_data
    except Exception as e:
        auth_service.log_event(db, user_id=current_user["id"], action="LOAN_PREDICTION", status="FAILURE", details=f"Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference pipeline failed: {str(e)}",
        )


# Dashboard Data
@app.get("/dashboard-data", response_model=DashboardDataResponse, tags=["Analytics"])
@app.get("/api/v1/dashboard-data", response_model=DashboardDataResponse, tags=["Analytics"])
def dashboard_data(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        stats = compute_analytics(db)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics computation failed: {str(e)}",
        )


# Model Metrics
@app.get("/model-metrics", tags=["Analytics"])
@app.get("/api/v1/model-metrics", tags=["Analytics"])
def model_metrics(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        # Load local JSON file metrics
        local_metrics = load_model_metrics()
        if local_metrics:
            return local_metrics
        # Fallback to database
        db = SessionLocal()
        metrics = db.query(ModelMetric).all()
        db.close()
        return {
            "best_model": "LightGBM",
            "metrics_by_model": {
                m.model_name: {
                    "accuracy": m.accuracy,
                    "precision": m.precision,
                    "recall": m.recall,
                    "f1": m.f1_score,
                    "roc_auc": m.roc_auc,
                }
                for m in metrics
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch model metrics: {str(e)}",
        )


# Get Borrowers List
@app.get("/api/v1/borrowers", response_model=List[BorrowerResponse], tags=["Borrowers"])
def list_borrowers(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        borrowers = db.query(Borrower).order_by(Borrower.created_at.desc()).all()
        return borrowers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


# Get Audit Logs
@app.get("/api/v1/audit-logs", response_model=List[AuditLogResponse], tags=["Admin"])
def list_audit_logs(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Enforce admin authorization
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Admin access required",
        )
    try:
        logs = (
            db.query(AuditLog, User.username)
            .outerjoin(User, AuditLog.user_id == User.id)
            .order_by(AuditLog.created_at.desc())
            .limit(100)
            .all()
        )

        result = []
        for log, username in logs:
            result.append(
                AuditLogResponse(
                    id=log.id,
                    user_id=log.user_id,
                    username=username,
                    action=log.action,
                    status=log.status,
                    ip_address=log.ip_address,
                    details=log.details,
                    created_at=log.created_at,
                )
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


# Get Reports
@app.get("/reports", tags=["Reports"])
@app.get("/api/v1/reports", tags=["Reports"])
def reports_list(current_user: Dict[str, Any] = Depends(get_current_user)):
    return list_reports()


# Serve React Frontend static files if dist folder exists
frontend_dist = os.path.join(PROJECT_ROOT, "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=5000, reload=True)
