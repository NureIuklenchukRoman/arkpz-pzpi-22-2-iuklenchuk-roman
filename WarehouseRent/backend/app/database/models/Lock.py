from sqlalchemy import Column, Integer, Float, ForeignKey, String, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime
from ..base_model import Base


class Lock(Base):
    __tablename__ = "locks"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", name="fk_lock_warehouse"), nullable=False)
    access_key = Column(Text)
    
    warehouse = relationship("Warehouse", back_populates="lock")
