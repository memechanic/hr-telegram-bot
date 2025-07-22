import logging

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from keyboards.content import get_tag_keyboard, main_content_keyboard, back_content_keyboard, get_media_list_keyboard
from locales.loader import t
from service.callback_data_factory import MediaTagList
from service.media import get_media_dirs, add_module_dir, add_media_document, get_media_by_tag, get_media_dict

router = Router()

logger = logging.getLogger(__name__)

class ContentState(StatesGroup):
    main = State()
    info = State()
    tag_list = State()
    media_list = State()
    add = State()
    delete = State()
    edit = State()

@router.message(Command('content'))
async def content(message: Message, state: FSMContext):
    logger.debug("content")

    await state.set_state(ContentState.main)
    await message.answer(
        text=t('admin.content.main'),
        reply_markup=main_content_keyboard,
    )

@router.callback_query(F.data == "main")
async def content_main(callback: CallbackQuery, state: FSMContext):
    logger.debug("content_main")

    await state.set_state(ContentState.main)
    await callback.message.edit_text(t('admin.content.main'))
    await callback.message.edit_reply_markup(reply_markup=main_content_keyboard)
    await callback.answer()

@router.callback_query(F.data == "info")
async def content_info(callback: CallbackQuery, state: FSMContext):
    logger.debug("content_info")

    await state.set_state(ContentState.info)
    await callback.message.edit_text(text=t('admin.content.info'))
    await callback.message.edit_reply_markup(reply_markup=back_content_keyboard)

    await callback.answer()

@router.callback_query(MediaTagList.filter(F.action == "add"))
async def content_add(callback: CallbackQuery, callback_data: MediaTagList, state: FSMContext):
    logger.debug("content_add")

    tag = callback_data.tag
    await state.set_state(ContentState.add)
    await state.update_data(tag=tag)
    await callback.message.answer(text=t('admin.content.add', tag=tag))

    await callback.answer()

@router.message(ContentState.add)
async def content_add_result(message: Message, bot: Bot, state: FSMContext):
    logger.debug("content_add_result")

    tag = await state.get_value('tag')
    if tag not in await get_media_dirs():
        await add_module_dir(tag)

    document = message.document or message.photo[-1] or message.video

    result = await add_media_document(document, tag, bot)

    if result:
        await message.answer(text=t('admin.content.add_success'))
        await state.clear()
    else:
        await message.answer(text=t('admin.content.error'))

@router.callback_query(F.data == "tag_list")
async def content_tag_list(callback: CallbackQuery, state: FSMContext):
    logger.debug("content_tag_list")

    await state.set_state(ContentState.tag_list)
    await state.update_data(number=0)
    keyboard = await get_tag_keyboard()
    await callback.message.edit_text(text=t('admin.content.tag_list'),)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()

@router.callback_query(ContentState.tag_list, MediaTagList.filter())
async def content_media_list(callback: CallbackQuery, callback_data: MediaTagList, state: FSMContext):
    logger.debug("content_tag")

    tag = callback_data.tag
    media = await get_media_by_tag(tag)

    old_number = await state.get_value('number')
    new_number = max(0, min(old_number + callback_data.number, len(media)-1))

    info = await get_media_dict(media[new_number])
    keyboard = get_media_list_keyboard(tag)

    try:
        await callback.message.edit_text(
            text=t('admin.content.media_info', **info, number=new_number+1),
            reply_markup=keyboard,
        )
    except TelegramBadRequest as e:
        if 'is not modified' in e.message:
            pass
        else:
            logger.error(e)
    else:
        await state.update_data(number=new_number)
        await callback.answer()

@router.callback_query(F.data == "delete")
async def content_delete(callback: CallbackQuery, state: FSMContext):
    logger.debug("content_delete")

    await state.set_state(ContentState.delete)
    await callback.answer()