import streamlit as st
import httpx
import os
from datetime import datetime, date

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN")
DEFAULT_HEADERS = {"X-API-Token": API_TOKEN} if API_TOKEN else {}

st.set_page_config(page_title="Кредиторы", page_icon="💳", layout="wide")
st.title("💳 Управление кредиторами")


def format_money(amount):
    """Format monetary amount with thousand separators"""
    if amount is None:
        return "—"
    return f"{float(amount):,.2f}".replace(",", " ").replace(".", ",") + " руб."


@st.cache_data(ttl=30)
def get_cases():
    """Fetch all cases from API"""
    try:
        response = httpx.get(f"{API_URL}/api/cases", headers=DEFAULT_HEADERS, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Ошибка при загрузке дел: {str(e)}")
        return []


def get_creditors(case_id: int):
    """Fetch creditors for a specific case"""
    try:
        response = httpx.get(
            f"{API_URL}/api/creditors/{case_id}",
            headers=DEFAULT_HEADERS,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Ошибка при загрузке кредиторов: {str(e)}")
        return []


def add_creditor(case_id: int, creditor_data: dict):
    """Add a new creditor to the case"""
    try:
        response = httpx.post(
            f"{API_URL}/api/creditors/{case_id}",
            json=creditor_data,
            headers=DEFAULT_HEADERS,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Ошибка сервера: {e.response.status_code}"
    except Exception as e:
        return None, f"Ошибка при добавлении кредитора: {str(e)}"


def delete_creditor(creditor_id: int):
    """Delete a creditor"""
    try:
        response = httpx.delete(
            f"{API_URL}/api/creditors/{creditor_id}",
            headers=DEFAULT_HEADERS,
            timeout=30.0
        )
        response.raise_for_status()
        return True, None
    except httpx.HTTPStatusError as e:
        return False, f"Ошибка сервера: {e.response.status_code}"
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
        return True, None
    except Exception as e:
        return False, f"Ошибка при обновлении суммы долга: {str(e)}"


# Get all cases
cases = get_cases()

if not cases:
    st.info("Нет дел. Сначала создайте дело в разделе '➕ Новое дело'")
    st.stop()

# Case selector
case_options = {c["id"]: f"{c['case_number']} — {c['full_name']}" for c in cases}
selected_case_id = st.selectbox(
    "Выберите дело",
    options=list(case_options.keys()),
    format_func=lambda x: case_options[x],
    help="Выберите дело для управления кредиторами"
)

# Get selected case details
selected_case = next((c for c in cases if c["id"] == selected_case_id), None)

if selected_case:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Номер дела", selected_case["case_number"])
    with col2:
        current_debt = selected_case.get("total_debt") or 0
        st.metric("Общий долг", format_money(current_debt))
    with col3:
        st.metric("Кредиторов", selected_case.get("creditors_count", 0))

st.divider()

# Refresh button
col_refresh, col_spacer = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 Обновить данные"):
        st.cache_data.clear()
        st.rerun()

# Get creditors for selected case
creditors = get_creditors(selected_case_id)

# Display creditors table
st.subheader("📋 Список кредиторов")

if creditors:
    # Creditor type mapping
    creditor_type_names = {
        "bank": "Банк",
        "mfo": "МФО",
        "individual": "Физическое лицо",
        "tax": "Налоговая",
        "other": "Другое",
        None: "—"
    }

    # Debt type mapping
    debt_type_names = {
        "credit": "Кредит",
        "microloan": "Микрозайм",
        "alimony": "Алименты",
        "tax": "Налоги",
        "utility": "ЖКХ",
        "other": "Другое",
        None: "—"
    }

    # Calculate total from creditors
    total_from_creditors = sum(float(c.get("debt_amount") or 0) for c in creditors)

    # Display each creditor
    for idx, creditor in enumerate(creditors, 1):
        with st.expander(
            f"**{idx}. {creditor['name']}** — {format_money(creditor.get('debt_amount'))}",
            expanded=False
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Тип кредитора:** {creditor_type_names.get(creditor.get('creditor_type'), '—')}")
                st.write(f"**Тип долга:** {debt_type_names.get(creditor.get('debt_type'), '—')}")
                st.write(f"**Сумма долга:** {format_money(creditor.get('debt_amount'))}")

            with col2:
                st.write(f"**Номер договора:** {creditor.get('contract_number') or '—'}")
                contract_date = creditor.get("contract_date")
                if contract_date:
                    try:
                        if isinstance(contract_date, str):
                            dt = datetime.fromisoformat(contract_date)
                            contract_date = dt.strftime("%d.%m.%Y")
                    except:
                        pass
                st.write(f"**Дата договора:** {contract_date or '—'}")
                st.write(f"**ID:** {creditor['id']}")

            # Delete button
            if st.button(
                "🗑️ Удалить кредитора",
                key=f"delete_{creditor['id']}",
                type="secondary"
            ):
                success, error = delete_creditor(creditor["id"])
                if success:
                    # Recalculate total debt
                    new_total = total_from_creditors - float(creditor.get("debt_amount") or 0)
                    update_case_total_debt(selected_case_id, new_total)
                    st.success("Кредитор удалён")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(error)

    # Summary
    st.divider()
    st.write(f"**Итого по кредиторам:** {format_money(total_from_creditors)}")

    # Button to sync total_debt with creditors sum
    if abs(float(selected_case.get("total_debt") or 0) - total_from_creditors) > 0.01:
        st.warning(
            f"Сумма долга в деле ({format_money(selected_case.get('total_debt'))}) "
            f"отличается от суммы по кредиторам ({format_money(total_from_creditors)})"
        )
        if st.button("🔄 Синхронизировать сумму долга"):
            success, error = update_case_total_debt(selected_case_id, total_from_creditors)
            if success:
                st.success("Сумма долга обновлена")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(error)
else:
    st.info("У этого дела пока нет кредиторов. Добавьте первого кредитора ниже.")

# Add new creditor form
st.divider()
st.subheader("➕ Добавить кредитора")

with st.form("add_creditor_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input(
            "Наименование кредитора *",
            placeholder="ПАО Сбербанк",
            help="Полное наименование кредитора"
        )

        creditor_type = st.selectbox(
            "Тип кредитора",
            options=["bank", "mfo", "individual", "tax", "other"],
            format_func=lambda x: {
                "bank": "Банк",
                "mfo": "МФО",
                "individual": "Физическое лицо",
                "tax": "Налоговая",
                "other": "Другое"
            }[x],
            help="Категория кредитора"
        )

        debt_amount = st.number_input(
            "Сумма долга (в рублях) *",
            min_value=0.0,
            step=1000.0,
            format="%.2f",
            help="Сумма задолженности перед кредитором"
        )

    with col2:
        debt_type = st.selectbox(
            "Тип долга",
            options=["credit", "microloan", "alimony", "tax", "utility", "other"],
            format_func=lambda x: {
                "credit": "Кредит",
                "microloan": "Микрозайм",
                "alimony": "Алименты",
                "tax": "Налоги",
                "utility": "ЖКХ",
                "other": "Другое"
            }[x],
            help="Тип задолженности"
        )

        contract_number = st.text_input(
            "Номер договора",
            placeholder="1234567890",
            help="Номер кредитного договора или иного документа"
        )

        contract_date = st.date_input(
            "Дата договора",
            value=None,
            max_value=date.today(),
            help="Дата заключения договора"
        )

    submitted = st.form_submit_button("➕ Добавить кредитора", type="primary")

    if submitted:
        if not name:
            st.error("Укажите наименование кредитора")
        elif debt_amount <= 0:
            st.error("Укажите сумму долга больше нуля")
        else:
            creditor_data = {
                "name": name,
                "creditor_type": creditor_type,
                "debt_amount": debt_amount,
                "debt_type": debt_type,
                "contract_number": contract_number or None,
                "contract_date": contract_date.isoformat() if contract_date else None
            }

            new_creditor, error = add_creditor(selected_case_id, creditor_data)

            if new_creditor:
                # Recalculate and update total debt
                current_creditors = get_creditors(selected_case_id)
                new_total = sum(float(c.get("debt_amount") or 0) for c in current_creditors)
                update_case_total_debt(selected_case_id, new_total)

                st.success(f"Кредитор '{name}' добавлен")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(error)
