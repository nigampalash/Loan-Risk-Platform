import os
import time
import bcrypt
from dotenv import load_dotenv
from typing import Any

from backend.database import get_engine
from sqlalchemy import text


class AuthService:
    """Simple token-based auth (no external JWT dependency).

    Token format:
      base64(user_id:expiry:random)

    For a demo/final-year project, we store sessions in DB logs only.
    """

    def __init__(self):
        load_dotenv()
        self.secret = os.getenv("FLASK_SECRET_KEY", "dev_secret")

    def _hash(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def _verify(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def register(self, username: str, password: str) -> None:
        if len(username) < 3:
            raise ValueError("username must be at least 3 chars")
        if len(password) < 6:
            raise ValueError("password must be at least 6 chars")

        engine = get_engine()
        with engine.begin() as conn:
            existing = conn.execute(text("SELECT id FROM users WHERE username=:u"), {"u": username}).fetchone()
            if existing:
                raise ValueError("username already exists")

            password_hash = self._hash(password)
            conn.execute(
                text("INSERT INTO users (username, password_hash, is_active) VALUES (:u, :ph, 1)"),
                {"u": username, "ph": password_hash},
            )

    def login(self, username: str, password: str) -> str:
        engine = get_engine()
        with engine.begin() as conn:
            row = conn.execute(
                text("SELECT id, password_hash, is_active FROM users WHERE username=:u"),
                {"u": username},
            ).fetchone()

        if not row:
            raise PermissionError("invalid credentials")

        user_id, password_hash, is_active = row
        if not is_active:
            raise PermissionError("user is inactive")

        if not self._verify(password, password_hash):
            raise PermissionError("invalid credentials")

        # Token is simplistic: store in-memory-like signature with expiry.
        expiry_seconds = int(os.getenv("TOKEN_EXPIRY_SECONDS", "36000"))
        expiry = int(time.time()) + expiry_seconds
        token = f"{user_id}:{expiry}:{self.secret}"
        # base64 for URL safety
        import base64

        return base64.urlsafe_b64encode(token.encode("utf-8")).decode("utf-8")

    def verify_token(self, token: str) -> dict[str, Any]:
        import base64

        try:
            raw = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
            user_id_s, expiry_s, signature = raw.split(":", 2)
            if signature != self.secret:
                return None  # type: ignore[return-value]
            if int(time.time()) > int(expiry_s):
                return None  # type: ignore[return-value]
            user_id = int(user_id_s)
        except Exception:
            return None  # type: ignore[return-value]

        engine = get_engine()
        with engine.begin() as conn:
            row = conn.execute(
                text("SELECT id, username, is_active FROM users WHERE id=:id"),
                {"id": user_id},
            ).fetchone()

        if not row or not row[2]:
            return None  # type: ignore[return-value]

        return {"id": row[0], "username": row[1]}

    def persist_prediction(
        self,
        user_id: int,
        applicant_json: dict[str, Any],
        approval_probability: float,
        approval_status: str,
        model_name: str,
        approval_threshold: float,
        risk_score: float,
        risk_category: str,
        shap_summary_path: str | None,
        shap_importance_path: str | None,
    ) -> dict[str, Any]:
        import json

        engine = get_engine()
        loan_amount = applicant_json.get("Loan Amount")
        loan_term = applicant_json.get("Loan Term")
        credit_history = applicant_json.get("Credit History")

        with engine.begin() as conn:
            res1 = conn.execute(
                text(
                    "INSERT INTO loan_applications (user_id, applicant_json, loan_amount, loan_term, credit_history) "
                    "VALUES (:uid, :aj, :la, :lt, :ch)"
                ),
                {
                    "uid": user_id,
                    "aj": json.dumps(applicant_json),
                    "la": loan_amount,
                    "lt": loan_term,
                    "ch": credit_history,
                },
            )
            loan_app_id = res1.lastrowid

            res2 = conn.execute(
                text(
                    "INSERT INTO predictions (loan_application_id, approval_probability, approval_status, model_name, approval_threshold) "
                    "VALUES (:lid, :ap, :as, :mn, :th)"
                ),
                {
                    "lid": loan_app_id,
                    "ap": approval_probability,
                    "as": approval_status,
                    "mn": model_name,
                    "th": approval_threshold,
                },
            )
            prediction_id = res2.lastrowid

            res3 = conn.execute(
                text(
                    "INSERT INTO risk_scores (prediction_id, risk_score, risk_category, shap_summary_path, shap_importance_path) "
                    "VALUES (:pid, :rs, :rc, :ss, :si)"
                ),
                {
                    "pid": prediction_id,
                    "rs": risk_score,
                    "rc": risk_category,
                    "ss": shap_summary_path,
                    "si": shap_importance_path,
                },
            )

        return {
            "loan_application_id": loan_app_id,
            "prediction_id": prediction_id,
        }

