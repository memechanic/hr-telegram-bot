import logging
from typing import Dict, List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

logger = logging.getLogger(__name__)

def get_inline_keyboard(data: Dict[str, str]) -> InlineKeyboardMarkup:
    logger.debug('get_inline_keyboard')

    builder = InlineKeyboardBuilder()

    for data, text in data.items():
        builder.add(InlineKeyboardButton(text=text, callback_data=data))
    keyboard: InlineKeyboardMarkup = builder.as_markup(resize_keyboard=True)

    return keyboard

def get_reply_keyboard(buttons: List[str]) -> ReplyKeyboardMarkup:
    logger.debug('get_reply_keyboard')

    builder = ReplyKeyboardBuilder()

    for text in buttons:
        builder.add(KeyboardButton(text=text))
    keyboards: ReplyKeyboardMarkup = builder.as_markup(resize_keyboard=True)

    return keyboards