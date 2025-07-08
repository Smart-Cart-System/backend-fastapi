from datetime import datetime, timezone
import enum
from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey, Boolean, Text, Enum, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class PaymentStatusEnum(enum.Enum):
    pending = "pending"
    successful = "successful"
    failed = "failed"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer,ForeignKey("customer_session.session_id"), nullable=False, unique=True)
    transaction_id = Column(String(255), unique=True, nullable=True)
    payment_id = Column(String(255), nullable=False, unique=True, index=True)
    payment_url = Column(String(255), nullable=False)
    total_amount = Column(Numeric(10,2), nullable=False)
    transaction_status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.pending)
    retry_attempts = Column(Integer, default=0)  # To limit retries
    callback_data = Column(Text, nullable=True)  # Stores raw callback for debugging
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    session = relationship("CustomerSession")

    class Config:
        from_attributes = True