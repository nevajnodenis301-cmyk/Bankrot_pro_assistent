from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои дела"), KeyboardButton(text="➕ Новое дело")],
            [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="💬 Спросить AI")],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_navigation_keyboard(show_back: bool = True) -> ReplyKeyboardMarkup:
    """Navigation keyboard for FSM with Back and Cancel buttons"""
    buttons = []
    if show_back:
        buttons.append([KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="❌ Отмена")])
    else:
        buttons.append([KeyboardButton(text="❌ Отмена")])

    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
    )
    return keyboard
