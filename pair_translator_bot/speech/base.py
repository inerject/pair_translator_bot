from abc import ABC, abstractmethod
from pathlib import Path

from ..language_pair import Language


class SpeechRecognitionError(Exception): ...


class SpeechRecognizer(ABC):
    @abstractmethod
    async def transcribe(
        self,
        audio_path: Path,
        language: Language,
    ) -> str: ...
