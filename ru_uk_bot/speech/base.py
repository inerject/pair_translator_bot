from abc import ABC, abstractmethod
from pathlib import Path

from ..direction import Language


class SpeechRecognitionError(Exception): ...


class SpeechRecognizer(ABC):
    @abstractmethod
    async def transcribe(
        self,
        audio_path: Path,
        language: Language,
    ) -> str: ...
