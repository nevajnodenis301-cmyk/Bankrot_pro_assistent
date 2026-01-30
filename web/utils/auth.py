"""
Authentication utilities for Streamlit web app.
Handles login, register, token management, and page protection.
"""
import os
import streamlit as st
import httpx
from functools import wraps
from datetime import datetime, timedelta

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def init_session_state():
    """Initialize authentication-related session state variables."""
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "refresh_token" not in st.session_state:
        st.session_state.refresh_token = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "token_expires_at" not in st.session_state:
        st.session_state.token_expires_at = None


def login(email: str, password: str) -> tuple[bool, str]:
    """
    Login with email and password.

    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        response = httpx.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["tokens"]["access_token"]
            st.session_state.refresh_token = data["tokens"]["refresh_token"]
            st.session_state.user = data["user"]
            # Calculate token expiration
            expires_in = data["tokens"].get("expires_in", 3600)
            st.session_state.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            return True, ""
        elif response.status_code == 401:
            return False, "Неверный email или пароль"
        else:
            error_detail = response.json().get("detail", "Ошибка входа")
            return False, error_detail

    except httpx.ConnectError:
        return False, "Не удалось подключиться к серверу. Проверьте, что API запущен."
    except httpx.TimeoutException:
        return False, "Превышено время ожидания ответа от сервера"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"


def register(email: str, password: str, full_name: str, phone: str = None) -> tuple[bool, str]:
    """
    Register new user account.

    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        payload = {
            "email": email,
            "password": password,
            "full_name": full_name,
        }
        if phone:
            payload["phone"] = phone

        response = httpx.post(
            f"{API_URL}/auth/register",
            json=payload,
            timeout=30.0
        )

        if response.status_code == 201:
            data = response.json()
            st.session_state.access_token = data["tokens"]["access_token"]
            st.session_state.refresh_token = data["tokens"]["refresh_token"]
            st.session_state.user = data["user"]
            expires_in = data["tokens"].get("expires_in", 3600)
            st.session_state.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            return True, ""
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "Ошибка регистрации")
            # Handle validation errors
            if isinstance(error_detail, list):
                errors = [e.get("msg", str(e)) for e in error_detail]
                return False, "; ".join(errors)
            return False, error_detail
        else:
            error_detail = response.json().get("detail", "Ошибка регистрации")
            return False, error_detail

    except httpx.ConnectError:
        return False, "Не удалось подключиться к серверу. Проверьте, что API запущен."
    except httpx.TimeoutException:
        return False, "Превышено время ожидания ответа от сервера"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"


def refresh_token() -> bool:
    """
    Refresh access token using refresh token.

    Returns:
        bool: True if successful, False otherwise
    """
    if not st.session_state.refresh_token:
        return False

    try:
        response = httpx.post(
            f"{API_URL}/auth/refresh",
            json={"refresh_token": st.session_state.refresh_token},
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()
            st.session_state.access_token = data["access_token"]
            st.session_state.refresh_token = data["refresh_token"]
            expires_in = data.get("expires_in", 3600)
            st.session_state.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            return True
        else:
            # Refresh failed, clear session
            logout()
            return False

    except Exception:
        return False


def logout():
    """Clear all authentication data from session state."""
    # Try to logout on server (revoke tokens)
    if st.session_state.access_token:
        try:
            httpx.post(
                f"{API_URL}/auth/logout",
                headers=get_auth_headers(),
                timeout=10.0
            )
        except Exception:
            pass  # Ignore errors during logout

    # Clear session state
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user = None
    st.session_state.token_expires_at = None


def get_auth_headers() -> dict:
    """
    Get authorization headers for API requests.

    Returns:
        dict: Headers with Bearer token if authenticated, empty dict otherwise
    """
    if st.session_state.access_token:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}


def is_authenticated() -> bool:
    """
    Check if user is authenticated.

    Returns:
        bool: True if authenticated with valid token
    """
    init_session_state()

    if not st.session_state.access_token:
        return False

    # Check if token is expired
    if st.session_state.token_expires_at:
        if datetime.utcnow() >= st.session_state.token_expires_at:
            # Try to refresh
            if not refresh_token():
                return False

    return True


def get_current_user() -> dict | None:
    """
    Get current authenticated user data.

    Returns:
        dict: User data or None if not authenticated
    """
    init_session_state()

    if not is_authenticated():
        return None

    return st.session_state.user


def fetch_current_user() -> dict | None:
    """
    Fetch current user from API (refreshes user data).

    Returns:
        dict: User data or None if failed
    """
    if not st.session_state.access_token:
        return None

    try:
        response = httpx.get(
            f"{API_URL}/auth/me",
            headers=get_auth_headers(),
            timeout=30.0
        )

        if response.status_code == 200:
            st.session_state.user = response.json()
            return st.session_state.user
        elif response.status_code == 401:
            # Token invalid, try refresh
            if refresh_token():
                return fetch_current_user()
            logout()
            return None
        else:
            return None

    except Exception:
        return None


def require_auth():
    """
    Require authentication for current page.

    If not authenticated, shows login prompt and stops execution.
    Should be called at the top of protected pages.

    Usage:
        require_auth()
        # Rest of page code...
    """
    init_session_state()

    if not is_authenticated():
        st.warning("Для доступа к этой странице необходимо войти в систему")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Перейти на страницу входа", use_container_width=True, type="primary"):
                st.switch_page("pages/0_🔐_Вход.py")

        st.stop()


def show_user_sidebar():
    """
    Show user info and logout button in sidebar.
    Should be called from main app.py.
    """
    init_session_state()

    if is_authenticated() and st.session_state.user:
        user = st.session_state.user

        st.sidebar.divider()
        st.sidebar.markdown(f"**{user.get('full_name', 'Пользователь')}**")
        st.sidebar.caption(user.get('email', ''))

        # Role badge
        role = user.get('role', 'user')
        role_labels = {
            'admin': '👑 Администратор',
            'manager': '📋 Менеджер',
            'user': '👤 Пользователь'
        }
        st.sidebar.caption(role_labels.get(role, role))

        # Telegram status
        if user.get('telegram_id'):
            st.sidebar.caption(f"📱 Telegram: @{user.get('telegram_username', 'связан')}")

        if st.sidebar.button("🚪 Выйти", use_container_width=True):
            logout()
            st.rerun()
    else:
        st.sidebar.divider()
        if st.sidebar.button("🔐 Войти", use_container_width=True, type="primary"):
            st.switch_page("pages/0_🔐_Вход.py")
