"""
Authentication service - JWT tokens, password hashing, user management.
"""
from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import JWTError, jwt

from models.user import User, RefreshToken
from schemas.auth import UserRegister, TokenResponse
from config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


class AuthService:
    """Service for authentication operations"""
    
    # ============== Password ==============
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    # ============== JWT Tokens ==============
    
    @staticmethod
    def create_access_token(user_id: int, email: str, role: str) -> str:
        """Create JWT access token"""
        expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "type": "access",
            "exp": expires,
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token() -> tuple[str, str]:
        """
        Create refresh token.
        Returns (token, token_hash) - store hash in DB, give token to user.
        """
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token, token_hash
    
    @staticmethod
    def hash_refresh_token(token: str) -> str:
        """Hash refresh token for storage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """Decode and validate access token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "access":
                return None
            return payload
        except JWTError:
            return None
    
    # ============== User Operations ==============
    
    async def register_user(self, db: AsyncSession, data: UserRegister) -> User:
        """Register new user"""
        # Check if email exists
        existing = await db.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Пользователь с таким email уже существует")
        
        # Create user
        user = User(
            email=data.email,
            password_hash=self.hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()
        
        return user
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_telegram_id(self, db: AsyncSession, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    # ============== Token Management ==============
    
    async def create_tokens(
        self, 
        db: AsyncSession, 
        user: User,
        device_info: str = None,
        ip_address: str = None
    ) -> TokenResponse:
        """Create access and refresh tokens for user"""
        # Access token
        access_token = self.create_access_token(user.id, user.email, user.role)
        
        # Refresh token
        refresh_token, token_hash = self.create_refresh_token()
        
        # Store refresh token in DB
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        db_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=expires_at,
        )
        db.add(db_token)
        await db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    async def refresh_tokens(
        self, 
        db: AsyncSession, 
        refresh_token: str,
        device_info: str = None,
        ip_address: str = None
    ) -> Optional[tuple[User, TokenResponse]]:
        """Refresh tokens using refresh token"""
        token_hash = self.hash_refresh_token(refresh_token)
        
        # Find token
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        )
        db_token = result.scalar_one_or_none()
        
        if not db_token:
            return None
        
        # Get user
        user = await self.get_user_by_id(db, db_token.user_id)
        if not user or not user.is_active:
            return None
        
        # Revoke old token
        db_token.revoked = True
        db_token.revoked_at = datetime.utcnow()
        
        # Create new tokens
        tokens = await self.create_tokens(db, user, device_info, ip_address)
        
        return user, tokens
    
    async def revoke_all_tokens(self, db: AsyncSession, user_id: int) -> int:
        """Revoke all refresh tokens for user (logout from all devices)"""
        result = await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
            .values(revoked=True, revoked_at=datetime.utcnow())
        )
        await db.commit()
        return result.rowcount
    
    # ============== Telegram Linking ==============
    
    async def generate_linking_code(self, db: AsyncSession, user_id: int) -> tuple[str, datetime]:
        """Generate code for linking Telegram account"""
        # Generate 6-char code
        code = secrets.token_hex(3).upper()  # e.g., "A1B2C3"
        expires = datetime.utcnow() + timedelta(minutes=15)
        
        # Update user
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(linking_code=code, linking_code_expires=expires)
        )
        await db.commit()
        
        return code, expires
    
    async def link_telegram(
        self, 
        db: AsyncSession, 
        linking_code: str, 
        telegram_id: int,
        telegram_username: str = None
    ) -> Optional[User]:
        """Link Telegram account using code"""
        # Find user by code
        result = await db.execute(
            select(User).where(
                User.linking_code == linking_code,
                User.linking_code_expires > datetime.utcnow()
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Check if telegram_id already linked to another user
        existing = await db.execute(
            select(User).where(
                User.telegram_id == telegram_id,
                User.id != user.id
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Этот Telegram аккаунт уже привязан к другому пользователю")
        
        # Link account
        user.telegram_id = telegram_id
        user.telegram_username = telegram_username
        user.telegram_linked_at = datetime.utcnow()
        user.linking_code = None
        user.linking_code_expires = None
        
        await db.commit()
        await db.refresh(user)
        
        return user
    
    async def unlink_telegram(self, db: AsyncSession, user_id: int) -> bool:
        """Unlink Telegram account"""
        result = await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                telegram_id=None,
                telegram_username=None,
                telegram_linked_at=None
            )
        )
        await db.commit()
        return result.rowcount > 0


# Singleton instance
auth_service = AuthService()
