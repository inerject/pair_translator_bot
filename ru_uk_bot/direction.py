from enum import Enum


class Language(str, Enum):
    RU = "ru"
    UK = "uk"


class Direction(str, Enum):
    RU_TO_UK = "ru_to_uk"
    UK_TO_RU = "uk_to_ru"

    @property
    def source(self) -> Language:
        match self:
            case Direction.RU_TO_UK:
                return Language.RU
            case Direction.UK_TO_RU:
                return Language.UK

    @property
    def target(self) -> Language:
        match self:
            case Direction.RU_TO_UK:
                return Language.UK
            case Direction.UK_TO_RU:
                return Language.RU

    @property
    def label(self) -> str:
        match self:
            case Direction.RU_TO_UK:
                return "RU → UK"
            case Direction.UK_TO_RU:
                return "UK → RU"

    def opposite(self) -> "Direction":
        match self:
            case Direction.RU_TO_UK:
                return Direction.UK_TO_RU
            case Direction.UK_TO_RU:
                return Direction.RU_TO_UK
