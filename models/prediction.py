from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from .base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    borrower_id = Column(Integer, ForeignKey("borrowers.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    approval_probability = Column(Float, nullable=False)
    approval_status = Column(String(20), nullable=False)  # approved / rejected
    approval_threshold = Column(Float, nullable=False)

    risk_score = Column(Float, nullable=False)  # 0-100
    risk_category = Column(String(50), nullable=False)  # Low Risk / Medium Risk / High Risk

    shap_summary_path = Column(String(500), nullable=True)
    shap_importance_path = Column(String(500), nullable=True)
    pdf_report_path = Column(String(500), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    borrower = relationship("Borrower", back_populates="predictions")
    user = relationship("User", back_populates="predictions")
