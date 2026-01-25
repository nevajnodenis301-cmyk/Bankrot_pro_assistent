from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.case_states import CreditorManagement
from keyboards.case_menu import (
    get_creditors_menu,
    get_creditor_selection_keyboard,
    get_creditor_edit_menu,
    get_confirm_delete_keyboard,
)
from services.api_client import APIClient
import logging

router = Router()
api = APIClient()
logger = logging.getLogger(__name__)


@router.callback_query(F.data.startswith("case:") & F.data.endswith(":creditors"))
async def show_creditors_menu(callback: CallbackQuery, state: FSMContext):
    """Show creditors management menu"""
    parts = callback.data.split(":")
    case_id = int(parts[1])

    try:
        case = await api.get_case(case_id)
        creditors_count = len(case.get('creditors', []))

        await callback.message.edit_text(
            f"💰 <b>Кредиторы</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Кредиторов: {creditors_count}\n\n"
            f"Выберите действие:",
            reply_markup=get_creditors_menu(case_id, case['case_number'], creditors_count),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(CreditorManagement.menu)
    except Exception as e:
        logger.error(f"Error showing creditors menu: {e}")
        await callback.answer("❌ Ошибка загрузки кредиторов", show_alert=True)


@router.callback_query(F.data.startswith("creditors:") & F.data.endswith(":menu"))
async def return_to_creditors_menu(callback: CallbackQuery, state: FSMContext):
    """Return to creditors menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        creditors_count = len(case.get('creditors', []))

        await callback.message.edit_text(
            f"💰 <b>Кредиторы</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Кредиторов: {creditors_count}\n\n"
            f"Выберите действие:",
            reply_markup=get_creditors_menu(case_id, case['case_number'], creditors_count),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(CreditorManagement.menu)
    except Exception as e:
        logger.error(f"Error returning to creditors menu: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ==================== ADD CREDITOR ====================

@router.callback_query(F.data.startswith("creditors:") & F.data.endswith(":add"))
async def start_add_creditor(callback: CallbackQuery, state: FSMContext):
    """Start adding new creditor"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "➕ <b>Добавление кредитора</b>\n\n"
        "Введите название организации-кредитора:\n"
        "<i>Например: ПАО Сбербанк</i>",
        parse_mode="HTML"
    )
    await state.set_state(CreditorManagement.add_name)
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.message(CreditorManagement.add_name)
async def process_creditor_name(message: Message, state: FSMContext):
    """Process creditor name and ask for OGRN"""
    await state.update_data(name=message.text.strip())

    await message.answer(
        "Введите ОГРН кредитора:\n"
        "<i>(13 цифр, например: 1027700132195)</i>\n\n"
        "Или отправьте <b>-</b> если неизвестен",
        parse_mode="HTML"
    )
    await state.set_state(CreditorManagement.add_ogrn)


@router.message(CreditorManagement.add_ogrn)
async def process_creditor_ogrn(message: Message, state: FSMContext):
    """Process OGRN and ask for INN"""
    ogrn = message.text.strip()

    # Validation
    if ogrn != "-" and (not ogrn.isdigit() or len(ogrn) != 13):
        await message.answer(
            "❌ ОГРН должен содержать ровно 13 цифр.\n"
            "Попробуйте снова или отправьте <b>-</b> если неизвестен:",
            parse_mode="HTML"
        )
        return

    await state.update_data(ogrn=None if ogrn == "-" else ogrn)

    await message.answer(
        "Введите ИНН кредитора:\n"
        "<i>(10 или 12 цифр)</i>\n\n"
        "Или отправьте <b>-</b> если неизвестен",
        parse_mode="HTML"
    )
    await state.set_state(CreditorManagement.add_inn)


@router.message(CreditorManagement.add_inn)
async def process_creditor_inn(message: Message, state: FSMContext):
    """Process INN and ask for address"""
    inn = message.text.strip()

    # Validation
    if inn != "-" and (not inn.isdigit() or len(inn) not in [10, 12]):
        await message.answer(
            "❌ ИНН должен содержать 10 или 12 цифр.\n"
            "Попробуйте снова или отправьте <b>-</b> если неизвестен:",
            parse_mode="HTML"
        )
        return

    await state.update_data(inn=None if inn == "-" else inn)

    await message.answer(
        "Введите юридический адрес кредитора:\n"
        "<i>Например: г. Москва, ул. Вавилова, д. 19</i>\n\n"
        "Или отправьте <b>-</b> если неизвестен",
        parse_mode="HTML"
    )
    await state.set_state(CreditorManagement.add_address)


@router.message(CreditorManagement.add_address)
async def process_creditor_address(message: Message, state: FSMContext):
    """Process address and ask for debt amount"""
    address = message.text.strip()
    await state.update_data(address=None if address == "-" else address)

    await message.answer(
        "Введите сумму задолженности перед этим кредитором в рублях:\n"
        "<i>Например: 500000</i>\n\n"
        "Или отправьте <b>0</b> если пока неизвестна",
        parse_mode="HTML"
    )
    await state.set_state(CreditorManagement.add_debt_amount)


@router.message(CreditorManagement.add_debt_amount)
async def process_creditor_debt_amount(message: Message, state: FSMContext):
    """Process debt amount and save creditor"""
    try:
        debt_amount = float(message.text.replace(",", "").replace(" ", ""))
    except ValueError:
        await message.answer("❌ Введите корректную сумму (только цифры). Попробуйте снова:")
        return

    data = await state.get_data()
    case_id = data['case_id']

    # Save creditor via API
    try:
        creditor_data = {
            "name": data['name'],
            "ogrn": data.get('ogrn'),
            "inn": data.get('inn'),
            "address": data.get('address'),
            "debt_amount": debt_amount if debt_amount > 0 else None
        }

        await api.add_creditor(case_id, creditor_data)

        # Get updated case
        case = await api.get_case(case_id)
        creditors_count = len(case.get('creditors', []))

        await message.answer(
            f"✅ Кредитор <b>{data['name']}</b> добавлен!\n\n"
            f"💰 <b>Кредиторы</b>\n"
            f"Всего: {creditors_count}",
            reply_markup=get_creditors_menu(case_id, case['case_number'], creditors_count),
            parse_mode="HTML"
        )

        await state.set_state(CreditorManagement.menu)

    except Exception as e:
        logger.error(f"Error adding creditor: {e}")
        await message.answer(
            f"❌ Ошибка при добавлении кредитора.\n\n"
            "Попробуйте снова позже."
        )
        await state.clear()


# ==================== LIST CREDITORS ====================

@router.callback_query(F.data.startswith("creditors:") & F.data.endswith(":list"))
async def list_creditors(callback: CallbackQuery, state: FSMContext):
    """Show list of all creditors"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        creditors = case.get('creditors', [])

        if not creditors:
            await callback.answer("Нет кредиторов", show_alert=True)
            return

        text = f"📋 <b>Список кредиторов</b>\n\n"

        for i, creditor in enumerate(creditors, 1):
            text += f"{i}. <b>{creditor['name']}</b>\n"
            if creditor.get('ogrn'):
                text += f"   ОГРН: {creditor['ogrn']}\n"
            if creditor.get('inn'):
                text += f"   ИНН: {creditor['inn']}\n"
            if creditor.get('address'):
                text += f"   Адрес: {creditor['address'][:50]}...\n" if len(creditor.get('address', '')) > 50 else f"   Адрес: {creditor['address']}\n"
            if creditor.get('debt_amount'):
                debt_formatted = f"{float(creditor['debt_amount']):,.0f}".replace(",", " ")
                text += f"   💰 Долг: {debt_formatted} ₽\n"
            text += "\n"

        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Назад", callback_data=f"creditors:{case_id}:menu")]
            ]),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error listing creditors: {e}")
        await callback.answer("❌ Ошибка загрузки списка", show_alert=True)


# ==================== EDIT CREDITOR ====================

@router.callback_query(F.data.startswith("creditors:") & F.data.endswith(":edit"))
async def select_creditor_to_edit(callback: CallbackQuery, state: FSMContext):
    """Show creditors list for edit selection"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        creditors = case.get('creditors', [])

        if not creditors:
            await callback.answer("Нет кредиторов для редактирования", show_alert=True)
            return

        await callback.message.edit_text(
            "✏️ <b>Редактирование кредитора</b>\n\n"
            "Выберите кредитора для редактирования:",
            reply_markup=get_creditor_selection_keyboard(creditors, 'edit', case_id),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)

    except Exception as e:
        logger.error(f"Error selecting creditor to edit: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("creditor:edit:") & ~F.data.contains(":confirm:"))
async def show_creditor_edit_menu(callback: CallbackQuery, state: FSMContext):
    """Show edit menu for selected creditor"""
    creditor_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    case_id = data.get('case_id')

    try:
        creditor = await api.get_creditor(creditor_id)

        debt_str = ""
        if creditor.get('debt_amount'):
            debt_formatted = f"{float(creditor['debt_amount']):,.0f}".replace(",", " ")
            debt_str = f"💰 Долг: {debt_formatted} ₽\n"

        await callback.message.edit_text(
            f"✏️ <b>Редактирование кредитора</b>\n\n"
            f"<b>{creditor['name']}</b>\n"
            f"ОГРН: {creditor.get('ogrn') or 'не указан'}\n"
            f"ИНН: {creditor.get('inn') or 'не указан'}\n"
            f"Адрес: {creditor.get('address') or 'не указан'}\n"
            f"{debt_str}\n"
            f"Выберите поле для редактирования:",
            reply_markup=get_creditor_edit_menu(creditor_id, case_id),
            parse_mode="HTML"
        )
        await state.update_data(creditor_id=creditor_id)

    except Exception as e:
        logger.error(f"Error showing creditor edit menu: {e}")
        await callback.answer("❌ Ошибка загрузки данных кредитора", show_alert=True)


@router.callback_query(F.data.startswith("crededit:"))
async def start_edit_creditor_field(callback: CallbackQuery, state: FSMContext):
    """Start editing a specific creditor field"""
    parts = callback.data.split(":")
    creditor_id = int(parts[1])
    field = parts[2]

    await state.update_data(creditor_id=creditor_id, edit_field=field)

    prompts = {
        'name': "Введите новое название кредитора:",
        'ogrn': "Введите новый ОГРН (13 цифр) или <b>-</b> для очистки:",
        'inn': "Введите новый ИНН (10 или 12 цифр) или <b>-</b> для очистки:",
        'address': "Введите новый адрес или <b>-</b> для очистки:",
        'debt': "Введите новую сумму долга в рублях или <b>0</b> для очистки:",
    }

    await callback.message.edit_text(
        f"✏️ <b>Редактирование</b>\n\n{prompts.get(field, 'Введите новое значение:')}",
        parse_mode="HTML"
    )
    await state.set_state(CreditorManagement.edit_name)
    await callback.answer()


@router.message(CreditorManagement.edit_name)
async def process_edit_creditor_field(message: Message, state: FSMContext):
    """Process edited creditor field"""
    data = await state.get_data()
    creditor_id = data.get('creditor_id')
    field = data.get('edit_field')
    case_id = data.get('case_id')
    value = message.text.strip()

    # Validation based on field
    update_data = {}

    if field == 'name':
        if not value:
            await message.answer("❌ Название не может быть пустым. Попробуйте снова:")
            return
        update_data['name'] = value

    elif field == 'ogrn':
        if value == "-":
            update_data['ogrn'] = None
        elif not value.isdigit() or len(value) != 13:
            await message.answer("❌ ОГРН должен содержать 13 цифр. Попробуйте снова:")
            return
        else:
            update_data['ogrn'] = value

    elif field == 'inn':
        if value == "-":
            update_data['inn'] = None
        elif not value.isdigit() or len(value) not in [10, 12]:
            await message.answer("❌ ИНН должен содержать 10 или 12 цифр. Попробуйте снова:")
            return
        else:
            update_data['inn'] = value

    elif field == 'address':
        update_data['address'] = None if value == "-" else value

    elif field == 'debt':
        try:
            debt = float(value.replace(",", "").replace(" ", ""))
            update_data['debt_amount'] = debt if debt > 0 else None
        except ValueError:
            await message.answer("❌ Введите корректную сумму. Попробуйте снова:")
            return

    try:
        await api.update_creditor(creditor_id, update_data)

        # Return to creditors menu
        case = await api.get_case(case_id)
        creditors_count = len(case.get('creditors', []))

        await message.answer(
            f"✅ Данные кредитора обновлены!\n\n"
            f"💰 <b>Кредиторы</b>\n"
            f"Всего: {creditors_count}",
            reply_markup=get_creditors_menu(case_id, case['case_number'], creditors_count),
            parse_mode="HTML"
        )
        await state.set_state(CreditorManagement.menu)

    except Exception as e:
        logger.error(f"Error updating creditor: {e}")
        await message.answer("❌ Ошибка при обновлении данных. Попробуйте позже.")
        await state.clear()


# ==================== DELETE CREDITOR ====================

@router.callback_query(F.data.startswith("creditors:") & F.data.endswith(":delete"))
async def select_creditor_to_delete(callback: CallbackQuery, state: FSMContext):
    """Show creditors list for deletion selection"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        creditors = case.get('creditors', [])

        if not creditors:
            await callback.answer("Нет кредиторов для удаления", show_alert=True)
            return

        await callback.message.edit_text(
            "🗑 <b>Удаление кредитора</b>\n\n"
            "Выберите кредитора для удаления:",
            reply_markup=get_creditor_selection_keyboard(creditors, 'delete', case_id),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)

    except Exception as e:
        logger.error(f"Error selecting creditor to delete: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("creditor:delete:") & ~F.data.contains(":confirm:"))
async def confirm_delete_creditor(callback: CallbackQuery, state: FSMContext):
    """Ask for confirmation before deleting"""
    creditor_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    case_id = data.get('case_id')

    try:
        creditor = await api.get_creditor(creditor_id)

        await callback.message.edit_text(
            f"⚠️ <b>Подтверждение удаления</b>\n\n"
            f"Вы уверены, что хотите удалить кредитора:\n"
            f"<b>{creditor['name']}</b>?\n\n"
            f"⚠️ Все связанные задолженности также будут удалены.",
            reply_markup=get_confirm_delete_keyboard('creditor', creditor_id, case_id),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error confirming delete creditor: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("creditor:delete:confirm:"))
async def delete_creditor_confirmed(callback: CallbackQuery, state: FSMContext):
    """Delete creditor after confirmation"""
    creditor_id = int(callback.data.split(":")[3])
    data = await state.get_data()
    case_id = data.get('case_id')

    try:
        await api.delete_creditor(creditor_id)

        # Get updated case
        case = await api.get_case(case_id)
        creditors_count = len(case.get('creditors', []))

        await callback.message.edit_text(
            f"✅ Кредитор удален!\n\n"
            f"💰 <b>Кредиторы</b>\n"
            f"Всего: {creditors_count}",
            reply_markup=get_creditors_menu(case_id, case['case_number'], creditors_count),
            parse_mode="HTML"
        )
        await state.set_state(CreditorManagement.menu)

    except Exception as e:
        logger.error(f"Error deleting creditor: {e}")
        await callback.answer("❌ Ошибка удаления", show_alert=True)
