from typing import Dict, List

from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_inline_keyboard(data: Dict[str, str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for data, text in data.items():
        builder.add(InlineKeyboardButton(text=text, callback_data=data))
    keyboard: InlineKeyboardMarkup = builder.as_markup(resize_keyboard=True)

    return keyboard

def get_reply_keyboard(buttons: List[str]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    for text in buttons:
        builder.add(KeyboardButton(text=text))
    keyboards: ReplyKeyboardMarkup = builder.as_markup(resize_keyboard=True)

    return keyboards