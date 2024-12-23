from ..base_model import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey,  String, Float, Boolean


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
    owned_by = Column(Integer, ForeignKey("users.id", name="fk_warehouse_user"), nullable=False)
    is_blocked = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)

    rentals = relationship("Rental", back_populates="warehouse")
    lock = relationship("Lock", uselist=False, back_populates="warehouse")
    owner = relationship("User", back_populates="warehouses")
    premium_services = relationship("PremiumService", back_populates="warehouse")