from abc import ABC, abstractmethod

from .direction import Language


class TranslationError(Exception):
    pass


class TranslationProvider(ABC):
    @abstractmethod
    async def translate(
        self,
        text: str,
        source: Language,
        target: Language,
    ) -> str: ...


class NoopTranslationProvider(TranslationProvider):
    async def translate(
        self,
        text: str,
        source: Language,
        target: Language,
    ) -> str:
        return f"[{source.value.upper()} → {target.value.upper()}]\n{text}"
