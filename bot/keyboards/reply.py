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
