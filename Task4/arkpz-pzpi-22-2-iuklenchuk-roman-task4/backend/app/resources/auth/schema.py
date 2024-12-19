import re
from .schema import *
from fastapi import Form
from pydantic import BaseModel, validator, EmailStr


class UserSchema(BaseModel):
    username: str
    email: str | None = None
    role: str | None = None
    last_name: str | None = None
    first_name: str | None = None
    phone: str | None = None


class UserInDB(UserSchema):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None
    role: str | None = None
    last_name: str | None = None
    first_name: str | None = None
    phone: str | None = None
    
    @validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', value):
            raise ValueError('Password must contain at least one digit')

        return value

class TokenWithRefreshToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    

