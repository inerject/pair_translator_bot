from abc import ABC, abstractmethod

from ..direction import Language


class TranslationError(Exception): ...


class TranslationProvider(ABC):
    @abstractmethod
    async def translate(
        self,
        text: str,
        source: Language,
        target: Language,
    ) -> str: ...
