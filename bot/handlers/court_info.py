from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states.case_states import CourtInfoEdit
from keyboards.case_menu import (
    get_court_info_menu,
    get_back_to_court_menu,
)
from services.api_client import APIClient
import logging

router = Router()
api = APIClient()
logger = logging.getLogger(__name__)


# ==================== COURT INFO MENU ====================

@router.callback_query(F.data.startswith("case:") & F.data.endswith(":court"))
async def show_court_menu(callback: CallbackQuery, state: FSMContext):
    """Show court info menu"""
    parts = callback.data.split(":")
    case_id = int(parts[1])

    try:
        case = await api.get_case(case_id)

        await callback.message.edit_text(
            f"⚖️ <b>Суд и СРО</b>\n\n"
            f"<b>Суд:</b> {case.get('court_name') or 'не указан'}\n"
            f"<b>Адрес:</b> {case.get('court_address') or 'не указан'}\n"
            f"<b>СРО:</b> {case.get('sro_name') or 'не указана'}\n"
            f"<b>Срок реструктуризации:</b> {case.get('restructuring_duration') or 'не указан'}\n"
            f"<b>Основания:</b> {case.get('insolvency_grounds') or 'не указаны'}\n\n"
            f"Выберите поле для редактирования:",
            reply_markup=get_court_info_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(CourtInfoEdit.menu)

    except Exception as e:
        logger.error(f"Error showing court menu: {e}")
        await callback.answer("❌ Ошибка загрузки", show_alert=True)


@router.callback_query(F.data.startswith("court:") & F.data.endswith(":menu"))
async def return_to_court_menu(callback: CallbackQuery, state: FSMContext):
    """Return to court info menu"""
    case_id = int(callback.data.split(":")[1])

    try:
        case = await api.get_case(case_id)

        await callback.message.edit_text(
            f"⚖️ <b>Суд и СРО</b>\n\n"
            f"<b>Суд:</b> {case.get('court_name') or 'не указан'}\n"
            f"<b>Адрес:</b> {case.get('court_address') or 'не указан'}\n"
            f"<b>СРО:</b> {case.get('sro_name') or 'не указана'}\n"
            f"<b>Срок реструктуризации:</b> {case.get('restructuring_duration') or 'не указан'}\n"
            f"<b>Основания:</b> {case.get('insolvency_grounds') or 'не указаны'}\n\n"
            f"Выберите поле для редактирования:",
            reply_markup=get_court_info_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.update_data(case_id=case_id, case_number=case['case_number'])
        await state.set_state(CourtInfoEdit.menu)

    except Exception as e:
        logger.error(f"Error returning to court menu: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


# ==================== EDIT COURT NAME ====================

@router.callback_query(F.data.startswith("court:") & F.data.endswith(":edit_name"))
async def edit_court_name(callback: CallbackQuery, state: FSMContext):
    """Start editing court name"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "⚖️ <b>Название суда</b>\n\n"
        "Введите название суда:\n"
        "<i>(Например: Арбитражный суд города Москвы)</i>",
        parse_mode="HTML"
    )
    await state.set_state(CourtInfoEdit.edit_court_name)
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.message(CourtInfoEdit.edit_court_name)
async def save_court_name(message: Message, state: FSMContext):
    """Save court name"""
    data = await state.get_data()
    case_id = data['case_id']
    court_name = message.text.strip()

    try:
        await api.update_case_court_data(case_id, {'court_name': court_name})
        case = await api.get_case(case_id)

        await message.answer(
            f"✅ Название суда сохранено!\n\n"
            f"⚖️ <b>Суд и СРО</b>\n\n"
            f"<b>Суд:</b> {case.get('court_name')}\n"
            f"<b>Адрес:</b> {case.get('court_address') or 'не указан'}\n"
            f"<b>СРО:</b> {case.get('sro_name') or 'не указана'}",
            reply_markup=get_court_info_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.set_state(CourtInfoEdit.menu)

    except Exception as e:
        logger.error(f"Error saving court name: {e}")
        await message.answer("❌ Ошибка сохранения. Попробуйте позже.")
        await state.clear()


# ==================== EDIT COURT ADDRESS ====================

@router.callback_query(F.data.startswith("court:") & F.data.endswith(":edit_address"))
async def edit_court_address(callback: CallbackQuery, state: FSMContext):
    """Start editing court address"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "📍 <b>Адрес суда</b>\n\n"
        "Введите адрес суда:\n"
        "<i>(Например: 115191, г. Москва, ул. Большая Тульская, д. 17)</i>",
        parse_mode="HTML"
    )
    await state.set_state(CourtInfoEdit.edit_court_address)
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.message(CourtInfoEdit.edit_court_address)
async def save_court_address(message: Message, state: FSMContext):
    """Save court address"""
    data = await state.get_data()
    case_id = data['case_id']
    court_address = message.text.strip()

    try:
        await api.update_case_court_data(case_id, {'court_address': court_address})
        case = await api.get_case(case_id)

        await message.answer(
            f"✅ Адрес суда сохранен!\n\n"
            f"⚖️ <b>Суд и СРО</b>\n\n"
            f"<b>Суд:</b> {case.get('court_name') or 'не указан'}\n"
            f"<b>Адрес:</b> {case.get('court_address')}\n"
            f"<b>СРО:</b> {case.get('sro_name') or 'не указана'}",
            reply_markup=get_court_info_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.set_state(CourtInfoEdit.menu)

    except Exception as e:
        logger.error(f"Error saving court address: {e}")
        await message.answer("❌ Ошибка сохранения. Попробуйте позже.")
        await state.clear()


# ==================== EDIT SRO NAME ====================

@router.callback_query(F.data.startswith("court:") & F.data.endswith(":edit_sro"))
async def edit_sro_name(callback: CallbackQuery, state: FSMContext):
    """Start editing SRO name"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "🏢 <b>Наименование СРО</b>\n\n"
        "Введите наименование саморегулируемой организации:\n"
        "<i>(Например: Ассоциация арбитражных управляющих «СИБИРИЯ»)</i>",
        parse_mode="HTML"
    )
    await state.set_state(CourtInfoEdit.edit_sro_name)
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.message(CourtInfoEdit.edit_sro_name)
async def save_sro_name(message: Message, state: FSMContext):
    """Save SRO name"""
    data = await state.get_data()
    case_id = data['case_id']
    sro_name = message.text.strip()

    try:
        await api.update_case_court_data(case_id, {'sro_name': sro_name})
        case = await api.get_case(case_id)

        await message.answer(
            f"✅ СРО сохранена!\n\n"
            f"⚖️ <b>Суд и СРО</b>\n\n"
            f"<b>Суд:</b> {case.get('court_name') or 'не указан'}\n"
            f"<b>Адрес:</b> {case.get('court_address') or 'не указан'}\n"
            f"<b>СРО:</b> {case.get('sro_name')}",
            reply_markup=get_court_info_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.set_state(CourtInfoEdit.menu)

    except Exception as e:
        logger.error(f"Error saving SRO name: {e}")
        await message.answer("❌ Ошибка сохранения. Попробуйте позже.")
        await state.clear()


# ==================== EDIT RESTRUCTURING DURATION ====================

@router.callback_query(F.data.startswith("court:") & F.data.endswith(":edit_duration"))
async def edit_restructuring_duration(callback: CallbackQuery, state: FSMContext):
    """Start editing restructuring duration"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "⏱ <b>Срок реструктуризации</b>\n\n"
        "Введите срок реструктуризации долгов:\n"
        "<i>(Например: 3 месяца, 6 месяцев)</i>",
        parse_mode="HTML"
    )
    await state.set_state(CourtInfoEdit.edit_restructuring_duration)
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.message(CourtInfoEdit.edit_restructuring_duration)
async def save_restructuring_duration(message: Message, state: FSMContext):
    """Save restructuring duration"""
    data = await state.get_data()
    case_id = data['case_id']
    duration = message.text.strip()

    try:
        await api.update_case_court_data(case_id, {'restructuring_duration': duration})
        case = await api.get_case(case_id)

        await message.answer(
            f"✅ Срок реструктуризации сохранен!\n\n"
            f"⚖️ <b>Суд и СРО</b>\n\n"
            f"<b>Суд:</b> {case.get('court_name') or 'не указан'}\n"
            f"<b>СРО:</b> {case.get('sro_name') or 'не указана'}\n"
            f"<b>Срок:</b> {case.get('restructuring_duration')}",
            reply_markup=get_court_info_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.set_state(CourtInfoEdit.menu)

    except Exception as e:
        logger.error(f"Error saving restructuring duration: {e}")
        await message.answer("❌ Ошибка сохранения. Попробуйте позже.")
        await state.clear()


# ==================== EDIT INSOLVENCY GROUNDS ====================

@router.callback_query(F.data.startswith("court:") & F.data.endswith(":edit_grounds"))
async def edit_insolvency_grounds(callback: CallbackQuery, state: FSMContext):
    """Start editing insolvency grounds"""
    case_id = int(callback.data.split(":")[1])

    await callback.message.edit_text(
        "📋 <b>Основания несостоятельности</b>\n\n"
        "Введите основания для признания несостоятельности:\n"
        "<i>(Например: гражданин прекратил расчеты с кредиторами, "
        "то есть перестал исполнять денежные обязательства, "
        "срок исполнения которых наступил)</i>",
        parse_mode="HTML"
    )
    await state.set_state(CourtInfoEdit.edit_insolvency_grounds)
    await state.update_data(case_id=case_id)
    await callback.answer()


@router.message(CourtInfoEdit.edit_insolvency_grounds)
async def save_insolvency_grounds(message: Message, state: FSMContext):
    """Save insolvency grounds"""
    data = await state.get_data()
    case_id = data['case_id']
    grounds = message.text.strip()

    try:
        await api.update_case_court_data(case_id, {'insolvency_grounds': grounds})
        case = await api.get_case(case_id)

        await message.answer(
            f"✅ Основания несостоятельности сохранены!\n\n"
            f"⚖️ <b>Суд и СРО</b>\n\n"
            f"<b>Суд:</b> {case.get('court_name') or 'не указан'}\n"
            f"<b>СРО:</b> {case.get('sro_name') or 'не указана'}\n"
            f"<b>Основания:</b> {case.get('insolvency_grounds')[:100]}...",
            reply_markup=get_court_info_menu(case_id, case['case_number'], case),
            parse_mode="HTML"
        )
        await state.set_state(CourtInfoEdit.menu)

    except Exception as e:
        logger.error(f"Error saving insolvency grounds: {e}")
        await message.answer("❌ Ошибка сохранения. Попробуйте позже.")
        await state.clear()
