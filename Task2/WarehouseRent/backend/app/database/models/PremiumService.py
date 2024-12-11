from app.database import Base
from sqlalchemy import Column, Integer, Text, Float, ForeignKey

class PremiumService(Base):
    __tablename__ = "premium_services"
    
    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", name="fk_premium_service_warehouse"), nullable=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)