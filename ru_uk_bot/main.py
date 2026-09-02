import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .config import settings
from .handlers import router
from .middleware import WhitelistMiddleware
from .translation.google import GoogleTranslationProvider


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=settings.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.outer_middleware(WhitelistMiddleware(settings.allowed_user_ids))
    dp.include_router(router)

    translator = GoogleTranslationProvider(
        project_id=settings.google_cloud_project,
    )

    await dp.start_polling(
        bot,
        translator=translator,
    )


if __name__ == "__main__":
    asyncio.run(main())
