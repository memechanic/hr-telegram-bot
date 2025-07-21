import logging
from typing import Dict, List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

logger = logging.getLogger(__name__)

def get_inline_keyboard(data: Dict[str, str], **kwargs) -> InlineKeyboardMarkup:
    logger.debug('get_inline_keyboard')

    builder = InlineKeyboardBuilder()

    for data, text in data.items():
        builder.add(InlineKeyboardButton(text=text, callback_data=data))

    if 'adjust' in kwargs:
        rows = kwargs['adjust']
        builder.adjust(*rows)

    keyboard: InlineKeyboardMarkup = builder.as_markup(**kwargs)

    return keyboard

def get_reply_keyboard(buttons: List[str], **kwargs) -> ReplyKeyboardMarkup:
    logger.debug('get_reply_keyboard')

    builder = ReplyKeyboardBuilder()

    for text in buttons:
        builder.add(KeyboardButton(text=text))

    if 'adjust' in kwargs:
        rows = kwargs['adjust']
        builder.adjust(*rows)

    keyboards: ReplyKeyboardMarkup = builder.as_markup(**kwargs)

    return keyboards