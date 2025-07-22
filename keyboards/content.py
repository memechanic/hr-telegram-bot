from aiogram.types import InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove

from keyboards.keyboard_builder import get_inline_keyboard
from locales.loader import t
from service.callback_data_factory import MediaTagList
from service.media import get_media_dirs

remove_keyboard = ReplyKeyboardRemove()

main_content_keyboard = get_inline_keyboard(
    data = {
        'info': t('admin.content.buttons.info'),
        'tag_list': t('admin.content.buttons.list'),
    },
    resize_keyboard=True,
    adjust=[1, 1, 1]
)

back_content_keyboard = get_inline_keyboard(
    data = {
        'main': t('admin.content.buttons.back'),
    },
    resize_keyboard=True,
)

def get_media_list_keyboard(tag:str, number: int = None) -> InlineKeyboardMarkup:
    keyboard = get_inline_keyboard(
        data = {
            MediaTagList(tag=tag, number=-1).pack(): t('admin.content.buttons.prev'),
            MediaTagList(tag=tag, number=+1).pack(): t('admin.content.buttons.next'),

            MediaTagList(tag=tag, number=number, action='add').pack(): t('admin.content.buttons.add'),
            MediaTagList(tag=tag, number=number, action='delete').pack(): t('admin.content.buttons.delete'),
            MediaTagList(tag=tag, number=number, action='edit').pack(): t('admin.content.buttons.edit'),

            'tag_list': t('admin.content.buttons.back'),
        },
        resize_keyboard=True,
        adjust=[2, 3, 1]
    )
    return keyboard


async def get_tag_keyboard() -> InlineKeyboardMarkup:
    buttons = await get_media_dirs()

    data = {'main': t('admin.content.buttons.back'),}
    for b in buttons:
        data.update({MediaTagList(tag=b).pack(): b})

    adjust = [1] + [2 for _ in range(len(buttons))]
    keyboard = get_inline_keyboard(
        data=data,
        resize_keyboard=True,
        one_time_keyboard=True,
        adjust=adjust,
    )
    return keyboard

