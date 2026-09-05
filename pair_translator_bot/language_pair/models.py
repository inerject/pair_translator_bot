from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class Direction(str, Enum):
    FORWARD = auto()
    REVERSE = auto()

    def opposite(self) -> Direction:
        return Direction.REVERSE if self is Direction.FORWARD else Direction.FORWARD


@dataclass(frozen=True)
class LanguageConfig:
    code: str
    google_speech_language_code: str


@dataclass(frozen=True)
class Language:
    code: str
    google_speech_language_code: str
    label: str
    unique_chars: frozenset[str]


@dataclass(frozen=True)
class LanguagePair:
    source: Language
    target: Language

    def source_for(self, direction: Direction) -> Language:
        if direction is Direction.FORWARD:
            return self.source
        return self.target

    def target_for(self, direction: Direction) -> Language:
        if direction is Direction.FORWARD:
            return self.target
        return self.source

    def label_for(self, direction: Direction) -> str:
        source = self.source_for(direction)
        target = self.target_for(direction)
        return f"{source.label} → {target.label}"

    def detect_direction(self, text: str) -> Direction | None:
        chars = set(text.casefold())

        has_source = bool(chars & self.source.unique_chars)
        has_target = bool(chars & self.target.unique_chars)

        if has_source and not has_target:
            return Direction.FORWARD

        if has_target and not has_source:
            return Direction.REVERSE

        return None
