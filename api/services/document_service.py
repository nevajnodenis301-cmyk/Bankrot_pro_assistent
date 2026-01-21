from io import BytesIO
from docxtpl import DocxTemplate
from datetime import datetime
from pathlib import Path
from decimal import Decimal

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Russian month names in genitive case
RUSSIAN_MONTHS = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}


def format_russian_date(date_obj) -> str:
    """Format date in Russian format: '01 января 2024'"""
    if not date_obj:
        return "отсутствует"
    day = date_obj.day
    month = RUSSIAN_MONTHS.get(date_obj.month, "")
    year = date_obj.year
    return f"{day:02d} {month} {year}"


def format_money(amount: Decimal | float | None) -> tuple[int, int]:
    """
    Split money into rubles and kopeks.
    Returns: (rubles, kopeks)
    """
    if amount is None:
        return (0, 0)

    if isinstance(amount, Decimal):
        amount = float(amount)

    rubles = int(amount)
    kopeks = int(round((amount - rubles) * 100))

    return (rubles, kopeks)


def get_gender_word(gender: str | None, male_form: str, female_form: str) -> str:
    """Return word form based on gender"""
    if gender == "M":
        return male_form
    elif gender == "F":
        return female_form
    else:
        # Default to male form if gender is not specified
        return male_form


def format_full_name_with_initials(full_name: str) -> str:
    """
    Convert 'Иванов Иван Иванович' to 'Иванов И.И.'
    """
    parts = full_name.strip().split()
    if len(parts) >= 2:
        last_name = parts[0]
        initials = ".".join([p[0].upper() for p in parts[1:]]) + "."
        return f"{last_name} {initials}"
    return full_name


def format_creditors_block(creditors: list) -> str:
    """Format creditors list for document"""
    if not creditors:
        return "Кредиторы не указаны"

    lines = []
    for idx, creditor in enumerate(creditors, 1):
        name = creditor.name
        debt = creditor.debt_amount if creditor.debt_amount else Decimal(0)
        debt_str = f"{debt:,.2f}".replace(",", " ")

        line = f"{idx}. {name} - {debt_str} руб."
        if creditor.debt_type:
            line += f" ({creditor.debt_type})"
        lines.append(line)

    return "\n".join(lines)


def format_creditors_header_block(creditors: list) -> str:
    """Format creditors list for header section"""
    if not creditors:
        return ""

    lines = []
    for creditor in creditors[:3]:  # Show only first 3 creditors in header
        lines.append(creditor.name)

    if len(creditors) > 3:
        lines.append(f"и др. (всего {len(creditors)})")

    return ", ".join(lines)


def format_family_status(marital_status: str | None, gender: str | None) -> str:
    """Format marital status text"""
    if not marital_status:
        return "семейное положение не указано"

    status_map = {
        "single": ("холост", "не замужем"),
        "married": ("женат", "замужем"),
        "divorced": ("разведен", "разведена"),
        "widowed": ("вдовец", "вдова")
    }

    if marital_status in status_map:
        male_form, female_form = status_map[marital_status]
        return get_gender_word(gender, male_form, female_form)

    return marital_status


def generate_bankruptcy_petition(case) -> BytesIO:
    """
    Generate bankruptcy petition document from Case object.

    Args:
        case: Case object with creditors relationship loaded

    Returns:
        BytesIO: Generated document
    """
    template_path = TEMPLATES_DIR / "bankruptcy_application.docx"
    doc = DocxTemplate(template_path)

    # Get gender for word declension
    gender = case.gender

    # Format dates
    birth_date_formatted = format_russian_date(case.birth_date)
    passport_date_formatted = format_russian_date(case.passport_issued_date)
    current_date_formatted = format_russian_date(datetime.now().date())

    # Format money
    total_rubles, total_kopeks = format_money(case.total_debt)

    # Format creditors
    creditors_block = format_creditors_block(case.creditors)
    creditors_header = format_creditors_header_block(case.creditors)

    # Prepare context for template
    context = {
        # Court information
        "court_name": case.court_name or "___________________________",
        "court_address": case.court_address or "___________________________",

        # Debtor information
        "debtor_full_name": case.full_name,
        "debtor_last_name_initials": format_full_name_with_initials(case.full_name),
        "debtor_birth_date": birth_date_formatted,
        "debtor_address": case.registration_address or "адрес не указан",
        "debtor_phone_or_absent": case.phone or "отсутствует",
        "debtor_inn": case.inn or "____________",
        "debtor_inn_or_absent": case.inn or "отсутствует",
        "debtor_snils": case.snils or "___-___-___ __",
        "debtor_snils_or_absent": case.snils or "отсутствует",

        # Passport information
        "passport_series": case.passport_series or "____",
        "passport_number": case.passport_number or "______",
        "passport_issued_by": case.passport_issued_by or "___________________________",
        "passport_date": passport_date_formatted,
        "passport_code": case.passport_code or "___-___",

        # Gender-dependent words (male/female forms)
        "debtor_having_word": get_gender_word(gender, "имеющий", "имеющая"),
        "debtor_registered_word": get_gender_word(gender, "зарегистрированный", "зарегистрированная"),
        "debtor_living_word": get_gender_word(gender, "проживающий", "проживающая"),
        "debtor_not_registered_word": get_gender_word(gender, "не зарегистрирован", "не зарегистрирована"),
        "debtor_insolvent_word": get_gender_word(gender, "несостоятельным", "несостоятельной"),

        # Financial information
        "total_debt_rubles": total_rubles,
        "total_debt_kopeks": total_kopeks,

        # Creditors
        "creditors_block": creditors_block,
        "creditors_header_block": creditors_header,

        # Family status
        "family_status_block": format_family_status(case.marital_status, gender),

        # Vehicle block (default: no vehicles)
        "vehicle_block": "Транспортных средств не имею",

        # Financial manager information
        "financial_manager_info": f"{case.sro_name or 'СРО не указано'}, {case.sro_address or 'адрес не указан'}",

        # Deposit deferral request
        "deposit_deferral_request": "Прошу предоставить отсрочку уплаты государственной пошлины в соответствии со ст. 333.41 НК РФ.",

        # Attachments list
        "attachments_list": """1. Копия паспорта гражданина РФ
2. Копия СНИЛС
3. Копия ИНН
4. Выписка из ЕГРН о правах на недвижимое имущество
5. Документы, подтверждающие задолженность перед кредиторами
6. Справка о доходах
7. Опись имущества должника""",

        # Current date
        "date": current_date_formatted,

        # Case number
        "case_number": case.case_number,
    }

    # Render template
    doc.render(context)

    # Save to BytesIO
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# Legacy function for backwards compatibility
def generate_bankruptcy_application(case_data: dict) -> bytes:
    """
    Legacy function for generating bankruptcy application document.
    This is kept for backwards compatibility but should be deprecated.
    Use generate_bankruptcy_petition() instead.
    """
    template_path = TEMPLATES_DIR / "bankruptcy_application.docx"
    doc = DocxTemplate(template_path)

    context = {
        "case_number": case_data["case_number"],
        "full_name": case_data["full_name"],
        "birth_date": case_data.get("birth_date", "___________"),
        "passport": f"{case_data.get('passport_series', '____')} {case_data.get('passport_number', '______')}",
        "inn": case_data.get("inn", "____________"),
        "address": case_data.get("registration_address", "_________________________"),
        "total_debt": f"{case_data.get('total_debt', 0):,.2f}".replace(",", " "),
        "creditors": case_data.get("creditors", []),
        "creditors_count": len(case_data.get("creditors", [])),
        "current_date": datetime.now().strftime("%d.%m.%Y"),
    }

    doc.render(context)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
