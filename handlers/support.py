import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from locales.loader import t

router = Router()

logger = logging.Logger(__name__)

@router.message(Command('help'))
async def help_cmd(message: Message):
    logger.debug('help_cmd')

    await message.answer(t('support.help'))

"""
/support - команда для связи с человеком
"""