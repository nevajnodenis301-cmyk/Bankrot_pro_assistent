from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from services.api_client import APIClient
from states.case_states import DocumentGeneration
from keyboards.inline import (
    get_document_types_keyboard,
    get_cases_for_document_keyboard,
    get_case_documents_keyboard,
)
from keyboards.reply import get_main_keyboard
from exceptions import BotException, APIError, APITimeoutError, DocumentGenerationError
import logging
import httpx

logger = logging.getLogger(__name__)
router = Router()
api = APIClient()

# Document type labels in Russian
DOCUMENT_TYPE_LABELS = {
    "bankruptcy_petition": "Заявление о банкротстве",
    "bankruptcy_application": "Простое заявление",
    "creditor_notification": "Уведомление кредиторов",
    "court_motion": "Ходатайство в суд",
}


@router.message(Command("документы", "documents"))
@router.message(F.text == "📄 Документы")
async def cmd_documents_menu(message: Message, state: FSMContext):
    """Open the Documents menu"""
    await state.clear()  # Clear any previous state
    await state.set_state(DocumentGeneration.select_document_type)

    await message.answer(
        "📄 <b>Генерация документов</b>\n\n"
        "Выберите тип документа для генерации:\n\n"
        "📜 <b>Заявление о банкротстве</b> — полное заявление со всеми данными\n\n"
        "📋 <b>Простое заявление</b> — базовый шаблон заявления\n\n"
        "📨 <b>Уведомление кредиторов</b> — письмо-уведомление для кредиторов\n\n"
        "⚖️ <b>Ходатайство в суд</b> — ходатайство по делу о банкротстве",
        parse_mode="HTML",
        reply_markup=get_document_types_keyboard()
    )


@router.callback_query(DocumentGeneration.select_document_type, F.data.startswith("doctype:"))
async def process_document_type_selection(callback: CallbackQuery, state: FSMContext):
    """Handle document type selection"""
    doc_type = callback.data.split(":")[1]

    if doc_type == "cancel":
        await state.clear()
        await callback.message.answer(
            "❌ Генерация документа отменена.",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return

    # Check if document type is supported (only petition and application are implemented)
    if doc_type not in ["bankruptcy_petition", "bankruptcy_application"]:
        await callback.answer(
            "⚠️ Этот тип документа пока в разработке",
            show_alert=True
        )
        return

    # Save selected document type
    await state.update_data(document_type=doc_type)

    # Get user's cases
    try:
        cases = await api.get_cases_by_user(callback.from_user.id)

        if not cases:
            await state.clear()
            await callback.message.answer(
                "📭 У вас пока нет дел.\n\n"
                "Сначала создайте дело: /новое_дело",
                reply_markup=get_main_keyboard()
            )
            await callback.answer()
            return

        await state.set_state(DocumentGeneration.select_case)

        doc_label = DOCUMENT_TYPE_LABELS.get(doc_type, doc_type)
        await callback.message.edit_text(
            f"📄 <b>Выбран документ:</b> {doc_label}\n\n"
            "Выберите дело для генерации документа:",
            parse_mode="HTML",
            reply_markup=get_cases_for_document_keyboard(cases)
        )

    except BotException as e:
        logger.error(f"Error getting cases for document: {e}")
        await callback.message.answer(f"❌ {e.user_message}")
        await state.clear()

    await callback.answer()


@router.callback_query(DocumentGeneration.select_case, F.data.startswith("doccase_"))
async def process_case_selection(callback: CallbackQuery, state: FSMContext):
    """Handle case selection for document generation"""
    action = callback.data.replace("doccase_", "")

    if action == "back":
        # Go back to document type selection
        await state.set_state(DocumentGeneration.select_document_type)
        await callback.message.edit_text(
            "📄 <b>Генерация документов</b>\n\n"
            "Выберите тип документа для генерации:",
            parse_mode="HTML",
            reply_markup=get_document_types_keyboard()
        )
        await callback.answer()
        return

    if action == "cancel":
        await state.clear()
        await callback.message.answer(
            "❌ Генерация документа отменена.",
            reply_markup=get_main_keyboard()
        )
        await callback.answer()
        return

    # Parse case_id
    try:
        case_id = int(action)
    except ValueError:
        await callback.answer("❌ Ошибка выбора дела", show_alert=True)
        return

    data = await state.get_data()
    document_type = data.get("document_type")

    if not document_type:
        await callback.answer("❌ Тип документа не выбран", show_alert=True)
        await state.clear()
        return

    # Generate the document
    await callback.message.answer("⏳ Генерирую документ, пожалуйста подождите...")

    try:
        # Generate document via API (this also saves it to case folder)
        doc_info = await api.generate_document(case_id, document_type)

        # Download the generated document
        doc_content = await api.download_document(case_id, doc_info["file_name"])

        if doc_content:
            # Send document to user
            document = BufferedInputFile(
                doc_content,
                filename=doc_info["file_name"]
            )

            doc_label = DOCUMENT_TYPE_LABELS.get(document_type, document_type)
            await callback.message.answer_document(
                document=document,
                caption=f"✅ <b>{doc_label}</b>\n\n"
                        f"📁 Документ сохранён в папку дела.\n"
                        f"📄 Файл: {doc_info['file_name']}",
                parse_mode="HTML"
            )

            # Show option to view all case documents
            case = await api.get_case(case_id)
            await callback.message.answer(
                f"📂 <b>Документы дела {case['case_number']}</b>\n\n"
                "Все сгенерированные документы сохранены в папке дела.\n"
                "Используйте меню дела для просмотра всех документов.",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )

            logger.info(f"Document {document_type} generated for case {case_id}")
        else:
            await callback.message.answer(
                "❌ Не удалось загрузить сгенерированный документ.",
                reply_markup=get_main_keyboard()
            )

    except BotException as e:
        logger.error(f"Error generating document: {e}")
        await callback.message.answer(
            f"❌ {e.user_message}",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.exception(f"Unexpected error generating document: {e}")
        await callback.message.answer(
            "❌ Произошла ошибка при генерации документа.\n"
            "Попробуйте позже или обратитесь к администратору.",
            reply_markup=get_main_keyboard()
        )

    await state.clear()
    await callback.answer()


# ==================== LEGACY HANDLERS ====================

@router.message(Command("документ", "document"))
async def cmd_document(message: Message):
    """Command to generate document (legacy)"""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "📄 <b>Генерация документов</b>\n\n"
            "Используйте меню «📄 Документы» для генерации документов.\n\n"
            "Или используйте:\n"
            "📋 Мои дела → выберите дело → 📄 Создать заявление",
            parse_mode="HTML",
        )
        return

    await message.answer(
        "ℹ️ Пожалуйста, используйте меню «📄 Документы» для генерации документов."
    )


@router.callback_query(F.data.startswith("doc_"))
async def generate_document(callback: CallbackQuery):
    """Generate bankruptcy petition document (from case menu)"""
    case_id = int(callback.data.split("_")[1])

    await callback.message.answer("⏳ Генерирую заявление о банкротстве...")

    try:
        # Use API client with authentication
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{api.base_url}/api/documents/{case_id}/bankruptcy-application",
                headers=api._headers  # This includes the API token
            )

            if response.status_code == 200:
                # Send document to user
                document = BufferedInputFile(
                    response.content,
                    filename=f"bankruptcy_petition_{case_id}.docx"
                )
                await callback.message.answer_document(
                    document=document,
                    caption="✅ <b>Заявление о банкротстве сформировано</b>\n\n"
                           "Документ готов к подаче в суд.\n"
                           "📁 Документ также сохранён в папку дела.",
                    parse_mode="HTML"
                )
                logger.info(f"Document generated successfully for case {case_id}")

            elif response.status_code == 404:
                await callback.message.answer(
                    "❌ Дело не найдено. Возможно, оно было удалено."
                )
                logger.warning(f"Case {case_id} not found for document generation")

            elif response.status_code == 401:
                await callback.message.answer(
                    "❌ Ошибка авторизации. Обратитесь к администратору."
                )
                logger.error(f"Authentication error generating document for case {case_id}")

            elif response.status_code >= 500:
                await callback.message.answer(
                    "❌ Ошибка сервера. Попробуйте позже."
                )
                logger.error(f"Server error {response.status_code} generating document for case {case_id}")

            else:
                await callback.message.answer(
                    f"❌ Ошибка генерации документа (код {response.status_code})"
                )
                logger.error(f"Unexpected status {response.status_code} for case {case_id}")

    except httpx.TimeoutException:
        await callback.message.answer(
            "❌ Превышено время ожидания. Попробуйте позже."
        )
        logger.error(f"Timeout generating document for case {case_id}")

    except Exception as e:
        await callback.message.answer(
            "❌ Произошла ошибка при генерации документа."
        )
        logger.error(f"Document generation error for case {case_id}: {e}", exc_info=True)

    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("case:") & F.data.endswith(":generate"))
async def generate_from_case_menu(callback: CallbackQuery):
    """Generate document from case detail menu"""
    parts = callback.data.split(":")
    case_number = parts[1]

    # Need to get case_id from case_number
    try:
        # This is a workaround - ideally case_id should be in callback_data
        # For now, extract from existing case data or fetch
        await callback.answer("⏳ Генерирую документ...", show_alert=False)

        # Try to find case by number
        cases = await api.get_cases_by_user(callback.from_user.id)
        case = next((c for c in cases if c.get('case_number') == case_number), None)

        if case:
            case_id = case['id']
            # Reuse the main generation function
            callback.data = f"doc_{case_id}"
            await generate_document(callback)
        else:
            await callback.message.answer("❌ Не удалось найти дело")

    except Exception as e:
        logger.error(f"Error in generate_from_case_menu: {e}")
        await callback.message.answer("❌ Ошибка генерации документа")
        await callback.answer()


# ==================== VIEW CASE DOCUMENTS ====================

@router.callback_query(F.data.startswith("case:") & F.data.endswith(":documents"))
async def view_case_documents(callback: CallbackQuery):
    """View all documents for a case"""
    parts = callback.data.split(":")
    case_number = parts[1]

    try:
        # Find case by number
        cases = await api.get_cases_by_user(callback.from_user.id)
        case = next((c for c in cases if c.get('case_number') == case_number), None)

        if not case:
            await callback.answer("❌ Дело не найдено", show_alert=True)
            return

        case_id = case['id']

        # Get case documents
        documents = await api.get_case_documents(case_id)

        if not documents:
            await callback.answer(
                "📭 Документы ещё не созданы. Используйте меню «📄 Документы».",
                show_alert=True
            )
            return

        await callback.message.edit_text(
            f"📂 <b>Документы дела {case_number}</b>\n\n"
            f"Найдено документов: {len(documents)}\n\n"
            "Выберите документ для скачивания:",
            parse_mode="HTML",
            reply_markup=get_case_documents_keyboard(case_id, documents)
        )

    except Exception as e:
        logger.error(f"Error viewing case documents: {e}")
        await callback.answer("❌ Ошибка загрузки документов", show_alert=True)

    await callback.answer()


@router.callback_query(F.data.startswith("download:"))
async def download_case_document(callback: CallbackQuery):
    """Download a specific document from a case"""
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("❌ Ошибка формата", show_alert=True)
        return

    case_id = int(parts[1])
    file_name = parts[2]

    try:
        # Download document
        content = await api.download_document(case_id, file_name)

        if content:
            document = BufferedInputFile(content, filename=file_name)
            await callback.message.answer_document(
                document=document,
                caption=f"📄 {file_name}"
            )
        else:
            await callback.answer("❌ Документ не найден", show_alert=True)

    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        await callback.answer("❌ Ошибка загрузки документа", show_alert=True)

    await callback.answer()
