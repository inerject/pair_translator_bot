from __future__ import annotations

import asyncio
import logging

from ..config import Settings
from .alphabets import get_language_alphabet
from .cache import load_language_pair, save_language_pair
from .models import Language, LanguageConfig, LanguagePair
from .validation import validate_language_configs

logger = logging.getLogger(__name__)


async def prepare_language_pair(settings: Settings) -> LanguagePair:
    source_config, target_config = _get_language_configs(settings)

    cached = load_language_pair(
        source=source_config,
        target=target_config,
    )
    if cached is not None:
        logger.info(
            "Loaded language pair from cache: %s → %s",
            cached.source.label,
            cached.target.label,
        )
        return cached

    pair = await asyncio.to_thread(
        _build_language_pair,
        settings.google_cloud_project,
        source_config,
        target_config,
    )

    save_language_pair(
        source_config=source_config,
        target_config=target_config,
        pair=pair,
    )

    logger.info(
        "Prepared language pair: %s → %s",
        pair.source.label,
        pair.target.label,
    )

    return pair


def _get_language_configs(
    settings: Settings,
) -> tuple[LanguageConfig, LanguageConfig]:
    return (
        LanguageConfig(
            code=settings.base_source_language_code.strip(),
            google_speech_language_code=(
                settings.base_source_google_speech_language_code.strip()
            ),
        ),
        LanguageConfig(
            code=settings.base_target_language_code.strip(),
            google_speech_language_code=(
                settings.base_target_google_speech_language_code.strip()
            ),
        ),
    )


def _build_language_pair(
    project_id: str,
    source_config: LanguageConfig,
    target_config: LanguageConfig,
) -> LanguagePair:
    source_config, target_config = validate_language_configs(
        project_id=project_id,
        source=source_config,
        target=target_config,
    )

    source_alphabet = get_language_alphabet(source_config.code)
    target_alphabet = get_language_alphabet(target_config.code)

    return LanguagePair(
        source=_build_language(
            source_config,
            source_alphabet - target_alphabet,
        ),
        target=_build_language(
            target_config,
            target_alphabet - source_alphabet,
        ),
    )


def _build_language(
    config: LanguageConfig,
    unique_chars: frozenset[str],
) -> Language:
    return Language(
        code=config.code,
        google_speech_language_code=config.google_speech_language_code,
        label=config.code.upper(),
        unique_chars=unique_chars,
    )
