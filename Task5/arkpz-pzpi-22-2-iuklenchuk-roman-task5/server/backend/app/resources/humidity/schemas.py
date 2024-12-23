from datetime import date
from typing import Optional
from pydantic import BaseModel

class HumiditySchema(BaseModel):
    value: str

# class LockGetSchema(BaseModel):
#     username: Optional[str] = None
#     email: Optional[str] = None
#     phone: Optional[str] = None
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
    
    
# class UserResponseSchema(BaseModel):
#     id: Optional[int]
#     username: Optional[str]
#     email: Optional[str]
#     phone: Optional[str]
#     first_name: Optional[str]
#     last_name: Optional[str]