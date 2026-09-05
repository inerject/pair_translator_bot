from __future__ import annotations

from google.api_core.exceptions import GoogleAPICallError, InvalidArgument
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import speech, translate_v3

from .errors import LanguagePairConfigurationError, LanguagePairPreparationError
from .models import LanguageConfig

SPEECH_TEST_SAMPLE_RATE = 16000
SPEECH_TEST_DURATION_SEC = 1


def validate_language_configs(
    project_id: str,
    source: LanguageConfig,
    target: LanguageConfig,
) -> tuple[LanguageConfig, LanguageConfig]:
    _validate_non_empty(source)
    _validate_non_empty(target)

    if source.code.casefold() == target.code.casefold():
        raise LanguagePairConfigurationError(
            "Source and target language codes must be different."
        )

    source, target = _validate_translation_codes(
        project_id=project_id,
        source=source,
        target=target,
    )

    _validate_speech_relation(source)
    _validate_speech_relation(target)
    _validate_speech_codes(source, target)

    return source, target


def _validate_non_empty(config: LanguageConfig) -> None:
    if not config.code:
        raise LanguagePairConfigurationError(
            "Translation language code must not be empty."
        )

    if not config.google_speech_language_code:
        raise LanguagePairConfigurationError(
            "Google Speech language code must not be empty."
        )


def _validate_translation_codes(
    project_id: str,
    source: LanguageConfig,
    target: LanguageConfig,
) -> tuple[LanguageConfig, LanguageConfig]:
    try:
        client = translate_v3.TranslationServiceClient()
        response = client.get_supported_languages(
            parent=f"projects/{project_id}/locations/global",
        )
    except (GoogleAPICallError, DefaultCredentialsError) as exc:
        raise LanguagePairPreparationError(
            "Failed to retrieve supported Google Translation languages."
        ) from exc

    languages = {item.language_code.casefold(): item for item in response.languages}

    source_item = languages.get(source.code.casefold())
    if source_item is None:
        raise LanguagePairConfigurationError(
            f"Unsupported Google Translation source language code: {source.code}"
        )
    if not source_item.support_source:
        raise LanguagePairConfigurationError(
            f"Google Translation language cannot be used as source: {source_item.language_code}"
        )

    target_item = languages.get(target.code.casefold())
    if target_item is None:
        raise LanguagePairConfigurationError(
            f"Unsupported Google Translation target language code: {target.code}"
        )
    if not target_item.support_target:
        raise LanguagePairConfigurationError(
            f"Google Translation language cannot be used as target: {target_item.language_code}"
        )

    return (
        LanguageConfig(
            code=source_item.language_code,
            google_speech_language_code=source.google_speech_language_code,
        ),
        LanguageConfig(
            code=target_item.language_code,
            google_speech_language_code=target.google_speech_language_code,
        ),
    )


def _validate_speech_relation(config: LanguageConfig) -> None:
    translation_primary = _primary_language_subtag(config.code)
    speech_primary = _primary_language_subtag(config.google_speech_language_code)

    if translation_primary != speech_primary:
        raise LanguagePairConfigurationError(
            "Google Speech language code "
            f"{config.google_speech_language_code!r} does not match "
            f"translation language code {config.code!r}."
        )


def _validate_speech_codes(
    source: LanguageConfig,
    target: LanguageConfig,
) -> None:
    try:
        client = speech.SpeechClient()

        for config in (source, target):
            _recognize_silence(
                client=client,
                language_code=config.google_speech_language_code,
            )
    except LanguagePairConfigurationError:
        raise
    except (GoogleAPICallError, DefaultCredentialsError) as exc:
        raise LanguagePairPreparationError(
            "Failed to validate Google Speech language codes."
        ) from exc


def _recognize_silence(
    client: speech.SpeechClient,
    language_code: str,
) -> None:
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SPEECH_TEST_SAMPLE_RATE,
        language_code=language_code,
    )
    audio = speech.RecognitionAudio(
        content=_make_silence_audio(),
    )

    try:
        client.recognize(
            config=config,
            audio=audio,
        )
    except InvalidArgument as exc:
        raise LanguagePairConfigurationError(
            f"Unsupported or invalid Google Speech language code: {language_code}"
        ) from exc


def _make_silence_audio() -> bytes:
    sample_count = SPEECH_TEST_SAMPLE_RATE * SPEECH_TEST_DURATION_SEC
    return b"\x00\x00" * sample_count


def _primary_language_subtag(language_code: str) -> str:
    return language_code.split("-", 1)[0].casefold()
