import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .config import settings
from .handlers import router
from .logging_config import setup_logging
from .middleware import WhitelistMiddleware
from .speech.google import GoogleSpeechRecognizer
from .translation.google import GoogleTranslationProvider


async def main() -> None:
    setup_logging()

    bot = Bot(token=settings.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.outer_middleware(WhitelistMiddleware(settings.allowed_user_ids))
    dp.include_router(router)

    translator = GoogleTranslationProvider(
        project_id=settings.google_cloud_project,
    )

    speech_recognizer = GoogleSpeechRecognizer()

    await dp.start_polling(
        bot,
        translator=translator,
        speech_recognizer=speech_recognizer,
    )


if __name__ == "__main__":
    asyncio.run(main())
