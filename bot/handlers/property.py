from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from datetime import datetime
from states.case_states import PropertyManagement
from keyboards.case_menu import (
    get_property_menu,
    get_vehicles_menu,
    get_vehicle_pledged_keyboard,
    get_vehicles_list_keyboard,
    get_back_to_property_menu,
    get_back_to_vehicles_menu,
)
from services.api_client import APIClient
import logging

router = Router()
api = APIClient()
logger = logging.getLogger(__name__)


# ==================== PROPERTY MENU ====================

@router.callback_query(F.data.startswith("case:") & F.data.endswith(":property"))
async def show_property_menu(callback: CallbackQuery, state: FSMContext):
    """Show property data menu"""
    parts = callback.data.split(":")
    case_id = int(parts[1])

    try:
        case = await api.get_case(case_id)
        properties = await api.get_properties(case_id)
        case['properties'] = properties

        await callback.message.edit_text(
            f"🏠 <b>Имущество</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Клиент: {case['full_name']}\n\n"
            f"Выберите действие:",
            reply_markup=get_property_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(PropertyManagement.menu)

    except Exception as e:
        logger.error(f"Error showing property menu: {e}")
        await callback.answer("❌ Ошибка загрузки данных", show_alert=True)


@router.callback_query(F.data.startswith("property:") & F.data.endswith(":menu"))
async def return_to_property_menu(callback: CallbackQuery, state: FSMContext):
    """Return to property menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)
        properties = await api.get_properties(case_id)
        case['properties'] = properties

        await callback.message.edit_text(
            f"🏠 <b>Имущество</b>\n\n"
            f"Дело: {case['case_number']}\n"
            f"Клиент: {case['full_name']}\n\n"
            f"Выберите действие:",
            reply_markup=get_property_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(PropertyManagement.menu)

    except Exception as e:
        logger.error(f"Error returning to property menu: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ==================== REAL ESTATE TOGGLE ====================

@router.callback_query(F.data.startswith("property:") & F.data.endswith(":toggle_real_estate"))
async def toggle_real_estate(callback: CallbackQuery, state: FSMContext):
    """Toggle real estate flag"""
    case_id = int(callback.data.split(":")[1])

    try:
        # Toggle the flag
        await api.toggle_real_estate(case_id)

        # Get updated case
        case = await api.get_case(case_id)
        properties = await api.get_properties(case_id)
        case['properties'] = properties

        status = "Есть" if case.get('has_real_estate') else "Нет"

        await callback.message.edit_text(
            f"✅ Статус недвижимости обновлен: {status}\n\n"
            f"🏠 <b>Имущество</b>\n\n"
            f"Выберите действие:",
            reply_markup=get_property_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.set_state(PropertyManagement.menu)

    except Exception as e:
        logger.error(f"Error toggling real estate: {e}")
        await callback.answer("❌ Ошибка обновления", show_alert=True)


# ==================== VEHICLES MENU ====================

@router.callback_query(F.data.startswith("property:") & F.data.endswith(":vehicles"))
async def show_vehicles_menu(callback: CallbackQuery, state: FSMContext):
    """Show vehicles management menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        properties = await api.get_properties(case_id)
        vehicles = [p for p in properties if p.get('property_type') == 'vehicle']

        await callback.message.edit_text(
            f"🚗 <b>Транспорт</b>\n\n"
            f"Всего транспортных средств: {len(vehicles)}\n\n"
            f"Выберите действие:",
            reply_markup=get_vehicles_menu(case_id, vehicles),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)

    except Exception as e:
        logger.error(f"Error showing vehicles menu: {e}")
        await callback.answer("❌ Ошибка загрузки", show_alert=True)


@router.callback_query(F.data.startswith("vehicles:") & F.data.endswith(":menu"))
async def return_to_vehicles_menu(callback: CallbackQuery, state: FSMContext):
    """Return to vehicles menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        properties = await api.get_properties(case_id)
        vehicles = [p for p in properties if p.get('property_type') == 'vehicle']

        await callback.message.edit_text(
            f"🚗 <b>Транспорт</b>\n\n"
            f"Всего транспортных средств: {len(vehicles)}\n\n"
            f"Выберите действие:",
            reply_markup=get_vehicles_menu(case_id, vehicles),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)

    except Exception as e:
        logger.error(f"Error returning to vehicles menu: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ==================== ADD VEHICLE ====================

@router.callback_query(F.data.startswith("vehicles:") & F.data.endswith(":add"))
async def start_add_vehicle(callback: CallbackQuery, state: FSMContext):
    """Start adding new vehicle"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "➕ <b>Добавление транспортного средства</b>\n\n"
        "Введите марку транспортного средства:\n"
        "(например: Toyota, BMW, ВАЗ)",
        parse_mode="HTML"
    )
    await state.set_state(PropertyManagement.add_vehicle_make)
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.message(PropertyManagement.add_vehicle_make)
async def process_vehicle_make(message: Message, state: FSMContext):
    """Process vehicle make"""
    make = message.text.strip()
    await state.update_data(vehicle_make=make)

    await message.answer(
        "🚗 <b>Модель</b>\n\n"
        "Введите модель транспортного средства:\n"
        "(например: Camry, X5, 2107)",
        parse_mode="HTML"
    )
    await state.set_state(PropertyManagement.add_vehicle_model)


@router.message(PropertyManagement.add_vehicle_model)
async def process_vehicle_model(message: Message, state: FSMContext):
    """Process vehicle model"""
    model = message.text.strip()
    await state.update_data(vehicle_model=model)

    current_year = datetime.now().year

    await message.answer(
        f"📅 <b>Год выпуска</b>\n\n"
        f"Введите год выпуска (1900-{current_year}):",
        parse_mode="HTML"
    )
    await state.set_state(PropertyManagement.add_vehicle_year)


@router.message(PropertyManagement.add_vehicle_year)
async def process_vehicle_year(message: Message, state: FSMContext):
    """Process vehicle year"""
    year_str = message.text.strip()
    current_year = datetime.now().year

    try:
        year = int(year_str)
        if year < 1900 or year > current_year:
            await message.answer(
                f"❌ Год должен быть в диапазоне 1900-{current_year}.\n"
                f"Попробуйте снова:"
            )
            return
    except ValueError:
        await message.answer("❌ Введите корректный год.\nПопробуйте снова:")
        return

    await state.update_data(vehicle_year=year)

    await message.answer(
        "🔢 <b>VIN номер</b>\n\n"
        "Введите VIN номер (17 символов):\n"
        "(или отправьте <b>-</b> если неизвестен)",
        parse_mode="HTML"
    )
    await state.set_state(PropertyManagement.add_vehicle_vin)


@router.message(PropertyManagement.add_vehicle_vin)
async def process_vehicle_vin(message: Message, state: FSMContext):
    """Process vehicle VIN"""
    vin = message.text.strip().upper()

    if vin != "-":
        # VIN validation (17 characters)
        if len(vin) != 17:
            await message.answer(
                "❌ VIN номер должен содержать 17 символов.\n"
                "Попробуйте снова или отправьте <b>-</b>:",
                parse_mode="HTML"
            )
            return
        await state.update_data(vehicle_vin=vin)
    else:
        await state.update_data(vehicle_vin=None)

    await message.answer(
        "🎨 <b>Цвет</b>\n\n"
        "Введите цвет транспортного средства:\n"
        "(например: белый, черный, серый)",
        parse_mode="HTML"
    )
    await state.set_state(PropertyManagement.add_vehicle_color)


@router.message(PropertyManagement.add_vehicle_color)
async def process_vehicle_color(message: Message, state: FSMContext):
    """Process vehicle color and ask about pledge"""
    color = message.text.strip()
    await state.update_data(vehicle_color=color)

    data = await state.get_data()
    case_id = data['case_id']

    await message.answer(
        "💰 <b>Залог</b>\n\n"
        "Находится ли транспортное средство в залоге?",
        reply_markup=get_vehicle_pledged_keyboard(case_id),
        parse_mode="HTML"
    )
    await state.set_state(PropertyManagement.add_vehicle_pledged)


@router.callback_query(F.data.startswith("vehicle_pledged:") & F.data.endswith(":no"))
async def vehicle_not_pledged(callback: CallbackQuery, state: FSMContext):
    """Vehicle is not pledged - save directly"""
    case_id = int(callback.data.split(":")[1])
    data = await state.get_data()

    property_data = {
        'property_type': 'vehicle',
        'description': f"{data['vehicle_make']} {data['vehicle_model']} ({data['vehicle_year']})",
        'vehicle_make': data['vehicle_make'],
        'vehicle_model': data['vehicle_model'],
        'vehicle_year': data['vehicle_year'],
        'vehicle_vin': data.get('vehicle_vin'),
        'vehicle_color': data.get('vehicle_color'),
        'is_pledged': False,
    }

    try:
        await api.add_property(case_id, property_data)

        properties = await api.get_properties(case_id)
        vehicles = [p for p in properties if p.get('property_type') == 'vehicle']

        await callback.message.edit_text(
            f"✅ Транспортное средство добавлено!\n\n"
            f"🚗 <b>Транспорт</b>\n"
            f"Всего: {len(vehicles)}",
            reply_markup=get_vehicles_menu(case_id, vehicles),
            parse_mode="HTML"
        )
        await state.set_state(PropertyManagement.menu)

    except Exception as e:
        logger.error(f"Error adding vehicle: {e}")
        await callback.answer("❌ Ошибка добавления", show_alert=True)


@router.callback_query(F.data.startswith("vehicle_pledged:") & F.data.endswith(":yes"))
async def vehicle_is_pledged(callback: CallbackQuery, state: FSMContext):
    """Vehicle is pledged - ask for creditor"""
    await state.update_data(is_pledged=True)

    await callback.message.edit_text(
        "💰 <b>Информация о залоге</b>\n\n"
        "Введите название залогодержателя (кредитора):\n"
        "(например: Сбербанк, ВТБ)",
        parse_mode="HTML"
    )
    await state.set_state(PropertyManagement.add_pledge_creditor)
    await callback.answer()


@router.message(PropertyManagement.add_pledge_creditor)
async def process_pledge_creditor(message: Message, state: FSMContext):
    """Process pledge creditor"""
    creditor = message.text.strip()
    await state.update_data(pledge_creditor=creditor)

    await message.answer(
        "📄 <b>Документ о залоге</b>\n\n"
        "Введите реквизиты документа о залоге:\n"
        "(например: договор залога №123 от 01.01.2024)\n\n"
        "Или отправьте <b>-</b> если неизвестен",
        parse_mode="HTML"
    )
    await state.set_state(PropertyManagement.add_pledge_document)


@router.message(PropertyManagement.add_pledge_document)
async def process_pledge_document_and_save(message: Message, state: FSMContext):
    """Process pledge document and save vehicle"""
    document = message.text.strip()
    data = await state.get_data()
    case_id = data['case_id']

    property_data = {
        'property_type': 'vehicle',
        'description': f"{data['vehicle_make']} {data['vehicle_model']} ({data['vehicle_year']})",
        'vehicle_make': data['vehicle_make'],
        'vehicle_model': data['vehicle_model'],
        'vehicle_year': data['vehicle_year'],
        'vehicle_vin': data.get('vehicle_vin'),
        'vehicle_color': data.get('vehicle_color'),
        'is_pledged': True,
        'pledge_creditor': data.get('pledge_creditor'),
    }

    if document != "-":
        property_data['pledge_document'] = document

    try:
        await api.add_property(case_id, property_data)

        properties = await api.get_properties(case_id)
        vehicles = [p for p in properties if p.get('property_type') == 'vehicle']

        await message.answer(
            f"✅ Транспортное средство добавлено!\n"
            f"(в залоге у {data.get('pledge_creditor')})\n\n"
            f"🚗 <b>Транспорт</b>\n"
            f"Всего: {len(vehicles)}",
            reply_markup=get_vehicles_menu(case_id, vehicles),
            parse_mode="HTML"
        )
        await state.set_state(PropertyManagement.menu)

    except Exception as e:
        logger.error(f"Error adding pledged vehicle: {e}")
        await message.answer("❌ Ошибка добавления. Попробуйте позже.")
        await state.clear()


# ==================== LIST VEHICLES ====================

@router.callback_query(F.data.startswith("vehicles:") & F.data.endswith(":list"))
async def list_vehicles(callback: CallbackQuery, state: FSMContext):
    """Show list of all vehicles"""
    case_id = int(callback.data.split(":")[1])

    try:
        properties = await api.get_properties(case_id)
        vehicles = [p for p in properties if p.get('property_type') == 'vehicle']

        if not vehicles:
            await callback.answer("Нет транспортных средств", show_alert=True)
            return

        text = f"📋 <b>Список транспорта</b>\n\n"

        for i, vehicle in enumerate(vehicles, 1):
            make = vehicle.get('vehicle_make', '')
            model = vehicle.get('vehicle_model', '')
            year = vehicle.get('vehicle_year', '')
            color = vehicle.get('vehicle_color', 'не указан')
            vin = vehicle.get('vehicle_vin', 'не указан')

            text += f"{i}. <b>{make} {model}</b> ({year})\n"
            text += f"   Цвет: {color}\n"
            text += f"   VIN: {vin}\n"

            if vehicle.get('is_pledged'):
                creditor = vehicle.get('pledge_creditor', 'не указан')
                text += f"   ⚠️ В залоге: {creditor}\n"

            text += "\n"

        await callback.message.edit_text(
            text,
            reply_markup=get_back_to_vehicles_menu(case_id),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error listing vehicles: {e}")
        await callback.answer("❌ Ошибка загрузки списка", show_alert=True)


# ==================== DELETE VEHICLE ====================

@router.callback_query(F.data.startswith("vehicles:") & F.data.endswith(":delete"))
async def select_vehicle_to_delete(callback: CallbackQuery, state: FSMContext):
    """Show vehicles list for deletion"""
    case_id = int(callback.data.split(":")[1])

    try:
        properties = await api.get_properties(case_id)
        vehicles = [p for p in properties if p.get('property_type') == 'vehicle']

        if not vehicles:
            await callback.answer("Нет транспорта для удаления", show_alert=True)
            return

        await callback.message.edit_text(
            "🗑 <b>Удаление транспорта</b>\n\n"
            "Выберите транспортное средство для удаления:",
            reply_markup=get_vehicles_list_keyboard(vehicles, case_id),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id)
        await state.set_state(PropertyManagement.delete_property_select)

    except Exception as e:
        logger.error(f"Error selecting vehicle to delete: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("vehicle:delete:") & ~F.data.contains(":confirm:"))
async def confirm_delete_vehicle(callback: CallbackQuery, state: FSMContext):
    """Confirm deletion of vehicle"""
    property_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    case_id = data.get('case_id')

    await callback.message.edit_text(
        f"⚠️ <b>Подтверждение удаления</b>\n\n"
        f"Вы уверены, что хотите удалить это транспортное средство?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"vehicle:delete:confirm:{property_id}")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"vehicles:{case_id}:menu")]
        ]),
        parse_mode="HTML"
    )
    await state.set_state(PropertyManagement.delete_property_confirm)


@router.callback_query(F.data.startswith("vehicle:delete:confirm:"))
async def delete_vehicle_confirmed(callback: CallbackQuery, state: FSMContext):
    """Delete vehicle after confirmation"""
    property_id = int(callback.data.split(":")[3])
    data = await state.get_data()
    case_id = data.get('case_id')

    try:
        await api.delete_property(property_id)

        properties = await api.get_properties(case_id)
        vehicles = [p for p in properties if p.get('property_type') == 'vehicle']

        await callback.message.edit_text(
            f"✅ Транспортное средство удалено!\n\n"
            f"🚗 <b>Транспорт</b>\n"
            f"Всего: {len(vehicles)}",
            reply_markup=get_vehicles_menu(case_id, vehicles),
            parse_mode="HTML"
        )
        await state.set_state(PropertyManagement.menu)

    except Exception as e:
        logger.error(f"Error deleting vehicle: {e}")
        await callback.answer("❌ Ошибка удаления", show_alert=True)
