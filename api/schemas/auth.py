"""
Pydantic schemas for authentication endpoints.
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# ============== Request Schemas ==============

class UserRegister(BaseModel):
    """Registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: str | None = Field(None, max_length=20)
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну букву')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        # Remove all non-digits
        digits = re.sub(r'\D', '', v)
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError('Неверный формат телефона')
        return v


class UserLogin(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну букву')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class TelegramLink(BaseModel):
    """Request to generate Telegram linking code"""
    pass  # No fields needed, user is identified by JWT


class TelegramLinkConfirm(BaseModel):
    """Confirm Telegram linking (called from bot)"""
    linking_code: str = Field(..., min_length=6, max_length=10)
    telegram_id: int
    telegram_username: str | None = None


# ============== Response Schemas ==============

class UserResponse(BaseModel):
    """User data in responses"""
    id: int
    uuid: str
    email: str
    full_name: str
    phone: str | None
    role: str
    is_active: bool
    is_verified: bool
    telegram_id: int | None
    telegram_username: str | None
    telegram_linked_at: datetime | None
    created_at: datetime
    last_login: datetime | None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT tokens response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthResponse(BaseModel):
    """Login/Register response with user and tokens"""
    user: UserResponse
    tokens: TokenResponse


class LinkingCodeResponse(BaseModel):
    """Telegram linking code response"""
    code: str
    expires_at: datetime
    instructions: str = "Отправьте этот код боту командой /link КОД"


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
