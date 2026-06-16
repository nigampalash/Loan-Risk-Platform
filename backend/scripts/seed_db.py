import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import SessionLocal, engine
from backend.auth import AuthService
from models.base import Base
from models.user import User
from models.borrower import Borrower
from models.prediction import Prediction
from models.model_metric import ModelMetric
from models.audit_log import AuditLog

load_dotenv()


def seed_database():
    print("Starting database seeding...")
    db = SessionLocal()
    auth = AuthService()

    # Recreate tables
    print("Recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    try:
        # 1. Create Users
        print("Seeding Users...")
        # password is 'password123'
        hashed_pw = auth.hash_password("password123")
        admin = User(username="admin", password_hash=hashed_pw, is_active=True, role="admin")
        analyst = User(username="analyst", password_hash=hashed_pw, is_active=True, role="user")
        officer = User(username="officer", password_hash=hashed_pw, is_active=True, role="user")
        db.add_all([admin, analyst, officer])
        db.commit()

        # 2. Create Borrowers
        print("Seeding Borrowers...")
        b1 = Borrower(
            user_id=admin.id, gender="Male", age=35, married="Yes", dependents=2,
            education="Graduate", employment_type="Salaried", monthly_income=8000.0,
            coapplicant_income=2000.0, loan_amount=150000.0, loan_term=360,
            credit_history=1.0, existing_debt=5000.0, property_area="Urban"
        )
        b2 = Borrower(
            user_id=admin.id, gender="Female", age=28, married="No", dependents=0,
            education="Graduate", employment_type="Salaried", monthly_income=6500.0,
            coapplicant_income=0.0, loan_amount=90000.0, loan_term=180,
            credit_history=1.0, existing_debt=15000.0, property_area="Semiurban"
        )
        b3 = Borrower(
            user_id=analyst.id, gender="Male", age=42, married="Yes", dependents=3,
            education="Not Graduate", employment_type="Self employed", monthly_income=4500.0,
            coapplicant_income=1200.0, loan_amount=120000.0, loan_term=360,
            credit_history=0.0, existing_debt=25000.0, property_area="Rural"
        )
        b4 = Borrower(
            user_id=analyst.id, gender="Female", age=50, married="Yes", dependents=1,
            education="Graduate", employment_type="Salaried", monthly_income=12000.0,
            coapplicant_income=4000.0, loan_amount=350000.0, loan_term=240,
            credit_history=1.0, existing_debt=8000.0, property_area="Urban"
        )
        b5 = Borrower(
            user_id=officer.id, gender="Male", age=23, married="No", dependents=0,
            education="Graduate", employment_type="Self employed", monthly_income=3200.0,
            coapplicant_income=0.0, loan_amount=60000.0, loan_term=120,
            credit_history=1.0, existing_debt=2000.0, property_area="Rural"
        )
        db.add_all([b1, b2, b3, b4, b5])
        db.commit()

        # 3. Create Predictions
        print("Seeding Predictions...")
        p1 = Prediction(
            borrower_id=b1.id, user_id=admin.id, approval_probability=0.885,
            approval_status="approved", approval_threshold=0.5, risk_score=11.5,
            risk_category="Low Risk"
        )
        p2 = Prediction(
            borrower_id=b2.id, user_id=admin.id, approval_probability=0.742,
            approval_status="approved", approval_threshold=0.5, risk_score=25.8,
            risk_category="Low Risk"
        )
        p3 = Prediction(
            borrower_id=b3.id, user_id=analyst.id, approval_probability=0.125,
            approval_status="rejected", approval_threshold=0.5, risk_score=87.5,
            risk_category="High Risk"
        )
        p4 = Prediction(
            borrower_id=b4.id, user_id=analyst.id, approval_probability=0.941,
            approval_status="approved", approval_threshold=0.5, risk_score=5.9,
            risk_category="Low Risk"
        )
        p5 = Prediction(
            borrower_id=b5.id, user_id=officer.id, approval_probability=0.620,
            approval_status="approved", approval_threshold=0.5, risk_score=38.0,
            risk_category="Medium Risk"
        )
        db.add_all([p1, p2, p3, p4, p5])
        db.commit()

        # 4. Create Model Metrics
        print("Seeding Model Metrics...")
        m1 = ModelMetric(
            model_name="LightGBM", accuracy=0.892, precision=0.910, recall=0.875,
            f1_score=0.892, roc_auc=0.948, confusion_matrix=json.dumps([[420, 41], [58, 481]])
        )
        m2 = ModelMetric(
            model_name="XGBoost", accuracy=0.885, precision=0.902, recall=0.868,
            f1_score=0.885, roc_auc=0.941, confusion_matrix=json.dumps([[415, 46], [61, 478]])
        )
        m3 = ModelMetric(
            model_name="RandomForest", accuracy=0.871, precision=0.889, recall=0.852,
            f1_score=0.870, roc_auc=0.932, confusion_matrix=json.dumps([[408, 53], [69, 470]])
        )
        m4 = ModelMetric(
            model_name="LogisticRegression", accuracy=0.835, precision=0.842, recall=0.828,
            f1_score=0.835, roc_auc=0.895, confusion_matrix=json.dumps([[389, 72], [93, 446]])
        )
        db.add_all([m1, m2, m3, m4])
        db.commit()

        # 5. Create Audit Logs
        print("Seeding Audit Logs...")
        l1 = AuditLog(user_id=admin.id, action="USER_LOGIN", status="SUCCESS", ip_address="127.0.0.1", details="Admin user logged in successfully")
        l2 = AuditLog(user_id=admin.id, action="MODEL_TRAINING", status="SUCCESS", ip_address="127.0.0.1", details="Retrained all credit risk models, LightGBM selected as best (ROC-AUC=0.948)")
        l3 = AuditLog(user_id=analyst.id, action="USER_LOGIN", status="SUCCESS", ip_address="127.0.0.1", details="Analyst user logged in successfully")
        l4 = AuditLog(user_id=analyst.id, action="LOAN_PREDICTION", status="SUCCESS", ip_address="127.0.0.1", details="Performed prediction for Borrower: rejected (prob=0.125, risk=87.5)")
        l5 = AuditLog(user_id=officer.id, action="USER_LOGIN", status="SUCCESS", ip_address="127.0.0.1", details="Officer user logged in successfully")
        db.add_all([l1, l2, l3, l4, l5])
        db.commit()

        print("Database seeding completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
