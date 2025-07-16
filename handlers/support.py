from aiogram import Router
from aiogram.types import Message

from locales.loader import t

router = Router()

@router.message()
async def help_cmd(message: Message):
    await message.answer(t('support.help'))

"""
/support - команда для связи с человеком
"""