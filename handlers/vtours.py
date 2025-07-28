import logging
from typing import List

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.media_group import MediaGroupBuilder

from keyboards.vtours import get_vtours_keyboard, vtours_back_keyboard
from locales.loader import t
from service.media import get_media_input_files

router = Router()

logger = logging.getLogger(__name__)

class VToursState(StatesGroup):
    main = State()
    choice = State()

@router.message(Command('vtours'))
async def vtours(message: Message, state: FSMContext):
    logger.debug('vtours')

    await state.set_state(VToursState.main)
    keyboard = await get_vtours_keyboard()
    await message.answer(text=t('info.vtours.main'), reply_markup=keyboard)

@router.callback_query(VToursState.main, F.data.startswith('vtours'))
async def vtours_choice(callback: CallbackQuery, state: FSMContext):
    logger.debug('vtours_choice')

    tag = callback.data
    files = await get_media_input_files(tag)
    videos_msg: List[Message] = []

    if len(files['videos']) == 1:
        msg = await callback.message.answer_video(video=files['videos'][0], caption=t('info.vtours.choice', tag=tag.split('.')[1]))
        videos_msg.append(msg)

    elif len(files['videos']) > 1:
        album = MediaGroupBuilder(caption=t('info.vtours.choice', tag=tag.split('.')[1]))
        for file in files['videos']:
            album.add_video(file)
        album_msg = await callback.message.answer_media_group(media=album.build())
        videos_msg += album_msg

    else:
        msg = await callback.message.answer(text=t('info.vtours.file_empty'))
        videos_msg.append(msg)

    await state.set_state(VToursState.choice)
    await state.update_data(videos_msg=videos_msg)
    await callback.message.edit_reply_markup(reply_markup=vtours_back_keyboard)
    await callback.answer()

@router.callback_query(VToursState.choice, F.data == "main")
async def vtours_back(callback: CallbackQuery, state: FSMContext):
    logger.debug('vtours_back')

    videos_msg: List[Message] = await state.get_value('videos_msg')
    if videos_msg is not None:
        for msg in videos_msg:
            await msg.delete()

    await state.set_state(VToursState.main)
    keyboard = await get_vtours_keyboard()
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()