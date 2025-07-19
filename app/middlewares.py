import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from mako.testing.helpers import result_lines

from service.users import is_user, is_admin, get_user

logger = logging.getLogger(__name__)

class CheckUserMiddleware(BaseMiddleware):

    def __init__(self, who: str):
        self.who = who

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data['event_from_user']
        check = await get_user(user.id)
        result = None

        if self.who == 'user' and check:
            result = await handler(user, data)
        elif self.who == 'admin' and check and check.is_admin:
            result = await handler(user, data)

        logger.debug(f"LoadUserMiddleware: event from user id={user.id}")
        return result