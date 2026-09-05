import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .keyboards import direction_keyboard
from .language_pair import Direction, Language, LanguagePair
from .speech.base import SpeechRecognizer
from .states import TranslationState
from .texts import get_help_text
from .translation.base import TranslationProvider

BASE_DIRECTION = Direction.FORWARD

message_logger = logging.getLogger("messages")
router = Router()


@router.message(CommandStart())
async def start(
    message: Message,
    state: FSMContext,
    translator: TranslationProvider,
    language_pair: LanguagePair,
) -> None:
    await _set_direction(state, BASE_DIRECTION)

    await _send_help(
        message=message,
        state=state,
        translator=translator,
        language_pair=language_pair,
        show_keyboard=True,
    )


@router.message(Command("help"))
async def help_command(
    message: Message,
    state: FSMContext,
    translator: TranslationProvider,
    language_pair: LanguagePair,
) -> None:
    await _send_help(
        message=message,
        state=state,
        translator=translator,
        language_pair=language_pair,
        show_keyboard=False,
    )


@router.message(F.voice)
async def translate_voice(
    message: Message,
    bot: Bot,
    state: FSMContext,
    translator: TranslationProvider,
    speech_recognizer: SpeechRecognizer,
    language_pair: LanguagePair,
) -> None:
    if message.voice is None:
        return

    direction = await _get_direction(state)
    source = language_pair.source_for(direction)

    with TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / "voice.ogg"

        await bot.download(
            message.voice,
            destination=audio_path,
        )

        text = await speech_recognizer.transcribe(
            audio_path,
            language=source,
        )

    await message.answer(
        f"🎤 {_lang_prefix(source)}{text}",
    )

    await _process_text(
        message=message,
        state=state,
        translator=translator,
        language_pair=language_pair,
        text=text,
        direction=direction,
    )


@router.message(F.text)
async def handle_text(
    message: Message,
    state: FSMContext,
    translator: TranslationProvider,
    language_pair: LanguagePair,
) -> None:
    if message.text is None:
        return

    text = message.text.strip()
    if not text:
        return

    direction = await _get_direction(state)

    if _is_direction_button(text, language_pair):
        direction = direction.opposite()
        await _set_direction(state, direction)

        await message.answer(
            language_pair.label_for(direction),
            reply_markup=direction_keyboard(
                direction,
                language_pair,
            ),
        )
        return

    await _process_text(
        message=message,
        state=state,
        translator=translator,
        language_pair=language_pair,
        text=text,
    )


async def _send_help(
    message: Message,
    state: FSMContext,
    translator: TranslationProvider,
    language_pair: LanguagePair,
    show_keyboard: bool,
) -> None:
    text = await get_help_text(
        translator,
        target_language_code=language_pair.target.code,
    )

    reply_markup = None

    if show_keyboard:
        direction = await _get_direction(state)
        reply_markup = direction_keyboard(
            direction,
            language_pair,
        )

    await message.answer(
        text,
        reply_markup=reply_markup,
    )


async def _process_text(
    message: Message,
    state: FSMContext,
    translator: TranslationProvider,
    language_pair: LanguagePair,
    text: str,
    direction: Direction | None = None,
) -> None:
    direction_changed = False

    if direction is None:
        direction = await _get_direction(state)

        detected_direction = language_pair.detect_direction(text)

        if detected_direction is not None and detected_direction is not direction:
            direction = detected_direction
            direction_changed = True
            await _set_direction(state, direction)

    source = language_pair.source_for(direction)
    target = language_pair.target_for(direction)

    user_id = message.from_user.id if message.from_user else None

    input_text = f"{_lang_prefix(source)}{text}"
    message_logger.info("%s < %s", user_id, input_text)

    result = await translator.translate(
        text=text,
        source=source,
        target=target,
    )

    output_text = f"{_lang_prefix(target)}{result}"

    await message.answer(
        output_text,
        reply_markup=(
            direction_keyboard(direction, language_pair) if direction_changed else None
        ),
    )

    message_logger.info("%s > %s", user_id, output_text)


def _is_direction_button(
    text: str,
    language_pair: LanguagePair,
) -> bool:
    return text in {
        language_pair.label_for(Direction.FORWARD),
        language_pair.label_for(Direction.REVERSE),
    }


def _lang_prefix(language: Language) -> str:
    return f"[{language.label}] "


async def _set_direction(
    state: FSMContext,
    direction: Direction,
) -> None:
    await state.set_state(
        TranslationState.forward
        if direction is Direction.FORWARD
        else TranslationState.reverse
    )


async def _get_direction(state: FSMContext) -> Direction:
    current_state = await state.get_state()

    if current_state == TranslationState.reverse.state:
        return Direction.REVERSE

    return Direction.FORWARD
