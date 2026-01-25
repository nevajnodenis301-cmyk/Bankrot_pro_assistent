from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime
from states.case_states import FamilyDataEdit
from keyboards.case_menu import (
    get_family_menu,
    get_marital_status_keyboard,
    get_children_menu,
    get_child_document_type_keyboard,
    get_children_list_keyboard,
    get_back_to_family_menu,
    get_back_to_children_menu,
)
from services.api_client import APIClient
import logging

router = Router()
api = APIClient()
logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> datetime | None:
    """Parse date from DD.MM.YYYY format"""
    try:
        return datetime.strptime(date_str.strip(), "%d.%m.%Y")
    except ValueError:
        return None


# ==================== FAMILY MENU ====================

@router.callback_query(F.data.startswith("case:") & F.data.endswith(":family"))
async def show_family_menu(callback: CallbackQuery, state: FSMContext):
    """Show family data menu"""
    parts = callback.data.split(":")
    case_id = int(parts[1])

    try:
        case = await api.get_case(case_id)
        children = await api.get_children(case_id)
        case['children'] = children

        await callback.message.edit_text(
            f"👨‍👩‍👧 <b>Семья</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Клиент: {case['full_name']}\n\n"
            f"Выберите действие:",
            reply_markup=get_family_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(FamilyDataEdit.menu)

    except Exception as e:
        logger.error(f"Error showing family menu: {e}")
        await callback.answer("❌ Ошибка загрузки данных", show_alert=True)


@router.callback_query(F.data.startswith("family:") & F.data.endswith(":menu"))
async def return_to_family_menu(callback: CallbackQuery, state: FSMContext):
    """Return to family menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        children = await api.get_children(case_id)
        case['children'] = children

        await callback.message.edit_text(
            f"👨‍👩‍👧 <b>Семья</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Клиент: {case['full_name']}\n\n"
            f"Выберите действие:",
            reply_markup=get_family_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(FamilyDataEdit.menu)

    except Exception as e:
        logger.error(f"Error returning to family menu: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ==================== MARITAL STATUS ====================

@router.callback_query(F.data.startswith("family:") & F.data.endswith(":edit_status"))
async def edit_marital_status(callback: CallbackQuery, state: FSMContext):
    """Start editing marital status"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "💍 <b>Семейное положение</b>\n\n"
        "Выберите текущее семейное положение:",
        reply_markup=get_marital_status_keyboard(case_id),
        parse_mode="HTML"
    )
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.callback_query(F.data.startswith("family:status:"))
async def process_marital_status(callback: CallbackQuery, state: FSMContext):
    """Process marital status selection"""
    parts = callback.data.split(":")
    status = parts[2]
    case_id = int(parts[3])

    try:
        # Save marital status
        await api.update_case_family_data(case_id, {'marital_status': status})

        if status == "married":
            # Ask for spouse name
            await callback.message.edit_text(
                "💍 <b>Информация о супруге</b>\n\n"
                "Введите ФИО супруга(и):",
                parse_mode="HTML"
            )
            await state.set_state(FamilyDataEdit.edit_spouse_name)
            await state.update_data(case_id=case_id)

        elif status == "divorced":
            # Ask for divorce certificate
            await callback.message.edit_text(
                "💔 <b>Свидетельство о расторжении брака</b>\n\n"
                "Введите номер свидетельства о расторжении брака:\n"
                "(или отправьте <b>-</b> если неизвестен)",
                parse_mode="HTML"
            )
            await state.set_state(FamilyDataEdit.edit_divorce_cert_number)
            await state.update_data(case_id=case_id)

        else:
            # Return to family menu
            case = await api.get_case(case_id)
            children = await api.get_children(case_id)
            case['children'] = children

            await callback.message.edit_text(
                f"✅ Семейное положение обновлено!\n\n"
                f"👨‍👩‍👧 <b>Семья</b>\n\n"
                f"Выберите действие:",
                reply_markup=get_family_menu(case_id, case['case_number'], case),
                parse_mode="HTML"
            )
            await state.set_state(FamilyDataEdit.menu)

    except Exception as e:
        logger.error(f"Error processing marital status: {e}")
        await callback.answer("❌ Ошибка сохранения", show_alert=True)


# ==================== SPOUSE INFO ====================

@router.callback_query(F.data.startswith("family:") & F.data.endswith(":spouse"))
async def edit_spouse_info(callback: CallbackQuery, state: FSMContext):
    """Edit spouse information"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "👥 <b>Информация о супруге</b>\n\n"
        "Введите ФИО супруга(и):",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.edit_spouse_name)
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.message(FamilyDataEdit.edit_spouse_name)
async def process_spouse_name(message: Message, state: FSMContext):
    """Process spouse name"""
    spouse_name = message.text.strip()
    await state.update_data(spouse_name=spouse_name)

    data = await state.get_data()
    case_id = data['case_id']

    try:
        await api.update_case_family_data(case_id, {'spouse_name': spouse_name})

        # Ask for marriage certificate
        await message.answer(
            "📄 <b>Свидетельство о браке</b>\n\n"
            "Введите номер свидетельства о браке:\n"
            "(или отправьте <b>-</b> если неизвестен)",
            parse_mode="HTML"
        )
        await state.set_state(FamilyDataEdit.edit_marriage_cert_number)

    except Exception as e:
        logger.error(f"Error saving spouse name: {e}")
        await message.answer("❌ Ошибка сохранения. Попробуйте позже.")
        await state.clear()


@router.message(FamilyDataEdit.edit_marriage_cert_number)
async def process_marriage_cert_number(message: Message, state: FSMContext):
    """Process marriage certificate number"""
    cert_number = message.text.strip()
    data = await state.get_data()
    case_id = data['case_id']

    if cert_number != "-":
        await api.update_case_family_data(case_id, {'marriage_certificate_number': cert_number})

    await message.answer(
        "📅 <b>Дата свидетельства о браке</b>\n\n"
        "Введите дату выдачи свидетельства (ДД.ММ.ГГГГ):\n"
        "(или отправьте <b>-</b> если неизвестна)",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.edit_marriage_cert_date)


@router.message(FamilyDataEdit.edit_marriage_cert_date)
async def process_marriage_cert_date(message: Message, state: FSMContext):
    """Process marriage certificate date"""
    date_str = message.text.strip()
    data = await state.get_data()
    case_id = data['case_id']

    if date_str != "-":
        parsed_date = parse_date(date_str)
        if not parsed_date:
            await message.answer(
                "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ\n"
                "(например: 15.06.2020)\n\n"
                "Попробуйте снова:"
            )
            return

        await api.update_case_family_data(case_id, {
            'marriage_certificate_date': parsed_date.strftime("%Y-%m-%d")
        })

    # Return to family menu
    try:
        case = await api.get_case(case_id)
        children = await api.get_children(case_id)
        case['children'] = children

        await message.answer(
            f"✅ Информация о браке сохранена!\n\n"
            f"👨‍👩‍👧 <b>Семья</b>\n\n"
            f"Выберите действие:",
            reply_markup=get_family_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.set_state(FamilyDataEdit.menu)

    except Exception as e:
        logger.error(f"Error saving marriage cert date: {e}")
        await message.answer("❌ Ошибка сохранения. Попробуйте позже.")
        await state.clear()


# ==================== DIVORCE CERTIFICATE ====================

@router.message(FamilyDataEdit.edit_divorce_cert_number)
async def process_divorce_cert_number(message: Message, state: FSMContext):
    """Process divorce certificate number"""
    cert_number = message.text.strip()
    data = await state.get_data()
    case_id = data['case_id']

    if cert_number != "-":
        await api.update_case_family_data(case_id, {'divorce_certificate_number': cert_number})

    await message.answer(
        "📅 <b>Дата свидетельства о расторжении брака</b>\n\n"
        "Введите дату выдачи свидетельства (ДД.ММ.ГГГГ):\n"
        "(или отправьте <b>-</b> если неизвестна)",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.edit_divorce_cert_date)


@router.message(FamilyDataEdit.edit_divorce_cert_date)
async def process_divorce_cert_date(message: Message, state: FSMContext):
    """Process divorce certificate date"""
    date_str = message.text.strip()
    data = await state.get_data()
    case_id = data['case_id']

    if date_str != "-":
        parsed_date = parse_date(date_str)
        if not parsed_date:
            await message.answer(
                "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ\n"
                "(например: 15.06.2020)\n\n"
                "Попробуйте снова:"
            )
            return

        await api.update_case_family_data(case_id, {
            'divorce_certificate_date': parsed_date.strftime("%Y-%m-%d")
        })

    # Return to family menu
    try:
        case = await api.get_case(case_id)
        children = await api.get_children(case_id)
        case['children'] = children

        await message.answer(
            f"✅ Информация о разводе сохранена!\n\n"
            f"👨‍👩‍👧 <b>Семья</b>\n\n"
            f"Выберите действие:",
            reply_markup=get_family_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.set_state(FamilyDataEdit.menu)

    except Exception as e:
        logger.error(f"Error saving divorce cert date: {e}")
        await message.answer("❌ Ошибка сохранения. Попробуйте позже.")
        await state.clear()


# ==================== CHILDREN MENU ====================

@router.callback_query(F.data.startswith("family:") & F.data.endswith(":children"))
async def show_children_menu(callback: CallbackQuery, state: FSMContext):
    """Show children management menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        children = await api.get_children(case_id)

        await callback.message.edit_text(
            f"👶 <b>Дети</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Всего детей: {len(children)}\n\n"
            f"Выберите действие:",
            reply_markup=get_children_menu(case_id, case['case_number'], children),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])

    except Exception as e:
        logger.error(f"Error showing children menu: {e}")
        await callback.answer("❌ Ошибка загрузки", show_alert=True)


@router.callback_query(F.data.startswith("children:") & F.data.endswith(":menu"))
async def return_to_children_menu(callback: CallbackQuery, state: FSMContext):
    """Return to children menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        children = await api.get_children(case_id)

        await callback.message.edit_text(
            f"👶 <b>Дети</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Всего детей: {len(children)}\n\n"
            f"Выберите действие:",
            reply_markup=get_children_menu(case_id, case['case_number'], children),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])

    except Exception as e:
        logger.error(f"Error returning to children menu: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ==================== ADD CHILD ====================

@router.callback_query(F.data.startswith("children:") & F.data.endswith(":add"))
async def start_add_child(callback: CallbackQuery, state: FSMContext):
    """Start adding new child"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "➕ <b>Добавление ребенка</b>\n\n"
        "Введите ФИО ребенка:",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.add_child_name)
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.message(FamilyDataEdit.add_child_name)
async def process_child_name(message: Message, state: FSMContext):
    """Process child name"""
    child_name = message.text.strip()
    await state.update_data(child_name=child_name)

    await message.answer(
        "📅 <b>Дата рождения</b>\n\n"
        "Введите дату рождения ребенка (ДД.ММ.ГГГГ):",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.add_child_birth_date)


@router.message(FamilyDataEdit.add_child_birth_date)
async def process_child_birth_date(message: Message, state: FSMContext):
    """Process child birth date and ask for document type"""
    date_str = message.text.strip()
    parsed_date = parse_date(date_str)

    if not parsed_date:
        await message.answer(
            "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ\n"
            "(например: 15.06.2015)\n\n"
            "Попробуйте снова:"
        )
        return

    await state.update_data(child_birth_date=parsed_date.strftime("%Y-%m-%d"))

    data = await state.get_data()
    case_id = data['case_id']

    await message.answer(
        "📄 <b>Тип документа</b>\n\n"
        "Выберите тип документа ребенка:",
        reply_markup=get_child_document_type_keyboard(case_id),
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.add_child_document_type)


@router.callback_query(F.data.startswith("child_doc:") & F.data.contains(":birth_certificate"))
async def select_birth_certificate(callback: CallbackQuery, state: FSMContext):
    """Selected birth certificate"""
    case_id = int(callback.data.split(":")[1])
    await state.update_data(child_has_certificate=True, child_has_passport=False)

    await callback.message.edit_text(
        "📄 <b>Свидетельство о рождении</b>\n\n"
        "Введите номер свидетельства о рождении:\n"
        "(или отправьте <b>-</b> если неизвестен)",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.add_child_cert_number)
    await callback.answer()


@router.message(FamilyDataEdit.add_child_cert_number)
async def process_child_cert_number(message: Message, state: FSMContext):
    """Process birth certificate number"""
    cert_number = message.text.strip()
    if cert_number != "-":
        await state.update_data(child_certificate_number=cert_number)

    await message.answer(
        "📅 <b>Дата выдачи свидетельства</b>\n\n"
        "Введите дату выдачи свидетельства (ДД.ММ.ГГГГ):\n"
        "(или отправьте <b>-</b> если неизвестна)",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.add_child_cert_date)


@router.message(FamilyDataEdit.add_child_cert_date)
async def process_child_cert_date_and_save(message: Message, state: FSMContext):
    """Process birth certificate date and save child"""
    date_str = message.text.strip()
    data = await state.get_data()
    case_id = data['case_id']

    child_data = {
        'child_name': data['child_name'],
        'child_birth_date': data['child_birth_date'],
        'child_has_certificate': True,
        'child_has_passport': False,
        'child_certificate_number': data.get('child_certificate_number'),
    }

    if date_str != "-":
        parsed_date = parse_date(date_str)
        if not parsed_date:
            await message.answer(
                "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ\n"
                "Попробуйте снова:"
            )
            return
        child_data['child_certificate_date'] = parsed_date.strftime("%Y-%m-%d")

    try:
        await api.add_child(case_id, child_data)

        case = await api.get_case(case_id)
        children = await api.get_children(case_id)

        await message.answer(
            f"✅ Ребенок <b>{data['child_name']}</b> добавлен!\n\n"
            f"👶 <b>Дети</b>\n"
            f"Всего: {len(children)}",
            reply_markup=get_children_menu(case_id, case['case_number'], children),
            parse_mode="HTML"
        )
        await state.set_state(FamilyDataEdit.menu)

    except Exception as e:
        logger.error(f"Error adding child: {e}")
        await message.answer("❌ Ошибка добавления ребенка. Попробуйте позже.")
        await state.clear()


# ==================== CHILD PASSPORT PATH ====================

@router.callback_query(F.data.startswith("child_doc:") & F.data.contains(":passport"))
async def select_passport(callback: CallbackQuery, state: FSMContext):
    """Selected passport"""
    case_id = int(callback.data.split(":")[1])
    await state.update_data(child_has_certificate=False, child_has_passport=True)

    await callback.message.edit_text(
        "🛂 <b>Паспорт ребенка</b>\n\n"
        "Введите серию паспорта (4 цифры):",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.add_child_passport_series)
    await callback.answer()


@router.message(FamilyDataEdit.add_child_passport_series)
async def process_child_passport_series(message: Message, state: FSMContext):
    """Process passport series"""
    series = message.text.strip()

    if not series.isdigit() or len(series) != 4:
        await message.answer(
            "❌ Серия паспорта должна содержать 4 цифры.\n"
            "Попробуйте снова:"
        )
        return

    await state.update_data(child_passport_series=series)

    await message.answer(
        "🛂 Введите номер паспорта (6 цифр):",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.add_child_passport_number)


@router.message(FamilyDataEdit.add_child_passport_number)
async def process_child_passport_number(message: Message, state: FSMContext):
    """Process passport number"""
    number = message.text.strip()

    if not number.isdigit() or len(number) != 6:
        await message.answer(
            "❌ Номер паспорта должен содержать 6 цифр.\n"
            "Попробуйте снова:"
        )
        return

    await state.update_data(child_passport_number=number)

    await message.answer(
        "🛂 Введите кем выдан паспорт:",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.add_child_passport_issued_by)


@router.message(FamilyDataEdit.add_child_passport_issued_by)
async def process_child_passport_issued_by(message: Message, state: FSMContext):
    """Process passport issued by"""
    issued_by = message.text.strip()
    await state.update_data(child_passport_issued_by=issued_by)

    await message.answer(
        "📅 Введите дату выдачи паспорта (ДД.ММ.ГГГГ):",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.add_child_passport_date)


@router.message(FamilyDataEdit.add_child_passport_date)
async def process_child_passport_date(message: Message, state: FSMContext):
    """Process passport date"""
    date_str = message.text.strip()
    parsed_date = parse_date(date_str)

    if not parsed_date:
        await message.answer(
            "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ\n"
            "Попробуйте снова:"
        )
        return

    await state.update_data(child_passport_date=parsed_date.strftime("%Y-%m-%d"))

    await message.answer(
        "🛂 Введите код подразделения (6 цифр, формат XXX-XXX):\n"
        "(или отправьте <b>-</b> если неизвестен)",
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.add_child_passport_code)


@router.message(FamilyDataEdit.add_child_passport_code)
async def process_child_passport_code_and_save(message: Message, state: FSMContext):
    """Process passport code and save child"""
    code = message.text.strip()
    data = await state.get_data()
    case_id = data['case_id']

    child_data = {
        'child_name': data['child_name'],
        'child_birth_date': data['child_birth_date'],
        'child_has_certificate': False,
        'child_has_passport': True,
        'child_passport_series': data.get('child_passport_series'),
        'child_passport_number': data.get('child_passport_number'),
        'child_passport_issued_by': data.get('child_passport_issued_by'),
        'child_passport_date': data.get('child_passport_date'),
    }

    if code != "-":
        # Validate code format (6 digits with optional hyphen)
        clean_code = code.replace("-", "")
        if len(clean_code) != 6:
            await message.answer(
                "❌ Код подразделения должен содержать 6 цифр.\n"
                "Попробуйте снова:"
            )
            return
        child_data['child_passport_code'] = code

    try:
        await api.add_child(case_id, child_data)

        case = await api.get_case(case_id)
        children = await api.get_children(case_id)

        await message.answer(
            f"✅ Ребенок <b>{data['child_name']}</b> добавлен!\n\n"
            f"👶 <b>Дети</b>\n"
            f"Всего: {len(children)}",
            reply_markup=get_children_menu(case_id, case['case_number'], children),
            parse_mode="HTML"
        )
        await state.set_state(FamilyDataEdit.menu)

    except Exception as e:
        logger.error(f"Error adding child with passport: {e}")
        await message.answer("❌ Ошибка добавления ребенка. Попробуйте позже.")
        await state.clear()


# ==================== LIST CHILDREN ====================

@router.callback_query(F.data.startswith("children:") & F.data.endswith(":list"))
async def list_children(callback: CallbackQuery, state: FSMContext):
    """Show list of all children"""
    case_id = int(callback.data.split(":")[1])

    try:
        children = await api.get_children(case_id)

        if not children:
            await callback.answer("Нет детей", show_alert=True)
            return

        text = f"📋 <b>Список детей</b>\n\n"

        for i, child in enumerate(children, 1):
            text += f"{i}. <b>{child['child_name']}</b>\n"
            text += f"   Дата рождения: {child.get('child_birth_date', 'не указана')[:10]}\n"

            if child.get('child_has_passport'):
                text += f"   🛂 Паспорт: {child.get('child_passport_series', '')} {child.get('child_passport_number', '')}\n"
            elif child.get('child_has_certificate'):
                text += f"   📄 Св-во о рождении: {child.get('child_certificate_number', 'не указано')}\n"
            text += "\n"

        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_children_menu(case_id),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error listing children: {e}")
        await callback.answer("❌ Ошибка загрузки списка", show_alert=True)


# ==================== DELETE CHILD ====================

@router.callback_query(F.data.startswith("children:") & F.data.endswith(":delete"))
async def select_child_to_delete(callback: CallbackQuery, state: FSMContext):
    """Show children list for deletion"""
    case_id = int(callback.data.split(":")[1])

    try:
        children = await api.get_children(case_id)

        if not children:
            await callback.answer("Нет детей для удаления", show_alert=True)
            return

        await callback.message.edit_text(
            "🗑 <b>Удаление ребенка</b>\n\n"
            "Выберите ребенка для удаления:",
            reply_markup=get_children_list_keyboard(children, case_id),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)
        await state.set_state(FamilyDataEdit.delete_child_select)

    except Exception as e:
        logger.error(f"Error selecting child to delete: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("child:delete:") & ~F.data.contains(":confirm:"))
async def confirm_delete_child(callback: CallbackQuery, state: FSMContext):
    """Confirm deletion of child"""
    child_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    case_id = data.get('case_id')

    # Ask for confirmation
    await callback.message.edit_text(
        f"⚠️ <b>Подтверждение удаления</b>\n\n"
        f"Вы уверены, что хотите удалить этого ребенка?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"child:delete:confirm:{child_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"children:{case_id}:menu")]
        ]),
        parse_mode="HTML"
    )
    await state.set_state(FamilyDataEdit.delete_child_confirm)


@router.callback_query(F.data.startswith("child:delete:confirm:"))
async def delete_child_confirmed(callback: CallbackQuery, state: FSMContext):
    """Delete child after confirmation"""
    child_id = int(callback.data.split(":")[3])
    data = await state.get_data()
    case_id = data.get('case_id')

    try:
        await api.delete_child(child_id)

        case = await api.get_case(case_id)
        children = await api.get_children(case_id)

        await callback.message.edit_text(
            f"✅ Ребенок удален!\n\n"
            f"👶 <b>Дети</b>\n"
            f"Всего: {len(children)}",
            reply_markup=get_children_menu(case_id, case['case_number'], children),
            parse_mode="HTML"
        )
        await state.set_state(FamilyDataEdit.menu)

    except Exception as e:
        logger.error(f"Error deleting child: {e}")
        await callback.answer("❌ Ошибка удаления", show_alert=True)
