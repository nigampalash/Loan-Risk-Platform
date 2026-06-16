from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from .base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    details = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="audit_logs")
