from __future__ import annotations

import unicodedata

from gflanguages import LoadLanguages

from .errors import LanguagePairConfigurationError


def get_language_alphabet(language_code: str) -> frozenset[str]:
    primary_code = _primary_language_subtag(language_code)
    languages = LoadLanguages()

    alphabet: set[str] = set()

    for language in languages.values():
        if language.language.casefold() != primary_code:
            continue
        if not language.HasField("exemplar_chars"):
            continue
        if not language.exemplar_chars.HasField("base"):
            continue

        alphabet.update(_parse_exemplar_characters(language.exemplar_chars.base))

    if not alphabet:
        raise LanguagePairConfigurationError(
            f"No exemplar alphabet found for language: {language_code}"
        )

    return frozenset(alphabet)


def _primary_language_subtag(language_code: str) -> str:
    return language_code.split("-", 1)[0].casefold()


def _parse_exemplar_characters(value: str) -> set[str]:
    result: set[str] = set()

    for char in unicodedata.normalize("NFC", value):
        if not char.isalpha():
            continue

        lower = char.lower()
        result.add(lower if len(lower) == 1 else char)

    return result
