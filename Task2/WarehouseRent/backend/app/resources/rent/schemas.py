from pydantic import BaseModel
from datetime import date

class RentWarehouseSchema(BaseModel):
    start_date: date
    end_date: date
    
class WarehouseDetails(BaseModel):
    id: int
    name: str
    location: str
    price_per_day: float
    busy_dates: list[date]