from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Yes/No inline keyboard with navigation"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="yes"),
                InlineKeyboardButton(text="❌ Нет, завершить", callback_data="no"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="back_creditor"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_case"),
            ]
        ]
    )
    return keyboard


def get_cases_keyboard(cases: list[dict]) -> InlineKeyboardMarkup:
    """Keyboard with list of cases"""
    buttons = []
    for case in cases[:10]:  # Limit to 10 cases
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{case['case_number']} - {case['full_name'][:20]}",
                    callback_data=f"case_{case['id']}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_case_keyboard(case_id: int) -> InlineKeyboardMarkup:
    """Keyboard for case actions"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Получить документ", callback_data=f"doc_{case_id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_list")],
        ]
    )
    return keyboard
