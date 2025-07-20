import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject

from service.users import is_user, is_admin

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
        result = None
        user_id = data['event_from_user'].id
        bot: Bot = data['bot']

        logger.debug(f"LoadUserMiddleware: event from user id={user_id}")

        flag_is_user = await is_user(user_id)
        flag_is_admin = await is_admin(user_id)

        if self.who == 'user' and flag_is_user:
            result = await handler(event, data)

        elif self.who == 'admin' and flag_is_admin:
            result = await handler(event, data)

        return result