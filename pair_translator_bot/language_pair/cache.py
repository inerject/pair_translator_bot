from __future__ import annotations

import json
import logging
from pathlib import Path

from .models import Language, LanguageConfig, LanguagePair

logger = logging.getLogger(__name__)

CACHE_SCHEMA_VERSION = 1
CACHE_PATH = Path("cache") / "language_pair.json"


def load_language_pair(
    source: LanguageConfig,
    target: LanguageConfig,
) -> LanguagePair | None:
    if not CACHE_PATH.exists():
        return None

    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))

        if data["schema_version"] != CACHE_SCHEMA_VERSION:
            return None

        if not _config_matches(data, source, target):
            return None

        return LanguagePair(
            source=_load_language(data["source"]),
            target=_load_language(data["target"]),
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
    ):
        logger.exception(
            "Failed to read language pair cache: %s",
            CACHE_PATH,
        )
        return None


def save_language_pair(
    source_config: LanguageConfig,
    target_config: LanguageConfig,
    pair: LanguagePair,
) -> None:
    data = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "config": {
            "source": _config_to_dict(source_config),
            "target": _config_to_dict(target_config),
        },
        "source": _language_to_dict(pair.source),
        "target": _language_to_dict(pair.target),
    }

    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError:
        logger.exception(
            "Failed to write language pair cache: %s",
            CACHE_PATH,
        )


def _config_matches(
    data: dict,
    source: LanguageConfig,
    target: LanguageConfig,
) -> bool:
    config = data["config"]

    return config["source"] == _config_to_dict(source) and config[
        "target"
    ] == _config_to_dict(target)


def _config_to_dict(config: LanguageConfig) -> dict[str, str]:
    return {
        "code": config.code,
        "google_speech_language_code": config.google_speech_language_code,
    }


def _language_to_dict(language: Language) -> dict[str, str]:
    return {
        "code": language.code,
        "google_speech_language_code": language.google_speech_language_code,
        "label": language.label,
        "unique_chars": "".join(sorted(language.unique_chars)),
    }


def _load_language(data: dict) -> Language:
    return Language(
        code=data["code"],
        google_speech_language_code=data["google_speech_language_code"],
        label=data["label"],
        unique_chars=frozenset(data["unique_chars"]),
    )
