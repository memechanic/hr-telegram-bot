import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from locales.loader import t
from keyboards.manage_events import events_main_keyboard, get_events_list_keyboard, events_back_keyboard, event_type_keyboard, \
    remove_keyboard, events_skip_keyboard, events_accept_keyboard, get_event_delete_keyboard
from service.events import get_corp_events, EVENTS_TYPE_LABELS, validate_datetime, add_corp_event, EVENTS_TYPES, \
    delete_event_by_id
from service.callback_data_factory import EventsManagerButton

router = Router()

logger = logging.getLogger(__name__)

class EventsState(StatesGroup):
    main = State()

    events_list = State()

    add = State()
    type = State()
    title = State()
    description = State()
    address = State()
    start_time = State()
    end_time = State()
    confirm = State()

    delete = State()

@router.message(Command('manage_events'))
async def manage_events(message: Message, state: FSMContext):
    logger.debug("manage_events")

    await state.set_state(EventsState.main)
    await message.answer(text=t('admin.events.main'), reply_markup=events_main_keyboard)

async def main_events(message: Message, state: FSMContext):
    logger.debug("manage_events")

    await state.set_state(EventsState.main)
    await message.answer(text=t('admin.events.main'), reply_markup=events_main_keyboard)


@router.callback_query(EventsManagerButton.filter(F.action == 'back'))
async def back_manage_events(callback: CallbackQuery, state: FSMContext):
    logger.debug("back_manage_events")

    await state.set_state(EventsState.main)
    await callback.message.edit_text(text=t('admin.events.main'))
    await callback.message.edit_reply_markup(reply_markup=events_main_keyboard)
    await callback.answer()

@router.callback_query(EventsManagerButton.filter(F.action == 'list'))
async def events_list(callback: CallbackQuery, state: FSMContext):
    logger.debug("events_list")

    await state.set_state(EventsState.events_list)
    await show_event_info(callback, state)
    await callback.answer()

@router.callback_query(EventsManagerButton.filter(F.action == 'turn'))
async def turn_events_list(callback: CallbackQuery, callback_data: EventsManagerButton, state: FSMContext):
    logger.debug("turn_events_list")

    page = await state.get_value('page')
    if page is None: page = 0

    turn_val = callback_data.turn_val
    page += turn_val
    await state.update_data(page=page)
    await show_event_info(callback, state)
    await callback.answer()

async def show_event_info(callback: CallbackQuery, state: FSMContext):
    logger.debug("show_event_info")

    events = await get_corp_events()
    page = await state.get_value('page')
    if page is None or page > len(events)-1 or page < 0:
        page = 0
        await state.update_data(page=page)


    if len(events) != 0:
        event_id = events[page]['id']
        keyboard = get_events_list_keyboard(event_id)
        event_info = events[page]
        event_type = EVENTS_TYPES[event_info['event_type'].value]
        event_info.update(event_type=event_type)
        await callback.message.edit_text(text=t('admin.events.event_info', **event_info))
        await callback.message.edit_reply_markup(reply_markup=keyboard)

    else:
        await callback.message.edit_text(text=t('admin.events.empty_events'))
        await callback.message.edit_reply_markup(reply_markup=events_back_keyboard)

    await callback.answer()

@router.callback_query(EventsManagerButton.filter(F.action == 'delete'), EventsState.events_list)
async def delete_event(callback: CallbackQuery, callback_data: EventsManagerButton, state: FSMContext):
    logger.debug("delete_event")

    event_id = callback_data.event_id
    text = callback.message.text + "\n\n" + t('admin.events.delete')

    await callback.message.edit_text(text=text)
    keyboard = get_event_delete_keyboard(event_id)
    await callback.message.edit_reply_markup(reply_markup=keyboard)

    await state.set_state(EventsState.delete)
    await callback.answer()

@router.callback_query(EventsManagerButton.filter(F.action == 'cancel'), EventsState.delete)
async def back_manage_events(callback: CallbackQuery, state: FSMContext):
    logger.debug("back_manage_events")

    await state.set_state(EventsState.events_list)
    await state.update_data(page=None)
    await show_event_info(callback, state)
    await callback.answer()

@router.callback_query(EventsManagerButton.filter(F.action == 'delete'), EventsState.delete)
async def delete_event_result(callback: CallbackQuery, callback_data: EventsManagerButton, state: FSMContext):
    logger.debug("delete_event_result")

    event_id = callback_data.event_id
    result = await delete_event_by_id(event_id)
    if not result:
        await callback.message.answer(text=t('admin.events.error'))
    await state.update_data(page=None)
    await show_event_info(callback, state)
    await callback.answer()



@router.callback_query(EventsManagerButton.filter(F.action == 'add'))
async def add_event(callback: CallbackQuery, state: FSMContext):
    logger.debug("add_event")

    await state.set_state(EventsState.add)
    await callback.message.answer(text=t('admin.events.add_event'), reply_markup=event_type_keyboard)
    await callback.answer()

@router.message(EventsState.add)
async def get_event_type(message: Message, state: FSMContext):
    logger.debug("get_event_type")

    await state.set_state(EventsState.type)
    event_type = message.text
    if event_type in EVENTS_TYPE_LABELS.keys():
        await state.update_data(event_type=event_type)
        await message.answer(text=t('admin.events.get_title'), reply_markup=remove_keyboard)
        await state.set_state(EventsState.title)
    elif event_type == t('admin.events.buttons.cancel'):
        await main_events(message, state)
    else:
        await message.answer(text=t('admin.events.no_type'))
        await state.set_state(EventsState.add)

@router.message(EventsState.title)
async def get_event_title(message: Message, state: FSMContext):
    logger.debug("get_event_title")

    event_title = message.text.strip()
    await state.update_data(title=event_title)
    await message.answer(text=t('admin.events.get_description'), reply_markup=events_skip_keyboard)
    await state.set_state(EventsState.description)

@router.message(EventsState.description)
async def get_event_description(message: Message, state: FSMContext):
    logger.debug("get_event_description")

    text = message.text.strip()
    if text == t('admin.events.buttons.skip'):
        text = None
    await state.update_data(description=text)

    await state.set_state(EventsState.address)
    await message.answer(text=t('admin.events.get_address'), reply_markup=events_skip_keyboard)

@router.message(EventsState.address)
async def get_event_address(message: Message, state: FSMContext):
    logger.debug("get_event_address")

    text = message.text.strip()
    if text == t('admin.events.buttons.skip'):
        text = None
    await state.update_data(address=text)

    await state.set_state(EventsState.start_time)
    await message.answer(text=t('admin.events.get_start_time'), reply_markup=events_skip_keyboard)

@router.message(EventsState.start_time)
async def get_event_start_time(message: Message, state: FSMContext):
    logger.debug("get_event_start_time")

    text = message.text.strip()
    if text != t('admin.events.buttons.skip'):
        dt = await validate_datetime(text)
        if dt is not None:
            await state.update_data(start_time=dt)
        else:
            await message.answer(text=t('admin.events.incorrect_format'))
            return
    else:
        await state.update_data(start_time=None)

    await state.set_state(EventsState.end_time)
    await message.answer(text=t('admin.events.get_end_time'), reply_markup=events_skip_keyboard)

@router.message(EventsState.end_time)
async def get_event_end_time(message: Message, state: FSMContext):
    logger.debug("get_event_end_time")

    text = message.text.strip()
    if text != t('admin.events.buttons.skip'):
        dt = await validate_datetime(text)
        if dt is not None:
            await state.update_data(end_time=dt)
        else:
            await message.answer(text=t('admin.events.incorrect_format'))
            return
    else:
        await state.update_data(end_time=None)

    event_data = await state.get_data()
    await state.set_state(EventsState.confirm)
    await message.answer(text=t('admin.events.event_info', **event_data), reply_markup=events_accept_keyboard)

@router.callback_query(EventsManagerButton.filter(F.action == 'cancel'), EventsState.confirm)
async def cancel_add_event(callback: CallbackQuery, state: FSMContext):
    logger.debug("cancel_add_event")

    await callback.message.answer(text=t('admin.events.cancel'), reply_markup=remove_keyboard)
    await callback.answer()
    await main_events(callback.message, state)
    return

@router.callback_query(EventsManagerButton.filter(F.action == 'accept'), EventsState.confirm)
async def accept_add_event(callback: CallbackQuery, state: FSMContext):
    logger.debug("accept_add_event")

    data = await state.get_data()
    event_type = EVENTS_TYPE_LABELS[data['event_type']]
    data.update(event_type=event_type)
    result = await add_corp_event(data)
    if result:
        await callback.answer(text=t('admin.events.add_success'))
        await show_event_info(callback, state)
        return
    else:
        await callback.message.answer(text=t('admin.events.add_fail'))

    await state.clear()
    await callback.answer()
