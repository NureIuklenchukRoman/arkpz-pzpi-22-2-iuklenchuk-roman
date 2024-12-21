from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, Text

from ..base_model import Base

class Lock(Base):
    __tablename__ = "locks"

    id = Column(Integer, primary_key=True, index=True)
    #maybe add lock name
    ip = Column(Text, unique=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", name="fk_lock_warehouse"), nullable=False)
    access_key = Column(Text)
    # maybe add is_locked boolean field later
    
    warehouse = relationship("Warehouse", back_populates="lock")
