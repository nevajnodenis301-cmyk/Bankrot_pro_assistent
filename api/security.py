"""
Security utilities - JWT verification, API token, dependencies.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from config import settings
from services.auth_service import auth_service
from models.user import User


# Bearer token extractor
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Raises 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = auth_service.decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истёкший токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload.get("sub"))
    user = await auth_service.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт деактивирован"
        )
    
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    Does not raise exception if not authenticated.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = auth_service.decode_access_token(token)
    
    if not payload:
        return None
    
    user_id = int(payload.get("sub"))
    user = await auth_service.get_user_by_id(db, user_id)
    
    if not user or not user.is_active:
        return None
    
    return user


def require_role(*roles: str):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @router.get("/admin")
        async def admin_only(user: User = Depends(require_role("admin"))):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется роль: {', '.join(roles)}"
            )
        return current_user
    
    return role_checker


# ============== API Token Authentication (for bot) ==============

async def verify_api_token(request: Request) -> bool:
    """
    Verify API token from header (for bot-to-API communication).
    """
    auth_header = request.headers.get("Authorization", "")
    
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        # Check if it's the API token (not JWT)
        if token == settings.API_TOKEN:
            return True
    
    # Also check X-API-Token header
    api_token = request.headers.get("X-API-Token", "")
    if api_token == settings.API_TOKEN:
        return True
    
    return False


async def require_api_token(request: Request) -> None:
    """
    Dependency that requires valid API token.
    Used for bot endpoints.
    """
    if not await verify_api_token(request):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token"
        )


# ============== Combined Auth (JWT or API Token) ==============

async def get_user_or_api_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Returns User if JWT auth, None if API token auth.
    Raises 401 if neither.
    """
    # Try API token first (for bot)
    if await verify_api_token(request):
        return None  # Authenticated via API token, no user context
    
    # Try JWT
    if credentials:
        token = credentials.credentials
        payload = auth_service.decode_access_token(token)
        
        if payload:
            user_id = int(payload.get("sub"))
            user = await auth_service.get_user_by_id(db, user_id)
            if user and user.is_active:
                return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Требуется авторизация",
        headers={"WWW-Authenticate": "Bearer"},
    )
