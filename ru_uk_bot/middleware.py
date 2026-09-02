from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User


class WhitelistMiddleware(BaseMiddleware):
    def __init__(self, allowed_user_ids: set[int]) -> None:
        self._allowed_user_ids = allowed_user_ids

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")

        if user is None or user.id not in self._allowed_user_ids:
            return None

        return await handler(event, data)
