from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.case_states import CaseCreation
from services.api_client import APIClient
from keyboards.inline import get_yes_no_keyboard, get_cases_keyboard, get_case_keyboard
from keyboards.reply import get_navigation_keyboard, get_main_keyboard

router = Router()
api = APIClient()


@router.message(Command("новое_дело", "new"))
@router.message(F.text == "➕ Новое дело")
async def cmd_new_case(message: Message, state: FSMContext):
    await state.set_state(CaseCreation.waiting_full_name)
    await message.answer(
        "📝 <b>Создание нового дела</b>\n\n"
        "Введите ФИО должника полностью:\n"
        "<i>Например: Иванов Иван Иванович</i>",
        parse_mode="HTML",
        reply_markup=get_navigation_keyboard(show_back=False)  # No back on first step
    )


@router.message(CaseCreation.waiting_full_name)
async def process_full_name(message: Message, state: FSMContext):
    # Handle cancel button
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "❌ Создание дела отменено.",
            reply_markup=get_main_keyboard()
        )
        return

    await state.update_data(full_name=message.text.strip())
    await state.set_state(CaseCreation.waiting_total_debt)
    await message.answer(
        "💰 Введите общую сумму долга (в рублях):\n"
        "<i>Например: 500000</i>",
        parse_mode="HTML",
        reply_markup=get_navigation_keyboard(show_back=True)
    )


@router.message(CaseCreation.waiting_total_debt)
async def process_total_debt(message: Message, state: FSMContext):
    # Handle back button
    if message.text == "⬅️ Назад":
        await state.set_state(CaseCreation.waiting_full_name)
        await message.answer(
            "📝 Введите ФИО должника полностью:\n"
            "<i>Например: Иванов Иван Иванович</i>",
            parse_mode="HTML",
            reply_markup=get_navigation_keyboard(show_back=False)
        )
        return

    # Handle cancel button
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "❌ Создание дела отменено.",
            reply_markup=get_main_keyboard()
        )
        return

    try:
        debt = float(message.text.replace(" ", "").replace(",", "."))
    except ValueError:
        await message.answer(
            "❌ Введите число. Например: 500000",
            reply_markup=get_navigation_keyboard(show_back=True)
        )
        return

    await state.update_data(total_debt=debt, creditors=[])
    await state.set_state(CaseCreation.waiting_creditor_name)
    await message.answer(
        "🏦 Введите название первого кредитора:\n"
        "<i>Например: Сбербанк, Альфа-Банк, МФО Быстроденьги</i>",
        parse_mode="HTML",
        reply_markup=get_navigation_keyboard(show_back=True)
    )


@router.message(CaseCreation.waiting_creditor_name)
async def process_creditor_name(message: Message, state: FSMContext):
    # Handle back button
    if message.text == "⬅️ Назад":
        data = await state.get_data()
        creditors = data.get("creditors", [])

        if creditors:
            # If there are creditors, go back to add_more_creditors state
            await state.set_state(CaseCreation.add_more_creditors)
            last_creditor = creditors[-1]
            await message.answer(
                f"✅ Последний добавленный кредитор: {last_creditor['name']} — {last_creditor['debt_amount']:,.0f} руб.\n\n"
                "Добавить ещё кредитора?",
                reply_markup=get_yes_no_keyboard()
            )
        else:
            # If no creditors yet, go back to total debt
            await state.set_state(CaseCreation.waiting_total_debt)
            await message.answer(
                "💰 Введите общую сумму долга (в рублях):\n"
                "<i>Например: 500000</i>",
                parse_mode="HTML",
                reply_markup=get_navigation_keyboard(show_back=True)
            )
        return

    # Handle cancel button
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "❌ Создание дела отменено.",
            reply_markup=get_main_keyboard()
        )
        return

    await state.update_data(current_creditor_name=message.text.strip())
    await state.set_state(CaseCreation.waiting_creditor_debt)
    await message.answer(
        "💵 Введите сумму долга этому кредитору (в рублях):\n"
        "<i>Например: 150000</i>",
        parse_mode="HTML",
        reply_markup=get_navigation_keyboard(show_back=True)
    )


@router.message(CaseCreation.waiting_creditor_debt)
async def process_creditor_debt(message: Message, state: FSMContext):
    # Handle back button
    if message.text == "⬅️ Назад":
        await state.set_state(CaseCreation.waiting_creditor_name)
        await message.answer(
            "🏦 Введите название кредитора:\n"
            "<i>Например: Сбербанк, Альфа-Банк, МФО Быстроденьги</i>",
            parse_mode="HTML",
            reply_markup=get_navigation_keyboard(show_back=True)
        )
        return

    # Handle cancel button
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "❌ Создание дела отменено.",
            reply_markup=get_main_keyboard()
        )
        return

    try:
        debt = float(message.text.replace(" ", "").replace(",", "."))
    except ValueError:
        await message.answer(
            "❌ Введите число. Например: 150000",
            reply_markup=get_navigation_keyboard(show_back=True)
        )
        return

    data = await state.get_data()
    creditors = data.get("creditors", [])
    creditors.append({"name": data["current_creditor_name"], "debt_amount": debt})
    await state.update_data(creditors=creditors)
    await state.set_state(CaseCreation.add_more_creditors)
    await message.answer(
        f"✅ Кредитор добавлен: {data['current_creditor_name']} — {debt:,.0f} руб.\n\n"
        "Добавить ещё кредитора?",
        reply_markup=get_yes_no_keyboard(),
    )


@router.callback_query(CaseCreation.add_more_creditors, F.data == "yes")
async def add_more_creditors(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CaseCreation.waiting_creditor_name)
    await callback.message.answer(
        "🏦 Введите название кредитора:\n"
        "<i>Например: Сбербанк, Альфа-Банк, МФО Быстроденьги</i>",
        parse_mode="HTML",
        reply_markup=get_navigation_keyboard(show_back=True)
    )
    await callback.answer()


@router.callback_query(CaseCreation.add_more_creditors, F.data == "back_creditor")
async def back_from_add_more(callback: CallbackQuery, state: FSMContext):
    """Go back to edit last creditor"""
    data = await state.get_data()
    creditors = data.get("creditors", [])

    if creditors:
        # Remove last creditor and go back to editing it
        last_creditor = creditors.pop()
        await state.update_data(
            creditors=creditors,
            current_creditor_name=last_creditor["name"]
        )
        await state.set_state(CaseCreation.waiting_creditor_debt)
        await callback.message.answer(
            f"⬅️ Возврат к редактированию кредитора: {last_creditor['name']}\n\n"
            f"💵 Введите сумму долга этому кредитору (в рублях):\n"
            f"<i>Например: 150000</i>",
            parse_mode="HTML",
            reply_markup=get_navigation_keyboard(show_back=True)
        )
    else:
        # No creditors to go back to, go to total debt
        await state.set_state(CaseCreation.waiting_total_debt)
        await callback.message.answer(
            "💰 Введите общую сумму долга (в рублях):\n"
            "<i>Например: 500000</i>",
            parse_mode="HTML",
            reply_markup=get_navigation_keyboard(show_back=True)
        )
    await callback.answer()


@router.callback_query(CaseCreation.add_more_creditors, F.data == "cancel_case")
async def cancel_from_add_more(callback: CallbackQuery, state: FSMContext):
    """Cancel case creation"""
    await state.clear()
    await callback.message.answer(
        "❌ Создание дела отменено.",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


@router.callback_query(CaseCreation.add_more_creditors, F.data == "no")
async def finish_creditors(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # Create case via API
    try:
        case = await api.create_case(
            full_name=data["full_name"],
            total_debt=data["total_debt"],
            telegram_user_id=callback.from_user.id,
            creditors=data["creditors"],
        )

        await state.clear()
        await callback.message.answer(
            f"✅ <b>Дело успешно создано!</b>\n\n"
            f"📁 Номер дела: <code>{case['case_number']}</code>\n"
            f"👤 ФИО: {case['full_name']}\n"
            f"💰 Общая сумма долга: {case['total_debt']:,.0f} руб.\n"
            f"🏦 Количество кредиторов: {len(data['creditors'])}\n\n"
            "ℹ️ <i>Дополнительные данные (паспорт, ИНН, СНИЛС) вы можете добавить через веб-интерфейс.</i>\n\n"
            "Используйте /список_дел для просмотра всех дел.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка при создании дела: {str(e)}",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

    await callback.answer()


@router.message(Command("список_дел", "list"))
@router.message(F.text == "📋 Мои дела")
async def cmd_list_cases(message: Message):
    try:
        cases = await api.get_cases_by_user(message.from_user.id)

        if not cases:
            await message.answer("📭 У вас пока нет дел. Создайте первое: /новое_дело")
            return

        text = "📋 <b>Ваши дела:</b>\n\n"
        for case in cases:
            status_emoji = {
                "new": "🆕",
                "in_progress": "⏳",
                "court": "⚖️",
                "completed": "✅",
            }.get(case["status"], "📁")
            text += f"{status_emoji} <code>{case['case_number']}</code> — {case['full_name']}\n"

        await message.answer(text, parse_mode="HTML", reply_markup=get_cases_keyboard(cases))
    except Exception as e:
        await message.answer(f"❌ Ошибка при получении списка дел: {str(e)}")


@router.callback_query(F.data.startswith("case_"))
async def show_case_details(callback: CallbackQuery):
    case_id = int(callback.data.split("_")[1])

    try:
        case = await api.get_case_public(case_id)

        status_emoji = {
            "new": "🆕",
            "in_progress": "⏳",
            "court": "⚖️",
            "completed": "✅",
        }.get(case["status"], "📁")

        text = (
            f"{status_emoji} <b>Дело {case['case_number']}</b>\n\n"
            f"👤 <b>ФИО:</b> {case['full_name']}\n"
            f"💰 <b>Долг:</b> {case['total_debt']:,.0f} ₽\n"
            f"🏦 <b>Кредиторов:</b> {case['creditors_count']}\n"
            f"📅 <b>Создано:</b> {case['created_at'][:10]}\n"
        )

        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_case_keyboard(case_id))
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data == "back_to_list")
async def back_to_list(callback: CallbackQuery):
    try:
        cases = await api.get_cases_by_user(callback.from_user.id)

        text = "📋 <b>Ваши дела:</b>\n\n"
        for case in cases:
            status_emoji = {
                "new": "🆕",
                "in_progress": "⏳",
                "court": "⚖️",
                "completed": "✅",
            }.get(case["status"], "📁")
            text += f"{status_emoji} <code>{case['case_number']}</code> — {case['full_name']}\n"

        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_cases_keyboard(cases))
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
