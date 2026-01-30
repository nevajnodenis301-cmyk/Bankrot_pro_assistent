import streamlit as st
st.set_page_config(page_title="Telegram", page_icon="💬", layout="centered")

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import require_auth, get_auth_headers, show_user_sidebar, fetch_current_user

# Require authentication
require_auth()

import httpx
from datetime import datetime

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def get_headers():
    """Get fresh auth headers for each API call."""
    return get_auth_headers()


def generate_link_code() -> tuple[dict | None, str | None]:
    """
    Generate a Telegram linking code.

    Returns:
        tuple: (data with code and expires_at, error message)
    """
    try:
        response = httpx.post(
            f"{API_URL}/auth/telegram/link",
            headers=get_headers(),
            timeout=30.0
        )

        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 400:
            error = response.json().get("detail", "Telegram уже привязан")
            return None, error
        else:
            error = response.json().get("detail", f"Ошибка сервера: {response.status_code}")
            return None, error

    except httpx.ConnectError:
        return None, "Не удалось подключиться к серверу"
    except httpx.TimeoutException:
        return None, "Превышено время ожидания ответа"
    except Exception as e:
        return None, f"Ошибка: {str(e)}"


def unlink_telegram() -> tuple[bool, str | None]:
    """
    Unlink Telegram account.

    Returns:
        tuple: (success, error message)
    """
    try:
        response = httpx.delete(
            f"{API_URL}/auth/telegram/unlink",
            headers=get_headers(),
            timeout=30.0
        )

        if response.status_code == 200:
            return True, None
        elif response.status_code == 400:
            error = response.json().get("detail", "Telegram не привязан")
            return False, error
        else:
            error = response.json().get("detail", f"Ошибка сервера: {response.status_code}")
            return False, error

    except httpx.ConnectError:
        return False, "Не удалось подключиться к серверу"
    except httpx.TimeoutException:
        return False, "Превышено время ожидания ответа"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"


def format_datetime(iso_string: str) -> str:
    """Format ISO datetime string to human-readable Russian format."""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y в %H:%M")
    except Exception:
        return iso_string


# Initialize session state for linking flow
if "telegram_link_code" not in st.session_state:
    st.session_state.telegram_link_code = None
if "telegram_link_expires" not in st.session_state:
    st.session_state.telegram_link_expires = None
if "telegram_link_error" not in st.session_state:
    st.session_state.telegram_link_error = None


st.title("💬 Привязка Telegram")
st.markdown("Свяжите свой аккаунт с Telegram для получения уведомлений")

# Get current user data (fresh from API)
user = fetch_current_user()

if not user:
    st.error("Не удалось загрузить данные пользователя")
    st.stop()

st.divider()

# ============== TELEGRAM LINKED ==============
if user.get("telegram_id"):
    st.success("✅ Telegram аккаунт привязан")

    # Show linked account info
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Telegram аккаунт:**")
        username = user.get("telegram_username")
        if username:
            st.markdown(f"@{username}")
        else:
            st.markdown(f"ID: {user.get('telegram_id')}")

    with col2:
        st.markdown("**Дата привязки:**")
        linked_at = user.get("telegram_linked_at")
        if linked_at:
            st.markdown(format_datetime(linked_at))
        else:
            st.markdown("—")

    st.divider()

    st.info("Вы будете получать уведомления о важных событиях в Telegram")

    # Unlink button
    st.markdown("---")
    st.subheader("Отключение Telegram")
    st.warning("После отключения вы перестанете получать уведомления в Telegram")

    if st.button("🔓 Отключить Telegram", type="secondary"):
        with st.spinner("Отключение..."):
            success, error = unlink_telegram()

        if success:
            # Clear linking state
            st.session_state.telegram_link_code = None
            st.session_state.telegram_link_expires = None
            st.success("Telegram успешно отключён")
            st.rerun()
        else:
            st.error(error)


# ============== TELEGRAM NOT LINKED ==============
else:
    st.info("📱 Telegram не привязан")
    st.markdown("""
    Привяжите Telegram аккаунт, чтобы:
    - Получать уведомления о новых событиях
    - Управлять делами через бота
    - Быстро отвечать на запросы
    """)

    st.divider()

    # Check if we have an active code
    has_active_code = (
        st.session_state.telegram_link_code and
        st.session_state.telegram_link_expires
    )

    # Check if code is expired
    code_expired = False
    if has_active_code:
        try:
            expires_at = datetime.fromisoformat(
                st.session_state.telegram_link_expires.replace('Z', '+00:00')
            )
            if datetime.now(expires_at.tzinfo) > expires_at:
                code_expired = True
                has_active_code = False
        except Exception:
            pass

    # Show expired warning
    if code_expired:
        st.warning("⏰ Код истёк. Нажмите кнопку ниже для генерации нового кода.")
        st.session_state.telegram_link_code = None
        st.session_state.telegram_link_expires = None

    # Generate code button
    if not has_active_code:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔗 Связать Telegram аккаунт", use_container_width=True, type="primary"):
                with st.spinner("Генерация кода..."):
                    data, error = generate_link_code()

                if data:
                    st.session_state.telegram_link_code = data.get("code")
                    st.session_state.telegram_link_expires = data.get("expires_at")
                    st.session_state.telegram_link_error = None
                    st.rerun()
                else:
                    st.session_state.telegram_link_error = error
                    st.error(error)

    # Show active code
    if has_active_code:
        st.subheader("Ваш код привязки:")

        # Large centered code display
        code = st.session_state.telegram_link_code

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 16px;
                padding: 30px;
                text-align: center;
                margin: 20px 0;
            ">
                <span style="
                    font-size: 48px;
                    font-weight: bold;
                    color: white;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                ">{code}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Instructions
        st.markdown("### 📝 Инструкция:")
        st.markdown(f"""
        1. Откройте Telegram бот **@BankrotProBot**
        2. Отправьте команду:
        """)

        # Command box
        st.code(f"/start {code}", language=None)

        st.markdown("""
        3. Дождитесь подтверждения привязки
        4. Страница обновится автоматически
        """)

        # Expiration info
        expires_at = st.session_state.telegram_link_expires
        if expires_at:
            st.caption(f"⏰ Код действителен до: {format_datetime(expires_at)}")

        st.divider()

        # Refresh and cancel buttons
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Проверить привязку", use_container_width=True):
                with st.spinner("Проверка..."):
                    updated_user = fetch_current_user()

                if updated_user and updated_user.get("telegram_id"):
                    st.session_state.telegram_link_code = None
                    st.session_state.telegram_link_expires = None
                    st.success("Telegram успешно привязан!")
                    st.rerun()
                else:
                    st.info("Привязка ещё не выполнена. Отправьте код в бот.")

        with col2:
            if st.button("❌ Отменить", use_container_width=True, type="secondary"):
                st.session_state.telegram_link_code = None
                st.session_state.telegram_link_expires = None
                st.rerun()

        # Auto-refresh for checking link status
        st.markdown("---")

        # Try to use st.fragment for auto-refresh (Streamlit 1.33+)
        try:
            @st.fragment(run_every=5)
            def check_telegram_link():
                """Auto-check if Telegram was linked."""
                updated_user = fetch_current_user()
                if updated_user and updated_user.get("telegram_id"):
                    st.session_state.telegram_link_code = None
                    st.session_state.telegram_link_expires = None
                    st.rerun()
                else:
                    st.caption("🔄 Автоматическая проверка каждые 5 секунд...")

            check_telegram_link()
        except (AttributeError, TypeError):
            # Fallback for older Streamlit versions
            st.caption("💡 Нажмите 'Проверить привязку' после отправки кода в бот")


# Show error if any
if st.session_state.telegram_link_error:
    st.error(st.session_state.telegram_link_error)

# Footer
st.divider()

# Show user in sidebar
show_user_sidebar()
