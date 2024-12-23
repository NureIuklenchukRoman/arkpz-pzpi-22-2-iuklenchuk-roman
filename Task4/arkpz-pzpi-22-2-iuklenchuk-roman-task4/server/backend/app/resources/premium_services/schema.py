from .schema import *
from typing import Optional
from pydantic import BaseModel

class ServiceSchema(BaseModel):
    warehouse_id: int
    name: str | None = None
    description: str
    price: float

class ServiceCreateSchema(ServiceSchema):
    pass

class ServiceUpdateSchema(BaseModel):
    # available_premium_services: Optional[list] = None
    warehouse_id: int | None = None
    name: str | None = None
    description: str | None = None
    price: float | None = None

class ServiceDeleteSchema(BaseModel):
    id: int


# class ServiceQuerySchema(BaseModel):
#     name: Optional[str] = None
#     location: Optional[str] = None


class ServiceResponseSchema(ServiceSchema):
    id: int
