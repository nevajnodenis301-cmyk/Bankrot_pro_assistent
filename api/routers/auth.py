"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.auth_service import auth_service
from schemas.auth import (
    UserRegister,
    UserLogin,
    PasswordChange,
    TokenRefresh,
    TelegramLinkConfirm,
    UserResponse,
    AuthResponse,
    TokenResponse,
    LinkingCodeResponse,
    MessageResponse,
)
from security import get_current_user, get_current_user_optional
from models.user import User


router = APIRouter(prefix="/auth", tags=["authentication"])


def get_client_info(request: Request) -> tuple[str, str]:
    """Extract device info and IP from request"""
    user_agent = request.headers.get("user-agent", "unknown")
    # Get real IP (considering proxies)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    return user_agent, ip


# ============== Registration & Login ==============

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user account.
    
    Returns user data and JWT tokens.
    """
    try:
        user = await auth_service.register_user(db, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    device_info, ip_address = get_client_info(request)
    tokens = await auth_service.create_tokens(db, user, device_info, ip_address)
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns user data and JWT tokens.
    """
    user = await auth_service.authenticate_user(db, data.email, data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    device_info, ip_address = get_client_info(request)
    tokens = await auth_service.create_tokens(db, user, device_info, ip_address)
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    data: TokenRefresh,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Old refresh token is revoked, new tokens are returned.
    """
    device_info, ip_address = get_client_info(request)
    result = await auth_service.refresh_tokens(db, data.refresh_token, device_info, ip_address)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истёкший refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user, tokens = result
    return tokens


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout from all devices (revoke all refresh tokens).
    """
    count = await auth_service.revoke_all_tokens(db, current_user.id)
    return MessageResponse(
        message=f"Выход выполнен. Отозвано токенов: {count}",
        success=True
    )


# ============== Current User ==============

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user info.
    """
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    full_name: str = None,
    phone: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile.
    """
    if full_name:
        current_user.full_name = full_name
    if phone:
        current_user.phone = phone
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password for current user.
    """
    # Verify current password
    if not auth_service.verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль"
        )
    
    # Update password
    current_user.password_hash = auth_service.hash_password(data.new_password)
    
    # Revoke all tokens (force re-login)
    await auth_service.revoke_all_tokens(db, current_user.id)
    
    await db.commit()
    
    return MessageResponse(
        message="Пароль успешно изменён. Войдите заново.",
        success=True
    )


# ============== Telegram Linking ==============

@router.post("/telegram/link", response_model=LinkingCodeResponse)
async def generate_telegram_link_code(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate code to link Telegram account.
    
    User should send this code to the bot: /link CODE
    """
    if current_user.telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram уже привязан. Сначала отвяжите текущий аккаунт."
        )
    
    code, expires = await auth_service.generate_linking_code(db, current_user.id)
    
    return LinkingCodeResponse(
        code=code,
        expires_at=expires,
        instructions=f"Отправьте боту команду: /link {code}"
    )


@router.post("/telegram/confirm", response_model=UserResponse)
async def confirm_telegram_link(
    data: TelegramLinkConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm Telegram linking (called from bot).
    
    This endpoint is called by the bot, not by the user directly.
    Protected by API token (not JWT).
    """
    try:
        user = await auth_service.link_telegram(
            db, 
            data.linking_code, 
            data.telegram_id,
            data.telegram_username
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Неверный или истёкший код привязки"
        )
    
    return UserResponse.model_validate(user)


@router.delete("/telegram/unlink", response_model=MessageResponse)
async def unlink_telegram(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Unlink Telegram account from current user.
    """
    if not current_user.telegram_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram не привязан"
        )
    
    await auth_service.unlink_telegram(db, current_user.id)
    
    return MessageResponse(
        message="Telegram успешно отвязан",
        success=True
    )


# ============== Bot Authentication ==============

@router.get("/telegram/user/{telegram_id}", response_model=UserResponse)
async def get_user_by_telegram(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by Telegram ID (for bot to check if user is linked).
    
    Protected by API token.
    """
    user = await auth_service.get_user_by_telegram_id(db, telegram_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким Telegram ID не найден"
        )
    
    return UserResponse.model_validate(user)
