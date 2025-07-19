import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject

from app.commands import COMMANDS, USER_COMMANDS, ADMIN_COMMANDS
from service.users import is_user, is_admin

logger = logging.getLogger(__name__)

class CheckUserMiddleware(BaseMiddleware):

    def __init__(self, who: str = ""):
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

        if self.who == "":
            await bot.set_my_commands(COMMANDS)

        elif self.who == 'user' and await is_user(user_id):
            await bot.set_my_commands(USER_COMMANDS)

        elif self.who == 'admin' and await is_admin(user_id):
            await bot.set_my_commands(ADMIN_COMMANDS)

        return await handler(event, data)