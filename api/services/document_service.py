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

PROCEDURE_TYPE_LABELS = {
    "Property Realization": "Property Realization",
    "Debt Restructuring": "Debt Restructuring",
}


def format_russian_date(date_obj) -> str:
    """Format date in Russian format: '01 января 2024'"""
    if not date_obj:
        return ""
    day = date_obj.day
    month = RUSSIAN_MONTHS.get(date_obj.month, "")
    year = date_obj.year
    return f"{day:02d} {month} {year}"


def format_money(amount: Decimal | float | None) -> tuple[int, int]:
    """Split money into rubles and kopeks. Returns: (rubles, kopeks)"""
    if amount is None:
        return (0, 0)
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    normalized = amount.quantize(Decimal("0.01"))
    rubles = int(normalized)
    kopeks = int((normalized - Decimal(rubles)) * 100)
    return (rubles, kopeks)


def rubles_declension(number: int) -> str:
    """Return proper declension: рубль/рубля/рублей"""
    if number % 10 == 1 and number % 100 != 11:
        return "рубль"
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return "рубля"
    else:
        return "рублей"


def kopecks_declension(number: int) -> str:
    """Return proper declension: копейка/копейки/копеек"""
    if number % 10 == 1 and number % 100 != 11:
        return "копейка"
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return "копейки"
    else:
        return "копеек"


def get_gender_pronoun(gender: str | None) -> str:
    """Return gender pronoun: он/она"""
    return "он" if gender == "M" else "она"


def format_full_name_with_initials(full_name: str) -> str:
    """Convert 'Иванов Иван Иванович' to 'Иванов И.И.'"""
    parts = full_name.strip().split()
    if len(parts) >= 2:
        last_name = parts[0]
        initials = ".".join([p[0].upper() for p in parts[1:]]) + "."
        return f"{last_name} {initials}"
    return full_name


def format_amount_with_words(rubles: int, kopecks: int) -> dict:
    """Format amount with proper Russian word declensions"""
    return {
        "amount_rubles": f"{rubles:,}".replace(",", " "),
        "amount_rubles_word": rubles_declension(rubles),
        "amount_kopecks": f"{kopecks:02d}",
        "amount_kopecks_word": kopecks_declension(kopecks)
    }

def get_procedure_type_context(case) -> dict:
    procedure_type = case.procedure_type or ""
    return {
        "procedure_type": procedure_type,
        "procedure_type_label": PROCEDURE_TYPE_LABELS.get(procedure_type, procedure_type),
    }

def format_total_debt(amount: Decimal | float | None) -> str:
    if amount is None:
        return "0"
    return f"{float(amount):,.0f}".replace(",", " ")


def generate_bankruptcy_petition(case) -> BytesIO:
    """
    Generate comprehensive bankruptcy petition from Case object.
    Uses the new comprehensive template with all fields.
    """
    template_path = TEMPLATES_DIR / "bankruptcy_petition_template.docx"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    doc = DocxTemplate(template_path)
    
    # === COURT INFORMATION ===
    court_name = case.court_name or "Арбитражный суд"
    court_address = case.court_address or ""
    
    # === DEBTOR PERSONAL DATA ===
    debtor_full_name = case.full_name
    debtor_surname = debtor_full_name.split()[0] if debtor_full_name else ""
    debtor_initials = format_full_name_with_initials(debtor_full_name).replace(debtor_surname, "").strip()
    
    birth_date = format_russian_date(case.birth_date)
    passport_date = format_russian_date(case.passport_issued_date)
    
    # === TOTAL DEBT ===
    total_rubles, total_kopecks = format_money(case.total_debt)
    total_debt_formatted = format_amount_with_words(total_rubles, total_kopecks)
    
    # === CREDITORS ===
    creditors_list = []
    for idx, creditor in enumerate(case.creditors, 1):
        creditors_list.append({
            "number": idx,
            "name": creditor.name,
            "ogrn": creditor.ogrn or "",
            "inn": creditor.inn or "",
            "address": creditor.address or ""
        })
    
    # === DEBTS ===
    debts_list = []
    for debt in case.debts:
        debt_formatted = format_amount_with_words(debt.amount_rubles, debt.amount_kopecks)
        debts_list.append({
            "number": debt.number or 1,
            "creditor_name": debt.creditor_name,
            **debt_formatted,
            "source": debt.source or "ОКБ"
        })
    
    # === MARITAL STATUS ===
    is_married = case.marital_status == "married"
    is_divorced = case.marital_status == "divorced"
    
    # === CHILDREN ===
    has_children = len(case.children) > 0
    multiple_children = len(case.children) > 1
    children_list = []
    for child in case.children:
        children_list.append({
            "child_name": child.child_name,
            "child_birth_date": format_russian_date(child.child_birth_date),
            "child_has_certificate": child.child_has_certificate,
            "child_certificate_number": child.child_certificate_number or "",
            "child_certificate_date": format_russian_date(child.child_certificate_date),
            "child_has_passport": child.child_has_passport,
            "child_passport_series": child.child_passport_series or "",
            "child_passport_number": child.child_passport_number or "",
            "child_passport_issued_by": child.child_passport_issued_by or "",
            "child_passport_date": format_russian_date(child.child_passport_date),
            "child_passport_code": child.child_passport_code or ""
        })
    
    # === INCOME ===
    income_years_list = []
    for income in case.income_records:
        income_formatted = format_amount_with_words(income.amount_rubles, income.amount_kopecks)
        income_years_list.append({
            "year": income.year,
            "amount": f"{income_formatted['amount_rubles']} рублей {income_formatted['amount_kopecks']} копеек",
            "amount_word": income_formatted["amount_rubles_word"],
            "certificate_number": income.certificate_number or ""
        })
    
    # === PROPERTY ===
    real_estate_list = [p for p in case.properties if p.property_type == "real_estate"]
    vehicles_list = [p for p in case.properties if p.property_type == "vehicle"]
    
    movable_property_description = ""
    if vehicles_list:
        vehicle = vehicles_list[0]
        movable_property_description = f"легковой автомобиль {vehicle.vehicle_make} {vehicle.vehicle_model} {vehicle.vehicle_year} года выпуска"
        if vehicle.vehicle_color:
            movable_property_description += f", {vehicle.vehicle_color} цвета"
        if vehicle.vehicle_vin:
            movable_property_description += f", VIN: {vehicle.vehicle_vin}"
    
    # === TRANSACTIONS ===
    trans_real_estate = [t for t in case.transactions if t.transaction_type == "real_estate"]
    trans_securities = [t for t in case.transactions if t.transaction_type == "securities"]
    trans_llc = [t for t in case.transactions if t.transaction_type == "llc_shares"]
    trans_vehicles = [t for t in case.transactions if t.transaction_type == "vehicles"]
    
    # === CREDITOR REGISTRY (for petition requests) ===
    creditor_registry = []
    for idx, creditor in enumerate(case.creditors, 1):
        rubles, kopecks = format_money(creditor.debt_amount)
        creditor_registry.append({
            "number": idx,
            "name": creditor.name,
            "amount": f"{rubles:,}".replace(",", " "),
            "kopecks": f"{kopecks:02d}"
        })
    
    # === BUILD CONTEXT ===
    context = {
        # Court
        "court_name": court_name,
        "court_address": court_address,
        
        # Debtor personal
        "debtor_full_name": debtor_full_name,
        "debtor_surname": debtor_surname,
        "debtor_initials": debtor_initials,
        "debtor_birth_date": birth_date,
        "debtor_passport_series": case.passport_series or "",
        "debtor_passport_number": case.passport_number or "",
        "debtor_passport_issued_by": case.passport_issued_by or "",
        "debtor_passport_date": passport_date,
        "debtor_passport_code": case.passport_code or "",
        "debtor_address": case.registration_address or "",
        "debtor_inn": case.inn or "",
        "debtor_snils": case.snils or "",
        "debtor_phone": case.phone or "",
        "debtor_gender_pronoun": get_gender_pronoun(case.gender),
        
        # IP Status
        "ip_certificate_number": case.ip_certificate_number or "",
        "ip_certificate_date": format_russian_date(case.ip_certificate_date),
        
        # Total debt
        "total_debt_rubles": total_debt_formatted["amount_rubles"],
        "total_debt_rubles_word": total_debt_formatted["amount_rubles_word"],
        "total_debt_kopecks": total_debt_formatted["amount_kopecks"],
        "total_debt_kopecks_word": total_debt_formatted["amount_kopecks_word"],
        
        # Creditors & Debts
        "creditors": creditors_list,
        "debts": debts_list,
        
        # Marital status
        "is_married": is_married,
        "is_divorced": is_divorced,
        "spouse_name": case.spouse_name or "",
        "marriage_certificate_number": case.marriage_certificate_number or "",
        "marriage_certificate_date": format_russian_date(case.marriage_certificate_date),
        "divorce_certificate_number": case.divorce_certificate_number or "",
        "divorce_certificate_date": format_russian_date(case.divorce_certificate_date),
        
        # Children
        "has_children": has_children,
        "multiple_children": multiple_children,
        "children": children_list,
        
        # Employment
        "is_employed": case.is_employed or False,
        "is_self_employed": case.is_self_employed or False,
        "income_years": income_years_list,
        
        # Property
        "has_real_estate": case.has_real_estate or False,
        "real_estate_description": "",
        "has_movable_property": case.has_movable_property or False,
        "movable_property_description": movable_property_description,
        "is_pledged": vehicles_list[0].is_pledged if vehicles_list else False,
        "property_type": "автомобиль",
        "pledge_creditor": vehicles_list[0].pledge_creditor if vehicles_list and vehicles_list[0].is_pledged else "",
        "pledge_document": vehicles_list[0].pledge_document if vehicles_list and vehicles_list[0].is_pledged else "",
        
        # Transactions
        "transactions_real_estate": trans_real_estate[0].description if trans_real_estate else False,
        "transactions_securities": trans_securities[0].description if trans_securities else False,
        "transactions_llc_shares": trans_llc[0].description if trans_llc else False,
        "transactions_vehicles": trans_vehicles[0].description if trans_vehicles else False,
        
        # Insolvency grounds
        "insolvency_grounds": case.insolvency_grounds or "гражданин прекратил расчеты с кредиторами",
        
        # Financial manager
        "sro_name": case.sro_name or "Ассоциация арбитражных управляющих",
        "restructuring_duration": case.restructuring_duration or "3 месяца",
        
        # Creditor registry
        "creditor_registry": creditor_registry,
        
        # Appendices (default list)
        "appendices": [
            {"number": 1, "description": "Копия паспорта гражданина РФ", "pages": 2},
            {"number": 2, "description": "Копия СНИЛС", "pages": 1},
            {"number": 3, "description": "Справка о неучастии в качестве ИП", "pages": 1},
            {"number": 4, "description": "Выписка из бюро кредитных историй", "pages": 10},
        ],
        
        # Date
        "petition_date": datetime.now().strftime("%d.%m.%Y"),
    }

    context.update(get_procedure_type_context(case))
    
    # Render template
    doc.render(context)
    
    # Save to BytesIO
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    return buffer


def generate_bankruptcy_application(case) -> BytesIO:
    """
    Generate basic bankruptcy application document from Case object.
    Uses the bankruptcy_application.docx template.
    """
    template_path = TEMPLATES_DIR / "bankruptcy_application.docx"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    doc = DocxTemplate(template_path)

    creditors_list = []
    for creditor in case.creditors:
        creditors_list.append(
            {
                "name": creditor.name,
                "debt_amount": format_total_debt(creditor.debt_amount),
                "debt_type": creditor.debt_type or "",
            }
        )

    passport_parts = [part for part in [case.passport_series, case.passport_number] if part]
    passport_value = " ".join(passport_parts)

    context = {
        "case_number": case.case_number,
        "full_name": case.full_name,
        "birth_date": format_russian_date(case.birth_date),
        "passport": passport_value,
        "inn": case.inn or "",
        "address": case.registration_address or "",
        "total_debt": format_total_debt(case.total_debt),
        "creditors_count": len(case.creditors),
        "creditors": creditors_list,
        "current_date": datetime.now().strftime("%d.%m.%Y"),
    }

    context.update(get_procedure_type_context(case))

    doc.render(context)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
