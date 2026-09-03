import asyncio

from google.cloud import translate_v3

from ..direction import Language
from .base import TranslationError, TranslationProvider


class GoogleTranslationProvider(TranslationProvider):
    def __init__(self, project_id: str) -> None:
        self._client = translate_v3.TranslationServiceClient()
        self._parent = f"projects/{project_id}/locations/global"

    async def translate(
        self,
        text: str,
        source: Language,
        target: Language,
    ) -> str:
        try:
            return await asyncio.to_thread(
                self._translate_sync,
                text,
                source,
                target,
            )
        except Exception as exc:
            raise TranslationError("Google translation failed") from exc

    def _translate_sync(
        self,
        text: str,
        source: Language,
        target: Language,
    ) -> str:
        response = self._client.translate_text(
            contents=[text],
            parent=self._parent,
            mime_type="text/plain",
            source_language_code=source.value,
            target_language_code=target.value,
        )

        if not response.translations:
            raise TranslationError("Google returned no translations")

        return response.translations[0].translated_text
