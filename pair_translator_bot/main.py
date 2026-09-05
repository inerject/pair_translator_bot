import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from ._version import __version__
from .config import settings
from .handlers import configuration_error_router, router
from .language_pair import prepare_language_pair
from .language_pair.errors import LanguagePairConfigurationError
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

    await bot.set_my_commands(
        [
            BotCommand(
                command="start",
                description="Start the bot",
            ),
            BotCommand(
                command="help",
                description="Help",
            ),
        ]
    )

    dp.update.outer_middleware(WhitelistMiddleware(settings.allowed_user_ids))

    try:
        try:
            language_pair = await prepare_language_pair(settings)
        except LanguagePairConfigurationError as exc:
            language_pair_error = str(exc)

            logger.error(
                "Invalid language pair configuration: %s",
                language_pair_error,
            )

            dp.include_router(configuration_error_router)

            await dp.start_polling(
                bot,
                language_pair_error=language_pair_error,
            )
        else:
            dp.include_router(router)

            await dp.start_polling(
                bot,
                translator=GoogleTranslationProvider(
                    project_id=settings.google_cloud_project,
                ),
                speech_recognizer=GoogleSpeechRecognizer(),
                language_pair=language_pair,
            )
    finally:
        logger.info("Stop %s", FULL_APP_NAME)


if __name__ == "__main__":
    asyncio.run(main())
