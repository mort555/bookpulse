from datetime import datetime

from app.core.enum import Roles
from pydantic import BaseModel, EmailStr


class UserCreationSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None
    weekly_report: bool = True


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    full_name: str | None = None
    role: Roles
    weekly_report: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
