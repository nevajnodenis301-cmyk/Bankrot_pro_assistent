from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from services.api_client import APIClient
from exceptions import BotException, APIError, APITimeoutError, DocumentGenerationError
import logging
import httpx

logger = logging.getLogger(__name__)
router = Router()
api = APIClient()


@router.message(Command("документ", "document"))
async def cmd_document(message: Message):
    """Command to generate document (legacy)"""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "📄 <b>Генерация документов</b>\n\n"
            "Использование: /документ [номер_дела]\n"
            "Пример: /документ BP-2024-0001",
            parse_mode="HTML",
        )
        return
    
    await message.answer(
        "ℹ️ Пожалуйста, используйте меню дела для генерации документа:\n"
        "📋 Мои дела → выберите дело → 📄 Создать заявление"
    )


@router.callback_query(F.data.startswith("doc_"))
async def generate_document(callback: CallbackQuery):
    """Generate bankruptcy petition document"""
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
                           "Документ готов к подаче в суд.",
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
