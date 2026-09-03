import asyncio
from pathlib import Path

from google.cloud import speech

from ..direction import Language
from .base import SpeechRecognitionError, SpeechRecognizer


class GoogleSpeechRecognizer(SpeechRecognizer):
    def __init__(self) -> None:
        self._client = speech.SpeechClient()

    async def transcribe(
        self,
        audio_path: Path,
        language: Language,
    ) -> str:
        try:
            return await asyncio.to_thread(
                self._transcribe_sync,
                audio_path,
                language,
            )
        except Exception as exc:
            raise SpeechRecognitionError("Google speech recognition failed") from exc

    def _transcribe_sync(
        self,
        audio_path: Path,
        language: Language,
    ) -> str:
        content = audio_path.read_bytes()

        audio = speech.RecognitionAudio(
            content=content,
        )

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,
            language_code=_language_code(language),
        )

        response = self._client.recognize(
            config=config,
            audio=audio,
        )

        return " ".join(
            result.alternatives[0].transcript
            for result in response.results
            if result.alternatives
        ).strip()


def _language_code(language: Language) -> str:
    match language:
        case Language.RU:
            return "ru-RU"
        case Language.UK:
            return "uk-UA"
