from __future__ import annotations

import asyncio
from pathlib import Path

from google.cloud import speech

from ..language_pair import Language
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
                language.google_speech_language_code,
            )
        except Exception as exc:
            raise SpeechRecognitionError("Google speech recognition failed") from exc

    def _transcribe_sync(
        self,
        audio_path: Path,
        language_code: str,
    ) -> str:
        audio = speech.RecognitionAudio(
            content=audio_path.read_bytes(),
        )

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=48000,
            language_code=language_code,
        )

        response = self._client.recognize(
            config=config,
            audio=audio,
        )

        if not response.results:
            raise SpeechRecognitionError(
                "Google returned no speech recognition results"
            )

        return " ".join(
            result.alternatives[0].transcript
            for result in response.results
            if result.alternatives
        )
