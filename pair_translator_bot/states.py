from aiogram.fsm.state import State, StatesGroup


class TranslationState(StatesGroup):
    forward = State()
    reverse = State()
