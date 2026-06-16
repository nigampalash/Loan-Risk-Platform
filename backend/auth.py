import os
import time
import bcrypt
import jwt
from typing import Any, Optional
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from models.user import User
from models.borrower import Borrower
from models.prediction import Prediction
from models.audit_log import AuditLog

load_dotenv()


class AuthService:
    """Production-grade JWT authentication and user session persistence service."""

    def __init__(self):
        self.secret = os.getenv("JWT_SECRET", os.getenv("FLASK_SECRET_KEY", "dev_secret"))
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.token_expiry = int(os.getenv("TOKEN_EXPIRY_SECONDS", "36000"))

    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except Exception:
            return False

    def register(self, db: Session, username: str, password: str) -> User:
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")

        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError("Username already exists")

        hashed_pw = self.hash_password(password)
        # Determine role (make first registered user admin for system access)
        role = "admin" if db.query(User).count() == 0 else "user"

        new_user = User(
            username=username,
            password_hash=hashed_pw,
            is_active=True,
            role=role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Log audit trail
        self.log_event(db, user_id=new_user.id, action="USER_REGISTRATION", status="SUCCESS", details=f"User {username} registered successfully.")

        return new_user

    def login(self, db: Session, username: str, password: str, ip_address: Optional[str] = None) -> str:
        user = db.query(User).filter(User.username == username).first()

        if not user:
            self.log_event(db, user_id=None, action="USER_LOGIN", status="FAILURE", ip_address=ip_address, details=f"Login attempt failed for non-existent username: {username}")
            raise PermissionError("Invalid username or password")

        if not user.is_active:
            self.log_event(db, user_id=user.id, action="USER_LOGIN", status="FAILURE", ip_address=ip_address, details=f"Inactive user {username} attempted login")
            raise PermissionError("User account is disabled")

        if not self.verify_password(password, user.password_hash):
            self.log_event(db, user_id=user.id, action="USER_LOGIN", status="FAILURE", ip_address=ip_address, details=f"Login attempt failed (incorrect password) for username: {username}")
            raise PermissionError("Invalid username or password")

        # Create JWT payload
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "exp": int(time.time()) + self.token_expiry,
            "iat": int(time.time())
        }

        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        self.log_event(db, user_id=user.id, action="USER_LOGIN", status="SUCCESS", ip_address=ip_address, details=f"User {username} logged in successfully")
        return token

    def verify_token(self, db: Session, token: str) -> Optional[dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            user_id = int(payload.get("sub", 0))
            if not user_id:
                return None

            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return None

            return {
                "id": user.id,
                "username": user.username,
                "role": user.role
            }
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

    def persist_prediction(
        self,
        db: Session,
        user_id: int,
        applicant_json: dict[str, Any],
        approval_probability: float,
        approval_status: str,
        model_name: str,
        approval_threshold: float,
        risk_score: float,
        risk_category: str,
        shap_summary_path: Optional[str] = None,
        shap_importance_path: Optional[str] = None,
        pdf_report_path: Optional[str] = None,
    ) -> Prediction:
        # Create and persist Borrower profile
        borrower = Borrower(
            user_id=user_id,
            gender=applicant_json.get("Gender", "Unknown"),
            age=int(applicant_json.get("Age", 0)),
            married=applicant_json.get("Married", "No"),
            dependents=int(applicant_json.get("Dependents", 0)),
            education=applicant_json.get("Education", "Graduate"),
            employment_type=applicant_json.get("Employment Type", "Salaried"),
            monthly_income=float(applicant_json.get("Monthly Income", 0.0)),
            coapplicant_income=float(applicant_json.get("CoApplicant Income", 0.0)),
            loan_amount=float(applicant_json.get("Loan Amount", 0.0)),
            loan_term=int(applicant_json.get("Loan Term", 360)),
            credit_history=float(applicant_json.get("Credit History", 1.0)),
            existing_debt=float(applicant_json.get("Existing Debt", 0.0)),
            property_area=applicant_json.get("Property Area", "Urban")
        )

        db.add(borrower)
        db.commit()
        db.refresh(borrower)

        # Create and persist Prediction linked to the Borrower
        prediction = Prediction(
            borrower_id=borrower.id,
            user_id=user_id,
            approval_probability=approval_probability,
            approval_status=approval_status,
            approval_threshold=approval_threshold,
            risk_score=risk_score,
            risk_category=risk_category,
            shap_summary_path=shap_summary_path,
            shap_importance_path=shap_importance_path,
            pdf_report_path=pdf_report_path
        )

        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        # Log event
        self.log_event(
            db,
            user_id=user_id,
            action="LOAN_PREDICTION",
            status="SUCCESS",
            details=f"Prediction generated for Borrower ID {borrower.id}: {approval_status.upper()} (Risk Score: {risk_score:.1f}, Category: {risk_category})"
        )

        return prediction

    def log_event(
        self,
        db: Session,
        user_id: Optional[int],
        action: str,
        status: str,
        ip_address: Optional[str] = None,
        details: Optional[str] = None
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            status=status,
            ip_address=ip_address,
            details=details
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
