from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .base import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, index=True)

    risk_score = Column(Float, nullable=False)  # 0-100
    risk_category = Column(String(20), nullable=False)  # Low/Medium/High

    shap_summary_path = Column(String(500), nullable=True)
    shap_importance_path = Column(String(500), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    prediction = relationship("Prediction", back_populates="risk_scores")

