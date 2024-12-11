from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey,  String, Float
from sqlalchemy.dialects.postgresql import JSONB
from ..base_model import Base
from sqlalchemy.orm import relationship
from sqlalchemy import select
from app.utils.verification import verify_password


"""
Later on frontend when creating warehouse existing premium services (user who created them creating now warehouse) will be shown in a dropdown
"""
class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    size_sqm = Column(Float, nullable=False)
    price_per_day = Column(Float, nullable=False)
    available_premium_services = Column(JSONB, nullable=True)  # JSON or comma-separated list
    owned_by = Column(Integer, ForeignKey("users.id", name="fk_warehouse_user"), nullable=False)

    rentals = relationship("Rental", back_populates="warehouse")
    lock = relationship("Lock", uselist=False, back_populates="warehouse")
    owner = relationship("User", back_populates="warehouses")
