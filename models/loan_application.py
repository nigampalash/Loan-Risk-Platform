import json
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from .base import Base


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Raw input features stored as JSON
    applicant_json = Column(String(10000), nullable=False)

    # Convenience fields
    loan_amount = Column(Float, nullable=True)
    loan_term = Column(Integer, nullable=True)
    credit_history = Column(Float, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    predictions = relationship("Prediction", back_populates="loan_application", cascade="all, delete-orphan")

