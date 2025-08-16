from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    preferred_language: str = "en"
    preferred_currency: str = "USD"


class UserCreate(UserBase):
    password: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_language: Optional[str] = None
    preferred_currency: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    telegram_id: Optional[str] = None
    password: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None