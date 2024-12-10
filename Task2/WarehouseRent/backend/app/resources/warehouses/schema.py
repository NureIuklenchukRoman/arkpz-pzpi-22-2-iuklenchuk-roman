from fastapi import Form
from pydantic import BaseModel
from .schema import *
from typing import Optional

class WarehouseSchema(BaseModel):
    name: str
    location: str | None = None
    size_sqm: float
    is_available: bool = True
    price_per_day: float
    available_premium_services: list | None = None

class WarehouseCreateSchema(WarehouseSchema):
    pass

class WarehouseUpdateSchema(WarehouseSchema):
    id: int
    name: Optional[str] = None
    location: Optional[str] = None
    size_sqm: Optional[float] = None
    is_available: Optional[bool] = None
    price_per_day: Optional[float] = None
    available_premium_services: Optional[list] = None

class WarehouseDeleteSchema(BaseModel):
    id: int


class WarehouseQuerySchema(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class WarehouseResponseSchema(BaseModel):
    id: int
    name: str
    location: str | None = None
    size_sqm: float
    is_available: bool = True
    price_per_day: float
    available_premium_services: list | None = None