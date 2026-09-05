from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from .models import Language, LanguageConfig, LanguagePair

logger = logging.getLogger(__name__)

CACHE_SCHEMA_VERSION = 1
CACHE_DIR = Path("cache") / "language_pairs"


def load_language_pair(
    source: LanguageConfig,
    target: LanguageConfig,
) -> LanguagePair | None:
    cache_path = _cache_path(source, target)

    if not cache_path.exists():
        return None

    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))

        if data["schema_version"] != CACHE_SCHEMA_VERSION:
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
            cache_path,
        )
        return None


def save_language_pair(
    source_config: LanguageConfig,
    target_config: LanguageConfig,
    pair: LanguagePair,
) -> None:
    cache_path = _cache_path(
        source_config,
        target_config,
    )

    data = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "source": _language_to_dict(pair.source),
        "target": _language_to_dict(pair.target),
    }

    try:
        cache_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        cache_path.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError:
        logger.exception(
            "Failed to write language pair cache: %s",
            cache_path,
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


def _cache_path(
    source: LanguageConfig,
    target: LanguageConfig,
) -> Path:
    values = [
        str(CACHE_SCHEMA_VERSION),
        source.code.casefold(),
        source.google_speech_language_code.casefold(),
        target.code.casefold(),
        target.google_speech_language_code.casefold(),
    ]

    digest = hashlib.sha256("\0".join(values).encode("utf-8")).hexdigest()[:12]

    return CACHE_DIR / f"language_pair.{digest}.json"
