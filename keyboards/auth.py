from aiogram.types import ReplyKeyboardRemove
from keyboards.keyboard_builder import get_inline_keyboard, get_reply_keyboard
from locales.loader import t

get_confirm_keyboard = get_inline_keyboard(
    {
        'confirm': t('auth.buttons.confirm'),
        'change': t('auth.buttons.change'),
    }
)

change_field_keyboard = get_reply_keyboard(
    [
        t('auth.buttons.full_name'),
        t('auth.buttons.email'),
        t('auth.buttons.phone_number')
    ],
    one_time_keyboard=True, resize_keyboard=True, adjust=[2, 1]
)

remove_keyboard = ReplyKeyboardRemove()