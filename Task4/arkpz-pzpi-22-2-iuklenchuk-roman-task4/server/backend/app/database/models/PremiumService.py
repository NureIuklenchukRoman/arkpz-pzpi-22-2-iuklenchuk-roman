from ..base_model import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, Float, ForeignKey


#On frontend available services for varahouse will be fetched by warehouse_id
class PremiumService(Base):
    __tablename__ = "premium_services"
    
    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", name="fk_premium_service_warehouse"), nullable=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    
    warehouse = relationship("Warehouse", back_populates="premium_services")