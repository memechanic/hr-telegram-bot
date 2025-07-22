import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from service.media import send_media

router = Router()

logger = logging.getLogger(__name__)

@router.message(Command('company'))
async def company(message: Message):
    logger.debug("company")

    await send_media(message, 'info', 'company')