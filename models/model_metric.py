from sqlalchemy import Column, DateTime, Float, Integer, String, func
from .base import Base


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    roc_auc = Column(Float, nullable=False)
    confusion_matrix = Column(String, nullable=False)  # JSON string representation of list of lists

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
