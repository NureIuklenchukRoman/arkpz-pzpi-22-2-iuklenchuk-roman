from datetime import datetime
from ..base_model import Base
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, Enum, DateTime

class PaymentStatus(PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, ForeignKey("rentals.id", name="fk_payment_rental"), nullable=False)
    # amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    # transaction_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    rental = relationship("Rental", back_populates="payment")
