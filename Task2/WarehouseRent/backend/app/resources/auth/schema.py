from fastapi import Form
from pydantic import BaseModel
from .schema import *

class UserSchema(BaseModel):
    username: str
    email: str | None = None


class UserInDB(UserSchema):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserCreate(BaseModel):
    username: str
    password: str
    email: str | None = None


class TokenWithRefreshToken(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    

