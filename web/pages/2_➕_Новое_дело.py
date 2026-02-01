import streamlit as st
st.set_page_config(page_title="Новое дело", page_icon="➕", layout="wide")

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.auth import require_auth, get_auth_headers, show_user_sidebar

# Require authentication
require_auth()

import httpx
from datetime import date, datetime

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def get_headers():
    """Get fresh auth headers for each API call."""
    return get_auth_headers()
# DOC_HELPERS
# DOC_HELPERS_OK
st.title("➕ Новое дело")

# Show user in sidebar
show_user_sidebar()


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def format_money(amount):
    """Format monetary amount with thousand separators"""
    if amount is None:
        return "—"
    return f"{float(amount):,.2f}".replace(",", " ").replace(".", ",") + " руб."


def format_date(date_value):
    """Format date to Russian format DD.MM.YYYY"""
    if not date_value:
        return "—"
    if isinstance(date_value, str):
        try:
            date_value = datetime.fromisoformat(date_value).date()
        except:
            return date_value
    return date_value.strftime("%d.%m.%Y")


# --- Creditors API ---
def get_creditors_for_case(case_id: int):
    try:
        response = httpx.get(f"{API_URL}/api/creditors/{case_id}", headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        return []


def add_creditor_to_api(case_id: int, creditor_data: dict):
    try:
        response = httpx.post(f"{API_URL}/api/creditors/{case_id}", json=creditor_data, headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return response.json(), None
    except Exception as e:
        return None, f"Ошибка: {str(e)}"


def delete_creditor_from_api(creditor_id: int):
    try:
        response = httpx.delete(f"{API_URL}/api/creditors/{creditor_id}", headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return True, None
    except Exception as e:
        return False, f"Ошибка: {str(e)}"


# --- Children API ---
def get_children_for_case(case_id: int):
    try:
        response = httpx.get(f"{API_URL}/api/children/{case_id}", headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        return []


def add_child_to_api(case_id: int, child_data: dict):
    try:
        response = httpx.post(f"{API_URL}/api/children/{case_id}", json=child_data, headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return response.json(), None
    except Exception as e:
        return None, f"Ошибка: {str(e)}"


def delete_child_from_api(child_id: int):
    try:
        response = httpx.delete(f"{API_URL}/api/children/{child_id}", headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return True, None
    except Exception as e:
        return False, f"Ошибка: {str(e)}"


# --- Properties API (vehicles + real estate) ---
def get_properties_for_case(case_id: int, property_type: str = None):
    try:
        response = httpx.get(f"{API_URL}/api/properties/{case_id}", headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        properties = response.json()
        if property_type:
            properties = [p for p in properties if p.get("property_type") == property_type]
        return properties
    except Exception:
        return []


def add_property_to_api(case_id: int, property_data: dict):
    try:
        response = httpx.post(f"{API_URL}/api/properties/{case_id}", json=property_data, headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return response.json(), None
    except Exception as e:
        return None, f"Ошибка: {str(e)}"


def delete_property_from_api(property_id: int):
    try:
        response = httpx.delete(f"{API_URL}/api/properties/{property_id}", headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return True, None
    except Exception as e:
        return False, f"Ошибка: {str(e)}"


# --- Transactions API (securities, bank accounts history) ---
def get_transactions_for_case(case_id: int, transaction_type: str = None):
    try:
        url = f"{API_URL}/api/transactions/{case_id}"
        if transaction_type:
            url += f"?transaction_type={transaction_type}"
        response = httpx.get(url, headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception:
        return []


def add_transaction_to_api(case_id: int, transaction_data: dict):
    try:
        response = httpx.post(f"{API_URL}/api/transactions/{case_id}", json=transaction_data, headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return response.json(), None
    except Exception as e:
        return None, f"Ошибка: {str(e)}"


def delete_transaction_from_api(transaction_id: int):
    try:
        response = httpx.delete(f"{API_URL}/api/transactions/{transaction_id}", headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return True, None
    except Exception as e:
        return False, f"Ошибка: {str(e)}"


# --- Case API ---
def update_case_total_debt(case_id: int, total_debt: float):
    try:
        response = httpx.put(f"{API_URL}/api/cases/{case_id}", json={"total_debt": total_debt}, headers=get_headers(), timeout=30.0)
        response.raise_for_status()
        return True
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

# Pending items for new cases (before case is created)
if "pending_creditors" not in st.session_state:
    st.session_state.pending_creditors = []
if "pending_children" not in st.session_state:
    st.session_state.pending_children = []
if "pending_vehicles" not in st.session_state:
    st.session_state.pending_vehicles = []
if "pending_real_estate" not in st.session_state:
    st.session_state.pending_real_estate = []
if "pending_bank_accounts" not in st.session_state:
    st.session_state.pending_bank_accounts = []
if "pending_securities" not in st.session_state:
    st.session_state.pending_securities = []

# Check if editing existing case
if "selected_case_id" in st.session_state:
    case_id = st.session_state.selected_case_id
    st.info(f"Редактирование дела ID: {case_id}")

    try:
        response = httpx.get(f"{API_URL}/api/cases/{case_id}", headers=get_headers())
        response.raise_for_status()
        existing_case = response.json()
    except Exception as e:
        st.error(f"Ошибка загрузки дела: {str(e)}")
        existing_case = None

    if st.button("⬅️ Создать новое дело"):
        del st.session_state.selected_case_id
        st.session_state.pending_creditors = []
        st.session_state.pending_children = []
        st.session_state.pending_vehicles = []
        st.session_state.pending_real_estate = []
        st.session_state.pending_bank_accounts = []
        st.session_state.pending_securities = []
        st.rerun()
else:
    existing_case = None


# ═══════════════════════════════════════════════════════════════════════════════
# TYPE MAPPINGS
# ═══════════════════════════════════════════════════════════════════════════════

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

property_type_names = {
    "vehicle": "Транспортное средство",
    "real_estate": "Недвижимость",
    "other": "Другое",
    None: "—"
}

real_estate_type_names = {
    "apartment": "Квартира",
    "house": "Дом",
    "land": "Земельный участок",
    "garage": "Гараж",
    "commercial": "Коммерческая недвижимость",
    "other": "Другое",
    None: "—"
}

vehicle_type_names = {
    "car": "Легковой автомобиль",
    "truck": "Грузовой автомобиль",
    "motorcycle": "Мотоцикл",
    "trailer": "Прицеп",
    "boat": "Лодка/Катер",
    "other": "Другое",
    None: "—"
}

securities_type_names = {
    "stocks": "Акции",
    "bonds": "Облигации",
    "mutual_fund": "Паевой фонд",
    "deposit": "Вклад/Депозит",
    "crypto": "Криптовалюта",
    "precious_metals": "Драгоценные металлы",
    "jewelry": "Ювелирные изделия",
    "other": "Другое",
    None: "—"
}


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN FORM
# ═══════════════════════════════════════════════════════════════════════════════

with st.form("case_form"):

    # ═══════════════════════════════════════════════════════════════
    # SECTION 1: Personal Data (👤 Личные данные)
    # ═══════════════════════════════════════════════════════════════
    st.subheader("👤 Раздел 1: Личные данные")

    col1, col2 = st.columns(2)

    with col1:
        full_name = st.text_input(
            "ФИО должника *",
            value=existing_case["full_name"] if existing_case else "",
            max_chars=255,
            placeholder="Иванов Иван Иванович",
            help="Введите полное ФИО должника (Фамилия Имя Отчество)"
        )

        if existing_case and existing_case.get("birth_date"):
            birth_date_value = datetime.fromisoformat(existing_case["birth_date"]).date() if isinstance(existing_case["birth_date"], str) else existing_case["birth_date"]
            birth_date = st.date_input("Дата рождения", value=birth_date_value, max_value=date.today())
        else:
            birth_date = st.date_input("Дата рождения", value=None, max_value=date.today())

        phone = st.text_input(
            "Телефон",
            value=existing_case.get("phone", "") if existing_case else "",
            placeholder="+7 (999) 123-45-67"
        )

    with col2:
        status = st.selectbox(
            "Статус дела",
            options=["new", "in_progress", "court", "completed"],
            format_func=lambda x: {"new": "Новое", "in_progress": "В работе", "court": "В суде", "completed": "Завершено"}[x],
            index=["new", "in_progress", "court", "completed"].index(existing_case["status"]) if existing_case else 0
        )

        email = st.text_input(
            "Email",
            value=existing_case.get("email", "") if existing_case else "",
            placeholder="ivanov@example.com"
        )

        telegram_user_id = st.number_input(
            "Telegram User ID",
            value=(existing_case.get("telegram_user_id") or 0) if existing_case else 0,
            min_value=0,
            step=1
        )

    col1, col2 = st.columns(2)

    with col1:
        gender = st.selectbox(
            "Пол",
            options=["M", "F", ""],
            format_func=lambda x: {"M": "Мужской", "F": "Женский", "": "Не указан"}[x],
            index=["M", "F", ""].index(existing_case.get("gender", "") or "") if existing_case else 2
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
            index=["single", "married", "divorced", "widowed", ""].index(existing_case.get("marital_status", "") or "") if existing_case else 4
        )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 2: Passport Data (📄 Паспортные данные)
    # ═══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("📄 Раздел 2: Паспортные данные")

    col1, col2 = st.columns(2)

    with col1:
        passport_series = st.text_input(
            "Серия паспорта",
            value=existing_case.get("passport_series", "") if existing_case else "",
            max_chars=4,
            placeholder="4510"
        )

        passport_number = st.text_input(
            "Номер паспорта",
            value=existing_case.get("passport_number", "") if existing_case else "",
            max_chars=6,
            placeholder="123456"
        )

    with col2:
        passport_issued_by = st.text_area(
            "Кем выдан паспорт",
            value=existing_case.get("passport_issued_by", "") if existing_case else "",
            placeholder="Отделением УФМС России по г. Москве"
        )

        if existing_case and existing_case.get("passport_issued_date"):
            passport_date_value = datetime.fromisoformat(existing_case["passport_issued_date"]).date() if isinstance(existing_case["passport_issued_date"], str) else existing_case["passport_issued_date"]
            passport_issued_date = st.date_input("Дата выдачи паспорта", value=passport_date_value, max_value=date.today())
        else:
            passport_issued_date = st.date_input("Дата выдачи паспорта", value=None, max_value=date.today())

    passport_code = st.text_input(
        "Код подразделения",
        value=existing_case.get("passport_code", "") if existing_case else "",
        max_chars=10,
        placeholder="770-001"
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 3: Documents - INN, SNILS (🆔 Документы)
    # ═══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("🆔 Раздел 3: Документы")

    col1, col2 = st.columns(2)

    with col1:
        inn = st.text_input(
            "ИНН",
            value=existing_case.get("inn", "") if existing_case else "",
            max_chars=12,
            placeholder="123456789012"
        )

    with col2:
        snils = st.text_input(
            "СНИЛС",
            value=existing_case.get("snils", "") if existing_case else "",
            max_chars=14,
            placeholder="123-456-789 00"
        )

    registration_address = st.text_area(
        "Адрес регистрации (по паспорту)",
        value=existing_case.get("registration_address", "") if existing_case else "",
        placeholder="г. Москва, ул. Ленина, д. 1, кв. 1"
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 4: Financial Data (💰 Финансовые данные)
    # ═══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("💰 Раздел 4: Финансовые данные")

    col1, col2 = st.columns(2)

    with col1:
        total_debt = st.number_input(
            "Общая сумма долга (руб.)",
            value=float(existing_case.get("total_debt", 0) or 0) if existing_case else 0.0,
            min_value=0.0,
            step=1000.0
        )

    with col2:
        monthly_income = st.number_input(
            "Ежемесячный доход (руб.)",
            value=float(existing_case.get("monthly_income", 0) or 0) if existing_case else 0.0,
            min_value=0.0,
            step=1000.0
        )

    notes = st.text_area(
        "Примечания",
        value=existing_case.get("notes", "") if existing_case else "",
        height=100
    )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 5: Court Data (⚖️ Данные для суда)
    # ═══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("⚖️ Раздел 5: Данные для суда")

    col1, col2 = st.columns(2)

    with col1:
        court_name = st.text_input(
            "Название арбитражного суда",
            value=existing_case.get("court_name", "") if existing_case else "",
            placeholder="Арбитражный суд города Москвы"
        )

        court_address = st.text_area(
            "Адрес арбитражного суда",
            value=existing_case.get("court_address", "") if existing_case else "",
            height=100,
            placeholder="г. Москва, ул. Большая Тульская, д. 17"
        )

        procedure_type_options = ["Property Realization", "Debt Restructuring"]
        if existing_case and existing_case.get("procedure_type") in procedure_type_options:
            procedure_index = procedure_type_options.index(existing_case.get("procedure_type"))
        else:
            procedure_index = 0
        procedure_type = st.selectbox(
            "Procedure Type *",
            options=procedure_type_options,
            index=procedure_index,
        )

    with col2:
        sro_name = st.text_input(
            "Название СРО арбитражных управляющих",
            value=existing_case.get("sro_name", "") if existing_case else "",
            placeholder="СРО 'Ассоциация антикризисных управляющих'"
        )

        sro_address = st.text_area(
            "Адрес СРО",
            value=existing_case.get("sro_address", "") if existing_case else "",
            height=100,
            placeholder="г. Москва, ул. Примерная, д. 1"
        )

    # ═══════════════════════════════════════════════════════════════
    # SECTION 6: Family - Spouse Data (👫 Данные о супруге)
    # ═══════════════════════════════════════════════════════════════
    st.divider()
    st.subheader("👫 Раздел 6: Данные о супруге")
    st.caption("Заполняется, если должник состоит или состоял в браке")

    col1, col2 = st.columns(2)

    with col1:
        spouse_name = st.text_input(
            "ФИО супруга/супруги",
            value=existing_case.get("spouse_name", "") if existing_case else "",
            placeholder="Иванова Мария Петровна"
        )

        marriage_certificate_number = st.text_input(
            "Номер свидетельства о браке",
            value=existing_case.get("marriage_certificate_number", "") if existing_case else "",
            placeholder="I-МЮ № 123456"
        )

        if existing_case and existing_case.get("marriage_certificate_date"):
            marriage_date_value = datetime.fromisoformat(existing_case["marriage_certificate_date"]).date() if isinstance(existing_case["marriage_certificate_date"], str) else existing_case["marriage_certificate_date"]
            marriage_certificate_date = st.date_input("Дата регистрации брака", value=marriage_date_value, max_value=date.today())
        else:
            marriage_certificate_date = st.date_input("Дата регистрации брака", value=None, max_value=date.today())

    with col2:
        st.write("**Если был развод:**")

        divorce_certificate_number = st.text_input(
            "Номер свидетельства о расторжении брака",
            value=existing_case.get("divorce_certificate_number", "") if existing_case else "",
            placeholder="I-МЮ № 654321"
        )

        if existing_case and existing_case.get("divorce_certificate_date"):
            divorce_date_value = datetime.fromisoformat(existing_case["divorce_certificate_date"]).date() if isinstance(existing_case["divorce_certificate_date"], str) else existing_case["divorce_certificate_date"]
            divorce_certificate_date = st.date_input("Дата расторжения брака", value=divorce_date_value, max_value=date.today())
        else:
            divorce_certificate_date = st.date_input("Дата расторжения брака", value=None, max_value=date.today())

    # Submit button at the end of main form
    st.divider()
    submitted = st.form_submit_button("💾 Сохранить основные данные" if existing_case else "➕ Создать дело", type="primary", use_container_width=True)

    if submitted:
        if not full_name:
            st.error("ФИО должника обязательно для заполнения")
        else:
            try:
                calculated_debt = total_debt
                if not existing_case and st.session_state.pending_creditors:
                    creditors_sum = sum(c.get("debt_amount", 0) for c in st.session_state.pending_creditors)
                    if total_debt == 0:
                        calculated_debt = creditors_sum

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
                    "procedure_type": procedure_type,
                    "sro_name": sro_name or None,
                    "sro_address": sro_address or None,
                    "notes": notes or None,
                    "spouse_name": spouse_name or None,
                    "marriage_certificate_number": marriage_certificate_number or None,
                    "marriage_certificate_date": marriage_certificate_date.isoformat() if marriage_certificate_date else None,
                    "divorce_certificate_number": divorce_certificate_number or None,
                    "divorce_certificate_date": divorce_certificate_date.isoformat() if divorce_certificate_date else None,
                }

                if existing_case:
                    data["telegram_user_id"] = telegram_user_id if telegram_user_id > 0 else None
                    response = httpx.put(f"{API_URL}/api/cases/{case_id}", json=data, timeout=30.0, headers=get_headers())
                    response.raise_for_status()
                    st.success("Дело обновлено!")
                else:
                    create_data = {
                        "full_name": full_name,
                        "total_debt": calculated_debt if calculated_debt > 0 else None,
                        "telegram_user_id": telegram_user_id if telegram_user_id > 0 else None,
                    }
                    response = httpx.post(f"{API_URL}/api/cases", json=create_data, timeout=30.0, headers=get_headers())
                    response.raise_for_status()
                    case = response.json()

                    response = httpx.put(f"{API_URL}/api/cases/{case['id']}", json=data, timeout=30.0, headers=get_headers())
                    response.raise_for_status()

                    # Add all pending items
                    for cred in st.session_state.pending_creditors:
                        add_creditor_to_api(case["id"], cred)
                    for child in st.session_state.pending_children:
                        add_child_to_api(case["id"], child)
                    for vehicle in st.session_state.pending_vehicles:
                        add_property_to_api(case["id"], vehicle)
                    for real_est in st.session_state.pending_real_estate:
                        add_property_to_api(case["id"], real_est)
                    for bank_acc in st.session_state.pending_bank_accounts:
                        add_transaction_to_api(case["id"], bank_acc)
                    for sec in st.session_state.pending_securities:
                        add_transaction_to_api(case["id"], sec)

                    # Recalculate debt
                    if st.session_state.pending_creditors:
                        creditors_total = sum(c.get("debt_amount", 0) for c in st.session_state.pending_creditors)
                        update_case_total_debt(case["id"], creditors_total)

                    st.success(f"Дело создано! Номер: {case['case_number']}")

                    # Clear pending and switch to edit mode
                    st.session_state.pending_creditors = []
                    st.session_state.pending_children = []
                    st.session_state.pending_vehicles = []
                    st.session_state.pending_real_estate = []
                    st.session_state.pending_bank_accounts = []
                    st.session_state.pending_securities = []
                    st.session_state.selected_case_id = case["id"]
                    st.rerun()

            except Exception as e:
                st.error(f"Ошибка: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: Children (👶 Дети)
# Outside main form - separate management
# ═══════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("👶 Раздел 7: Дети (иждивенцы)")

if existing_case:
    children = get_children_for_case(case_id)

    if children:
        st.write(f"**Детей:** {len(children)}")
        for idx, child in enumerate(children, 1):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{idx}. {child['child_name']}**")
                birth_str = format_date(child.get('child_birth_date'))
                doc_type = "Паспорт" if child.get('child_has_passport') else "Свид-во о рождении"
                st.caption(f"Дата рождения: {birth_str} | {doc_type}")
            with col2:
                if child.get('child_has_passport'):
                    st.caption(f"Паспорт: {child.get('child_passport_series', '')} {child.get('child_passport_number', '')}")
                else:
                    st.caption(f"Свид-во: {child.get('child_certificate_number', '—')}")
            with col3:
                if st.button("🗑️", key=f"del_child_{child['id']}", help="Удалить"):
                    success, error = delete_child_from_api(child["id"])
                    if success:
                        st.success("Ребёнок удалён")
                        st.rerun()
                    else:
                        st.error(error)
    else:
        st.info("Нет данных о детях")

    # Add child form
    st.write("---")
    st.write("**Добавить ребёнка:**")
    with st.form("add_child_existing", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            child_name = st.text_input("ФИО ребёнка *", placeholder="Иванов Петр Иванович")
            child_birth_date = st.date_input("Дата рождения *", value=None, max_value=date.today())
            child_has_passport = st.checkbox("Есть паспорт (14+ лет)")
        with col2:
            if not child_has_passport:
                child_certificate_number = st.text_input("Номер свидетельства о рождении", placeholder="I-МЮ № 123456")
                child_certificate_date = st.date_input("Дата выдачи свидетельства", value=None, max_value=date.today())
            else:
                child_passport_series = st.text_input("Серия паспорта", max_chars=4, placeholder="4510")
                child_passport_number = st.text_input("Номер паспорта", max_chars=6, placeholder="123456")

        if st.form_submit_button("➕ Добавить ребёнка"):
            if not child_name or not child_birth_date:
                st.error("Укажите ФИО и дату рождения")
            else:
                child_data = {
                    "child_name": child_name,
                    "child_birth_date": child_birth_date.isoformat(),
                    "child_has_passport": child_has_passport,
                    "child_has_certificate": not child_has_passport,
                }
                if child_has_passport:
                    child_data["child_passport_series"] = child_passport_series if 'child_passport_series' in dir() else None
                    child_data["child_passport_number"] = child_passport_number if 'child_passport_number' in dir() else None
                else:
                    child_data["child_certificate_number"] = child_certificate_number if 'child_certificate_number' in dir() else None
                    child_data["child_certificate_date"] = child_certificate_date.isoformat() if 'child_certificate_date' in dir() and child_certificate_date else None

                result, error = add_child_to_api(case_id, child_data)
                if result:
                    st.success(f"Ребёнок '{child_name}' добавлен")
                    st.rerun()
                else:
                    st.error(error)
else:
    # Pending children for new case
    if st.session_state.pending_children:
        st.write(f"**Детей добавлено:** {len(st.session_state.pending_children)}")
        for idx, child in enumerate(st.session_state.pending_children):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{idx + 1}. {child['child_name']}** — {child['child_birth_date']}")
            with col2:
                if st.button("🗑️", key=f"del_pending_child_{idx}"):
                    st.session_state.pending_children.pop(idx)
                    st.rerun()
        st.caption("Дети будут добавлены после создания дела")
    else:
        st.info("Добавьте детей ниже. Они будут сохранены вместе с делом.")

    with st.form("add_child_new", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            child_name = st.text_input("ФИО ребёнка *", placeholder="Иванов Петр Иванович", key="new_child_name")
            child_birth_date = st.date_input("Дата рождения *", value=None, max_value=date.today(), key="new_child_birth")
        with col2:
            child_has_passport = st.checkbox("Есть паспорт (14+ лет)", key="new_child_passport")
            child_certificate_number = st.text_input("Номер свид-ва/паспорта", key="new_child_doc")

        if st.form_submit_button("➕ Добавить в список"):
            if not child_name or not child_birth_date:
                st.error("Укажите ФИО и дату рождения")
            else:
                child_data = {
                    "child_name": child_name,
                    "child_birth_date": child_birth_date.isoformat(),
                    "child_has_passport": child_has_passport,
                    "child_has_certificate": not child_has_passport,
                    "child_certificate_number": child_certificate_number if not child_has_passport else None,
                    "child_passport_series": child_certificate_number[:4] if child_has_passport and len(child_certificate_number) >= 4 else None,
                    "child_passport_number": child_certificate_number[4:] if child_has_passport and len(child_certificate_number) > 4 else None,
                }
                st.session_state.pending_children.append(child_data)
                st.success(f"Ребёнок '{child_name}' добавлен в список")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: Movable Property - Vehicles (🚗 Транспортные средства)
# ═══════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("🚗 Раздел 8: Транспортные средства")

if existing_case:
    vehicles = get_properties_for_case(case_id, "vehicle")

    if vehicles:
        st.write(f"**Транспортных средств:** {len(vehicles)}")
        for idx, vehicle in enumerate(vehicles, 1):
            with st.expander(f"**{idx}. {vehicle.get('vehicle_make', '')} {vehicle.get('vehicle_model', '')}** ({vehicle.get('vehicle_year', '—')})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Марка:** {vehicle.get('vehicle_make', '—')}")
                    st.write(f"**Модель:** {vehicle.get('vehicle_model', '—')}")
                    st.write(f"**Год выпуска:** {vehicle.get('vehicle_year', '—')}")
                    st.write(f"**Цвет:** {vehicle.get('vehicle_color', '—')}")
                with col2:
                    st.write(f"**VIN:** {vehicle.get('vehicle_vin', '—')}")
                    st.write(f"**В залоге:** {'Да' if vehicle.get('is_pledged') else 'Нет'}")
                    if vehicle.get('is_pledged'):
                        st.write(f"**Залогодержатель:** {vehicle.get('pledge_creditor', '—')}")
                    st.write(f"**Описание:** {vehicle.get('description', '—')}")

                if st.button("🗑️ Удалить", key=f"del_vehicle_{vehicle['id']}"):
                    success, error = delete_property_from_api(vehicle["id"])
                    if success:
                        st.success("ТС удалено")
                        st.rerun()
                    else:
                        st.error(error)
    else:
        st.info("Нет данных о транспортных средствах")

    st.write("---")
    st.write("**Добавить транспортное средство:**")
    with st.form("add_vehicle_existing", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            v_make = st.text_input("Марка *", placeholder="Toyota")
            v_model = st.text_input("Модель *", placeholder="Camry")
            v_year = st.number_input("Год выпуска", min_value=1900, max_value=date.today().year, value=2020)
            v_color = st.text_input("Цвет", placeholder="Белый")
        with col2:
            v_vin = st.text_input("VIN номер", placeholder="JTDKN3DU5A0123456", max_chars=17)
            v_pledged = st.checkbox("В залоге")
            v_pledge_creditor = st.text_input("Залогодержатель", placeholder="ПАО Сбербанк")
            v_description = st.text_input("Описание", placeholder="Легковой автомобиль")

        if st.form_submit_button("➕ Добавить ТС"):
            if not v_make or not v_model:
                st.error("Укажите марку и модель")
            else:
                vehicle_data = {
                    "property_type": "vehicle",
                    "description": v_description or f"{v_make} {v_model}",
                    "vehicle_make": v_make,
                    "vehicle_model": v_model,
                    "vehicle_year": v_year,
                    "vehicle_vin": v_vin or None,
                    "vehicle_color": v_color or None,
                    "is_pledged": v_pledged,
                    "pledge_creditor": v_pledge_creditor if v_pledged else None,
                }
                result, error = add_property_to_api(case_id, vehicle_data)
                if result:
                    st.success(f"ТС '{v_make} {v_model}' добавлено")
                    st.rerun()
                else:
                    st.error(error)
else:
    if st.session_state.pending_vehicles:
        st.write(f"**ТС добавлено:** {len(st.session_state.pending_vehicles)}")
        for idx, v in enumerate(st.session_state.pending_vehicles):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{idx + 1}. {v.get('vehicle_make', '')} {v.get('vehicle_model', '')}** ({v.get('vehicle_year', '')})")
            with col2:
                if st.button("🗑️", key=f"del_pending_vehicle_{idx}"):
                    st.session_state.pending_vehicles.pop(idx)
                    st.rerun()
    else:
        st.info("Добавьте транспортные средства ниже.")

    with st.form("add_vehicle_new", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            v_make = st.text_input("Марка *", placeholder="Toyota", key="new_v_make")
            v_model = st.text_input("Модель *", placeholder="Camry", key="new_v_model")
            v_year = st.number_input("Год выпуска", min_value=1900, max_value=date.today().year, value=2020, key="new_v_year")
        with col2:
            v_vin = st.text_input("VIN номер", placeholder="JTDKN3DU5A0123456", key="new_v_vin")
            v_pledged = st.checkbox("В залоге", key="new_v_pledged")
            v_pledge_creditor = st.text_input("Залогодержатель", key="new_v_creditor")

        if st.form_submit_button("➕ Добавить в список"):
            if not v_make or not v_model:
                st.error("Укажите марку и модель")
            else:
                vehicle_data = {
                    "property_type": "vehicle",
                    "description": f"{v_make} {v_model}",
                    "vehicle_make": v_make,
                    "vehicle_model": v_model,
                    "vehicle_year": v_year,
                    "vehicle_vin": v_vin or None,
                    "is_pledged": v_pledged,
                    "pledge_creditor": v_pledge_creditor if v_pledged else None,
                }
                st.session_state.pending_vehicles.append(vehicle_data)
                st.success(f"ТС '{v_make} {v_model}' добавлено в список")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: Real Estate (🏠 Недвижимость)
# ═══════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("🏠 Раздел 9: Недвижимость")

if existing_case:
    real_estate = get_properties_for_case(case_id, "real_estate")

    if real_estate:
        st.write(f"**Объектов недвижимости:** {len(real_estate)}")
        for idx, prop in enumerate(real_estate, 1):
            with st.expander(f"**{idx}. {prop.get('description', 'Объект')}**"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Описание:** {prop.get('description', '—')}")
                    st.write(f"**В залоге:** {'Да' if prop.get('is_pledged') else 'Нет'}")
                with col2:
                    if prop.get('is_pledged'):
                        st.write(f"**Залогодержатель:** {prop.get('pledge_creditor', '—')}")
                        st.write(f"**Документ залога:** {prop.get('pledge_document', '—')}")

                if st.button("🗑️ Удалить", key=f"del_realestate_{prop['id']}"):
                    success, error = delete_property_from_api(prop["id"])
                    if success:
                        st.success("Объект удалён")
                        st.rerun()
                    else:
                        st.error(error)
    else:
        st.info("Нет данных о недвижимости")

    st.write("---")
    st.write("**Добавить объект недвижимости:**")
    with st.form("add_realestate_existing", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            re_type = st.selectbox("Тип объекта", options=list(real_estate_type_names.keys())[:-1], format_func=lambda x: real_estate_type_names[x])
            re_description = st.text_area("Описание *", placeholder="Квартира по адресу: г. Москва, ул. Ленина, д. 1, кв. 10, площадь 50 кв.м.")
        with col2:
            re_pledged = st.checkbox("В залоге (ипотека)")
            re_pledge_creditor = st.text_input("Залогодержатель", placeholder="ПАО Сбербанк")
            re_pledge_document = st.text_input("Документ о залоге", placeholder="Договор ипотеки № 123")

        if st.form_submit_button("➕ Добавить объект"):
            if not re_description:
                st.error("Укажите описание объекта")
            else:
                realestate_data = {
                    "property_type": "real_estate",
                    "description": re_description,
                    "is_pledged": re_pledged,
                    "pledge_creditor": re_pledge_creditor if re_pledged else None,
                    "pledge_document": re_pledge_document if re_pledged else None,
                }
                result, error = add_property_to_api(case_id, realestate_data)
                if result:
                    st.success("Объект недвижимости добавлен")
                    st.rerun()
                else:
                    st.error(error)
else:
    if st.session_state.pending_real_estate:
        st.write(f"**Объектов добавлено:** {len(st.session_state.pending_real_estate)}")
        for idx, prop in enumerate(st.session_state.pending_real_estate):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{idx + 1}. {prop.get('description', '')}**")
                if prop.get('is_pledged'):
                    st.caption(f"В залоге у: {prop.get('pledge_creditor', '—')}")
            with col2:
                if st.button("🗑️", key=f"del_pending_realestate_{idx}"):
                    st.session_state.pending_real_estate.pop(idx)
                    st.rerun()
    else:
        st.info("Добавьте объекты недвижимости ниже.")

    with st.form("add_realestate_new", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            re_description = st.text_area("Описание *", placeholder="Квартира по адресу...", key="new_re_desc")
        with col2:
            re_pledged = st.checkbox("В залоге (ипотека)", key="new_re_pledged")
            re_pledge_creditor = st.text_input("Залогодержатель", key="new_re_creditor")

        if st.form_submit_button("➕ Добавить в список"):
            if not re_description:
                st.error("Укажите описание объекта")
            else:
                realestate_data = {
                    "property_type": "real_estate",
                    "description": re_description,
                    "is_pledged": re_pledged,
                    "pledge_creditor": re_pledge_creditor if re_pledged else None,
                }
                st.session_state.pending_real_estate.append(realestate_data)
                st.success("Объект добавлен в список")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10: Bank Accounts (🏦 Банковские счета)
# ═══════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("🏦 Раздел 10: Банковские счета")
st.caption("Информация о счетах должника в банках")

if existing_case:
    # Bank accounts stored as transactions with type "bank_account"
    bank_accounts = get_transactions_for_case(case_id, "bank_account")

    if bank_accounts:
        st.write(f"**Счетов:** {len(bank_accounts)}")
        for idx, acc in enumerate(bank_accounts, 1):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{idx}. {acc.get('description', '—')}**")
            with col2:
                if acc.get('amount'):
                    st.write(f"Остаток: {format_money(acc.get('amount'))}")
            with col3:
                if st.button("🗑️", key=f"del_bank_{acc['id']}"):
                    success, error = delete_transaction_from_api(acc["id"])
                    if success:
                        st.success("Счёт удалён")
                        st.rerun()
                    else:
                        st.error(error)
    else:
        st.info("Нет данных о банковских счетах")

    st.write("---")
    st.write("**Добавить банковский счёт:**")
    with st.form("add_bank_existing", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            bank_name = st.text_input("Название банка *", placeholder="ПАО Сбербанк")
            bank_account_number = st.text_input("Номер счёта", placeholder="40817810000000000001")
        with col2:
            bank_balance = st.number_input("Остаток на счёте (руб.)", min_value=0.0, step=100.0)
            bank_currency = st.selectbox("Валюта", options=["RUB", "USD", "EUR"], format_func=lambda x: {"RUB": "Рубли", "USD": "Доллары", "EUR": "Евро"}[x])

        if st.form_submit_button("➕ Добавить счёт"):
            if not bank_name:
                st.error("Укажите название банка")
            else:
                account_desc = f"{bank_name}"
                if bank_account_number:
                    account_desc += f" (счёт {bank_account_number})"
                if bank_currency != "RUB":
                    account_desc += f" [{bank_currency}]"

                bank_data = {
                    "transaction_type": "bank_account",
                    "description": account_desc,
                    "amount": bank_balance if bank_balance > 0 else None,
                }
                result, error = add_transaction_to_api(case_id, bank_data)
                if result:
                    st.success(f"Счёт в {bank_name} добавлен")
                    st.rerun()
                else:
                    st.error(error)
else:
    if st.session_state.pending_bank_accounts:
        st.write(f"**Счетов добавлено:** {len(st.session_state.pending_bank_accounts)}")
        for idx, acc in enumerate(st.session_state.pending_bank_accounts):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{idx + 1}. {acc.get('description', '')}**")
            with col2:
                if st.button("🗑️", key=f"del_pending_bank_{idx}"):
                    st.session_state.pending_bank_accounts.pop(idx)
                    st.rerun()
    else:
        st.info("Добавьте банковские счета ниже.")

    with st.form("add_bank_new", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            bank_name = st.text_input("Название банка *", placeholder="ПАО Сбербанк", key="new_bank_name")
            bank_account_number = st.text_input("Номер счёта", key="new_bank_acc")
        with col2:
            bank_balance = st.number_input("Остаток (руб.)", min_value=0.0, step=100.0, key="new_bank_bal")

        if st.form_submit_button("➕ Добавить в список"):
            if not bank_name:
                st.error("Укажите название банка")
            else:
                account_desc = f"{bank_name}"
                if bank_account_number:
                    account_desc += f" (счёт {bank_account_number})"

                bank_data = {
                    "transaction_type": "bank_account",
                    "description": account_desc,
                    "amount": bank_balance if bank_balance > 0 else None,
                }
                st.session_state.pending_bank_accounts.append(bank_data)
                st.success(f"Счёт в {bank_name} добавлен в список")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 11: Securities & Valuables (💎 Ценные бумаги и ценности)
# ═══════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("💎 Раздел 11: Ценные бумаги и ценности")

if existing_case:
    securities = get_transactions_for_case(case_id, "securities")

    if securities:
        st.write(f"**Записей:** {len(securities)}")
        for idx, sec in enumerate(securities, 1):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{idx}. {sec.get('description', '—')}**")
            with col2:
                if sec.get('amount'):
                    st.write(f"Стоимость: {format_money(sec.get('amount'))}")
            with col3:
                if st.button("🗑️", key=f"del_sec_{sec['id']}"):
                    success, error = delete_transaction_from_api(sec["id"])
                    if success:
                        st.success("Запись удалена")
                        st.rerun()
                    else:
                        st.error(error)
    else:
        st.info("Нет данных о ценных бумагах и ценностях")

    st.write("---")
    st.write("**Добавить ценную бумагу/ценность:**")
    with st.form("add_securities_existing", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sec_type = st.selectbox("Тип", options=list(securities_type_names.keys())[:-1], format_func=lambda x: securities_type_names[x])
            sec_description = st.text_area("Описание *", placeholder="Акции ПАО Газпром, 100 шт.")
        with col2:
            sec_amount = st.number_input("Оценочная стоимость (руб.)", min_value=0.0, step=1000.0)
            sec_date = st.date_input("Дата приобретения", value=None, max_value=date.today())

        if st.form_submit_button("➕ Добавить"):
            if not sec_description:
                st.error("Укажите описание")
            else:
                sec_data = {
                    "transaction_type": "securities",
                    "description": f"[{securities_type_names[sec_type]}] {sec_description}",
                    "amount": sec_amount if sec_amount > 0 else None,
                    "transaction_date": sec_date.isoformat() if sec_date else None,
                }
                result, error = add_transaction_to_api(case_id, sec_data)
                if result:
                    st.success("Запись добавлена")
                    st.rerun()
                else:
                    st.error(error)
else:
    if st.session_state.pending_securities:
        st.write(f"**Записей добавлено:** {len(st.session_state.pending_securities)}")
        for idx, sec in enumerate(st.session_state.pending_securities):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{idx + 1}. {sec.get('description', '')}**")
                if sec.get('amount'):
                    st.caption(f"Стоимость: {format_money(sec.get('amount'))}")
            with col2:
                if st.button("🗑️", key=f"del_pending_sec_{idx}"):
                    st.session_state.pending_securities.pop(idx)
                    st.rerun()
    else:
        st.info("Добавьте ценные бумаги и ценности ниже.")

    with st.form("add_securities_new", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sec_type = st.selectbox("Тип", options=list(securities_type_names.keys())[:-1], format_func=lambda x: securities_type_names[x], key="new_sec_type")
            sec_description = st.text_area("Описание *", placeholder="Акции ПАО Газпром, 100 шт.", key="new_sec_desc")
        with col2:
            sec_amount = st.number_input("Оценочная стоимость (руб.)", min_value=0.0, step=1000.0, key="new_sec_amount")

        if st.form_submit_button("➕ Добавить в список"):
            if not sec_description:
                st.error("Укажите описание")
            else:
                sec_data = {
                    "transaction_type": "securities",
                    "description": f"[{securities_type_names[sec_type]}] {sec_description}",
                    "amount": sec_amount if sec_amount > 0 else None,
                }
                st.session_state.pending_securities.append(sec_data)
                st.success("Запись добавлена в список")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 12: Creditors (💳 Кредиторы) - Original section
# ═══════════════════════════════════════════════════════════════════════════════
st.divider()
st.subheader("💳 Раздел 12: Кредиторы")

if existing_case:
    creditors = get_creditors_for_case(case_id)

    if creditors:
        st.write(f"**Кредиторов:** {len(creditors)}")

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
                        remaining = [c for c in creditors if c["id"] != creditor["id"]]
                        new_total = sum(float(c.get("debt_amount") or 0) for c in remaining)
                        update_case_total_debt(case_id, new_total)
                        st.success("Кредитор удалён")
                        st.rerun()
                    else:
                        st.error(error)

        total_from_creditors = sum(float(c.get("debt_amount") or 0) for c in creditors)
        st.write(f"**Итого:** {format_money(total_from_creditors)}")
    else:
        st.info("У этого дела пока нет кредиторов")

    st.write("---")
    st.write("**Добавить кредитора:**")

    with st.form("add_creditor_existing", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            new_cred_name = st.text_input("Наименование *", placeholder="ПАО Сбербанк")
            new_cred_type = st.selectbox("Тип кредитора", options=["bank", "mfo", "individual", "tax", "other"], format_func=lambda x: creditor_type_names[x])
            new_cred_amount = st.number_input("Сумма долга *", min_value=0.0, step=1000.0, format="%.2f")

        with col2:
            new_cred_debt_type = st.selectbox("Тип долга", options=["credit", "microloan", "alimony", "tax", "utility", "other"], format_func=lambda x: debt_type_names[x])
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
                    updated_creditors = get_creditors_for_case(case_id)
                    new_total = sum(float(c.get("debt_amount") or 0) for c in updated_creditors)
                    update_case_total_debt(case_id, new_total)
                    st.success(f"Кредитор '{new_cred_name}' добавлен")
                    st.rerun()
                else:
                    st.error(error)

else:
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

        total_pending = sum(c.get("debt_amount", 0) for c in st.session_state.pending_creditors)
        st.write(f"**Итого:** {format_money(total_pending)}")
        st.caption("Кредиторы будут добавлены после создания дела")
    else:
        st.info("Добавьте кредиторов ниже. Они будут сохранены вместе с делом.")

    st.write("---")
    st.write("**Добавить кредитора:**")

    with st.form("add_creditor_new", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            new_cred_name = st.text_input("Наименование *", placeholder="ПАО Сбербанк", key="new_name")
            new_cred_type = st.selectbox("Тип кредитора", options=["bank", "mfo", "individual", "tax", "other"], format_func=lambda x: creditor_type_names[x], key="new_type")
            new_cred_amount = st.number_input("Сумма долга *", min_value=0.0, step=1000.0, format="%.2f", key="new_amount")

        with col2:
            new_cred_debt_type = st.selectbox("Тип долга", options=["credit", "microloan", "alimony", "tax", "utility", "other"], format_func=lambda x: debt_type_names[x], key="new_debt_type")
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


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 13: Documents (📄 Документы) - Download section
# ═══════════════════════════════════════════════════════════════════════════════
if existing_case:
    st.divider()
    st.subheader("📄 Раздел 13: Документы")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Скачать заявление о банкротстве (Полное)", use_container_width=True):
            try:
                response = httpx.get(
                    f"{API_URL}/api/documents/cases/{case_id}/document/petition",
                    timeout=60.0,
                    headers=get_headers(),
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
        if st.button("📥 Скачать заявление (Базовое)", use_container_width=True):
            try:
                response = httpx.get(
                    f"{API_URL}/api/documents/{case_id}/bankruptcy-application",
                    timeout=60.0,
                    headers=get_headers(),
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
