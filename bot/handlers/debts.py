from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.case_states import DebtManagement
from keyboards.case_menu import (
    get_debts_menu,
    get_debt_selection_keyboard,
    get_creditor_for_debt_keyboard,
    get_debt_edit_menu,
    get_confirm_delete_keyboard,
)
from services.api_client import APIClient
import logging

router = Router()
api = APIClient()
logger = logging.getLogger(__name__)


async def calculate_total_debt(debts: list) -> float:
    """Calculate total debt from debts list"""
    total = 0
    for debt in debts:
        rubles = debt.get('amount_rubles', 0) or 0
        kopecks = debt.get('amount_kopecks', 0) or 0
        total += rubles + kopecks / 100
    return total


@router.callback_query(F.data.startswith("case:") & F.data.endswith(":debts"))
async def show_debts_menu(callback: CallbackQuery, state: FSMContext):
    """Show debts management menu"""
    parts = callback.data.split(":")
    case_id = int(parts[1])

    try:
        case = await api.get_case(case_id)
        debts = case.get('debts', [])
        debts_count = len(debts)
        total_debt = await calculate_total_debt(debts)

        await callback.message.edit_text(
            f"📊 <b>Задолженность</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Записей: {debts_count}\n\n"
            f"Выберите действие:",
            reply_markup=get_debts_menu(case_id, case['case_number'], debts_count, total_debt),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(DebtManagement.menu)
    except Exception as e:
        logger.error(f"Error showing debts menu: {e}")
        await callback.answer("❌ Ошибка загрузки задолженностей", show_alert=True)


@router.callback_query(F.data.startswith("debts:") & F.data.endswith(":menu"))
async def return_to_debts_menu(callback: CallbackQuery, state: FSMContext):
    """Return to debts menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        debts = case.get('debts', [])
        debts_count = len(debts)
        total_debt = await calculate_total_debt(debts)

        await callback.message.edit_text(
            f"📊 <b>Задолженность</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Записей: {debts_count}\n\n"
            f"Выберите действие:",
            reply_markup=get_debts_menu(case_id, case['case_number'], debts_count, total_debt),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(DebtManagement.menu)
    except Exception as e:
        logger.error(f"Error returning to debts menu: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# Noop callback handler
@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery):
    """Handle noop callbacks (info buttons)"""
    await callback.answer()


# ==================== ADD DEBT ====================

@router.callback_query(F.data.startswith("debts:") & F.data.endswith(":add"))
async def start_add_debt(callback: CallbackQuery, state: FSMContext):
    """Start adding new debt - first select creditor"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        creditors = case.get('creditors', [])

        await callback.message.edit_text(
            "➕ <b>Добавление задолженности</b>\n\n"
            "Выберите кредитора или введите название вручную:",
            reply_markup=get_creditor_for_debt_keyboard(creditors, case_id),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)
        await state.set_state(DebtManagement.add_creditor_select)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error starting add debt: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("debtcred:"), DebtManagement.add_creditor_select)
async def select_creditor_for_debt(callback: CallbackQuery, state: FSMContext):
    """Process creditor selection for new debt"""
    creditor_part = callback.data.split(":")[1]

    if creditor_part == "manual":
        await callback.message.edit_text(
            "✍️ <b>Добавление задолженности</b>\n\n"
            "Введите название кредитора:",
            parse_mode="HTML"
        )
        await state.update_data(creditor_id=None)
        await state.set_state(DebtManagement.add_creditor_select)
        await callback.answer()
        return

    # Creditor selected from list
    creditor_id = int(creditor_part)

    try:
        creditor = await api.get_creditor(creditor_id)
        await state.update_data(
            creditor_id=creditor_id,
            creditor_name=creditor['name']
        )

        await callback.message.edit_text(
            f"💰 <b>Добавление задолженности</b>\n\n"
            f"Кредитор: <b>{creditor['name']}</b>\n\n"
            f"Введите сумму задолженности в <b>рублях</b>:\n"
            f"<i>Например: 150000</i>",
            parse_mode="HTML"
        )
        await state.set_state(DebtManagement.add_amount_rubles)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error selecting creditor for debt: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.message(DebtManagement.add_creditor_select)
async def process_manual_creditor_name(message: Message, state: FSMContext):
    """Process manually entered creditor name"""
    creditor_name = message.text.strip()
    await state.update_data(creditor_id=None, creditor_name=creditor_name)

    await message.answer(
        f"💰 <b>Добавление задолженности</b>\n\n"
        f"Кредитор: <b>{creditor_name}</b>\n\n"
        f"Введите сумму задолженности в <b>рублях</b>:\n"
        f"<i>Например: 150000</i>",
        parse_mode="HTML"
    )
    await state.set_state(DebtManagement.add_amount_rubles)


@router.message(DebtManagement.add_amount_rubles)
async def process_debt_amount_rubles(message: Message, state: FSMContext):
    """Process debt amount in rubles"""
    try:
        rubles = int(message.text.replace(",", "").replace(" ", ""))
        if rubles < 0:
            raise ValueError("Negative value")
    except ValueError:
        await message.answer(
            "❌ Введите корректную сумму в рублях (целое число).\n"
            "Попробуйте снова:",
            parse_mode="HTML"
        )
        return

    await state.update_data(amount_rubles=rubles)

    await message.answer(
        f"Введите сумму в <b>копейках</b>:\n"
        f"<i>Например: 50 (для 50 копеек)</i>\n\n"
        f"Или отправьте <b>0</b> если копеек нет",
        parse_mode="HTML"
    )
    await state.set_state(DebtManagement.add_amount_kopecks)


@router.message(DebtManagement.add_amount_kopecks)
async def process_debt_amount_kopecks(message: Message, state: FSMContext):
    """Process debt amount in kopecks"""
    try:
        kopecks = int(message.text.replace(",", "").replace(" ", ""))
        if kopecks < 0 or kopecks > 99:
            raise ValueError("Invalid kopecks value")
    except ValueError:
        await message.answer(
            "❌ Введите корректную сумму копеек (0-99).\n"
            "Попробуйте снова:",
            parse_mode="HTML"
        )
        return

    await state.update_data(amount_kopecks=kopecks)

    await message.answer(
        f"Введите источник информации о задолженности:\n"
        f"<i>Например: ОКБ, СКОРИНГ БЮРО, договор №123</i>\n\n"
        f"Или отправьте <b>-</b> если неизвестен",
        parse_mode="HTML"
    )
    await state.set_state(DebtManagement.add_source)


@router.message(DebtManagement.add_source)
async def process_debt_source(message: Message, state: FSMContext):
    """Process debt source and save debt"""
    source = message.text.strip()
    data = await state.get_data()
    case_id = data['case_id']

    try:
        debt_data = {
            "creditor_name": data['creditor_name'],
            "amount_rubles": data['amount_rubles'],
            "amount_kopecks": data['amount_kopecks'],
            "source": None if source == "-" else source,
            "creditor_id": data.get('creditor_id')
        }

        await api.add_debt(case_id, debt_data)

        # Get updated case
        case = await api.get_case(case_id)
        debts = case.get('debts', [])
        debts_count = len(debts)
        total_debt = await calculate_total_debt(debts)

        amount = data['amount_rubles'] + data['amount_kopecks'] / 100
        amount_formatted = f"{amount:,.2f}".replace(",", " ")

        await message.answer(
            f"✅ Задолженность добавлена!\n\n"
            f"Кредитор: {data['creditor_name']}\n"
            f"Сумма: {amount_formatted} ₽\n\n"
            f"📊 <b>Задолженность</b>\n"
            f"Записей: {debts_count}",
            reply_markup=get_debts_menu(case_id, case['case_number'], debts_count, total_debt),
            parse_mode="HTML"
        )

        await state.set_state(DebtManagement.menu)

    except Exception as e:
        logger.error(f"Error adding debt: {e}")
        await message.answer(
            f"❌ Ошибка при добавлении задолженности.\n\n"
            "Попробуйте снова позже."
        )
        await state.clear()


# ==================== LIST DEBTS ====================

@router.callback_query(F.data.startswith("debts:") & F.data.endswith(":list"))
async def list_debts(callback: CallbackQuery, state: FSMContext):
    """Show list of all debts"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        debts = case.get('debts', [])

        if not debts:
            await callback.answer("Нет задолженностей", show_alert=True)
            return

        text = f"📋 <b>Список задолженностей</b>\n\n"

        total = 0
        for i, debt in enumerate(debts, 1):
            rubles = debt.get('amount_rubles', 0) or 0
            kopecks = debt.get('amount_kopecks', 0) or 0
            amount = rubles + kopecks / 100
            total += amount
            amount_formatted = f"{amount:,.2f}".replace(",", " ")

            text += f"{i}. <b>{debt['creditor_name']}</b>\n"
            text += f"   💰 Сумма: {amount_formatted} ₽\n"
            if debt.get('source'):
                text += f"   📄 Источник: {debt['source']}\n"
            text += "\n"

        total_formatted = f"{total:,.2f}".replace(",", " ")
        text += f"<b>Итого: {total_formatted} ₽</b>"

        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Назад", callback_data=f"debts:{case_id}:menu")]
            ]),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error listing debts: {e}")
        await callback.answer("❌ Ошибка загрузки списка", show_alert=True)


# ==================== EDIT DEBT ====================

@router.callback_query(F.data.startswith("debts:") & F.data.endswith(":edit"))
async def select_debt_to_edit(callback: CallbackQuery, state: FSMContext):
    """Show debts list for edit selection"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        debts = case.get('debts', [])

        if not debts:
            await callback.answer("Нет задолженностей для редактирования", show_alert=True)
            return

        await callback.message.edit_text(
            "✏️ <b>Редактирование задолженности</b>\n\n"
            "Выберите запись для редактирования:",
            reply_markup=get_debt_selection_keyboard(debts, 'edit', case_id),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)

    except Exception as e:
        logger.error(f"Error selecting debt to edit: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("debt:edit:") & ~F.data.contains(":confirm:"))
async def show_debt_edit_menu(callback: CallbackQuery, state: FSMContext):
    """Show edit menu for selected debt"""
    debt_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    case_id = data.get('case_id')

    try:
        debt = await api.get_debt(debt_id)

        rubles = debt.get('amount_rubles', 0) or 0
        kopecks = debt.get('amount_kopecks', 0) or 0
        amount = rubles + kopecks / 100
        amount_formatted = f"{amount:,.2f}".replace(",", " ")

        await callback.message.edit_text(
            f"✏️ <b>Редактирование задолженности</b>\n\n"
            f"Кредитор: <b>{debt['creditor_name']}</b>\n"
            f"Сумма: {amount_formatted} ₽\n"
            f"Источник: {debt.get('source') or 'не указан'}\n\n"
            f"Выберите поле для редактирования:",
            reply_markup=get_debt_edit_menu(debt_id, case_id),
            parse_mode="HTML"
        )
        await state.update_data(debt_id=debt_id)

    except Exception as e:
        logger.error(f"Error showing debt edit menu: {e}")
        await callback.answer("❌ Ошибка загрузки данных", show_alert=True)


@router.callback_query(F.data.startswith("debtedit:"))
async def start_edit_debt_field(callback: CallbackQuery, state: FSMContext):
    """Start editing a specific debt field"""
    parts = callback.data.split(":")
    debt_id = int(parts[1])
    field = parts[2]

    await state.update_data(debt_id=debt_id, edit_field=field)

    prompts = {
        'creditor': "Введите новое название кредитора:",
        'rubles': "Введите новую сумму в рублях:",
        'kopecks': "Введите новую сумму в копейках (0-99):",
        'source': "Введите новый источник или <b>-</b> для очистки:",
    }

    await callback.message.edit_text(
        f"✏️ <b>Редактирование</b>\n\n{prompts.get(field, 'Введите новое значение:')}",
        parse_mode="HTML"
    )
    await state.set_state(DebtManagement.edit_amount_rubles)
    await callback.answer()


@router.message(DebtManagement.edit_amount_rubles)
async def process_edit_debt_field(message: Message, state: FSMContext):
    """Process edited debt field"""
    data = await state.get_data()
    debt_id = data.get('debt_id')
    field = data.get('edit_field')
    case_id = data.get('case_id')
    value = message.text.strip()

    update_data = {}

    if field == 'creditor':
        if not value:
            await message.answer("❌ Название не может быть пустым. Попробуйте снова:")
            return
        update_data['creditor_name'] = value

    elif field == 'rubles':
        try:
            rubles = int(value.replace(",", "").replace(" ", ""))
            if rubles < 0:
                raise ValueError()
            update_data['amount_rubles'] = rubles
        except ValueError:
            await message.answer("❌ Введите корректную сумму. Попробуйте снова:")
            return

    elif field == 'kopecks':
        try:
            kopecks = int(value)
            if kopecks < 0 or kopecks > 99:
                raise ValueError()
            update_data['amount_kopecks'] = kopecks
        except ValueError:
            await message.answer("❌ Введите значение от 0 до 99. Попробуйте снова:")
            return

    elif field == 'source':
        update_data['source'] = None if value == "-" else value

    try:
        await api.update_debt(debt_id, update_data)

        # Return to debts menu
        case = await api.get_case(case_id)
        debts = case.get('debts', [])
        debts_count = len(debts)
        total_debt = await calculate_total_debt(debts)

        await message.answer(
            f"✅ Данные обновлены!\n\n"
            f"📊 <b>Задолженность</b>\n"
            f"Записей: {debts_count}",
            reply_markup=get_debts_menu(case_id, case['case_number'], debts_count, total_debt),
            parse_mode="HTML"
        )
        await state.set_state(DebtManagement.menu)

    except Exception as e:
        logger.error(f"Error updating debt: {e}")
        await message.answer("❌ Ошибка при обновлении данных. Попробуйте позже.")
        await state.clear()


# ==================== DELETE DEBT ====================

@router.callback_query(F.data.startswith("debts:") & F.data.endswith(":delete"))
async def select_debt_to_delete(callback: CallbackQuery, state: FSMContext):
    """Show debts list for deletion selection"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        debts = case.get('debts', [])

        if not debts:
            await callback.answer("Нет задолженностей для удаления", show_alert=True)
            return

        await callback.message.edit_text(
            "🗑 <b>Удаление задолженности</b>\n\n"
            "Выберите запись для удаления:",
            reply_markup=get_debt_selection_keyboard(debts, 'delete', case_id),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)

    except Exception as e:
        logger.error(f"Error selecting debt to delete: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("debt:delete:") & ~F.data.contains(":confirm:"))
async def confirm_delete_debt(callback: CallbackQuery, state: FSMContext):
    """Ask for confirmation before deleting"""
    debt_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    case_id = data.get('case_id')

    try:
        debt = await api.get_debt(debt_id)

        rubles = debt.get('amount_rubles', 0) or 0
        kopecks = debt.get('amount_kopecks', 0) or 0
        amount = rubles + kopecks / 100
        amount_formatted = f"{amount:,.2f}".replace(",", " ")

        await callback.message.edit_text(
            f"⚠️ <b>Подтверждение удаления</b>\n\n"
            f"Вы уверены, что хотите удалить задолженность:\n"
            f"<b>{debt['creditor_name']}</b>\n"
            f"Сумма: {amount_formatted} ₽?",
            reply_markup=get_confirm_delete_keyboard('debt', debt_id, case_id),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error confirming delete debt: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("debt:delete:confirm:"))
async def delete_debt_confirmed(callback: CallbackQuery, state: FSMContext):
    """Delete debt after confirmation"""
    debt_id = int(callback.data.split(":")[3])
    data = await state.get_data()
    case_id = data.get('case_id')

    try:
        await api.delete_debt(debt_id)

        # Get updated case
        case = await api.get_case(case_id)
        debts = case.get('debts', [])
        debts_count = len(debts)
        total_debt = await calculate_total_debt(debts)

        await callback.message.edit_text(
            f"✅ Задолженность удалена!\n\n"
            f"📊 <b>Задолженность</b>\n"
            f"Записей: {debts_count}",
            reply_markup=get_debts_menu(case_id, case['case_number'], debts_count, total_debt),
            parse_mode="HTML"
        )
        await state.set_state(DebtManagement.menu)

    except Exception as e:
        logger.error(f"Error deleting debt: {e}")
        await callback.answer("❌ Ошибка удаления", show_alert=True)
