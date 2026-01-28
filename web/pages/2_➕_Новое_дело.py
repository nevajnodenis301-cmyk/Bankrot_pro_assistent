import streamlit as st
st.set_page_config(page_title="Новое дело", page_icon="➕", layout="wide")

import httpx
import os
from datetime import date, datetime

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN")
DEFAULT_HEADERS = {"X-API-Token": API_TOKEN} if API_TOKEN else {}

st.title("➕ Новое дело")


def format_money(amount):
    """Format monetary amount with thousand separators"""
    if amount is None:
        return "—"
    return f"{float(amount):,.2f}".replace(",", " ").replace(".", ",") + " руб."


def get_creditors_for_case(case_id: int):
    """Fetch creditors from API"""
    try:
        response = httpx.get(
            f"{API_URL}/api/creditors/{case_id}",
            headers=DEFAULT_HEADERS,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return []


def add_creditor_to_api(case_id: int, creditor_data: dict):
    """Add creditor via API"""
    try:
        response = httpx.post(
            f"{API_URL}/api/creditors/{case_id}",
            json=creditor_data,
            headers=DEFAULT_HEADERS,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json(), None
    except Exception as e:
        return None, f"Ошибка при добавлении кредитора: {str(e)}"


def delete_creditor_from_api(creditor_id: int):
    """Delete creditor via API"""
    try:
        response = httpx.delete(
            f"{API_URL}/api/creditors/{creditor_id}",
            headers=DEFAULT_HEADERS,
            timeout=30.0
        )
        response.raise_for_status()
        return True, None
    except Exception as e:
        return False, f"Ошибка при удалении кредитора: {str(e)}"


def update_case_total_debt(case_id: int, total_debt: float):
    """Update total_debt in the case"""
    try:
        response = httpx.put(
            f"{API_URL}/api/cases/{case_id}",
            json={"total_debt": total_debt},
            headers=DEFAULT_HEADERS,
            timeout=30.0
        )
        response.raise_for_status()
        return True
    except Exception:
        return False


# Initialize session state for pending creditors (for new cases)
if "pending_creditors" not in st.session_state:
    st.session_state.pending_creditors = []

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
        st.session_state.pending_creditors = []
        st.rerun()
else:
    existing_case = None

# Form
with st.form("case_form"):
    st.subheader("👤 Личные данные")

    col1, col2 = st.columns(2)

    with col1:
        full_name = st.text_input(
            "ФИО должника *",
            value=existing_case["full_name"] if existing_case else "",
            max_chars=255,
            placeholder="Иванов Иван Иванович",
            help="Введите полное ФИО должника (Фамилия Имя Отчество)"
        )

        # Fix: Use conditional value for date_input to avoid None
        if existing_case and existing_case.get("birth_date"):
            birth_date_value = datetime.fromisoformat(existing_case["birth_date"]).date() if isinstance(existing_case["birth_date"], str) else existing_case["birth_date"]
            birth_date = st.date_input(
                "Дата рождения",
                value=birth_date_value,
                max_value=date.today(),
                help="Выберите дату рождения должника"
            )
        else:
            birth_date = st.date_input(
                "Дата рождения",
                max_value=date.today(),
                help="Выберите дату рождения должника"
            )

        phone = st.text_input(
            "Телефон",
            value=existing_case.get("phone", "") if existing_case else "",
            placeholder="+7 (999) 123-45-67",
            help="Контактный телефон должника"
        )

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
            help="Текущий статус дела"
        )

        email = st.text_input(
            "Email",
            value=existing_case.get("email", "") if existing_case else "",
            placeholder="ivanov@example.com",
            help="Электронная почта для связи"
        )

        telegram_user_id = st.number_input(
            "Telegram User ID",
            value=existing_case.get("telegram_user_id", 0) if existing_case else 0,
            min_value=0,
            step=1,
            help="ID пользователя в Telegram (заполняется автоматически при работе через бот)"
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
                "single": "Не женат/Не замужем",
                "married": "Женат/Замужем",
                "divorced": "Разведён/Разведена",
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
            "Серия паспорта",
            value=existing_case.get("passport_series", "") if existing_case else "",
            max_chars=4,
            placeholder="4510",
            help="4 цифры серии паспорта (например: 4510)"
        )

        passport_number = st.text_input(
            "Номер паспорта",
            value=existing_case.get("passport_number", "") if existing_case else "",
            max_chars=6,
            placeholder="123456",
            help="6 цифр номера паспорта (например: 123456)"
        )

    with col2:
        passport_issued_by = st.text_area(
            "Кем выдан паспорт",
            value=existing_case.get("passport_issued_by", "") if existing_case else "",
            placeholder="Отделением УФМС России по г. Москве",
            help="Полное наименование органа, выдавшего паспорт"
        )

        # Fix: Use conditional value for date_input to avoid None
        if existing_case and existing_case.get("passport_issued_date"):
            passport_date_value = datetime.fromisoformat(existing_case["passport_issued_date"]).date() if isinstance(existing_case["passport_issued_date"], str) else existing_case["passport_issued_date"]
            passport_issued_date = st.date_input(
                "Дата выдачи паспорта",
                value=passport_date_value,
                max_value=date.today(),
                help="Дата выдачи паспорта"
            )
        else:
            passport_issued_date = st.date_input(
                "Дата выдачи паспорта",
                max_value=date.today(),
                help="Дата выдачи паспорта"
            )

    passport_code = st.text_input(
        "Код подразделения",
        value=existing_case.get("passport_code", "") if existing_case else "",
        max_chars=10,
        placeholder="770-001",
        help="Код подразделения в формате XXX-XXX (например: 770-001)"
    )

    st.divider()
    st.subheader("🆔 Документы")

    col1, col2 = st.columns(2)

    with col1:
        inn = st.text_input(
            "ИНН",
            value=existing_case.get("inn", "") if existing_case else "",
            max_chars=12,
            placeholder="123456789012",
            help="ИНН физического лица (12 цифр)"
        )

    with col2:
        snils = st.text_input(
            "СНИЛС",
            value=existing_case.get("snils", "") if existing_case else "",
            max_chars=14,
            placeholder="123-456-789 00",
            help="СНИЛС в формате XXX-XXX-XXX XX (например: 123-456-789 00)"
        )

    registration_address = st.text_area(
        "Адрес регистрации (по паспорту)",
        value=existing_case.get("registration_address", "") if existing_case else "",
        placeholder="г. Москва, ул. Ленина, д. 1, кв. 1",
        help="Адрес регистрации по месту жительства (прописка)"
    )

    st.divider()
    st.subheader("💰 Финансовые данные")

    col1, col2 = st.columns(2)

    with col1:
        total_debt = st.number_input(
            "Общая сумма долга (в рублях)",
            value=float(existing_case.get("total_debt", 0) or 0) if existing_case else 0.0,
            min_value=0.0,
            step=1000.0,
            help="Общая сумма задолженности перед всеми кредиторами (рассчитывается автоматически при добавлении кредиторов)"
        )

    with col2:
        monthly_income = st.number_input(
            "Ежемесячный доход (в рублях)",
            value=float(existing_case.get("monthly_income", 0) or 0) if existing_case else 0.0,
            min_value=0.0,
            step=1000.0,
            help="Средний ежемесячный доход должника"
        )

    notes = st.text_area(
        "Примечания",
        value=existing_case.get("notes", "") if existing_case else "",
        height=100,
        help="Дополнительная информация о деле"
    )

    st.divider()
    st.subheader("⚖️ Данные для суда")

    col1, col2 = st.columns(2)

    with col1:
        court_name = st.text_input(
            "Название арбитражного суда",
            value=existing_case.get("court_name", "") if existing_case else "",
            max_chars=255,
            placeholder="Арбитражный суд города Москвы",
            help="Полное официальное название арбитражного суда"
        )

        court_address = st.text_area(
            "Адрес арбитражного суда",
            value=existing_case.get("court_address", "") if existing_case else "",
            height=100,
            placeholder="г. Москва, ул. Большая Тульская, д. 17",
            help="Полный почтовый адрес суда"
        )

    with col2:
        sro_name = st.text_input(
            "Название СРО арбитражных управляющих",
            value=existing_case.get("sro_name", "") if existing_case else "",
            max_chars=255,
            placeholder="СРО 'Ассоциация антикризисных управляющих'",
            help="Саморегулируемая организация арбитражных управляющих"
        )

        sro_address = st.text_area(
            "Адрес СРО",
            value=existing_case.get("sro_address", "") if existing_case else "",
            height=100,
            placeholder="г. Москва, ул. Примерная, д. 1",
            help="Полный почтовый адрес СРО"
        )

    # Submit
    submitted = st.form_submit_button("💾 Сохранить" if existing_case else "➕ Создать дело")

    if submitted:
        if not full_name:
            st.error("ФИО должника обязательно для заполнения")
        else:
            try:
                # Calculate total debt from pending creditors if creating new case
                calculated_debt = total_debt
                if not existing_case and st.session_state.pending_creditors:
                    calculated_debt = sum(c.get("debt_amount", 0) for c in st.session_state.pending_creditors)
                    if total_debt == 0:
                        calculated_debt = calculated_debt
                    else:
                        calculated_debt = total_debt  # Use manual value if specified

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
                    "total_debt": calculated_debt if calculated_debt > 0 else None,
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
                    st.success("Дело обновлено!")
                else:
                    # Create
                    create_data = {
                        "full_name": full_name,
                        "total_debt": calculated_debt if calculated_debt > 0 else None,
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

                    # Add pending creditors
                    creditors_added = 0
                    for creditor_data in st.session_state.pending_creditors:
                        result, error = add_creditor_to_api(case["id"], creditor_data)
                        if result:
                            creditors_added += 1

                    # Update total_debt based on creditors
                    if creditors_added > 0:
                        creditors_total = sum(c.get("debt_amount", 0) for c in st.session_state.pending_creditors)
                        update_case_total_debt(case["id"], creditors_total)

                    st.success(f"Дело создано! Номер: {case['case_number']}")
                    if creditors_added > 0:
                        st.info(f"Добавлено кредиторов: {creditors_added}")

                    # Clear pending creditors and store case ID for editing
                    st.session_state.pending_creditors = []
                    st.session_state.selected_case_id = case["id"]

            except Exception as e:
                st.error(f"Ошибка: {str(e)}")

# Creditors section (outside the main form)
st.divider()
st.subheader("💳 Кредиторы")

# Creditor type and debt type mappings
creditor_type_names = {
    "bank": "Банк",
    "mfo": "МФО",
    "individual": "Физическое лицо",
    "tax": "Налоговая",
    "other": "Другое",
    None: "—"
}

debt_type_names = {
    "credit": "Кредит",
    "microloan": "Микрозайм",
    "alimony": "Алименты",
    "tax": "Налоги",
    "utility": "ЖКХ",
    "other": "Другое",
    None: "—"
}

if existing_case:
    # Show existing creditors from API
    creditors = get_creditors_for_case(case_id)

    if creditors:
        st.write(f"**Кредиторов в деле:** {len(creditors)}")

        for idx, creditor in enumerate(creditors, 1):
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.write(f"**{idx}. {creditor['name']}**")
                st.caption(f"{creditor_type_names.get(creditor.get('creditor_type'), '—')} | {debt_type_names.get(creditor.get('debt_type'), '—')}")

            with col2:
                st.write(format_money(creditor.get("debt_amount")))
                if creditor.get("contract_number"):
                    st.caption(f"Договор: {creditor['contract_number']}")

            with col3:
                if st.button("🗑️", key=f"del_cred_{creditor['id']}", help="Удалить кредитора"):
                    success, error = delete_creditor_from_api(creditor["id"])
                    if success:
                        # Recalculate total debt
                        remaining = [c for c in creditors if c["id"] != creditor["id"]]
                        new_total = sum(float(c.get("debt_amount") or 0) for c in remaining)
                        update_case_total_debt(case_id, new_total)
                        st.success("Кредитор удалён")
                        st.rerun()
                    else:
                        st.error(error)

        # Total
        total_from_creditors = sum(float(c.get("debt_amount") or 0) for c in creditors)
        st.write(f"**Итого:** {format_money(total_from_creditors)}")
    else:
        st.info("У этого дела пока нет кредиторов")

    # Add creditor form for existing case
    st.write("---")
    st.write("**Добавить кредитора:**")

    with st.form("add_creditor_existing", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            new_cred_name = st.text_input("Наименование *", placeholder="ПАО Сбербанк")
            new_cred_type = st.selectbox(
                "Тип кредитора",
                options=["bank", "mfo", "individual", "tax", "other"],
                format_func=lambda x: creditor_type_names[x]
            )
            new_cred_amount = st.number_input("Сумма долга *", min_value=0.0, step=1000.0, format="%.2f")

        with col2:
            new_cred_debt_type = st.selectbox(
                "Тип долга",
                options=["credit", "microloan", "alimony", "tax", "utility", "other"],
                format_func=lambda x: debt_type_names[x]
            )
            new_cred_contract = st.text_input("Номер договора", placeholder="1234567890")
            new_cred_date = st.date_input("Дата договора", value=None, max_value=date.today())

        if st.form_submit_button("➕ Добавить"):
            if not new_cred_name:
                st.error("Укажите наименование кредитора")
            elif new_cred_amount <= 0:
                st.error("Укажите сумму долга больше нуля")
            else:
                creditor_data = {
                    "name": new_cred_name,
                    "creditor_type": new_cred_type,
                    "debt_amount": new_cred_amount,
                    "debt_type": new_cred_debt_type,
                    "contract_number": new_cred_contract or None,
                    "contract_date": new_cred_date.isoformat() if new_cred_date else None
                }
                result, error = add_creditor_to_api(case_id, creditor_data)
                if result:
                    # Recalculate total debt
                    updated_creditors = get_creditors_for_case(case_id)
                    new_total = sum(float(c.get("debt_amount") or 0) for c in updated_creditors)
                    update_case_total_debt(case_id, new_total)
                    st.success(f"Кредитор '{new_cred_name}' добавлен")
                    st.rerun()
                else:
                    st.error(error)

else:
    # Show pending creditors for new case
    if st.session_state.pending_creditors:
        st.write(f"**Кредиторов добавлено:** {len(st.session_state.pending_creditors)}")

        for idx, creditor in enumerate(st.session_state.pending_creditors):
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.write(f"**{idx + 1}. {creditor['name']}**")
                st.caption(f"{creditor_type_names.get(creditor.get('creditor_type'), '—')} | {debt_type_names.get(creditor.get('debt_type'), '—')}")

            with col2:
                st.write(format_money(creditor.get("debt_amount")))
                if creditor.get("contract_number"):
                    st.caption(f"Договор: {creditor['contract_number']}")

            with col3:
                if st.button("🗑️", key=f"del_pending_{idx}", help="Удалить"):
                    st.session_state.pending_creditors.pop(idx)
                    st.rerun()

        # Total
        total_pending = sum(c.get("debt_amount", 0) for c in st.session_state.pending_creditors)
        st.write(f"**Итого:** {format_money(total_pending)}")
        st.caption("Кредиторы будут добавлены после создания дела")
    else:
        st.info("Добавьте кредиторов ниже. Они будут сохранены вместе с делом.")

    # Add creditor form for new case
    st.write("---")
    st.write("**Добавить кредитора:**")

    with st.form("add_creditor_new", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            new_cred_name = st.text_input("Наименование *", placeholder="ПАО Сбербанк", key="new_name")
            new_cred_type = st.selectbox(
                "Тип кредитора",
                options=["bank", "mfo", "individual", "tax", "other"],
                format_func=lambda x: creditor_type_names[x],
                key="new_type"
            )
            new_cred_amount = st.number_input("Сумма долга *", min_value=0.0, step=1000.0, format="%.2f", key="new_amount")

        with col2:
            new_cred_debt_type = st.selectbox(
                "Тип долга",
                options=["credit", "microloan", "alimony", "tax", "utility", "other"],
                format_func=lambda x: debt_type_names[x],
                key="new_debt_type"
            )
            new_cred_contract = st.text_input("Номер договора", placeholder="1234567890", key="new_contract")
            new_cred_date = st.date_input("Дата договора", value=None, max_value=date.today(), key="new_date")

        if st.form_submit_button("➕ Добавить в список"):
            if not new_cred_name:
                st.error("Укажите наименование кредитора")
            elif new_cred_amount <= 0:
                st.error("Укажите сумму долга больше нуля")
            else:
                creditor_data = {
                    "name": new_cred_name,
                    "creditor_type": new_cred_type,
                    "debt_amount": new_cred_amount,
                    "debt_type": new_cred_debt_type,
                    "contract_number": new_cred_contract or None,
                    "contract_date": new_cred_date.isoformat() if new_cred_date else None
                }
                st.session_state.pending_creditors.append(creditor_data)
                st.success(f"Кредитор '{new_cred_name}' добавлен в список")
                st.rerun()

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
                st.error(f"Ошибка генерации документа: {str(e)}")

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
                st.error(f"Ошибка генерации документа: {str(e)}")
