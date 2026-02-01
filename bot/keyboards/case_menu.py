from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_case_detail_menu(case_id: int, case_number: str) -> InlineKeyboardMarkup:
    """
    Main menu when viewing a case.
    Shows 8 sections + document options.
    """
    keyboard = [
        [InlineKeyboardButton(text="👤 Данные клиента", callback_data=f"case:{case_id}:client")],
        [InlineKeyboardButton(text="💰 Кредиторы", callback_data=f"case:{case_id}:creditors")],
        [InlineKeyboardButton(text="📊 Задолженность", callback_data=f"case:{case_id}:debts")],
        [InlineKeyboardButton(text="👨‍👩‍👧 Семья", callback_data=f"case:{case_id}:family")],
        [InlineKeyboardButton(text="💼 Занятость", callback_data=f"case:{case_id}:employment")],
        [InlineKeyboardButton(text="🏠 Имущество", callback_data=f"case:{case_id}:property")],
        [InlineKeyboardButton(text="📝 Сделки (3 года)", callback_data=f"case:{case_id}:transactions")],
        [InlineKeyboardButton(text="⚖️ Суд и СРО", callback_data=f"case:{case_id}:court")],
        [
            InlineKeyboardButton(text="📄 Создать документ", callback_data=f"doc_{case_id}"),
            InlineKeyboardButton(text="📂 Документы дела", callback_data=f"case:{case_number}:documents"),
        ],
        [InlineKeyboardButton(text="◀️ Назад к списку", callback_data="back_to_list")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_client_data_menu(case_id: int) -> InlineKeyboardMarkup:
    """
    Menu for client data section.
    Options: view data, edit passport, edit address, edit INN/SNILS.
    """
    keyboard = [
        [InlineKeyboardButton(text="👁 Просмотр данных", callback_data=f"client:{case_id}:view")],
        [InlineKeyboardButton(text="✏️ Паспорт", callback_data=f"client:{case_id}:edit_passport")],
        [InlineKeyboardButton(text="✏️ Адрес и телефон", callback_data=f"client:{case_id}:edit_address")],
        [InlineKeyboardButton(text="✏️ ИНН и СНИЛС", callback_data=f"client:{case_id}:edit_inn_snils")],
        [InlineKeyboardButton(text="✏️ Дата рождения", callback_data=f"client:{case_id}:edit_birth")],
        [InlineKeyboardButton(text="✏️ Пол", callback_data=f"client:{case_id}:edit_gender")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"case_{case_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_client_menu(case_id: int) -> InlineKeyboardMarkup:
    """Simple back button to client data menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"client:{case_id}:menu")]
    ])


def get_passport_edit_menu(case_id: int) -> InlineKeyboardMarkup:
    """Menu for passport editing options"""
    keyboard = [
        [InlineKeyboardButton(text="📝 Серия паспорта", callback_data=f"passport:{case_id}:series")],
        [InlineKeyboardButton(text="📝 Номер паспорта", callback_data=f"passport:{case_id}:number")],
        [InlineKeyboardButton(text="📝 Кем выдан", callback_data=f"passport:{case_id}:issued_by")],
        [InlineKeyboardButton(text="📝 Дата выдачи", callback_data=f"passport:{case_id}:date")],
        [InlineKeyboardButton(text="📝 Код подразделения", callback_data=f"passport:{case_id}:code")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"client:{case_id}:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_address_edit_menu(case_id: int) -> InlineKeyboardMarkup:
    """Menu for address and phone editing options"""
    keyboard = [
        [InlineKeyboardButton(text="📝 Адрес регистрации", callback_data=f"address:{case_id}:registration")],
        [InlineKeyboardButton(text="📝 Телефон", callback_data=f"address:{case_id}:phone")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"client:{case_id}:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_edit_keyboard(case_id: int) -> InlineKeyboardMarkup:
    """Cancel button during editing"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"client:{case_id}:menu")]
    ])


def get_gender_selection_keyboard(case_id: int) -> InlineKeyboardMarkup:
    """Keyboard for gender selection"""
    keyboard = [
        [
            InlineKeyboardButton(text="👨 Мужской", callback_data=f"gender:{case_id}:M"),
            InlineKeyboardButton(text="👩 Женский", callback_data=f"gender:{case_id}:F"),
        ],
        [InlineKeyboardButton(text="◀️ Отмена", callback_data=f"client:{case_id}:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# === Creditors Management Keyboards ===

def get_creditors_menu(case_id: int, case_number: str, creditors_count: int = 0) -> InlineKeyboardMarkup:
    """Creditors management menu"""
    keyboard = [
        [InlineKeyboardButton(
            text=f"➕ Добавить кредитора (всего: {creditors_count})",
            callback_data=f"creditors:{case_id}:add"
        )],
    ]

    if creditors_count > 0:
        keyboard.extend([
            [InlineKeyboardButton(text="📋 Список кредиторов", callback_data=f"creditors:{case_id}:list")],
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"creditors:{case_id}:edit")],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"creditors:{case_id}:delete")],
        ])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"case_{case_id}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_creditor_selection_keyboard(creditors: list, action: str, case_id: int) -> InlineKeyboardMarkup:
    """
    Show list of creditors for selection (for edit/delete).

    Args:
        creditors: List of creditor dicts with 'id' and 'name'
        action: 'edit' or 'delete'
        case_id: Case ID for back button
    """
    keyboard = []

    for creditor in creditors:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{creditor['name'][:40]}",
                callback_data=f"creditor:{action}:{creditor['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data=f"creditors:{case_id}:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_creditor_edit_menu(creditor_id: int, case_id: int) -> InlineKeyboardMarkup:
    """Menu for editing creditor fields"""
    keyboard = [
        [InlineKeyboardButton(text="📝 Название", callback_data=f"crededit:{creditor_id}:name")],
        [InlineKeyboardButton(text="📝 ОГРН", callback_data=f"crededit:{creditor_id}:ogrn")],
        [InlineKeyboardButton(text="📝 ИНН", callback_data=f"crededit:{creditor_id}:inn")],
        [InlineKeyboardButton(text="📝 Адрес", callback_data=f"crededit:{creditor_id}:address")],
        [InlineKeyboardButton(text="📝 Сумма долга", callback_data=f"crededit:{creditor_id}:debt")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"creditors:{case_id}:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# === Debts Management Keyboards ===

def get_debts_menu(case_id: int, case_number: str, debts_count: int = 0, total_debt: float = 0) -> InlineKeyboardMarkup:
    """Debts management menu"""
    total_formatted = f"{total_debt:,.0f} ₽".replace(",", " ") if total_debt else "0 ₽"

    keyboard = [
        [InlineKeyboardButton(
            text=f"➕ Добавить задолженность (всего: {debts_count})",
            callback_data=f"debts:{case_id}:add"
        )],
        [InlineKeyboardButton(
            text=f"💰 Общий долг: {total_formatted}",
            callback_data="noop"
        )],
    ]

    if debts_count > 0:
        keyboard.extend([
            [InlineKeyboardButton(text="📋 Список задолженностей", callback_data=f"debts:{case_id}:list")],
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"debts:{case_id}:edit")],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"debts:{case_id}:delete")],
        ])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"case_{case_id}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_debt_selection_keyboard(debts: list, action: str, case_id: int) -> InlineKeyboardMarkup:
    """Show list of debts for selection"""
    keyboard = []

    for debt in debts:
        amount = debt.get('amount_rubles', 0)
        creditor = debt.get('creditor_name', 'Неизвестно')
        amount_formatted = f"{amount:,}".replace(",", " ")
        keyboard.append([
            InlineKeyboardButton(
                text=f"{creditor[:20]}: {amount_formatted} ₽",
                callback_data=f"debt:{action}:{debt['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data=f"debts:{case_id}:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_creditor_for_debt_keyboard(creditors: list, case_id: int) -> InlineKeyboardMarkup:
    """Show list of creditors for selecting when adding debt"""
    keyboard = []

    for creditor in creditors:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{creditor['name'][:40]}",
                callback_data=f"debtcred:{creditor['id']}"
            )
        ])

    # Option to enter creditor name manually
    keyboard.append([InlineKeyboardButton(text="✍️ Ввести вручную", callback_data="debtcred:manual")])
    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data=f"debts:{case_id}:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_debt_edit_menu(debt_id: int, case_id: int) -> InlineKeyboardMarkup:
    """Menu for editing debt fields"""
    keyboard = [
        [InlineKeyboardButton(text="📝 Кредитор", callback_data=f"debtedit:{debt_id}:creditor")],
        [InlineKeyboardButton(text="📝 Сумма (рубли)", callback_data=f"debtedit:{debt_id}:rubles")],
        [InlineKeyboardButton(text="📝 Сумма (копейки)", callback_data=f"debtedit:{debt_id}:kopecks")],
        [InlineKeyboardButton(text="📝 Источник", callback_data=f"debtedit:{debt_id}:source")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"debts:{case_id}:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_delete_keyboard(item_type: str, item_id: int, case_id: int) -> InlineKeyboardMarkup:
    """Confirmation keyboard for deletion"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"{item_type}:delete:confirm:{item_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"{item_type}s:{case_id}:menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ==================== GROUP 1: FAMILY KEYBOARDS ====================

def get_family_menu(case_id: int, case_number: str, case_data: dict) -> InlineKeyboardMarkup:
    """Family data menu showing current status"""
    marital_status = case_data.get('marital_status')
    children = case_data.get('children', [])
    children_count = len(children) if isinstance(children, list) else 0

    status_text = {
        "married": "В браке",
        "divorced": "Разведен(а)",
        "single": "Не женат/не замужем",
        "never_married": "Никогда не состоял(а) в браке"
    }.get(marital_status, "Не указано")

    keyboard = [
        [InlineKeyboardButton(
            text=f"💍 Семейное положение: {status_text}",
            callback_data=f"family:{case_id}:edit_status"
        )],
    ]

    # Show spouse option if married or divorced
    if marital_status in ["married", "divorced"]:
        spouse_name = case_data.get('spouse_name', 'не указано')
        spouse_display = spouse_name[:20] if spouse_name else 'не указано'
        keyboard.append([InlineKeyboardButton(
            text=f"👥 Супруг(а): {spouse_display}",
            callback_data=f"family:{case_id}:spouse"
        )])

    keyboard.extend([
        [InlineKeyboardButton(
            text=f"👶 Дети ({children_count})",
            callback_data=f"family:{case_id}:children"
        )],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"case_{case_id}")]
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_marital_status_keyboard(case_id: int) -> InlineKeyboardMarkup:
    """Select marital status"""
    keyboard = [
        [InlineKeyboardButton(text="💑 В браке", callback_data=f"family:status:married:{case_id}")],
        [InlineKeyboardButton(text="💔 Разведен(а)", callback_data=f"family:status:divorced:{case_id}")],
        [InlineKeyboardButton(text="🙂 Не женат/не замужем", callback_data=f"family:status:single:{case_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"family:{case_id}:menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_children_menu(case_id: int, case_number: str, children: list) -> InlineKeyboardMarkup:
    """Children management menu"""
    keyboard = [
        [InlineKeyboardButton(
            text=f"➕ Добавить ребенка (всего: {len(children)})",
            callback_data=f"children:{case_id}:add"
        )]
    ]

    if children:
        keyboard.extend([
            [InlineKeyboardButton(text="📋 Список детей", callback_data=f"children:{case_id}:list")],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"children:{case_id}:delete")]
        ])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"family:{case_id}:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_child_document_type_keyboard(case_id: int) -> InlineKeyboardMarkup:
    """Choose document type for child"""
    keyboard = [
        [InlineKeyboardButton(
            text="📄 Свидетельство о рождении (до 14 лет)",
            callback_data=f"child_doc:{case_id}:birth_certificate"
        )],
        [InlineKeyboardButton(
            text="🛂 Паспорт РФ (14+ лет)",
            callback_data=f"child_doc:{case_id}:passport"
        )],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"children:{case_id}:menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_children_list_keyboard(children: list, case_id: int) -> InlineKeyboardMarkup:
    """List children for deletion"""
    keyboard = []

    for child in children:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑 {child['child_name'][:30]}",
                callback_data=f"child:delete:{child['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data=f"children:{case_id}:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_family_menu(case_id: int) -> InlineKeyboardMarkup:
    """Simple back button to family menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"family:{case_id}:menu")]
    ])


def get_back_to_children_menu(case_id: int) -> InlineKeyboardMarkup:
    """Simple back button to children menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"children:{case_id}:menu")]
    ])


# ==================== GROUP 1: EMPLOYMENT KEYBOARDS ====================

def get_employment_menu(case_id: int, case_number: str, case_data: dict) -> InlineKeyboardMarkup:
    """Employment data menu"""
    is_employed = case_data.get('is_employed', False)
    is_self_employed = case_data.get('is_self_employed', False)
    income_records = case_data.get('income_records', [])
    income_count = len(income_records) if isinstance(income_records, list) else 0

    status_text = "Не указано"
    if is_employed:
        status_text = "Трудоустроен"
        employer = case_data.get('employer_name', '')
        if employer:
            status_text += f" ({employer[:20]})"
    elif is_self_employed:
        status_text = "Самозанятый"
    elif is_employed is False and is_self_employed is False:
        status_text = "Безработный"

    keyboard = [
        [InlineKeyboardButton(
            text=f"💼 Статус: {status_text}",
            callback_data=f"employment:{case_id}:status"
        )],
    ]

    if is_self_employed:
        keyboard.append([InlineKeyboardButton(
            text=f"💰 Доходы ({income_count} год(а))",
            callback_data=f"employment:{case_id}:income"
        )])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"case_{case_id}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_employment_status_keyboard(case_id: int) -> InlineKeyboardMarkup:
    """Select employment status"""
    keyboard = [
        [InlineKeyboardButton(text="💼 Трудоустроен", callback_data=f"employ:status:employed:{case_id}")],
        [InlineKeyboardButton(text="👨‍💼 Самозанятый", callback_data=f"employ:status:self_employed:{case_id}")],
        [InlineKeyboardButton(text="🚫 Безработный", callback_data=f"employ:status:unemployed:{case_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"employment:{case_id}:menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_income_menu(case_id: int, income_records: list) -> InlineKeyboardMarkup:
    """Income records menu"""
    keyboard = [
        [InlineKeyboardButton(
            text=f"➕ Добавить доход (всего: {len(income_records)})",
            callback_data=f"income:{case_id}:add"
        )]
    ]

    if income_records:
        keyboard.extend([
            [InlineKeyboardButton(text="📋 Список доходов", callback_data=f"income:{case_id}:list")],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"income:{case_id}:delete")]
        ])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"employment:{case_id}:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_income_list_keyboard(income_records: list, case_id: int) -> InlineKeyboardMarkup:
    """List income records for deletion"""
    keyboard = []

    for income in income_records:
        amount = income.get('amount_rubles', 0)
        year = income.get('year', '')
        amount_formatted = f"{amount:,}".replace(",", " ")
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑 {year}: {amount_formatted} ₽",
                callback_data=f"income:delete:{income['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data=f"income:{case_id}:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_employment_menu(case_id: int) -> InlineKeyboardMarkup:
    """Simple back button to employment menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"employment:{case_id}:menu")]
    ])


def get_back_to_income_menu(case_id: int) -> InlineKeyboardMarkup:
    """Simple back button to income menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"income:{case_id}:menu")]
    ])


# ==================== GROUP 2: PROPERTY KEYBOARDS ====================

def get_property_menu(case_id: int, case_number: str, case_data: dict) -> InlineKeyboardMarkup:
    """Property management menu"""
    has_real_estate = case_data.get('has_real_estate', False)
    properties = case_data.get('properties', [])
    vehicles_count = len([p for p in properties if p.get('property_type') == 'vehicle']) if isinstance(properties, list) else 0

    real_estate_text = "✅ Есть" if has_real_estate else "❌ Нет"

    keyboard = [
        [InlineKeyboardButton(
            text=f"🏠 Недвижимость: {real_estate_text}",
            callback_data=f"property:{case_id}:toggle_real_estate"
        )],
        [InlineKeyboardButton(
            text=f"🚗 Транспорт ({vehicles_count})",
            callback_data=f"property:{case_id}:vehicles"
        )],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"case_{case_id}")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_vehicles_menu(case_id: int, vehicles: list) -> InlineKeyboardMarkup:
    """Vehicles management menu"""
    keyboard = [
        [InlineKeyboardButton(
            text=f"➕ Добавить транспорт (всего: {len(vehicles)})",
            callback_data=f"vehicles:{case_id}:add"
        )]
    ]

    if vehicles:
        keyboard.extend([
            [InlineKeyboardButton(text="📋 Список транспорта", callback_data=f"vehicles:{case_id}:list")],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"vehicles:{case_id}:delete")]
        ])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"property:{case_id}:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_vehicle_pledged_keyboard(case_id: int) -> InlineKeyboardMarkup:
    """Ask if vehicle is pledged"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Да, в залоге", callback_data=f"vehicle_pledged:{case_id}:yes")],
        [InlineKeyboardButton(text="❌ Нет, без залога", callback_data=f"vehicle_pledged:{case_id}:no")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_vehicles_list_keyboard(vehicles: list, case_id: int) -> InlineKeyboardMarkup:
    """List vehicles for deletion"""
    keyboard = []

    for vehicle in vehicles:
        make = vehicle.get('vehicle_make', '')
        model = vehicle.get('vehicle_model', '')
        year = vehicle.get('vehicle_year', '')
        text = f"🗑 {make} {model} ({year})"
        keyboard.append([
            InlineKeyboardButton(
                text=text[:40],
                callback_data=f"vehicle:delete:{vehicle['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data=f"vehicles:{case_id}:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_property_menu(case_id: int) -> InlineKeyboardMarkup:
    """Simple back button to property menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"property:{case_id}:menu")]
    ])


def get_back_to_vehicles_menu(case_id: int) -> InlineKeyboardMarkup:
    """Simple back button to vehicles menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"vehicles:{case_id}:menu")]
    ])


# ==================== GROUP 2: TRANSACTIONS KEYBOARDS ====================

def get_transactions_menu(case_id: int, case_number: str, transactions: list) -> InlineKeyboardMarkup:
    """Transaction history menu"""
    if not isinstance(transactions, list):
        transactions = []

    # Count by type
    real_estate = len([t for t in transactions if t.get('transaction_type') == 'real_estate'])
    securities = len([t for t in transactions if t.get('transaction_type') == 'securities'])
    llc_shares = len([t for t in transactions if t.get('transaction_type') == 'llc_shares'])
    vehicles = len([t for t in transactions if t.get('transaction_type') == 'vehicles'])

    keyboard = [
        [InlineKeyboardButton(
            text=f"➕ Добавить сделку (всего: {len(transactions)})",
            callback_data=f"transactions:{case_id}:add"
        )],
    ]

    if transactions:
        keyboard.extend([
            [InlineKeyboardButton(
                text=f"🏠 Недвижимость ({real_estate})",
                callback_data=f"transactions:{case_id}:list:real_estate"
            )],
            [InlineKeyboardButton(
                text=f"📈 Ценные бумаги ({securities})",
                callback_data=f"transactions:{case_id}:list:securities"
            )],
            [InlineKeyboardButton(
                text=f"🏢 Доли в ООО ({llc_shares})",
                callback_data=f"transactions:{case_id}:list:llc_shares"
            )],
            [InlineKeyboardButton(
                text=f"🚗 Транспорт ({vehicles})",
                callback_data=f"transactions:{case_id}:list:vehicles"
            )],
            [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"transactions:{case_id}:delete")]
        ])

    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"case_{case_id}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_transaction_type_keyboard(case_id: int) -> InlineKeyboardMarkup:
    """Select transaction type"""
    keyboard = [
        [InlineKeyboardButton(text="🏠 Недвижимость", callback_data=f"trans_type:{case_id}:real_estate")],
        [InlineKeyboardButton(text="📈 Ценные бумаги", callback_data=f"trans_type:{case_id}:securities")],
        [InlineKeyboardButton(text="🏢 Доли в ООО", callback_data=f"trans_type:{case_id}:llc_shares")],
        [InlineKeyboardButton(text="🚗 Транспорт", callback_data=f"trans_type:{case_id}:vehicles")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"transactions:{case_id}:menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_transactions_list_keyboard(transactions: list, case_id: int) -> InlineKeyboardMarkup:
    """List transactions for deletion"""
    keyboard = []

    for trans in transactions:
        desc = trans.get('description', '')[:20]
        date_str = trans.get('transaction_date', '')
        if date_str and isinstance(date_str, str):
            date_str = date_str[:10]
        text = f"🗑 {date_str}: {desc}"
        keyboard.append([
            InlineKeyboardButton(
                text=text[:40],
                callback_data=f"transaction:delete:{trans['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data=f"transactions:{case_id}:menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_transactions_menu(case_id: int) -> InlineKeyboardMarkup:
    """Simple back button to transactions menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"transactions:{case_id}:menu")]
    ])


# ==================== GROUP 3: COURT INFO KEYBOARDS ====================

def get_court_info_menu(case_id: int, case_number: str, case_data: dict) -> InlineKeyboardMarkup:
    """Court and SRO info menu"""
    court_name = case_data.get('court_name', 'не указан')
    court_name_display = court_name[:30] if court_name else 'не указан'
    sro_name = case_data.get('sro_name', 'не указана')
    sro_name_display = sro_name[:30] if sro_name else 'не указана'

    keyboard = [
        [InlineKeyboardButton(
            text=f"⚖️ Суд: {court_name_display}",
            callback_data=f"court:{case_id}:edit_name"
        )],
        [InlineKeyboardButton(
            text="📍 Адрес суда",
            callback_data=f"court:{case_id}:edit_address"
        )],
        [InlineKeyboardButton(
            text=f"🏢 СРО: {sro_name_display}",
            callback_data=f"court:{case_id}:edit_sro"
        )],
        [InlineKeyboardButton(
            text="⏱ Срок реструктуризации",
            callback_data=f"court:{case_id}:edit_duration"
        )],
        [InlineKeyboardButton(
            text="📋 Основания несостоятельности",
            callback_data=f"court:{case_id}:edit_grounds"
        )],
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"case_{case_id}")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_court_menu(case_id: int) -> InlineKeyboardMarkup:
    """Simple back button to court menu"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"court:{case_id}:menu")]
    ])
