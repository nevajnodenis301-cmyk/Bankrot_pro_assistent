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
