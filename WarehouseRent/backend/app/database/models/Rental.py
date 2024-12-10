from sqlalchemy import Column, Integer, ForeignKey, Date, Float, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from ..base_model import Base

class RentalStatus(PyEnum):
    RESERVED = "reserved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", name="fk_rental_user"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", name="fk_rental_warehouse"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum(RentalStatus), default=RentalStatus.RESERVED)

    user = relationship("User", back_populates="rentals")
    warehouse = relationship("Warehouse", back_populates="rentals")
    payment = relationship("Payment", back_populates="rental", uselist=False)
