from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from service.users import is_user, is_admin


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

        user = data['event_from_user']
        check = await is_user(user.id)

        if check:
            result = await handler(event, data)
        else: result = None

        return result

class AdminMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:

        user = data['event_from_user']
        check = await is_admin(user.id)

        if check:
            result = await handler(event, data)
        else: result = None

        return result