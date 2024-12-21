from datetime import date
from typing import Optional
from pydantic import BaseModel

class RentWarehouseSchema(BaseModel):
    start_date: date
    end_date: date
    selected_services: Optional[list[int]]
    
class WarehouseDetails(BaseModel):
    id: int
    name: str
    location: str
    price_per_day: float
    busy_dates: list[date]
    
    
class RentalResponseSchema(BaseModel):
    id: int
    warehouse_name: str
    warehouse_location: str
    start_date: date
    end_date: date
    status: str
    total_price: float
    renter_name: str
    renter_email: str