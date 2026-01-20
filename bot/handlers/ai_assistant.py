from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from services.api_client import APIClient

router = Router()
api = APIClient()


@router.message(Command("ai"))
@router.message(F.text == "💬 Спросить AI")
async def cmd_ai(message: Message):
    question = message.text.replace("/ai", "").strip()

    if not question or question == "💬 Спросить AI":
        await message.answer(
            "❓ <b>AI-ассистент по 127-ФЗ</b>\n\n"
            "Задайте вопрос по банкротству физических лиц.\n\n"
            "<b>Примеры:</b>\n"
            "• Какие документы нужны для банкротства?\n"
            "• Что такое реструктуризация долгов?\n"
            "• Кто такой финансовый управляющий?\n\n"
            "Используйте: /ai [ваш вопрос]",
            parse_mode="HTML",
        )
        return

    wait_msg = await message.answer("🤔 Думаю...")

    try:
        answer = await api.ask_ai(question)
        await wait_msg.edit_text(f"💡 <b>Ответ AI-ассистента:</b>\n\n{answer}", parse_mode="HTML")
    except Exception as e:
        await wait_msg.edit_text(
            "❌ Ошибка при обращении к AI. Попробуйте позже.\n\n"
            "Возможные причины:\n"
            "• AI сервис временно недоступен\n"
            "• Не настроен API ключ"
        )
