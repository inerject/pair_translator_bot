from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .language_pair import Direction, LanguagePair


def direction_keyboard(
    direction: Direction,
    language_pair: LanguagePair,
) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=language_pair.label_for(direction)),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
