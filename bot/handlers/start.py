import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, CommandObject
from keyboards.reply import get_main_keyboard
from services.api_client import APIClient

router = Router()
api = APIClient()
logger = logging.getLogger(__name__)

DISCLAIMER = """⚠️ <b>Юридический дисклеймер</b>

Данный бот предоставляет информационную поддержку и НЕ является юридической консультацией.

Для принятия решений по вашему делу обратитесь к квалифицированному юристу.

Персональные данные (паспорт, ИНН) хранятся на защищённом сервере и не передаются через Telegram."""


@router.message(CommandStart(deep_link=True))
async def cmd_start_with_code(message: Message, command: CommandObject):
    """Handle /start with deep link code for Telegram linking."""
    code = command.args

    if not code:
        # No code provided, show regular welcome
        await cmd_start(message)
        return

    # Clean the code (remove whitespace)
    code = code.strip()

    # Validate code format (6-10 alphanumeric characters)
    if not code.isalnum() or len(code) < 6 or len(code) > 10:
        await message.answer(
            "❌ <b>Неверный формат кода</b>\n\n"
            "Код должен содержать 6-10 символов.\n"
            "Проверьте код и попробуйте снова.",
            parse_mode="HTML"
        )
        return

    telegram_id = message.from_user.id
    telegram_username = message.from_user.username

    logger.info(f"Telegram linking attempt: user={telegram_id}, code={code[:3]}***")

    # Check if user is already linked
    try:
        existing_user = await api.get_user_by_telegram_id(telegram_id)
        if existing_user:
            await message.answer(
                f"ℹ️ <b>Telegram уже привязан</b>\n\n"
                f"Ваш аккаунт уже связан с пользователем:\n"
                f"<b>{existing_user.get('full_name', 'Неизвестно')}</b>\n"
                f"📧 {existing_user.get('email', '')}\n\n"
                "Для привязки к другому аккаунту сначала отвяжите текущий в веб-интерфейсе.",
                parse_mode="HTML"
            )
            return
    except Exception as e:
        logger.error(f"Error checking existing link: {e}")
        # Continue with linking attempt

    # Attempt to confirm the linking
    try:
        await message.answer(
            "⏳ <b>Проверка кода...</b>",
            parse_mode="HTML"
        )

        user = await api.confirm_telegram_link(
            linking_code=code,
            telegram_id=telegram_id,
            telegram_username=telegram_username
        )

        if user:
            logger.info(f"Telegram linked successfully: user_id={user.get('id')}, telegram_id={telegram_id}")
            await message.answer(
                f"✅ <b>Telegram успешно привязан!</b>\n\n"
                f"Добро пожаловать, <b>{user.get('full_name', 'Пользователь')}</b>!\n\n"
                f"Теперь вы будете получать уведомления о важных событиях.\n\n"
                f"📋 <b>Доступные команды:</b>\n"
                f"/новое_дело — создать дело\n"
                f"/список_дел — ваши дела\n"
                f"/помощь — справка",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
        else:
            logger.warning(f"Linking failed for telegram_id={telegram_id}, code={code[:3]}***")
            await message.answer(
                "❌ <b>Не удалось привязать Telegram</b>\n\n"
                "Возможные причины:\n"
                "• Код истёк (действует 10 минут)\n"
                "• Код уже был использован\n"
                "• Неверный код\n\n"
                "Получите новый код в веб-интерфейсе:\n"
                "💬 Telegram → Связать аккаунт",
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"Error during telegram linking: {e}")
        await message.answer(
            "❌ <b>Ошибка при привязке</b>\n\n"
            "Произошла техническая ошибка. Попробуйте позже.\n\n"
            "Если ошибка повторяется, обратитесь в поддержку.",
            parse_mode="HTML"
        )


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command without deep link."""
    # Check if user is already linked
    telegram_id = message.from_user.id
    linked_info = ""

    try:
        user = await api.get_user_by_telegram_id(telegram_id)
        if user:
            linked_info = f"\n\n✅ <b>Аккаунт привязан:</b> {user.get('full_name', '')}"
    except Exception:
        pass  # Ignore errors, just don't show linked info

    await message.answer(
        f"👋 Здравствуйте, {message.from_user.first_name}!\n\n"
        "Я бот-помощник по банкротству физических лиц.\n\n"
        f"{DISCLAIMER}"
        f"{linked_info}\n\n"
        "📋 <b>Доступные команды:</b>\n"
        "/новое_дело — создать дело\n"
        "/список_дел — ваши дела\n"
        "/документы — генерация документов\n"
        "/ai [вопрос] — спросить по 127-ФЗ\n"
        "/помощь — справка\n\n"
        "🔗 <b>Привязка аккаунта:</b>\n"
        "Для привязки Telegram к веб-аккаунту\n"
        "перейдите в веб-интерфейс → 💬 Telegram",
        parse_mode="HTML",
        reply_markup=get_main_keyboard(),
    )


@router.message(Command("помощь", "help"))
@router.message(F.text == "❓ Помощь")
async def cmd_help(message: Message):
    """Handle /help command."""
    await message.answer(
        "📖 <b>Справка</b>\n\n"
        "<b>Основные команды:</b>\n"
        "/новое_дело — создать новое дело о банкротстве\n"
        "/список_дел — просмотреть все ваши дела\n"
        "/документы — генерировать документы для дел\n"
        "/ai [вопрос] — задать вопрос AI-ассистенту по 127-ФЗ\n\n"
        "<b>Типы документов:</b>\n"
        "📜 Заявление о банкротстве — полное заявление\n"
        "📋 Простое заявление — базовый шаблон\n"
        "📨 Уведомление кредиторов — письмо кредиторам\n"
        "⚖️ Ходатайство в суд — судебное ходатайство\n\n"
        "<b>Типы процедур:</b>\n"
        "🏠 Реализация имущества — продажа имущества для погашения\n"
        "📊 Реструктуризация долгов — план погашения долгов\n\n"
        "<b>Привязка аккаунта:</b>\n"
        "Для привязки Telegram перейдите в веб-интерфейс,\n"
        "откройте раздел 💬 Telegram и следуйте инструкциям.\n\n"
        f"{DISCLAIMER}",
        parse_mode="HTML",
    )


@router.message(Command("link", "связать"))
async def cmd_link_info(message: Message):
    """Show info about how to link Telegram account."""
    await message.answer(
        "🔗 <b>Привязка Telegram аккаунта</b>\n\n"
        "Чтобы привязать Telegram к вашему аккаунту:\n\n"
        "1️⃣ Войдите в веб-интерфейс\n"
        "2️⃣ Откройте раздел <b>💬 Telegram</b>\n"
        "3️⃣ Нажмите <b>«Связать Telegram»</b>\n"
        "4️⃣ Скопируйте код и отправьте его сюда\n\n"
        "Формат: <code>/start КОД</code>\n\n"
        "Например: <code>/start ABC123</code>",
        parse_mode="HTML"
    )
