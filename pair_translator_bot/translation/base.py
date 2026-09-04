from abc import ABC, abstractmethod

from ..direction import Language


class TranslationError(Exception): ...


class TranslationProvider(ABC):
    @abstractmethod
    async def translate_codes(
        self,
        text: str,
        source_code: str,
        target_code: str,
    ) -> str: ...

    async def translate(
        self,
        text: str,
        source: Language,
        target: Language,
    ) -> str:
        return await self.translate_codes(
            text,
            source.value,
            target.value,
        )
