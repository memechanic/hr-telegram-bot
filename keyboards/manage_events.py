from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup

from keyboards.keyboard_builder import get_inline_keyboard, get_reply_keyboard
from locales.loader import t
from service.callback_data_factory import EventsManagerButton
from db.models import EventTypeEnum

remove_keyboard = ReplyKeyboardRemove()

events_main_keyboard = get_inline_keyboard(
    data={
        EventsManagerButton(action='add').pack(): t('admin.events.buttons.add'),
        EventsManagerButton(action='list').pack(): t('admin.events.buttons.list'),
    },
    resize_keyboard = True,
    adjust=[1]
)
def get_events_list_keyboard(event_id: int) -> InlineKeyboardMarkup:

    keyboard = get_inline_keyboard(
        data={
            EventsManagerButton(action='turn', turn_val=-1).pack(): t('admin.events.buttons.prev'),
            EventsManagerButton(action='turn', turn_val=+1).pack(): t('admin.events.buttons.next'),
            EventsManagerButton(action='back').pack(): t('admin.events.buttons.back'),
            EventsManagerButton(action='delete', event_id=event_id).pack(): t('admin.events.buttons.delete'),
        },
        resize_keyboard = True,
        adjust=[2,1]
    )
    return keyboard

events_back_keyboard = get_inline_keyboard(
    data={
        EventsManagerButton(action='back').pack(): t('admin.events.buttons.back')
    },
    resize_keyboard = True,
)

event_type_keyboard = get_reply_keyboard(
    buttons=[
        t('admin.events.buttons.cancel'),
        t(f"admin.events.buttons.{EventTypeEnum.event.value}"),
        t(f"admin.events.buttons.{EventTypeEnum.excursion.value}"),
    ],
    one_time_keyboard=True,
    resize_keyboard = True,
    adjust=[1]
)

events_skip_keyboard = get_reply_keyboard(
    buttons=[
        t(f"admin.events.buttons.skip")
    ],
    resize_keyboard = True, one_time_keyboard = True,
)

events_accept_keyboard = get_inline_keyboard(
    data={
        EventsManagerButton(action='accept').pack(): t('admin.events.buttons.add'),
        EventsManagerButton(action='cancel').pack(): t('admin.events.buttons.cancel'),
    }
)
def get_event_delete_keyboard(event_id: int) -> InlineKeyboardMarkup:
    keyboard = get_inline_keyboard(
        data={
            EventsManagerButton(action='delete', event_id=event_id).pack(): t('admin.events.buttons.delete'),
            EventsManagerButton(action='cancel').pack(): t('admin.events.buttons.cancel'),
        },
        resize_keyboard = True,
        adjust=[1]
    )
    return keyboard