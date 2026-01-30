import streamlit as st

st.set_page_config(
    page_title="Вход в систему",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import (
    login,
    register,
    is_authenticated,
    get_current_user,
    logout,
    init_session_state
)

# Initialize session state
init_session_state()

# Initialize form mode
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# If already authenticated, show user info and option to logout
if is_authenticated():
    user = get_current_user()

    st.title("✅ Вы вошли в систему")

    st.success(f"Добро пожаловать, **{user.get('full_name', 'Пользователь')}**!")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Email:**")
        st.markdown("**Роль:**")
        st.markdown("**Telegram:**")

    with col2:
        st.markdown(user.get('email', '—'))
        role_labels = {'admin': 'Администратор', 'manager': 'Менеджер', 'user': 'Пользователь'}
        st.markdown(role_labels.get(user.get('role', 'user'), user.get('role', '—')))
        if user.get('telegram_id'):
            st.markdown(f"@{user.get('telegram_username', 'связан')}")
        else:
            st.markdown("Не привязан")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏠 На главную", use_container_width=True, type="primary"):
            st.switch_page("app.py")

    with col2:
        if st.button("🚪 Выйти", use_container_width=True):
            logout()
            st.rerun()

    st.stop()


# Not authenticated - show login/register forms
st.title("🔐 Вход в систему")
st.markdown("**Банкрот ПРО** — система управления делами о банкротстве")

# Toggle between login and register
col1, col2 = st.columns(2)

with col1:
    if st.button(
        "Вход",
        use_container_width=True,
        type="primary" if st.session_state.auth_mode == "login" else "secondary"
    ):
        st.session_state.auth_mode = "login"
        st.rerun()

with col2:
    if st.button(
        "Регистрация",
        use_container_width=True,
        type="primary" if st.session_state.auth_mode == "register" else "secondary"
    ):
        st.session_state.auth_mode = "register"
        st.rerun()

st.divider()

# ============== LOGIN FORM ==============
if st.session_state.auth_mode == "login":
    st.subheader("Вход в аккаунт")

    with st.form("login_form"):
        email = st.text_input(
            "Email",
            placeholder="user@example.com",
            help="Введите email, указанный при регистрации"
        )

        password = st.text_input(
            "Пароль",
            type="password",
            placeholder="Введите пароль",
            help="Минимум 8 символов"
        )

        submitted = st.form_submit_button("Войти", use_container_width=True, type="primary")

        if submitted:
            if not email:
                st.error("Введите email")
            elif not password:
                st.error("Введите пароль")
            else:
                with st.spinner("Вход..."):
                    success, error = login(email, password)

                if success:
                    st.success("Вход выполнен успешно!")
                    st.balloons()
                    # Redirect to home
                    st.switch_page("app.py")
                else:
                    st.error(error)

    st.caption("Нет аккаунта? Нажмите 'Регистрация' выше")


# ============== REGISTER FORM ==============
elif st.session_state.auth_mode == "register":
    st.subheader("Создание аккаунта")

    with st.form("register_form"):
        full_name = st.text_input(
            "ФИО *",
            placeholder="Иванов Иван Иванович",
            help="Полное имя (минимум 2 символа)"
        )

        email = st.text_input(
            "Email *",
            placeholder="user@example.com",
            help="Будет использоваться для входа"
        )

        col1, col2 = st.columns(2)

        with col1:
            password = st.text_input(
                "Пароль *",
                type="password",
                placeholder="Минимум 8 символов",
                help="Должен содержать буквы и цифры"
            )

        with col2:
            password_confirm = st.text_input(
                "Подтвердите пароль *",
                type="password",
                placeholder="Повторите пароль"
            )

        phone = st.text_input(
            "Телефон",
            placeholder="+7 999 123-45-67",
            help="Необязательно"
        )

        # Password requirements
        st.caption("""
        **Требования к паролю:**
        - От 8 до 100 символов
        - Хотя бы одна буква (a-z, A-Z)
        - Хотя бы одна цифра (0-9)
        """)

        submitted = st.form_submit_button("Зарегистрироваться", use_container_width=True, type="primary")

        if submitted:
            # Validation
            errors = []

            if not full_name or len(full_name) < 2:
                errors.append("Введите ФИО (минимум 2 символа)")
            elif len(full_name) > 255:
                errors.append("ФИО слишком длинное (максимум 255 символов)")

            if not email or "@" not in email:
                errors.append("Введите корректный email")
            elif len(email) > 255:
                errors.append("Email слишком длинный (максимум 255 символов)")

            if not password:
                errors.append("Введите пароль")
            elif len(password) < 8:
                errors.append("Пароль должен быть минимум 8 символов")
            elif len(password) > 100:
                errors.append("Пароль слишком длинный (максимум 100 символов)")
            elif not any(c.isalpha() for c in password):
                errors.append("Пароль должен содержать хотя бы одну букву")
            elif not any(c.isdigit() for c in password):
                errors.append("Пароль должен содержать хотя бы одну цифру")

            if password != password_confirm:
                errors.append("Пароли не совпадают")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                with st.spinner("Регистрация..."):
                    success, error = register(
                        email=email,
                        password=password,
                        full_name=full_name,
                        phone=phone if phone else None
                    )

                if success:
                    st.success("Регистрация успешна! Добро пожаловать!")
                    st.balloons()
                    # Redirect to home
                    st.switch_page("app.py")
                else:
                    st.error(error)

    st.caption("Уже есть аккаунт? Нажмите 'Вход' выше")


# Footer
st.divider()
st.caption("© 2025 Банкрот ПРО. Все права защищены.")
