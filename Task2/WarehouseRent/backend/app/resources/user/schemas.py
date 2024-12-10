from pydantic import BaseModel
from datetime import date
class RentalResponseSchema(BaseModel):
    id: int
    warehouse_name: str
    warehouse_location: str
    start_date: date
    end_date: date
    total_price: float
    status: str
    