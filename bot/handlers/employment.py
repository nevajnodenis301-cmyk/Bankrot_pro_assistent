from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime
from states.case_states import EmploymentDataEdit
from keyboards.case_menu import (
    get_employment_menu,
    get_employment_status_keyboard,
    get_income_menu,
    get_income_list_keyboard,
    get_back_to_employment_menu,
    get_back_to_income_menu,
)
from services.api_client import APIClient
import logging

router = Router()
api = APIClient()
logger = logging.getLogger(__name__)


# ==================== EMPLOYMENT MENU ====================

@router.callback_query(F.data.startswith("case:") & F.data.endswith(":employment"))
async def show_employment_menu(callback: CallbackQuery, state: FSMContext):
    """Show employment data menu"""
    parts = callback.data.split(":")
    case_id = int(parts[1])

    try:
        case = await api.get_case(case_id)
        income_records = await api.get_income(case_id)
        case['income_records'] = income_records

        await callback.message.edit_text(
            f"💼 <b>Занятость</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Клиент: {case['full_name']}\n\n"
            f"Выберите действие:",
            reply_markup=get_employment_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(EmploymentDataEdit.menu)

    except Exception as e:
        logger.error(f"Error showing employment menu: {e}")
        await callback.answer("❌ Ошибка загрузки данных", show_alert=True)


@router.callback_query(F.data.startswith("employment:") & F.data.endswith(":menu"))
async def return_to_employment_menu(callback: CallbackQuery, state: FSMContext):
    """Return to employment menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        income_records = await api.get_income(case_id)
        case['income_records'] = income_records

        await callback.message.edit_text(
            f"💼 <b>Занятость</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Клиент: {case['full_name']}\n\n"
            f"Выберите действие:",
            reply_markup=get_employment_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(EmploymentDataEdit.menu)

    except Exception as e:
        logger.error(f"Error returning to employment menu: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ==================== EMPLOYMENT STATUS ====================

@router.callback_query(F.data.startswith("employment:") & F.data.endswith(":status"))
async def edit_employment_status(callback: CallbackQuery, state: FSMContext):
    """Start editing employment status"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "💼 <b>Статус занятости</b>\n\n"
        "Выберите текущий статус занятости:",
        reply_markup=get_employment_status_keyboard(case_id),
        parse_mode="HTML"
    )
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.callback_query(F.data.startswith("employ:status:"))
async def process_employment_status(callback: CallbackQuery, state: FSMContext):
    """Process employment status selection"""
    parts = callback.data.split(":")
    status = parts[2]
    case_id = int(parts[3])

    try:
        if status == "employed":
            # Save status and ask for employer
            await api.update_case_employment_data(case_id, {
                'is_employed': True,
                'is_self_employed': False
            })

            await callback.message.edit_text(
                "💼 <b>Информация о работодателе</b>\n\n"
                "Введите название организации-работодателя:",
                parse_mode="HTML"
            )
            await state.set_state(EmploymentDataEdit.edit_employer_name)
            await state.update_data(case_id=case_id)

        elif status == "self_employed":
            # Save status
            await api.update_case_employment_data(case_id, {
                'is_employed': False,
                'is_self_employed': True,
                'employer_name': None
            })

            # Return to menu with income options
            case = await api.get_case(case_id)
            income_records = await api.get_income(case_id)
            case['income_records'] = income_records

            await callback.message.edit_text(
                f"✅ Статус занятости обновлен!\n\n"
                f"💼 <b>Занятость</b>\n"
                f"Статус: Самозанятый\n\n"
                f"Теперь вы можете добавить информацию о доходах:",
                reply_markup=get_employment_menu(case_id, case['case_number'], case),
                parse_mode="HTML"
            )
            await state.set_state(EmploymentDataEdit.menu)

        else:  # unemployed
            # Save status
            await api.update_case_employment_data(case_id, {
                'is_employed': False,
                'is_self_employed': False,
                'employer_name': None
            })

            # Return to menu
            case = await api.get_case(case_id)
            income_records = await api.get_income(case_id)
            case['income_records'] = income_records

            await callback.message.edit_text(
                f"✅ Статус занятости обновлен!\n\n"
                f"💼 <b>Занятость</b>\n\n"
                f"Выберите действие:",
                reply_markup=get_employment_menu(case_id, case['case_number'], case),
                parse_mode="HTML"
            )
            await state.set_state(EmploymentDataEdit.menu)

    except Exception as e:
        logger.error(f"Error processing employment status: {e}")
        await callback.answer("❌ Ошибка сохранения", show_alert=True)


@router.message(EmploymentDataEdit.edit_employer_name)
async def process_employer_name(message: Message, state: FSMContext):
    """Process employer name"""
    employer_name = message.text.strip()
    data = await state.get_data()
    case_id = data['case_id']

    try:
        await api.update_case_employment_data(case_id, {'employer_name': employer_name})

        case = await api.get_case(case_id)
        income_records = await api.get_income(case_id)
        case['income_records'] = income_records

        await message.answer(
            f"✅ Информация о работодателе сохранена!\n\n"
            f"💼 <b>Занятость</b>\n"
            f"Статус: Трудоустроен ({employer_name})\n\n"
            f"Выберите действие:",
            reply_markup=get_employment_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.set_state(EmploymentDataEdit.menu)

    except Exception as e:
        logger.error(f"Error saving employer name: {e}")
        await message.answer("❌ Ошибка сохранения. Попробуйте позже.")
        await state.clear()


# ==================== INCOME MENU ====================

@router.callback_query(F.data.startswith("employment:") & F.data.endswith(":income"))
async def show_income_menu(callback: CallbackQuery, state: FSMContext):
    """Show income records menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        income_records = await api.get_income(case_id)

        await callback.message.edit_text(
            f"💰 <b>Доходы самозанятого</b>\n\n"
            f"Всего записей: {len(income_records)}\n\n"
            f"Выберите действие:",
            reply_markup=get_income_menu(case_id, income_records),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)

    except Exception as e:
        logger.error(f"Error showing income menu: {e}")
        await callback.answer("❌ Ошибка загрузки", show_alert=True)


@router.callback_query(F.data.startswith("income:") & F.data.endswith(":menu"))
async def return_to_income_menu(callback: CallbackQuery, state: FSMContext):
    """Return to income menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        income_records = await api.get_income(case_id)

        await callback.message.edit_text(
            f"💰 <b>Доходы самозанятого</b>\n\n"
            f"Всего записей: {len(income_records)}\n\n"
            f"Выберите действие:",
            reply_markup=get_income_menu(case_id, income_records),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)

    except Exception as e:
        logger.error(f"Error returning to income menu: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ==================== ADD INCOME ====================

@router.callback_query(F.data.startswith("income:") & F.data.endswith(":add"))
async def start_add_income(callback: CallbackQuery, state: FSMContext):
    """Start adding new income record"""
    case_id = int(callback.data.split(":")[1])

    current_year = datetime.now().year
    years_range = f"{current_year - 5}-{current_year}"

    await callback.message.edit_text(
        f"➕ <b>Добавление дохода</b>\n\n"
        f"Введите год ({years_range}):",
        parse_mode="HTML"
    )
    await state.set_state(EmploymentDataEdit.add_income_year)
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.message(EmploymentDataEdit.add_income_year)
async def process_income_year(message: Message, state: FSMContext):
    """Process income year"""
    year_str = message.text.strip()
    current_year = datetime.now().year

    try:
        year = int(year_str)
        if year < current_year - 5 or year > current_year:
            await message.answer(
                f"❌ Год должен быть в диапазоне {current_year - 5}-{current_year}.\n"
                f"Попробуйте снова:"
            )
            return
    except ValueError:
        await message.answer("❌ Введите корректный год (например: 2024).\nПопробуйте снова:")
        return

    await state.update_data(income_year=str(year))

    await message.answer(
        "💵 <b>Сумма дохода</b>\n\n"
        "Введите сумму дохода в рублях:",
        parse_mode="HTML"
    )
    await state.set_state(EmploymentDataEdit.add_income_rubles)


@router.message(EmploymentDataEdit.add_income_rubles)
async def process_income_rubles(message: Message, state: FSMContext):
    """Process income rubles"""
    try:
        rubles = int(message.text.replace(" ", "").replace(",", ""))
        if rubles < 0:
            raise ValueError("Negative amount")
    except ValueError:
        await message.answer(
            "❌ Введите корректную сумму (только цифры).\n"
            "Попробуйте снова:"
        )
        return

    await state.update_data(income_rubles=rubles)

    await message.answer(
        "💵 <b>Копейки</b>\n\n"
        "Введите копейки (0-99):\n"
        "(или отправьте <b>0</b> если нет копеек)",
        parse_mode="HTML"
    )
    await state.set_state(EmploymentDataEdit.add_income_kopecks)


@router.message(EmploymentDataEdit.add_income_kopecks)
async def process_income_kopecks(message: Message, state: FSMContext):
    """Process income kopecks"""
    try:
        kopecks = int(message.text.strip())
        if kopecks < 0 or kopecks > 99:
            raise ValueError("Invalid kopecks")
    except ValueError:
        await message.answer(
            "❌ Введите корректное количество копеек (0-99).\n"
            "Попробуйте снова:"
        )
        return

    await state.update_data(income_kopecks=kopecks)

    await message.answer(
        "📄 <b>Номер справки</b>\n\n"
        "Введите номер справки о доходах:\n"
        "(или отправьте <b>-</b> если неизвестен)",
        parse_mode="HTML"
    )
    await state.set_state(EmploymentDataEdit.add_income_cert_number)


@router.message(EmploymentDataEdit.add_income_cert_number)
async def process_income_cert_and_save(message: Message, state: FSMContext):
    """Process certificate number and save income"""
    cert_number = message.text.strip()
    data = await state.get_data()
    case_id = data['case_id']

    income_data = {
        'year': data['income_year'],
        'amount_rubles': data['income_rubles'],
        'amount_kopecks': data.get('income_kopecks', 0),
    }

    if cert_number != "-":
        income_data['certificate_number'] = cert_number

    try:
        await api.add_income(case_id, income_data)

        income_records = await api.get_income(case_id)
        amount_formatted = f"{data['income_rubles']:,}".replace(",", " ")

        await message.answer(
            f"✅ Доход за {data['income_year']} год добавлен!\n"
            f"Сумма: {amount_formatted} ₽\n\n"
            f"💰 <b>Доходы самозанятого</b>\n"
            f"Всего записей: {len(income_records)}",
            reply_markup=get_income_menu(case_id, income_records),
            parse_mode="HTML"
        )
        await state.set_state(EmploymentDataEdit.menu)

    except Exception as e:
        logger.error(f"Error adding income: {e}")
        await message.answer("❌ Ошибка добавления дохода. Попробуйте позже.")
        await state.clear()


# ==================== LIST INCOME ====================

@router.callback_query(F.data.startswith("income:") & F.data.endswith(":list"))
async def list_income(callback: CallbackQuery, state: FSMContext):
    """Show list of all income records"""
    case_id = int(callback.data.split(":")[1])

    try:
        income_records = await api.get_income(case_id)

        if not income_records:
            await callback.answer("Нет записей о доходах", show_alert=True)
            return

        text = f"📋 <b>Список доходов</b>\n\n"

        total = 0
        for income in income_records:
            year = income.get('year', '')
            rubles = income.get('amount_rubles', 0)
            kopecks = income.get('amount_kopecks', 0)
            cert = income.get('certificate_number', 'не указан')

            amount_formatted = f"{rubles:,}".replace(",", " ")
            text += f"📅 <b>{year}</b>: {amount_formatted},{kopecks:02d} ₽\n"
            text += f"   Справка: {cert}\n\n"
            total += rubles

        total_formatted = f"{total:,}".replace(",", " ")
        text += f"<b>Итого: {total_formatted} ₽</b>"

        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_income_menu(case_id),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error listing income: {e}")
        await callback.answer("❌ Ошибка загрузки списка", show_alert=True)


# ==================== DELETE INCOME ====================

@router.callback_query(F.data.startswith("income:") & F.data.endswith(":delete"))
async def select_income_to_delete(callback: CallbackQuery, state: FSMContext):
    """Show income list for deletion"""
    case_id = int(callback.data.split(":")[1])

    try:
        income_records = await api.get_income(case_id)

        if not income_records:
            await callback.answer("Нет записей для удаления", show_alert=True)
            return

        await callback.message.edit_text(
            "🗑 <b>Удаление записи о доходе</b>\n\n"
            "Выберите запись для удаления:",
            reply_markup=get_income_list_keyboard(income_records, case_id),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)
        await state.set_state(EmploymentDataEdit.delete_income_select)

    except Exception as e:
        logger.error(f"Error selecting income to delete: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("income:delete:") & ~F.data.contains(":confirm:"))
async def confirm_delete_income(callback: CallbackQuery, state: FSMContext):
    """Confirm deletion of income"""
    income_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    case_id = data.get('case_id')

    await callback.message.edit_text(
        f"⚠️ <b>Подтверждение удаления</b>\n\n"
        f"Вы уверены, что хотите удалить эту запись о доходе?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"income:delete:confirm:{income_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"income:{case_id}:menu")]
        ]),
        parse_mode="HTML"
    )
    await state.set_state(EmploymentDataEdit.delete_income_confirm)


@router.callback_query(F.data.startswith("income:delete:confirm:"))
async def delete_income_confirmed(callback: CallbackQuery, state: FSMContext):
    """Delete income after confirmation"""
    income_id = int(callback.data.split(":")[3])
    data = await state.get_data()
    case_id = data.get('case_id')

    try:
        await api.delete_income(income_id)

        income_records = await api.get_income(case_id)

        await callback.message.edit_text(
            f"✅ Запись о доходе удалена!\n\n"
            f"💰 <b>Доходы самозанятого</b>\n"
            f"Всего записей: {len(income_records)}",
            reply_markup=get_income_menu(case_id, income_records),
            parse_mode="HTML"
        )
        await state.set_state(EmploymentDataEdit.menu)

    except Exception as e:
        logger.error(f"Error deleting income: {e}")
        await callback.answer("❌ Ошибка удаления", show_alert=True)
