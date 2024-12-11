from fastapi import Form
from pydantic import BaseModel
from .schema import *
from typing import Optional

class ServiceSchema(BaseModel):
    warehouse_id: int
    name: str | None = None
    description: str
    price: float

class ServiceCreateSchema(ServiceSchema):
    pass

class ServiceUpdateSchema(ServiceSchema):
    id: int
    name: Optional[str] = None
    location: Optional[str] = None
    size_sqm: Optional[float] = None
    is_available: Optional[bool] = None
    price_per_day: Optional[float] = None
    available_premium_services: Optional[list] = None

class ServiceDeleteSchema(BaseModel):
    id: int


# class ServiceQuerySchema(BaseModel):
#     name: Optional[str] = None
#     location: Optional[str] = None


class ServiceResponseSchema(ServiceSchema):
    id: int
