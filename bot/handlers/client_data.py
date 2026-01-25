from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.case_states import ClientDataEdit
from keyboards.case_menu import (
    get_client_data_menu,
    get_back_to_client_menu,
    get_passport_edit_menu,
    get_address_edit_menu,
    get_cancel_edit_keyboard,
    get_gender_selection_keyboard,
)
from services.api_client import APIClient
from exceptions import BotException, CaseNotFoundError
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

router = Router()
api = APIClient()


def format_date(date_str: str | None) -> str:
    """Format date string for display"""
    if not date_str:
        return "не указана"
    try:
        if isinstance(date_str, str):
            # Handle ISO format
            if "T" in date_str:
                date_str = date_str.split("T")[0]
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%d.%m.%Y")
    except (ValueError, TypeError):
        pass
    return str(date_str) if date_str else "не указана"


def format_passport(case: dict) -> str:
    """Format passport info for display"""
    series = case.get("passport_series") or "____"
    number = case.get("passport_number") or "______"
    issued_by = case.get("passport_issued_by") or "не указано"
    issued_date = format_date(case.get("passport_issued_date"))
    code = case.get("passport_code") or "___-___"

    return (
        f"<b>Серия:</b> {series}\n"
        f"<b>Номер:</b> {number}\n"
        f"<b>Кем выдан:</b> {issued_by}\n"
        f"<b>Дата выдачи:</b> {issued_date}\n"
        f"<b>Код подразделения:</b> {code}"
    )


def format_gender(gender: str | None) -> str:
    """Format gender for display"""
    if gender == "M":
        return "Мужской"
    elif gender == "F":
        return "Женский"
    return "не указан"


# === Client Menu ===

@router.callback_query(F.data.regexp(r"^case:(\d+):client$"))
async def show_client_menu(callback: CallbackQuery, state: FSMContext):
    """Show client data menu"""
    match = re.match(r"^case:(\d+):client$", callback.data)
    case_id = int(match.group(1))

    try:
        case = await api.get_case(case_id)
        await state.update_data(current_case_id=case_id, case_number=case["case_number"])

        await callback.message.edit_text(
            f"👤 <b>Данные клиента</b>\n\n"
            f"Дело: <code>{case['case_number']}</code>\n"
            f"ФИО: {case['full_name']}\n\n"
            f"Выберите действие:",
            reply_markup=get_client_data_menu(case_id),
            parse_mode="HTML"
        )
    except CaseNotFoundError:
        await callback.answer("Дело не найдено", show_alert=True)
    except BotException as e:
        await callback.answer(f"Ошибка: {e.user_message}", show_alert=True)

    await callback.answer()


@router.callback_query(F.data.regexp(r"^client:(\d+):menu$"))
async def back_to_client_menu(callback: CallbackQuery, state: FSMContext):
    """Return to client data menu"""
    await state.set_state(None)  # Clear any editing state

    match = re.match(r"^client:(\d+):menu$", callback.data)
    case_id = int(match.group(1))

    try:
        case = await api.get_case(case_id)

        await callback.message.edit_text(
            f"👤 <b>Данные клиента</b>\n\n"
            f"Дело: <code>{case['case_number']}</code>\n"
            f"ФИО: {case['full_name']}\n\n"
            f"Выберите действие:",
            reply_markup=get_client_data_menu(case_id),
            parse_mode="HTML"
        )
    except CaseNotFoundError:
        await callback.answer("Дело не найдено", show_alert=True)
    except BotException as e:
        await callback.answer(f"Ошибка: {e.user_message}", show_alert=True)

    await callback.answer()


# === View Client Data ===

@router.callback_query(F.data.regexp(r"^client:(\d+):view$"))
async def view_client_data(callback: CallbackQuery):
    """Display current client data"""
    match = re.match(r"^client:(\d+):view$", callback.data)
    case_id = int(match.group(1))

    try:
        case = await api.get_case(case_id)

        text = f"👤 <b>Данные клиента</b>\n\n"
        text += f"<b>ФИО:</b> {case['full_name']}\n"
        text += f"<b>Дата рождения:</b> {format_date(case.get('birth_date'))}\n"
        text += f"<b>Пол:</b> {format_gender(case.get('gender'))}\n\n"

        text += f"<b>📕 Паспорт:</b>\n"
        text += format_passport(case) + "\n\n"

        text += f"<b>📍 Контакты:</b>\n"
        text += f"<b>Адрес:</b> {case.get('registration_address') or 'не указан'}\n"
        text += f"<b>Телефон:</b> {case.get('phone') or 'не указан'}\n"
        text += f"<b>Email:</b> {case.get('email') or 'не указан'}\n\n"

        text += f"<b>📋 Документы:</b>\n"
        text += f"<b>ИНН:</b> {case.get('inn') or 'не указан'}\n"
        text += f"<b>СНИЛС:</b> {case.get('snils') or 'не указан'}\n"

        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except CaseNotFoundError:
        await callback.answer("Дело не найдено", show_alert=True)
    except BotException as e:
        await callback.answer(f"Ошибка: {e.user_message}", show_alert=True)

    await callback.answer()


# === Passport Editing ===

@router.callback_query(F.data.regexp(r"^client:(\d+):edit_passport$"))
async def show_passport_edit_menu(callback: CallbackQuery):
    """Show passport editing options"""
    match = re.match(r"^client:(\d+):edit_passport$", callback.data)
    case_id = int(match.group(1))

    try:
        case = await api.get_case(case_id)

        text = f"✏️ <b>Редактирование паспорта</b>\n\n"
        text += f"<b>Текущие данные:</b>\n"
        text += format_passport(case) + "\n\n"
        text += "Выберите поле для редактирования:"

        await callback.message.edit_text(
            text,
            reply_markup=get_passport_edit_menu(case_id),
            parse_mode="HTML"
        )
    except CaseNotFoundError:
        await callback.answer("Дело не найдено", show_alert=True)
    except BotException as e:
        await callback.answer(f"Ошибка: {e.user_message}", show_alert=True)

    await callback.answer()


@router.callback_query(F.data.regexp(r"^passport:(\d+):series$"))
async def start_edit_passport_series(callback: CallbackQuery, state: FSMContext):
    """Start editing passport series"""
    match = re.match(r"^passport:(\d+):series$", callback.data)
    case_id = int(match.group(1))

    await state.set_state(ClientDataEdit.edit_passport_series)
    await state.update_data(current_case_id=case_id)

    await callback.message.edit_text(
        "📝 <b>Введите серию паспорта</b>\n\n"
        "Формат: 4 цифры\n"
        "<i>Например: 4510</i>",
        reply_markup=get_cancel_edit_keyboard(case_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ClientDataEdit.edit_passport_series)
async def process_passport_series(message: Message, state: FSMContext):
    """Process passport series input"""
    data = await state.get_data()
    case_id = data["current_case_id"]

    series = message.text.strip().replace(" ", "")

    # Validate: must be 4 digits
    if not re.match(r"^\d{4}$", series):
        await message.answer(
            "❌ Серия паспорта должна содержать 4 цифры.\n"
            "Попробуйте снова или нажмите Отмена.",
            reply_markup=get_cancel_edit_keyboard(case_id),
            parse_mode="HTML"
        )
        return

    try:
        await api.update_case_client_data(case_id, {"passport_series": series})
        await state.set_state(None)

        await message.answer(
            f"✅ Серия паспорта успешно обновлена: <b>{series}</b>",
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await message.answer(f"❌ Ошибка: {e.user_message}")


@router.callback_query(F.data.regexp(r"^passport:(\d+):number$"))
async def start_edit_passport_number(callback: CallbackQuery, state: FSMContext):
    """Start editing passport number"""
    match = re.match(r"^passport:(\d+):number$", callback.data)
    case_id = int(match.group(1))

    await state.set_state(ClientDataEdit.edit_passport_number)
    await state.update_data(current_case_id=case_id)

    await callback.message.edit_text(
        "📝 <b>Введите номер паспорта</b>\n\n"
        "Формат: 6 цифр\n"
        "<i>Например: 123456</i>",
        reply_markup=get_cancel_edit_keyboard(case_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ClientDataEdit.edit_passport_number)
async def process_passport_number(message: Message, state: FSMContext):
    """Process passport number input"""
    data = await state.get_data()
    case_id = data["current_case_id"]

    number = message.text.strip().replace(" ", "")

    # Validate: must be 6 digits
    if not re.match(r"^\d{6}$", number):
        await message.answer(
            "❌ Номер паспорта должен содержать 6 цифр.\n"
            "Попробуйте снова или нажмите Отмена.",
            reply_markup=get_cancel_edit_keyboard(case_id),
            parse_mode="HTML"
        )
        return

    try:
        await api.update_case_client_data(case_id, {"passport_number": number})
        await state.set_state(None)

        await message.answer(
            f"✅ Номер паспорта успешно обновлен: <b>{number}</b>",
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await message.answer(f"❌ Ошибка: {e.user_message}")


@router.callback_query(F.data.regexp(r"^passport:(\d+):issued_by$"))
async def start_edit_passport_issued_by(callback: CallbackQuery, state: FSMContext):
    """Start editing passport issued by"""
    match = re.match(r"^passport:(\d+):issued_by$", callback.data)
    case_id = int(match.group(1))

    await state.set_state(ClientDataEdit.edit_passport_issued_by)
    await state.update_data(current_case_id=case_id)

    await callback.message.edit_text(
        "📝 <b>Введите, кем выдан паспорт</b>\n\n"
        "<i>Например: Отделением УФМС России по г. Москве</i>",
        reply_markup=get_cancel_edit_keyboard(case_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ClientDataEdit.edit_passport_issued_by)
async def process_passport_issued_by(message: Message, state: FSMContext):
    """Process passport issued by input"""
    data = await state.get_data()
    case_id = data["current_case_id"]

    issued_by = message.text.strip()

    if len(issued_by) < 5:
        await message.answer(
            "❌ Слишком короткое значение.\n"
            "Попробуйте снова или нажмите Отмена.",
            reply_markup=get_cancel_edit_keyboard(case_id),
            parse_mode="HTML"
        )
        return

    try:
        await api.update_case_client_data(case_id, {"passport_issued_by": issued_by})
        await state.set_state(None)

        await message.answer(
            f"✅ Поле 'Кем выдан' успешно обновлено",
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await message.answer(f"❌ Ошибка: {e.user_message}")


@router.callback_query(F.data.regexp(r"^passport:(\d+):date$"))
async def start_edit_passport_date(callback: CallbackQuery, state: FSMContext):
    """Start editing passport issue date"""
    match = re.match(r"^passport:(\d+):date$", callback.data)
    case_id = int(match.group(1))

    await state.set_state(ClientDataEdit.edit_passport_date)
    await state.update_data(current_case_id=case_id)

    await callback.message.edit_text(
        "📝 <b>Введите дату выдачи паспорта</b>\n\n"
        "Формат: ДД.ММ.ГГГГ\n"
        "<i>Например: 15.03.2015</i>",
        reply_markup=get_cancel_edit_keyboard(case_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ClientDataEdit.edit_passport_date)
async def process_passport_date(message: Message, state: FSMContext):
    """Process passport issue date input"""
    data = await state.get_data()
    case_id = data["current_case_id"]

    date_str = message.text.strip()

    # Try to parse date
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        iso_date = dt.strftime("%Y-%m-%d")
    except ValueError:
        await message.answer(
            "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ\n"
            "<i>Например: 15.03.2015</i>",
            reply_markup=get_cancel_edit_keyboard(case_id),
            parse_mode="HTML"
        )
        return

    try:
        await api.update_case_client_data(case_id, {"passport_issued_date": iso_date})
        await state.set_state(None)

        await message.answer(
            f"✅ Дата выдачи паспорта успешно обновлена: <b>{date_str}</b>",
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await message.answer(f"❌ Ошибка: {e.user_message}")


@router.callback_query(F.data.regexp(r"^passport:(\d+):code$"))
async def start_edit_passport_code(callback: CallbackQuery, state: FSMContext):
    """Start editing passport division code"""
    match = re.match(r"^passport:(\d+):code$", callback.data)
    case_id = int(match.group(1))

    await state.set_state(ClientDataEdit.edit_passport_code)
    await state.update_data(current_case_id=case_id)

    await callback.message.edit_text(
        "📝 <b>Введите код подразделения</b>\n\n"
        "Формат: XXX-XXX\n"
        "<i>Например: 770-001</i>",
        reply_markup=get_cancel_edit_keyboard(case_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ClientDataEdit.edit_passport_code)
async def process_passport_code(message: Message, state: FSMContext):
    """Process passport division code input"""
    data = await state.get_data()
    case_id = data["current_case_id"]

    code = message.text.strip()

    # Allow formats: XXX-XXX or XXXXXX
    clean_code = code.replace("-", "").replace(" ", "")
    if not re.match(r"^\d{6}$", clean_code):
        await message.answer(
            "❌ Код подразделения должен содержать 6 цифр.\n"
            "Формат: XXX-XXX или XXXXXX",
            reply_markup=get_cancel_edit_keyboard(case_id),
            parse_mode="HTML"
        )
        return

    # Format as XXX-XXX
    formatted_code = f"{clean_code[:3]}-{clean_code[3:]}"

    try:
        await api.update_case_client_data(case_id, {"passport_code": formatted_code})
        await state.set_state(None)

        await message.answer(
            f"✅ Код подразделения успешно обновлен: <b>{formatted_code}</b>",
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await message.answer(f"❌ Ошибка: {e.user_message}")


# === Address Editing ===

@router.callback_query(F.data.regexp(r"^client:(\d+):edit_address$"))
async def show_address_edit_menu(callback: CallbackQuery):
    """Show address editing options"""
    match = re.match(r"^client:(\d+):edit_address$", callback.data)
    case_id = int(match.group(1))

    try:
        case = await api.get_case(case_id)

        text = f"✏️ <b>Редактирование адреса и телефона</b>\n\n"
        text += f"<b>Текущие данные:</b>\n"
        text += f"<b>Адрес:</b> {case.get('registration_address') or 'не указан'}\n"
        text += f"<b>Телефон:</b> {case.get('phone') or 'не указан'}\n\n"
        text += "Выберите поле для редактирования:"

        await callback.message.edit_text(
            text,
            reply_markup=get_address_edit_menu(case_id),
            parse_mode="HTML"
        )
    except CaseNotFoundError:
        await callback.answer("Дело не найдено", show_alert=True)
    except BotException as e:
        await callback.answer(f"Ошибка: {e.user_message}", show_alert=True)

    await callback.answer()


@router.callback_query(F.data.regexp(r"^address:(\d+):registration$"))
async def start_edit_address(callback: CallbackQuery, state: FSMContext):
    """Start editing registration address"""
    match = re.match(r"^address:(\d+):registration$", callback.data)
    case_id = int(match.group(1))

    await state.set_state(ClientDataEdit.edit_address)
    await state.update_data(current_case_id=case_id)

    await callback.message.edit_text(
        "📝 <b>Введите адрес регистрации</b>\n\n"
        "<i>Например: г. Москва, ул. Ленина, д. 10, кв. 5</i>",
        reply_markup=get_cancel_edit_keyboard(case_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ClientDataEdit.edit_address)
async def process_address(message: Message, state: FSMContext):
    """Process registration address input"""
    data = await state.get_data()
    case_id = data["current_case_id"]

    address = message.text.strip()

    if len(address) < 10:
        await message.answer(
            "❌ Адрес слишком короткий.\n"
            "Попробуйте снова или нажмите Отмена.",
            reply_markup=get_cancel_edit_keyboard(case_id),
            parse_mode="HTML"
        )
        return

    try:
        await api.update_case_client_data(case_id, {"registration_address": address})
        await state.set_state(None)

        await message.answer(
            f"✅ Адрес регистрации успешно обновлен",
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await message.answer(f"❌ Ошибка: {e.user_message}")


@router.callback_query(F.data.regexp(r"^address:(\d+):phone$"))
async def start_edit_phone(callback: CallbackQuery, state: FSMContext):
    """Start editing phone"""
    match = re.match(r"^address:(\d+):phone$", callback.data)
    case_id = int(match.group(1))

    await state.set_state(ClientDataEdit.edit_phone)
    await state.update_data(current_case_id=case_id)

    await callback.message.edit_text(
        "📝 <b>Введите номер телефона</b>\n\n"
        "<i>Например: +7 (999) 123-45-67</i>",
        reply_markup=get_cancel_edit_keyboard(case_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ClientDataEdit.edit_phone)
async def process_phone(message: Message, state: FSMContext):
    """Process phone input"""
    data = await state.get_data()
    case_id = data["current_case_id"]

    phone = message.text.strip()

    # Simple validation: at least 10 digits
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 10:
        await message.answer(
            "❌ Номер телефона должен содержать не менее 10 цифр.\n"
            "Попробуйте снова или нажмите Отмена.",
            reply_markup=get_cancel_edit_keyboard(case_id),
            parse_mode="HTML"
        )
        return

    try:
        await api.update_case_client_data(case_id, {"phone": phone})
        await state.set_state(None)

        await message.answer(
            f"✅ Номер телефона успешно обновлен: <b>{phone}</b>",
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await message.answer(f"❌ Ошибка: {e.user_message}")


# === INN/SNILS Editing ===

@router.callback_query(F.data.regexp(r"^client:(\d+):edit_inn_snils$"))
async def show_inn_snils_menu(callback: CallbackQuery, state: FSMContext):
    """Show INN/SNILS editing options"""
    match = re.match(r"^client:(\d+):edit_inn_snils$", callback.data)
    case_id = int(match.group(1))

    try:
        case = await api.get_case(case_id)

        text = f"✏️ <b>Редактирование ИНН и СНИЛС</b>\n\n"
        text += f"<b>Текущие данные:</b>\n"
        text += f"<b>ИНН:</b> {case.get('inn') or 'не указан'}\n"
        text += f"<b>СНИЛС:</b> {case.get('snils') or 'не указан'}\n\n"
        text += "Выберите поле для редактирования:"

        keyboard = [
            [InlineKeyboardButton(text="📝 ИНН", callback_data=f"inn_snils:{case_id}:inn")],
            [InlineKeyboardButton(text="📝 СНИЛС", callback_data=f"inn_snils:{case_id}:snils")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data=f"client:{case_id}:menu")],
        ]

        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )
    except CaseNotFoundError:
        await callback.answer("Дело не найдено", show_alert=True)
    except BotException as e:
        await callback.answer(f"Ошибка: {e.user_message}", show_alert=True)

    await callback.answer()


@router.callback_query(F.data.regexp(r"^inn_snils:(\d+):inn$"))
async def start_edit_inn(callback: CallbackQuery, state: FSMContext):
    """Start editing INN"""
    match = re.match(r"^inn_snils:(\d+):inn$", callback.data)
    case_id = int(match.group(1))

    await state.set_state(ClientDataEdit.edit_inn)
    await state.update_data(current_case_id=case_id)

    await callback.message.edit_text(
        "📝 <b>Введите ИНН</b>\n\n"
        "Формат: 12 цифр (для физических лиц)\n"
        "<i>Например: 123456789012</i>",
        reply_markup=get_cancel_edit_keyboard(case_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ClientDataEdit.edit_inn)
async def process_inn(message: Message, state: FSMContext):
    """Process INN input"""
    data = await state.get_data()
    case_id = data["current_case_id"]

    inn = message.text.strip().replace(" ", "")

    # Validate: 10 or 12 digits
    if not re.match(r"^\d{10}$|^\d{12}$", inn):
        await message.answer(
            "❌ ИНН должен содержать 10 или 12 цифр.\n"
            "Попробуйте снова или нажмите Отмена.",
            reply_markup=get_cancel_edit_keyboard(case_id),
            parse_mode="HTML"
        )
        return

    try:
        await api.update_case_client_data(case_id, {"inn": inn})
        await state.set_state(None)

        await message.answer(
            f"✅ ИНН успешно обновлен: <b>{inn}</b>",
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await message.answer(f"❌ Ошибка: {e.user_message}")


@router.callback_query(F.data.regexp(r"^inn_snils:(\d+):snils$"))
async def start_edit_snils(callback: CallbackQuery, state: FSMContext):
    """Start editing SNILS"""
    match = re.match(r"^inn_snils:(\d+):snils$", callback.data)
    case_id = int(match.group(1))

    await state.set_state(ClientDataEdit.edit_snils)
    await state.update_data(current_case_id=case_id)

    await callback.message.edit_text(
        "📝 <b>Введите СНИЛС</b>\n\n"
        "Формат: XXX-XXX-XXX XX или 11 цифр\n"
        "<i>Например: 123-456-789 01</i>",
        reply_markup=get_cancel_edit_keyboard(case_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(ClientDataEdit.edit_snils)
async def process_snils(message: Message, state: FSMContext):
    """Process SNILS input"""
    data = await state.get_data()
    case_id = data["current_case_id"]

    snils = message.text.strip()

    # Extract digits
    digits = re.sub(r"\D", "", snils)
    if len(digits) != 11:
        await message.answer(
            "❌ СНИЛС должен содержать 11 цифр.\n"
            "Попробуйте снова или нажмите Отмена.",
            reply_markup=get_cancel_edit_keyboard(case_id),
            parse_mode="HTML"
        )
        return

    # Format as XXX-XXX-XXX XX
    formatted_snils = f"{digits[:3]}-{digits[3:6]}-{digits[6:9]} {digits[9:]}"

    try:
        await api.update_case_client_data(case_id, {"snils": formatted_snils})
        await state.set_state(None)

        await message.answer(
            f"✅ СНИЛС успешно обновлен: <b>{formatted_snils}</b>",
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await message.answer(f"❌ Ошибка: {e.user_message}")


# === Birth Date Editing ===

@router.callback_query(F.data.regexp(r"^client:(\d+):edit_birth$"))
async def start_edit_birth_date(callback: CallbackQuery, state: FSMContext):
    """Start editing birth date"""
    match = re.match(r"^client:(\d+):edit_birth$", callback.data)
    case_id = int(match.group(1))

    await state.set_state(ClientDataEdit.edit_birth_date)
    await state.update_data(current_case_id=case_id)

    try:
        case = await api.get_case(case_id)
        current_date = format_date(case.get("birth_date"))

        await callback.message.edit_text(
            f"📝 <b>Введите дату рождения</b>\n\n"
            f"<b>Текущее значение:</b> {current_date}\n\n"
            f"Формат: ДД.ММ.ГГГГ\n"
            f"<i>Например: 25.12.1985</i>",
            reply_markup=get_cancel_edit_keyboard(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await callback.answer(f"Ошибка: {e.user_message}", show_alert=True)

    await callback.answer()


@router.message(ClientDataEdit.edit_birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    """Process birth date input"""
    data = await state.get_data()
    case_id = data["current_case_id"]

    date_str = message.text.strip()

    # Try to parse date
    try:
        dt = datetime.strptime(date_str, "%d.%m.%Y")
        iso_date = dt.strftime("%Y-%m-%d")
    except ValueError:
        await message.answer(
            "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ\n"
            "<i>Например: 25.12.1985</i>",
            reply_markup=get_cancel_edit_keyboard(case_id),
            parse_mode="HTML"
        )
        return

    try:
        await api.update_case_client_data(case_id, {"birth_date": iso_date})
        await state.set_state(None)

        await message.answer(
            f"✅ Дата рождения успешно обновлена: <b>{date_str}</b>",
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await message.answer(f"❌ Ошибка: {e.user_message}")


# === Gender Editing ===

@router.callback_query(F.data.regexp(r"^client:(\d+):edit_gender$"))
async def start_edit_gender(callback: CallbackQuery, state: FSMContext):
    """Start editing gender"""
    match = re.match(r"^client:(\d+):edit_gender$", callback.data)
    case_id = int(match.group(1))

    try:
        case = await api.get_case(case_id)
        current_gender = format_gender(case.get("gender"))

        await callback.message.edit_text(
            f"📝 <b>Выберите пол</b>\n\n"
            f"<b>Текущее значение:</b> {current_gender}",
            reply_markup=get_gender_selection_keyboard(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await callback.answer(f"Ошибка: {e.user_message}", show_alert=True)

    await callback.answer()


@router.callback_query(F.data.regexp(r"^gender:(\d+):(M|F)$"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Process gender selection"""
    match = re.match(r"^gender:(\d+):(M|F)$", callback.data)
    case_id = int(match.group(1))
    gender = match.group(2)

    try:
        await api.update_case_client_data(case_id, {"gender": gender})

        gender_text = "Мужской" if gender == "M" else "Женский"
        await callback.message.edit_text(
            f"✅ Пол успешно обновлен: <b>{gender_text}</b>",
            reply_markup=get_back_to_client_menu(case_id),
            parse_mode="HTML"
        )
    except BotException as e:
        await callback.answer(f"Ошибка: {e.user_message}", show_alert=True)

    await callback.answer()
