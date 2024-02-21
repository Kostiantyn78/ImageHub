from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from src.entity.models import Role


class UserModel(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=10)


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    avatar: str
    created_at: datetime
    role: Role

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    username: str
    email: EmailStr
    avatar: str
    count_photo: Optional[int]
    created_at: datetime


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RequestEmail(BaseModel):
    email: EmailStr
