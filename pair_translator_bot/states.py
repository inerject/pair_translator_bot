from aiogram.fsm.state import State, StatesGroup


class TranslationState(StatesGroup):
    ru_to_uk = State()
    uk_to_ru = State()
