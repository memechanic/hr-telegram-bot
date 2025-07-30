import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from locales.loader import t

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command('admin'))
async def admin(message: Message):
    await message.answer(text=t('admin.help.message'))