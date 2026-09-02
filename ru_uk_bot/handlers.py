from pathlib import Path
from tempfile import TemporaryDirectory

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .direction import Direction, Language
from .keyboards import direction_keyboard
from .speech.base import SpeechRecognizer
from .states import TranslationState
from .translation.base import TranslationProvider

router = Router()

UK_UNIQUE_CHARS = frozenset("іїєґ")
RU_UNIQUE_CHARS = frozenset("ыэёъ")


@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    direction = Direction.RU_TO_UK
    await _set_direction(state, direction)

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
    direction = (await _get_direction(state)).opposite()
    await _set_direction(state, direction)

    await message.answer(
        direction.label,
        reply_markup=direction_keyboard(direction),
    )


@router.message(F.voice)
async def translate_voice(
    message: Message,
    bot: Bot,
    state: FSMContext,
    translator: TranslationProvider,
    speech_recognizer: SpeechRecognizer,
) -> None:
    if message.voice is None:
        return

    direction = await _get_direction(state)

    with TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / "voice.ogg"

        await bot.download(
            message.voice,
            destination=audio_path,
        )

        text = await speech_recognizer.transcribe(
            audio_path,
            language=direction.source,
        )

    await message.answer(
        f"🎤 {_answer_prefix(direction.source)}{text}",
    )

    await _process_text(
        message=message,
        state=state,
        translator=translator,
        text=text,
        direction=direction,
    )


@router.message(F.text)
async def translate_text(
    message: Message,
    state: FSMContext,
    translator: TranslationProvider,
) -> None:
    if message.text is None:
        return

    text = message.text.strip()
    if not text:
        return

    await _process_text(
        message=message,
        state=state,
        translator=translator,
        text=text,
    )


async def _process_text(
    message: Message,
    state: FSMContext,
    translator: TranslationProvider,
    text: str,
    direction: Direction | None = None,
) -> None:
    direction_changed = False

    if direction is None:
        direction = await _get_direction(state)

        detected_direction = _detect_direction(text)
        if detected_direction is not None and detected_direction != direction:
            direction = detected_direction
            direction_changed = True
            await _set_direction(state, direction)

    result = await translator.translate(
        text=text,
        source=direction.source,
        target=direction.target,
    )

    await message.answer(
        f"{_answer_prefix(direction.target)}{result}",
        reply_markup=direction_keyboard(direction) if direction_changed else None,
    )


def _detect_direction(text: str) -> Direction | None:
    chars = set(text.lower())

    has_uk = bool(chars & UK_UNIQUE_CHARS)
    has_ru = bool(chars & RU_UNIQUE_CHARS)

    if has_uk and not has_ru:
        return Direction.UK_TO_RU

    if has_ru and not has_uk:
        return Direction.RU_TO_UK

    return None


async def _get_direction(state: FSMContext) -> Direction:
    current_state = await state.get_state()

    if current_state == TranslationState.uk_to_ru.state:
        return Direction.UK_TO_RU

    return Direction.RU_TO_UK


async def _set_direction(
    state: FSMContext,
    direction: Direction,
) -> None:
    match direction:
        case Direction.RU_TO_UK:
            await state.set_state(TranslationState.ru_to_uk)
        case Direction.UK_TO_RU:
            await state.set_state(TranslationState.uk_to_ru)


def _answer_prefix(lang: Language) -> str:
    return f"[{lang.value.upper()}] "
