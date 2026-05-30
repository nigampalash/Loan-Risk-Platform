from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    loan_application_id = Column(Integer, ForeignKey("loan_applications.id"), nullable=False, index=True)

    approval_probability = Column(Float, nullable=False)
    approval_status = Column(String(10), nullable=False)  # approved / rejected

    model_name = Column(String(100), nullable=False)
    approval_threshold = Column(Float, nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    loan_application = relationship("LoanApplication", back_populates="predictions")
    risk_scores = relationship("RiskScore", back_populates="prediction", cascade="all, delete-orphan")

