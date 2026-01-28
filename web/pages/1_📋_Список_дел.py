import streamlit as st
st.set_page_config(page_title="Список дел", page_icon="📋", layout="wide")

import httpx
import os
from datetime import datetime

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN")
DEFAULT_HEADERS = {"X-API-Token": API_TOKEN} if API_TOKEN else {}

st.title("📋 Список дел")


@st.cache_data(ttl=30)
def get_cases():
    """Fetch all cases from API"""
    try:
        response = httpx.get(f"{API_URL}/api/cases", headers=DEFAULT_HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Ошибка при загрузке дел: {str(e)}")
        return []


# Status filter
status_options = {
    "all": "Все",
    "new": "Новые",
    "in_progress": "В работе",
    "court": "В суде",
    "completed": "Завершенные",
}

selected_status = st.selectbox(
    "Фильтр по статусу", options=list(status_options.keys()), format_func=lambda x: status_options[x]
)

# Refresh button
if st.button("🔄 Обновить"):
    st.cache_data.clear()
    st.rerun()

# Get cases
cases = get_cases()

if selected_status != "all":
    cases = [c for c in cases if c["status"] == selected_status]

if not cases:
    st.info("Нет дел. Создайте первое в разделе '➕ Новое дело'")
else:
    st.write(f"**Найдено дел:** {len(cases)}")

    # Display cases
    for case in cases:
        status_emoji = {
            "new": "🆕",
            "in_progress": "⏳",
            "court": "⚖️",
            "completed": "✅",
        }.get(case["status"], "📁")

        with st.expander(f"{status_emoji} {case['case_number']} — {case['full_name']}"):
            col1, col2 = st.columns(2)

            with col1:
                # Translate status to Russian
                status_russian = {
                    "new": "Новое",
                    "in_progress": "В работе",
                    "court": "В суде",
                    "completed": "Завершено",
                }.get(case['status'], case['status'])
                st.write(f"**Статус:** {status_russian}")

                debt = case.get("total_debt")
                st.write(f"**Долг:** {float(debt or 0):,.0f} руб." if debt else "**Долг:** не указан")
                st.write(f"**Кредиторов:** {case.get('creditors_count', 0)}")

            with col2:
                # Format date in Russian format (DD.MM.YYYY)
                if "created_at" in case and case["created_at"]:
                    try:
                        created_date = datetime.fromisoformat(case["created_at"].replace('Z', '+00:00'))
                        created = created_date.strftime("%d.%m.%Y")
                    except:
                        created = case["created_at"][:10]
                else:
                    created = "—"
                st.write(f"**Создано:** {created}")
                st.write(f"**ID:** {case['id']}")

            # View full details button
            if st.button("📄 Открыть полную карточку", key=f"open_{case['id']}"):
                st.session_state.selected_case_id = case["id"]
                st.switch_page("pages/2_➕_Новое_дело.py")

# Summary stats
if cases:
    st.divider()
    st.subheader("📊 Статистика")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_debt = sum(float(c.get("total_debt", 0) or 0) for c in cases)
        st.metric("Общая сумма долга", f"{total_debt:,.0f} руб.")

    with col2:
        avg_debt = total_debt / len(cases) if cases else 0
        st.metric("Средний долг", f"{avg_debt:,.0f} руб.")

    with col3:
        total_creditors = sum(c.get("creditors_count", 0) for c in cases)
        st.metric("Всего кредиторов", total_creditors)
