from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from .translation.base import TranslationError, TranslationProvider

logger = logging.getLogger(__name__)

HELP_TEXT_EN = """Send a text or voice message to translate it between the two configured languages.

Tap the direction button to switch the current translation direction.

For text messages, the translation direction may switch automatically when the input language can be identified reliably. Otherwise, the current direction is kept.

Voice messages are recognized in the language shown before the arrow on the direction button.
"""

CACHE_DIR = Path("cache") / "texts"

_help_text_cache: dict[str, str] = {}


async def get_help_text(
    translator: TranslationProvider,
    target_language_code: str,
) -> str:
    cached = _help_text_cache.get(target_language_code)
    if cached is not None:
        return cached

    source_hash = _text_hash(HELP_TEXT_EN)
    cache_path = CACHE_DIR / f"help.{target_language_code}.{source_hash}.txt"

    if cache_path.exists():
        try:
            text = cache_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            logger.exception("Failed to read cached help text: %s", cache_path)
        else:
            _help_text_cache[target_language_code] = text
            return text

    try:
        text = await translator.translate_codes(
            text=HELP_TEXT_EN,
            source_code="en",
            target_code=target_language_code,
        )
    except TranslationError:
        logger.exception(
            "Failed to translate help text to %s",
            target_language_code,
        )
        return HELP_TEXT_EN

    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(text, encoding="utf-8")
    except OSError:
        logger.exception("Failed to cache help text: %s", cache_path)

    _help_text_cache[target_language_code] = text
    return text


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
