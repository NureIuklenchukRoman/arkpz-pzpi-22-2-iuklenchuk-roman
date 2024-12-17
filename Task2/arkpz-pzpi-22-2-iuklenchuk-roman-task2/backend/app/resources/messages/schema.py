from fastapi import Form
from pydantic import BaseModel
from .schema import *
from typing import Optional
from datetime import datetime

class MessageSchema(BaseModel):
    user_id: int
    text: str
    created_at: datetime

# class ServiceCreateSchema(ServiceSchema):
#     pass

# class ServiceUpdateSchema(ServiceSchema):
#     id: int
#     name: Optional[str] = None
#     location: Optional[str] = None
#     size_sqm: Optional[float] = None
#     price_per_day: Optional[float] = None
#     # available_premium_services: Optional[list] = None

# class ServiceDeleteSchema(BaseModel):
#     id: int


# class ServiceQuerySchema(BaseModel):
#     name: Optional[str] = None
#     location: Optional[str] = None


class MessageResponseSchema(MessageSchema):
    id: int
