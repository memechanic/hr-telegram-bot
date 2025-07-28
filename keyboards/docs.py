from aiogram.types import InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove

from keyboards.keyboard_builder import get_inline_keyboard
from locales.loader import t
from service.media import get_media_dirs

remove_keyboard = ReplyKeyboardRemove()

async def get_docs_keyboard() -> InlineKeyboardMarkup:
    data = {}

    buttons = await get_media_dirs('docs')
    for b in buttons:
        data.update({f"docs.{b}":b})

    keyboard = get_inline_keyboard(
        data=data,
        resize_keyboard=True,
        adjust=[1]
    )
    return keyboard

doc_back_keyboard = get_inline_keyboard(
    data = {
        "main": t('info.buttons.back')
    },
    resize_keyboard=True,
)