from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_case_detail_menu(case_id: int, case_number: str) -> InlineKeyboardMarkup:
    """
    Main menu when viewing a case.
    Shows 8 sections + generate document button.
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
        [InlineKeyboardButton(text="📄 Создать заявление", callback_data=f"doc_{case_id}")],
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
