import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from ._version import __version__
from .config import settings
from .handlers import router
from .logging_config import setup_logging
from .middleware import WhitelistMiddleware
from .speech.google import GoogleSpeechRecognizer
from .translation.google import GoogleTranslationProvider

APP_NAME = "pair-translator-bot"
FULL_APP_NAME = f"{APP_NAME} v{__version__}"

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()

    logger.info("Start %s", FULL_APP_NAME)

    bot = Bot(token=settings.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.outer_middleware(WhitelistMiddleware(settings.allowed_user_ids))
    dp.include_router(router)

    translator = GoogleTranslationProvider(
        project_id=settings.google_cloud_project,
    )

    speech_recognizer = GoogleSpeechRecognizer()

    try:
        await dp.start_polling(
            bot,
            translator=translator,
            speech_recognizer=speech_recognizer,
        )
    finally:
        logger.info("Stop %s", FULL_APP_NAME)


if __name__ == "__main__":
    asyncio.run(main())
