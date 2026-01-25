from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from states.case_states import TransactionManagement
from keyboards.case_menu import (
    get_transactions_menu,
    get_transaction_type_keyboard,
    get_transactions_list_keyboard,
    get_back_to_transactions_menu,
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


def is_within_3_years(date: datetime) -> bool:
    """Check if date is within last 3 years"""
    three_years_ago = datetime.now() - timedelta(days=3*365)
    return date >= three_years_ago


# ==================== TRANSACTIONS MENU ====================

@router.callback_query(F.data.startswith("case:") & F.data.endswith(":transactions"))
async def show_transactions_menu(callback: CallbackQuery, state: FSMContext):
    """Show transactions menu"""
    parts = callback.data.split(":")
    case_id = int(parts[1])

    try:
        case = await api.get_case(case_id)
        transactions = await api.get_transactions(case_id)

        await callback.message.edit_text(
            f"📝 <b>Сделки за последние 3 года</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Клиент: {case['full_name']}\n\n"
            f"Всего сделок: {len(transactions)}\n\n"
            f"Выберите действие:",
            reply_markup=get_transactions_menu(case_id, case['case_number'], transactions),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(TransactionManagement.menu)

    except Exception as e:
        logger.error(f"Error showing transactions menu: {e}")
        await callback.answer("❌ Ошибка загрузки данных", show_alert=True)


@router.callback_query(F.data.startswith("transactions:") & F.data.endswith(":menu"))
async def return_to_transactions_menu(callback: CallbackQuery, state: FSMContext):
    """Return to transactions menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        transactions = await api.get_transactions(case_id)

        await callback.message.edit_text(
            f"📝 <b>Сделки за последние 3 года</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Всего сделок: {len(transactions)}\n\n"
            f"Выберите действие:",
            reply_markup=get_transactions_menu(case_id, case['case_number'], transactions),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(TransactionManagement.menu)

    except Exception as e:
        logger.error(f"Error returning to transactions menu: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ==================== ADD TRANSACTION ====================

@router.callback_query(F.data.startswith("transactions:") & F.data.endswith(":add"))
async def start_add_transaction(callback: CallbackQuery, state: FSMContext):
    """Start adding new transaction"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "➕ <b>Добавление сделки</b>\n\n"
        "Выберите тип сделки:",
        reply_markup=get_transaction_type_keyboard(case_id),
        parse_mode="HTML"
    )
    await state.set_state(TransactionManagement.add_transaction_type)
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.callback_query(F.data.startswith("trans_type:"))
async def process_transaction_type(callback: CallbackQuery, state: FSMContext):
    """Process transaction type selection"""
    parts = callback.data.split(":")
    case_id = int(parts[1])
    trans_type = parts[2]

    type_names = {
        'real_estate': 'Недвижимость',
        'securities': 'Ценные бумаги',
        'llc_shares': 'Доли в ООО',
        'vehicles': 'Транспорт'
    }

    await state.update_data(transaction_type=trans_type, case_id=case_id)

    await callback.message.edit_text(
        f"📝 <b>Сделка: {type_names.get(trans_type, trans_type)}</b>\n\n"
        f"Введите описание сделки (минимум 5 символов):\n"
        f"(например: Продажа квартиры по адресу...)",
        parse_mode="HTML"
    )
    await state.set_state(TransactionManagement.add_transaction_description)
    await callback.answer()


@router.message(TransactionManagement.add_transaction_description)
async def process_transaction_description(message: Message, state: FSMContext):
    """Process transaction description"""
    description = message.text.strip()

    if len(description) < 5:
        await message.answer(
            "❌ Описание должно содержать минимум 5 символов.\n"
            "Попробуйте снова:"
        )
        return

    await state.update_data(description=description)

    await message.answer(
        "📅 <b>Дата сделки</b>\n\n"
        "Введите дату совершения сделки (ДД.ММ.ГГГГ):\n"
        "<i>Дата должна быть в пределах последних 3 лет</i>",
        parse_mode="HTML"
    )
    await state.set_state(TransactionManagement.add_transaction_date)


@router.message(TransactionManagement.add_transaction_date)
async def process_transaction_date(message: Message, state: FSMContext):
    """Process transaction date"""
    date_str = message.text.strip()
    parsed_date = parse_date(date_str)

    if not parsed_date:
        await message.answer(
            "❌ Неверный формат даты. Используйте ДД.ММ.ГГГГ\n"
            "(например: 15.06.2023)\n\n"
            "Попробуйте снова:"
        )
        return

    if not is_within_3_years(parsed_date):
        await message.answer(
            "❌ Дата должна быть в пределах последних 3 лет.\n"
            "Попробуйте снова:"
        )
        return

    if parsed_date > datetime.now():
        await message.answer(
            "❌ Дата не может быть в будущем.\n"
            "Попробуйте снова:"
        )
        return

    await state.update_data(transaction_date=parsed_date.strftime("%Y-%m-%d"))

    await message.answer(
        "💰 <b>Сумма сделки</b>\n\n"
        "Введите сумму сделки в рублях:\n"
        "(или отправьте <b>0</b> если сумма неизвестна)",
        parse_mode="HTML"
    )
    await state.set_state(TransactionManagement.add_transaction_amount)


@router.message(TransactionManagement.add_transaction_amount)
async def process_transaction_amount_and_save(message: Message, state: FSMContext):
    """Process transaction amount and save"""
    amount_str = message.text.strip().replace(" ", "").replace(",", "")

    try:
        amount = float(amount_str)
        if amount < 0:
            raise ValueError("Negative amount")
    except ValueError:
        await message.answer(
            "❌ Введите корректную сумму (только цифры).\n"
            "Попробуйте снова:"
        )
        return

    data = await state.get_data()
    case_id = data['case_id']

    transaction_data = {
        'transaction_type': data['transaction_type'],
        'description': data['description'],
        'transaction_date': data['transaction_date'],
        'amount': amount if amount > 0 else None
    }

    try:
        await api.add_transaction(case_id, transaction_data)

        transactions = await api.get_transactions(case_id)
        case = await api.get_case(case_id)

        type_names = {
            'real_estate': 'Недвижимость',
            'securities': 'Ценные бумаги',
            'llc_shares': 'Доли в ООО',
            'vehicles': 'Транспорт'
        }

        await message.answer(
            f"✅ Сделка добавлена!\n"
            f"Тип: {type_names.get(data['transaction_type'], data['transaction_type'])}\n\n"
            f"📝 <b>Сделки за последние 3 года</b>\n"
            f"Всего: {len(transactions)}",
            reply_markup=get_transactions_menu(case_id, case['case_number'], transactions),
            parse_mode="HTML"
        )
        await state.set_state(TransactionManagement.menu)

    except Exception as e:
        logger.error(f"Error adding transaction: {e}")
        await message.answer("❌ Ошибка добавления сделки. Попробуйте позже.")
        await state.clear()


# ==================== LIST TRANSACTIONS ====================

@router.callback_query(F.data.startswith("transactions:") & F.data.contains(":list:"))
async def list_transactions_by_type(callback: CallbackQuery, state: FSMContext):
    """Show transactions filtered by type"""
    parts = callback.data.split(":")
    case_id = int(parts[1])
    trans_type = parts[3]

    type_names = {
        'real_estate': 'Недвижимость',
        'securities': 'Ценные бумаги',
        'llc_shares': 'Доли в ООО',
        'vehicles': 'Транспорт'
    }

    try:
        transactions = await api.get_transactions(case_id, trans_type)

        if not transactions:
            await callback.answer(f"Нет сделок типа '{type_names.get(trans_type, trans_type)}'", show_alert=True)
            return

        text = f"📋 <b>Сделки: {type_names.get(trans_type, trans_type)}</b>\n\n"

        for i, trans in enumerate(transactions, 1):
            desc = trans.get('description', '')
            date_str = trans.get('transaction_date', '')
            if date_str:
                date_str = date_str[:10]
            amount = trans.get('amount')

            text += f"{i}. <b>{desc[:50]}</b>\n"
            text += f"   📅 Дата: {date_str}\n"
            if amount:
                amount_formatted = f"{float(amount):,.0f}".replace(",", " ")
                text += f"   💰 Сумма: {amount_formatted} ₽\n"
            text += "\n"

        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_transactions_menu(case_id),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error listing transactions: {e}")
        await callback.answer("❌ Ошибка загрузки списка", show_alert=True)


# ==================== DELETE TRANSACTION ====================

@router.callback_query(F.data.startswith("transactions:") & F.data.endswith(":delete"))
async def select_transaction_to_delete(callback: CallbackQuery, state: FSMContext):
    """Show transactions list for deletion"""
    case_id = int(callback.data.split(":")[1])

    try:
        transactions = await api.get_transactions(case_id)

        if not transactions:
            await callback.answer("Нет сделок для удаления", show_alert=True)
            return

        await callback.message.edit_text(
            "🗑 <b>Удаление сделки</b>\n\n"
            "Выберите сделку для удаления:",
            reply_markup=get_transactions_list_keyboard(transactions, case_id),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)
        await state.set_state(TransactionManagement.delete_transaction_select)

    except Exception as e:
        logger.error(f"Error selecting transaction to delete: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("transaction:delete:") & ~F.data.contains(":confirm:"))
async def confirm_delete_transaction(callback: CallbackQuery, state: FSMContext):
    """Confirm deletion of transaction"""
    transaction_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    case_id = data.get('case_id')

    await callback.message.edit_text(
        f"⚠️ <b>Подтверждение удаления</b>\n\n"
        f"Вы уверены, что хотите удалить эту сделку?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"transaction:delete:confirm:{transaction_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"transactions:{case_id}:menu")]
        ]),
        parse_mode="HTML"
    )
    await state.set_state(TransactionManagement.delete_transaction_confirm)


@router.callback_query(F.data.startswith("transaction:delete:confirm:"))
async def delete_transaction_confirmed(callback: CallbackQuery, state: FSMContext):
    """Delete transaction after confirmation"""
    transaction_id = int(callback.data.split(":")[3])
    data = await state.get_data()
    case_id = data.get('case_id')

    try:
        await api.delete_transaction(transaction_id)

        transactions = await api.get_transactions(case_id)
        case = await api.get_case(case_id)

        await callback.message.edit_text(
            f"✅ Сделка удалена!\n\n"
            f"📝 <b>Сделки за последние 3 года</b>\n"
            f"Всего: {len(transactions)}",
            reply_markup=get_transactions_menu(case_id, case['case_number'], transactions),
            parse_mode="HTML"
        )
        await state.set_state(TransactionManagement.menu)

    except Exception as e:
        logger.error(f"Error deleting transaction: {e}")
        await callback.answer("❌ Ошибка удаления", show_alert=True)
