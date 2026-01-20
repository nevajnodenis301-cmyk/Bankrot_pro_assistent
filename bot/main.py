import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from bot.config import settings
from bot.handlers import start, cases, documents, ai_assistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=settings.TELEGRAM_TOKEN)

    # Redis storage for FSM
    redis = Redis.from_url(settings.REDIS_URL)
    storage = RedisStorage(redis=redis)

    dp = Dispatcher(storage=storage)

    # Include routers
    dp.include_router(start.router)
    dp.include_router(cases.router)
    dp.include_router(documents.router)
    dp.include_router(ai_assistant.router)

    logger.info("Bot started")

    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        await bot.session.close()
        await redis.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
