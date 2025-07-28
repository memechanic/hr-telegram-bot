import logging
from typing import List

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from keyboards.docs import get_docs_keyboard, doc_back_keyboard
from locales.loader import t
from service.media import get_media_input_files

router = Router()

logger = logging.getLogger(__name__)

class DocState(StatesGroup):
    main = State()
    choice = State()

@router.message(Command('docs'))
async def docs(message: Message, state: FSMContext):
    logger.debug("docs")

    await state.set_state(DocState.main)
    keyboard = await get_docs_keyboard()
    await message.answer(text=t('info.docs.main'), reply_markup=keyboard)

@router.callback_query(DocState.main, F.data.startswith('docs'))
async def docs_choice(callback: CallbackQuery, state: FSMContext):
    logger.debug("docs_choice")

    tag = callback.data
    files = await get_media_input_files(tag)
    docs_msg: List[Message] = []

    if len(files['applications']) == 1:
        msg = await callback.message.answer_document(document=files['applications'][0], caption=t('info.docs.choice'))
        docs_msg.append(msg)

    elif len(files['applications']) > 1:
        msg_caption = await callback.message.answer_document(document=files['applications'][0], caption=t('info.docs.choice'))
        docs_msg.append(msg_caption)
        for file in files['applications'][1:10]:
            msg = await callback.message.answer_document(document=file)
            docs_msg.append(msg)

    else:
        msg = await callback.message.answer(text=t('info.docs.file_empty'))
        docs_msg.append(msg)

    await state.set_state(DocState.choice)
    await state.update_data(docs_msg=docs_msg)
    await callback.message.edit_reply_markup(reply_markup=doc_back_keyboard)
    await callback.answer()

@router.callback_query(DocState.choice, F.data == "main")
async def docs_back(callback: CallbackQuery, state: FSMContext):
    logger.debug("docs_back")

    doc_msg: List[Message] = await state.get_value('docs_msg')
    if doc_msg is not None:
        for msg in doc_msg:
            await msg.delete()

    await state.set_state(DocState.main)
    keyboard = await get_docs_keyboard()
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()