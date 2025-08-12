from keyboards.keyboard_builder import get_inline_keyboard
from locales.loader import t

corp_events_list_keyboard = get_inline_keyboard(
    data={
        '-1': t('corp_events.buttons.prev'),
        '+1': t('corp_events.buttons.next'),
    },
    resize_keyboard=True,
    adjust=[2]
)