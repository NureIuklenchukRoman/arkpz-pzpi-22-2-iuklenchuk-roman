from datetime import date
from typing import Optional
from pydantic import BaseModel

class LockResponseSchema(BaseModel):
    id: int
    ip: str | None
    warehouse_id: int
    access_key: Optional[str]
    
class LockCreateSchema(BaseModel):
    warehouse_id: int
    ip: str

class LockUnlockSchema(BaseModel):
    access_key: Optional[str]

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