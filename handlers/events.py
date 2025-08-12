import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from locales.loader import t
from service.events import get_corp_events
from keyboards.events import corp_events_list_keyboard

router = Router()

logger = logging.getLogger(__name__)

class CorpEvents(StatesGroup):
    corp_event_list = State()

@router.message(Command('events'))
async def corp_event_list(message: Message, state: FSMContext):
    logger.debug(f"corp_event_list")

    await state.set_state(CorpEvents.corp_event_list)

    corp_events = await get_corp_events()
    await state.update_data(corp_events=corp_events)
    page = 0
    await state.update_data(page=page)

    event_info = await get_corp_event_info(state)
    await message.answer(text=event_info, reply_markup=corp_events_list_keyboard)

@router.callback_query(CorpEvents.corp_event_list)
async def corp_events_turn(callback: CallbackQuery, state: FSMContext):
    logger.debug(f"corp_events_turn")

    turn = int(callback.data)
    page = await state.get_value('page')
    corp_events = await state.get_value('corp_events')

    page += turn
    if page < 0 or page > len(corp_events) - 1:
        page = 0
    await state.update_data(page=page)

    event_info = await get_corp_event_info(state)
    await callback.message.edit_text(event_info)
    await callback.message.edit_reply_markup(reply_markup=corp_events_list_keyboard)
    await callback.answer()

async def get_corp_event_info(state: FSMContext) -> str:
    logger.debug(f"get_event_info")

    page = await state.get_value('page')
    corp_events = await state.get_value('corp_events')

    event_dict = corp_events[page]
    event_info = t('corp_events.title', title=event_dict['title'])

    if event_dict['start_time'] is not None:
        event_info += t('corp_events.start_time', start_time=event_dict['start_time'].strftime("%d.%m.%Y %H:%M"))

    if event_dict['end_time'] is not None:
        event_info += t('corp_events.end_time', end_time=event_dict['end_time'].strftime("%d.%m.%Y %H:%M"))

    if event_dict['address'] is not None:
        event_info += t('corp_events.address', address=event_dict['address'])

    if event_dict['description'] is not None:
        event_info += t('corp_events.description', description=event_dict['description'])

    return event_info