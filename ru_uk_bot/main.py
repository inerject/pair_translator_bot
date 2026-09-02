import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .config import settings
from .handlers import router
from .middleware import WhitelistMiddleware
from .translator import NoopTranslationProvider


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot_token.get_secret_value())

    dp = Dispatcher(storage=MemoryStorage())

    dp.update.outer_middleware(WhitelistMiddleware(settings.allowed_user_ids))

    dp.include_router(router)

    await dp.start_polling(
        bot,
        translator=NoopTranslationProvider(),
    )


if __name__ == "__main__":
    asyncio.run(main())
