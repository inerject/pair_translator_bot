from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .direction import Direction
from .keyboards import direction_keyboard
from .states import TranslationState
from .translation.base import TranslationProvider

router = Router()

UK_UNIQUE_CHARS = frozenset("іїєґ")
RU_UNIQUE_CHARS = frozenset("ыэёъ")


def detect_direction(text: str) -> Direction | None:
    chars = set(text.lower())

    has_uk = bool(chars & UK_UNIQUE_CHARS)
    has_ru = bool(chars & RU_UNIQUE_CHARS)

    if has_uk and not has_ru:
        return Direction.UK_TO_RU

    if has_ru and not has_uk:
        return Direction.RU_TO_UK

    return None


async def get_direction(state: FSMContext) -> Direction:
    current_state = await state.get_state()

    if current_state == TranslationState.uk_to_ru.state:
        return Direction.UK_TO_RU

    return Direction.RU_TO_UK


async def set_direction(
    state: FSMContext,
    direction: Direction,
) -> None:
    match direction:
        case Direction.RU_TO_UK:
            await state.set_state(TranslationState.ru_to_uk)
        case Direction.UK_TO_RU:
            await state.set_state(TranslationState.uk_to_ru)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    direction = Direction.RU_TO_UK
    await set_direction(state, direction)

    await message.answer(
        "Надішли текст для перекладу.",
        reply_markup=direction_keyboard(direction),
    )


@router.message(
    F.text.in_(
        {
            Direction.RU_TO_UK.label,
            Direction.UK_TO_RU.label,
        }
    )
)
async def toggle_direction(message: Message, state: FSMContext) -> None:
    direction = (await get_direction(state)).opposite()
    await set_direction(state, direction)

    await message.answer(
        direction.label,
        reply_markup=direction_keyboard(direction),
    )


@router.message(F.text)
async def translate(
    message: Message,
    state: FSMContext,
    translator: TranslationProvider,
) -> None:
    if message.text is None:
        return

    text = message.text.strip()
    if not text:
        return

    direction = await get_direction(state)

    detected_direction = detect_direction(text)
    direction_changed = (
        detected_direction is not None and detected_direction != direction
    )

    if detected_direction is not None:
        direction = detected_direction
        await set_direction(state, direction)

    result = await translator.translate(
        text=text,
        source=direction.source,
        target=direction.target,
    )

    await message.answer(
        result,
        reply_markup=(direction_keyboard(direction) if direction_changed else None),
    )
