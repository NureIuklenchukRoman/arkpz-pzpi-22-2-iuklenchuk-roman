from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey,  String, Float
from ..base_model import Base
from sqlalchemy.orm import relationship
from sqlalchemy import select
from app.utils.verification import verify_password

class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    size_sqm = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    price_per_day = Column(Float, nullable=False)
    premium_services = Column(String, nullable=True)  # JSON or comma-separated list

    rentals = relationship("Rental", back_populates="warehouse")