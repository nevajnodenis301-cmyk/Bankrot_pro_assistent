"""
User model for authentication system.
Supports both web login and Telegram bot linking.
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, BigInteger, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    """
    User account for authentication.
    Can be linked to Telegram for bot access.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=lambda: str(uuid4()))
    
    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    
    # Profile
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    
    # Telegram linking
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, index=True)
    telegram_username: Mapped[str | None] = mapped_column(String(100))
    telegram_linked_at: Mapped[datetime | None] = mapped_column(DateTime)
    
    # Linking code (temporary, for connecting Telegram)
    linking_code: Mapped[str | None] = mapped_column(String(10), unique=True, index=True)
    linking_code_expires: Mapped[datetime | None] = mapped_column(DateTime)
    
    # Role & permissions
    role: Mapped[str] = mapped_column(String(20), default="user")  # admin, manager, user
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)  # email verified
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[datetime | None] = mapped_column(DateTime)
    
    # Relationships - user owns cases
    cases: Mapped[list["Case"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class RefreshToken(Base):
    """
    Refresh tokens for JWT authentication.
    Allows token rotation and revocation.
    """
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # Device/session info
    device_info: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    
    # Validity
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
