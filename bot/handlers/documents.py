from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.filters import Command
import httpx
from config import settings

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
            response.raise_for_status()

            # Send document
            document = BufferedInputFile(response.content, filename=f"bankruptcy_{case_id}.docx")
            await callback.message.answer_document(
                document=document, caption="📄 Заявление о банкротстве сформировано"
            )
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при генерации документа: {str(e)}")

    await callback.answer()
