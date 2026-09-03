from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .direction import Direction


def direction_keyboard(direction: Direction) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=direction.label),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
