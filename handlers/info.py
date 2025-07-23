import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder
from locales.loader import t
from service.media import get_media_input_files

router = Router()

logger = logging.getLogger(__name__)

@router.message(Command('company'))
async def company(message: Message):
    logger.debug("company")

    files = await get_media_input_files('company')

    if files['photos'] or files['videos']:
        album = MediaGroupBuilder(caption=t('info.company.text'))
        media_files = files['photos'] + files['videos']
        for file in media_files[:10]:
            album.add_photo(file)
        await message.answer_media_group(media=album.build())

    if files['applications']:
        album = MediaGroupBuilder(caption=t('info.company.applications'))
        for file in files['applications']:
            album.add_document(file)
        await message.answer_media_group(media=album.build())

    if not (files['video'] and files['photos'] and files['applications']):
        await message.answer(text=t('info.company.text'))

@router.message(Command('cafeteria'))
async def cafeteria(message: Message):
    logger.debug("cafeteria")

    files = await get_media_input_files('cafeteria')
    working_hours = t('info.cafeteria.working_hours')

    if files['photos']:
        album = MediaGroupBuilder(caption=t('info.cafeteria.photo', working_hours=working_hours))
        for photo in files['photos']:
            album.add_photo(photo)
        await message.answer_media_group(media=album.build())
    elif files['applications']:
        album = MediaGroupBuilder(caption=t('info.cafeteria.photo', working_hours=working_hours))
        for application in files['applications']:
            album.add_document(application)
        await message.answer_media_group(media=album.build())
    else:
        menu = t('info.cafeteria.menu')
        await message.answer(text=t('info.cafeteria.text', working_hours=working_hours, menu=menu))

@router.message(Command('structure'))
async def structure(message: Message):
    logger.debug("structure")

    files = await get_media_input_files('structure')
    if files['applications']:
        album = MediaGroupBuilder(caption=t('info.structure.application'))
        for application in files['applications']:
            album.add_document(application)
        await message.answer_media_group(media=album.build())
    else:
        await message.answer(text=t('info.structure.text'))