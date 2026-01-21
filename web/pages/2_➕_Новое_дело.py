import streamlit as st
import httpx
import os
from datetime import date

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN")
DEFAULT_HEADERS = {"X-API-Token": API_TOKEN} if API_TOKEN else {}

st.title("➕ Новое дело")

# Check if editing existing case
if "selected_case_id" in st.session_state:
    case_id = st.session_state.selected_case_id
    st.info(f"Редактирование дела ID: {case_id}")

    try:
        response = httpx.get(f"{API_URL}/api/cases/{case_id}", headers=DEFAULT_HEADERS)
        response.raise_for_status()
        existing_case = response.json()
    except Exception as e:
        st.error(f"Ошибка загрузки дела: {str(e)}")
        existing_case = None

    if st.button("⬅️ Создать новое дело"):
        del st.session_state.selected_case_id
        st.rerun()
else:
    existing_case = None

# Form
with st.form("case_form"):
    st.subheader("👤 Основные данные")

    col1, col2 = st.columns(2)

    with col1:
        full_name = st.text_input(
            "ФИО должника *", value=existing_case["full_name"] if existing_case else "", max_chars=255
        )

        birth_date = st.date_input(
            "Дата рождения",
            value=existing_case["birth_date"] if existing_case and existing_case.get("birth_date") else None,
            max_value=date.today(),
        )

        phone = st.text_input("Телефон", value=existing_case.get("phone", "") if existing_case else "")

    with col2:
        status = st.selectbox(
            "Статус дела",
            options=["new", "in_progress", "court", "completed"],
            format_func=lambda x: {
                "new": "Новое",
                "in_progress": "В работе",
                "court": "В суде",
                "completed": "Завершено",
            }[x],
            index=["new", "in_progress", "court", "completed"].index(existing_case["status"])
            if existing_case
            else 0,
        )

        email = st.text_input("Email", value=existing_case.get("email", "") if existing_case else "")

        telegram_user_id = st.number_input(
            "Telegram User ID",
            value=existing_case.get("telegram_user_id", 0) if existing_case else 0,
            min_value=0,
            step=1,
        )

    col1, col2 = st.columns(2)

    with col1:
        gender = st.selectbox(
            "Пол",
            options=["M", "F", ""],
            format_func=lambda x: {"M": "Мужской", "F": "Женский", "": "Не указан"}[x],
            index=["M", "F", ""].index(existing_case.get("gender", "")) if existing_case else 2,
        )

    with col2:
        marital_status = st.selectbox(
            "Семейное положение",
            options=["single", "married", "divorced", "widowed", ""],
            format_func=lambda x: {
                "single": "Холост/Не замужем",
                "married": "Женат/Замужем",
                "divorced": "Разведен(а)",
                "widowed": "Вдовец/Вдова",
                "": "Не указано",
            }[x],
            index=["single", "married", "divorced", "widowed", ""].index(existing_case.get("marital_status", ""))
            if existing_case
            else 4,
        )

    st.divider()
    st.subheader("📄 Паспортные данные")

    col1, col2 = st.columns(2)

    with col1:
        passport_series = st.text_input(
            "Серия паспорта", value=existing_case.get("passport_series", "") if existing_case else "", max_chars=4
        )

        passport_number = st.text_input(
            "Номер паспорта", value=existing_case.get("passport_number", "") if existing_case else "", max_chars=6
        )

    with col2:
        passport_issued_by = st.text_area(
            "Кем выдан", value=existing_case.get("passport_issued_by", "") if existing_case else ""
        )

        passport_issued_date = st.date_input(
            "Дата выдачи",
            value=existing_case["passport_issued_date"]
            if existing_case and existing_case.get("passport_issued_date")
            else None,
            max_value=date.today(),
        )

    passport_code = st.text_input(
        "Код подразделения",
        value=existing_case.get("passport_code", "") if existing_case else "",
        max_chars=10,
        placeholder="000-000",
    )

    st.divider()
    st.subheader("🆔 Документы")

    col1, col2 = st.columns(2)

    with col1:
        inn = st.text_input("ИНН", value=existing_case.get("inn", "") if existing_case else "", max_chars=12)

    with col2:
        snils = st.text_input(
            "СНИЛС", value=existing_case.get("snils", "") if existing_case else "", max_chars=14
        )

    registration_address = st.text_area(
        "Адрес регистрации", value=existing_case.get("registration_address", "") if existing_case else ""
    )

    st.divider()
    st.subheader("💰 Финансовые данные")

    col1, col2 = st.columns(2)

    with col1:
        total_debt = st.number_input(
            "Общая сумма долга (₽)",
            value=float(existing_case.get("total_debt", 0) or 0) if existing_case else 0.0,
            min_value=0.0,
            step=1000.0,
        )

    with col2:
        monthly_income = st.number_input(
            "Ежемесячный доход (₽)",
            value=float(existing_case.get("monthly_income", 0) or 0) if existing_case else 0.0,
            min_value=0.0,
            step=1000.0,
        )

    notes = st.text_area("Примечания", value=existing_case.get("notes", "") if existing_case else "", height=100)

    st.divider()
    st.subheader("⚖️ Суд и СРО")

    col1, col2 = st.columns(2)

    with col1:
        court_name = st.text_input(
            "Название арбитражного суда",
            value=existing_case.get("court_name", "") if existing_case else "",
            max_chars=255,
        )

        court_address = st.text_area(
            "Адрес суда", value=existing_case.get("court_address", "") if existing_case else "", height=100
        )

    with col2:
        sro_name = st.text_input(
            "Название СРО финансового управляющего",
            value=existing_case.get("sro_name", "") if existing_case else "",
            max_chars=255,
        )

        sro_address = st.text_area(
            "Адрес СРО", value=existing_case.get("sro_address", "") if existing_case else "", height=100
        )

    # Submit
    submitted = st.form_submit_button("💾 Сохранить" if existing_case else "➕ Создать дело")

    if submitted:
        if not full_name:
            st.error("ФИО должника обязательно для заполнения")
        else:
            try:
                data = {
                    "full_name": full_name,
                    "status": status,
                    "birth_date": birth_date.isoformat() if birth_date else None,
                    "phone": phone or None,
                    "email": email or None,
                    "gender": gender or None,
                    "marital_status": marital_status or None,
                    "passport_series": passport_series or None,
                    "passport_number": passport_number or None,
                    "passport_issued_by": passport_issued_by or None,
                    "passport_issued_date": passport_issued_date.isoformat() if passport_issued_date else None,
                    "passport_code": passport_code or None,
                    "inn": inn or None,
                    "snils": snils or None,
                    "registration_address": registration_address or None,
                    "total_debt": total_debt if total_debt > 0 else None,
                    "monthly_income": monthly_income if monthly_income > 0 else None,
                    "court_name": court_name or None,
                    "court_address": court_address or None,
                    "sro_name": sro_name or None,
                    "sro_address": sro_address or None,
                    "notes": notes or None,
                }

                if existing_case:
                    # Update
                    data["telegram_user_id"] = telegram_user_id if telegram_user_id > 0 else None
                    response = httpx.put(
                        f"{API_URL}/api/cases/{case_id}", json=data, timeout=30.0, headers=DEFAULT_HEADERS
                    )
                    response.raise_for_status()
                    st.success("✅ Дело обновлено!")
                else:
                    # Create
                    create_data = {
                        "full_name": full_name,
                        "total_debt": total_debt if total_debt > 0 else None,
                        "telegram_user_id": telegram_user_id if telegram_user_id > 0 else None,
                    }
                    response = httpx.post(
                        f"{API_URL}/api/cases", json=create_data, timeout=30.0, headers=DEFAULT_HEADERS
                    )
                    response.raise_for_status()
                    case = response.json()

                    # Update with full data
                    response = httpx.put(
                        f"{API_URL}/api/cases/{case['id']}",
                        json=data,
                        timeout=30.0,
                        headers=DEFAULT_HEADERS,
                    )
                    response.raise_for_status()

                    st.success(f"✅ Дело создано! Номер: {case['case_number']}")

                    # Store case ID for editing
                    st.session_state.selected_case_id = case["id"]

            except Exception as e:
                st.error(f"❌ Ошибка: {str(e)}")

# Show download document button if editing
if existing_case:
    st.divider()
    st.subheader("📄 Документы")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Скачать заявление о банкротстве (Полное)"):
            try:
                response = httpx.get(
                    f"{API_URL}/api/documents/cases/{case_id}/document/petition",
                    timeout=60.0,
                    headers=DEFAULT_HEADERS,
                )
                response.raise_for_status()

                st.download_button(
                    label="💾 Сохранить документ",
                    data=response.content,
                    file_name=f"bankruptcy_petition_{existing_case['case_number']}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            except Exception as e:
                st.error(f"❌ Ошибка генерации документа: {str(e)}")

    with col2:
        if st.button("📥 Скачать заявление (Базовое)"):
            try:
                response = httpx.get(
                    f"{API_URL}/api/documents/{case_id}/bankruptcy-application",
                    timeout=60.0,
                    headers=DEFAULT_HEADERS,
                )
                response.raise_for_status()

                st.download_button(
                    label="💾 Сохранить базовый документ",
                    data=response.content,
                    file_name=f"bankruptcy_{existing_case['case_number']}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            except Exception as e:
                st.error(f"❌ Ошибка генерации документа: {str(e)}")
