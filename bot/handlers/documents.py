from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.filters import Command
import httpx
from config import settings
from exceptions import (
    BotException,
    APIError,
    APITimeoutError,
    DocumentGenerationError,
)
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("документ", "document"))
async def cmd_document(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "📄 <b>Генерация документов</b>\n\n"
            "Использование: /документ [номер_дела]\n"
            "Пример: /документ BP-2024-0001",
            parse_mode="HTML",
        )
        return

    case_number = parts[1].strip()
    await message.answer("⏳ Генерирую документ...")

    # Note: This is a simplified version. In production, you'd need to:
    # 1. Find case by case_number
    # 2. Download document from API
    # 3. Send to user
    await message.answer(
        "ℹ️ Генерация документов через бот будет доступна в следующей версии.\n"
        "Пожалуйста, используйте веб-интерфейс для получения документов."
    )


@router.callback_query(F.data.startswith("doc_"))
async def generate_document(callback: CallbackQuery):
    case_id = int(callback.data.split("_")[1])

    await callback.message.answer("⏳ Генерирую документ...")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{settings.API_BASE_URL}/api/documents/{case_id}/bankruptcy-application")

            if response.status_code == 200:
                # Send document
                document = BufferedInputFile(response.content, filename=f"bankruptcy_{case_id}.docx")
                await callback.message.answer_document(
                    document=document, caption="📄 Заявление о банкротстве сформировано"
                )
            elif response.status_code == 404:
                await callback.message.answer(
                    "❌ Дело не найдено. Проверьте номер дела."
                )
            elif response.status_code >= 500:
                raise APIError(f"Server error: {response.status_code}", status_code=response.status_code)
            else:
                raise DocumentGenerationError(f"Failed to generate document: {response.status_code}")

    except httpx.TimeoutException:
        logger.error(f"Timeout generating document for case {case_id}")
        await callback.message.answer(
            "❌ Сервер не отвечает. Генерация документа занимает больше времени, чем ожидалось.\n"
            "Попробуйте позже или обратитесь к администратору."
        )
    except httpx.NetworkError as e:
        logger.error(f"Network error generating document for case {case_id}: {e}")
        await callback.message.answer(
            "❌ Ошибка сети. Проверьте подключение к интернету и попробуйте позже."
        )
    except DocumentGenerationError as e:
        logger.error(f"Document generation error for case {case_id}: {e}")
        await callback.message.answer(f"❌ {e.user_message}")
    except BotException as e:
        logger.error(f"Bot exception generating document for case {case_id}: {e}")
        await callback.message.answer(f"❌ {e.user_message}")
    except Exception as e:
        logger.exception(f"Unexpected error generating document for case {case_id}: {e}")
        await callback.message.answer(
            "❌ Произошла непредвиденная ошибка при генерации документа.\n"
            "Попробуйте позже или обратитесь к администратору."
        )

    await callback.answer()
