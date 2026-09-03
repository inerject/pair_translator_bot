import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import settings

_FORMATTER = logging.Formatter(
    "%(asctime)s.%(msecs)03d | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_LOG_DIR = Path("logs")
_MESSAGE_LOG_DIR = _LOG_DIR / "messages"

_configured = False


def setup_logging() -> None:
    global _configured
    if _configured:
        return

    _setup_root_logger()
    _setup_message_logger()
    _configured = True


def _setup_root_logger() -> None:
    root_logger = logging.getLogger()

    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    app_handler = RotatingFileHandler(
        _LOG_DIR / "app.log",
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    app_handler.setFormatter(_FORMATTER)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(_FORMATTER)

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(console_handler)


def _setup_message_logger() -> None:
    message_logger = logging.getLogger("messages")
    message_logger.propagate = False

    if not settings.log_message_text:
        return

    _MESSAGE_LOG_DIR.mkdir(parents=True, exist_ok=True)

    message_handler = RotatingFileHandler(
        _MESSAGE_LOG_DIR / "messages.log",
        maxBytes=settings.message_log_max_bytes,
        backupCount=settings.message_log_backup_count,
        encoding="utf-8",
    )
    message_handler.setFormatter(_FORMATTER)

    message_logger.setLevel(logging.INFO)
    message_logger.addHandler(message_handler)
