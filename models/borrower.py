from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from .base import Base


class Borrower(Base):
    __tablename__ = "borrowers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Features
    gender = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False)
    married = Column(String(10), nullable=False)
    dependents = Column(Integer, nullable=False)
    education = Column(String(50), nullable=False)
    employment_type = Column(String(50), nullable=False)
    monthly_income = Column(Float, nullable=False)
    coapplicant_income = Column(Float, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_term = Column(Integer, nullable=False)
    credit_history = Column(Float, nullable=False)
    existing_debt = Column(Float, nullable=False)
    property_area = Column(String(50), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="borrowers")
    predictions = relationship("Prediction", back_populates="borrower", cascade="all, delete-orphan")
