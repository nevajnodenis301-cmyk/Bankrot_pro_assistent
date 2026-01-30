import streamlit as st

st.set_page_config(
    page_title="Банкрот ПРО",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.auth import init_session_state, is_authenticated, get_current_user, logout, show_user_sidebar

# Initialize session state
init_session_state()

# Disable browser auto-translation
st.markdown(
    """
    <meta name="google" content="notranslate">
    <meta http-equiv="Content-Language" content="ru">
    <script>
        document.documentElement.setAttribute('lang', 'ru');
        document.documentElement.setAttribute('translate', 'no');
    </script>
    """,
    unsafe_allow_html=True
)

st.title("⚖️ Банкрот ПРО")
st.markdown("Система управления делами по банкротству физических лиц")

# Show different content based on authentication
if is_authenticated():
    user = get_current_user()
    st.success(f"Добро пожаловать, **{user.get('full_name', 'Пользователь')}**!")

    st.markdown(
        """
### Навигация

- 📋 **Список дел** — просмотр и управление делами
- ➕ **Новое дело** — создание дела с полными данными
- 📊 **Статистика** — аналитика по делам
- 💳 **Кредиторы** — управление кредиторами

### Быстрые действия
"""
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📋 Список дел", use_container_width=True):
            st.switch_page("pages/1_📋_Список_дел.py")

    with col2:
        if st.button("➕ Новое дело", use_container_width=True):
            st.switch_page("pages/2_➕_Новое_дело.py")

    with col3:
        if st.button("📊 Статистика", use_container_width=True):
            st.switch_page("pages/3_📊_Статистика.py")

else:
    st.info("Войдите в систему для доступа к функциям")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Войти в систему", use_container_width=True, type="primary"):
            st.switch_page("pages/0_🔐_Вход.py")

st.markdown(
    """
---

### О системе

**Банкрот ПРО** — комплексная система для юристов, специализирующихся на банкротстве физических лиц по 127-ФЗ РФ.

**Возможности:**
- Управление делами о банкротстве
- Хранение конфиденциальных данных клиентов
- Генерация документов (заявления, реестры кредиторов)
- AI-ассистент по вопросам законодательства
- Telegram-бот для быстрого доступа

**Безопасность:**
- Авторизация с использованием JWT токенов
- Конфиденциальные данные (паспорт, ИНН) доступны только авторизованным пользователям
- Telegram-бот работает только с публичными данными
- Все данные хранятся в защищенной БД PostgreSQL

---

⚠️ **Юридический дисклеймер:** Система предоставляет информационную поддержку и не заменяет профессиональную юридическую консультацию.
"""
)

# Sidebar
st.sidebar.title("Информация")
st.sidebar.info(
    """
**Версия:** 1.0.0

**Технологии:**
- FastAPI (Backend)
- Streamlit (Web UI)
- Aiogram (Telegram Bot)
- PostgreSQL (Database)
- Redis (Cache & FSM)
"""
)

# Show user info and logout in sidebar
show_user_sidebar()

if not is_authenticated():
    st.sidebar.success("Выберите раздел выше ☝️")
