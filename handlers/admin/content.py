import logging
from typing import List

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile, PhotoSize

from keyboards.content import get_tag_keyboard, main_content_keyboard, back_content_keyboard, get_media_list_keyboard, \
    get_delete_keyboard, get_media_empty_keyboard
from locales.loader import t
from service.callback_data_factory import MediaTagList
from service.media import add_media_document, get_media_by_tag, get_media_dict, delete_media_by_id, is_module_has_dirs, \
    add_module_dir

logger = logging.getLogger(__name__)

router = Router()

class ContentState(StatesGroup):
    main = State()
    info = State()
    tag_list = State()
    add_chapter = State()
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

@router.callback_query(F.data == "tag_list")
async def content_tag_list(callback: CallbackQuery, state: FSMContext):
    logger.debug("content_tag_list")

    await show_tag_list(callback, state)

async def show_tag_list(callback: CallbackQuery, state: FSMContext, module: str = None):
    logger.debug("show_tag_list")

    await state.set_state(ContentState.tag_list)

    media_msg = await state.get_value('show_media_message')
    if media_msg is not None:
        await media_msg.delete()
        await state.update_data(show_media_message=None)

    keyboard = await get_tag_keyboard(module)
    await callback.message.edit_text(text=t('admin.content.tag_list'), )
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()

@router.callback_query(ContentState.tag_list, MediaTagList.filter((F.action == 'add_chapter')))
async def add_chapter(callback: CallbackQuery, callback_data: MediaTagList, state: FSMContext):
    logger.debug("add_chapter")

    tag = callback_data.tag
    await state.set_state(ContentState.add_chapter)
    await state.update_data(chapter_module=tag)
    add_chapter_msg = await callback.message.answer(text=t('admin.content.add_chapter', module=tag))
    await state.update_data(add_chapter_msg=add_chapter_msg)
    await callback.answer()

@router.message(ContentState.add_chapter, F.text)
async def add_chapter_result(message: Message, state: FSMContext):
    logger.debug("add_chapter_result")

    text = message.text
    if text == '.':
        await message.delete()
        add_chapter_msg = await state.get_value('add_chapter_msg')
        await add_chapter_msg.delete()
        await state.set_state(ContentState.tag_list)
        return

    tag = await state.get_value('chapter_module')
    new_chapter = tag + '.' + text[0].upper() + text[1:].lower()

    result = await add_module_dir(new_chapter)
    if result:
        await message.answer(text=t('admin.content.add_chapter_success'))
        await state.clear()
    else:
        await message.answer(text=t('admin.content.error'))

@router.callback_query(ContentState.tag_list, MediaTagList.filter(F.action == None))
async def content_media_list(callback: CallbackQuery, callback_data: MediaTagList, state: FSMContext):
    logger.debug("content_tag")

    tag = callback_data.tag
    if await is_module_has_dirs(tag):
        await show_tag_list(callback, state, tag)
        return

    await show_media_info(callback, callback_data, state)

async def show_media_info(callback: CallbackQuery, callback_data: MediaTagList, state: FSMContext):
    tag = callback_data.tag
    media = await get_media_by_tag(tag)

    if len(media) == 0:
        keyboard = get_media_empty_keyboard(tag)
        await callback.message.edit_text(
            text=t('admin.content.empty', tag=tag),
            reply_markup=keyboard,
        )
        await callback.answer()
        return

    old_number = await state.get_value('number')
    if old_number is None: old_number = 0
    new_number = max(0, min(old_number + callback_data.number, len(media) - 1))

    info = await get_media_dict(media[new_number])
    await state.update_data(media_id=info['id'])
    keyboard = get_media_list_keyboard(tag, info['id'])

    try:
        await callback.message.edit_text(
            text=t('admin.content.media_info', **info, number=new_number + 1),
            reply_markup=keyboard,
        )

        media_type = info['type'].split('/')[0]
        input_media = FSInputFile(info['path'])

        message: Message = await state.get_value('show_media_message')

        if message is not None:
            await message.delete()
        if media_type == 'image':
            message = await callback.message.answer_photo(photo=input_media)
        elif media_type == 'video':
            message = await callback.message.answer_video(video=input_media)
        elif media_type == 'application':
            message = await callback.message.answer_document(document=input_media)
        else:
            message = await callback.message.answer(text=t('admin.content.show_error'))

        await state.update_data(show_media_message=message)
        await callback.answer()

    except TelegramBadRequest as e:
        if 'is not modified' in e.message:
            pass
        else:
            logger.error(e)
    finally:
        await state.update_data(number=new_number)
        await callback.answer()

@router.callback_query(MediaTagList.filter(F.action == "add"))
async def content_add(callback: CallbackQuery, callback_data: MediaTagList, state: FSMContext):
    logger.debug("content_add")

    tag = callback_data.tag
    await state.set_state(ContentState.add)
    await state.update_data(tag=tag)
    await callback.message.answer(text=t('admin.content.add', tag=tag))

    await callback.answer()

@router.message(ContentState.add, F.content_type.in_({'photo', 'video', 'document'}))
async def content_add_result(message: Message, bot: Bot, state: FSMContext):
    logger.debug("content_add_result")

    tag = await state.get_value('tag')

    document = message.document or message.photo or message.video

    if document is List[PhotoSize]:
        document = document[-1]

    result = await add_media_document(document, tag, bot)

    if result:
        await message.answer(text=t('admin.content.add_success'))
        await state.clear()
    else:
        await message.answer(text=t('admin.content.error'))

@router.message(ContentState.add, F.text)
async def content_add_cancel(message: Message, state: FSMContext):
    logger.debug("content_add_cancel")

    await state.set_state(ContentState.main)
    await message.answer(
        text=t('admin.content.main'),
        reply_markup=main_content_keyboard,
    )

@router.callback_query(ContentState.tag_list, MediaTagList.filter(F.action == "delete"))
async def content_delete(callback: CallbackQuery, callback_data: MediaTagList, state: FSMContext):
    logger.debug("content_delete")

    tag = callback_data.tag
    media_id = await state.get_value('media_id')
    number = await state.get_value('number')
    keyboard = get_delete_keyboard(tag, number, media_id)

    old_text = callback.message.text
    new_text = '\n\n'.join([old_text, t('admin.content.delete')])

    await callback.message.edit_text(text=new_text)
    await callback.message.edit_reply_markup(reply_markup=keyboard)

    await state.set_state(ContentState.delete)
    await callback.answer()

@router.callback_query(ContentState.delete, MediaTagList.filter(F.action == "delete"))
async def content_delete_result(callback: CallbackQuery, callback_data: MediaTagList, state: FSMContext):
    logger.debug("content_delete_result")

    media_id = callback_data.id
    result = await delete_media_by_id(media_id)
    if result:
        await state.update_data(number=0)
        await state.set_state(ContentState.tag_list)
        await show_media_info(callback, callback_data, state)

        await callback.answer(text=t('admin.content.delete_success'), show_alert=True)
    else:
        await callback.answer(text=t('admin.content.error'), show_alert=True)

@router.callback_query(ContentState.delete, MediaTagList.filter(F.action == None))
async def content_delete_cancel(callback: CallbackQuery, callback_data: MediaTagList, state: FSMContext):
    logger.debug("content_delete_cancel")

    tag = callback_data.tag
    number = callback_data.number
    media = await get_media_by_tag(tag)

    info = await get_media_dict(media[number])
    keyboard = get_media_list_keyboard(tag, info['id'])

    await callback.message.edit_text(
        text=t('admin.content.media_info', **info, number=number + 1),
        reply_markup=keyboard,
    )
    await state.set_state(ContentState.tag_list)
    await callback.answer()