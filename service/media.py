import logging
from datetime import datetime
from pathlib import Path
from typing import List

from aiogram import Bot
from aiogram.types import PhotoSize, Video, Document, Message, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy import select

from db.models import SourceTypeEnum, Media
from db.requests.media import add_media, get_media
from locales.loader import t

logger = logging.getLogger(__name__)

_MEDIA_PATH = Path(__file__).resolve().parent.parent / 'media'

async def get_media_dirs() -> List[str]:
    logger.debug("get_media_dirs")

    raw = [str(d) for d in _MEDIA_PATH.iterdir()]
    res = [d[d.rfind('\\')+1:] for d in raw]
    return res

async def add_module_dir(name: str) -> bool:
    logger.debug("add_module_dir")

    new_module = _MEDIA_PATH / name
    try:new_module.mkdir()
    except Exception as e:
        logger.error(f"add_module_dir: {e}")
        return False
    else: return True


async def add_media_document(doc: PhotoSize | Video | Document, tag: str, bot: Bot) -> bool:
    logger.debug("add_media_data")

    filename: str
    doc_type: str

    if type(doc) is PhotoSize:
        filename = f"{tag}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.jpeg"
        doc_type = 'image/jpeg'
    else:
        filename = doc.file_name + doc.mime_type.split('/')[-1]
        doc_type = doc.mime_type

    path = _MEDIA_PATH / tag / filename
    data = {
        'file_id': doc.file_id,
        'filename': filename,
        'path': str(path),
        'type': doc_type,
        'tag': tag,
        'source_type': SourceTypeEnum.telegram
    }
    media = Media(**data)

    result = await add_media(media)
    if result:
        await bot.download(media.file_id, path)
    return result

async def get_media_dict(media: Media) -> dict:
    logger.debug("get_media_dict")

    data = {
        'id': media.id,
        'file_id': media.file_id,
        'filename': media.filename,
        'path': media.path,
        'type': media.type,
        'tag': media.tag,
        'source_type': media.source_type,
        'created_at': media.created_at,
    }
    return data

async def get_media_by_tag(tag: str) -> List[Media]:
    logger.debug("get_media_by_tag")
    stmt = select(Media).where(Media.tag == tag)
    result = await get_media(stmt=stmt)
    return result

async def send_media(message: Message, module: str, tag: str):
    logger.debug("send_media")

    media = await get_media_by_tag(tag)
    photos = list(filter(lambda p: p.type.startswith('image'), media))
    videos = list(filter(lambda p: p.type.startswith('video'), media))
    applications = list(filter(lambda p: p.type.startswith('application'), media))

    if len(photos) == 0 and len(videos) == 0 and len(applications) == 0:
        await message.answer(text=t(f'{module}.{tag}.text'))
        return

    if len(photos) == 1:
        await message.answer_photo(photo=FSInputFile(photos[0].path), caption=t(f'{module}.{tag}.photo'))

    elif len(photos) > 1:
        album_builder = MediaGroupBuilder(caption=t(f'{module}.{tag}.photo'))
        for photo in photos[:10]:
            album_builder.add_photo(FSInputFile(photo.path))
        await message.answer_media_group(media=album_builder.build())

    if len(videos) == 1:
        await message.answer_video(video=FSInputFile(videos[0].path), caption=t(f'{module}.{tag}.video'))

    elif len(videos) > 1:
        album_builder = MediaGroupBuilder(caption=t(f'{module}.{tag}.video'))
        for video in videos[:10]:
            album_builder.add_video(FSInputFile(video.path))
        await message.answer_media_group(media=album_builder.build())

    if len(applications) == 1:
        await message.answer_document(text=t(f'{module}.{tag}.document'), document=FSInputFile(applications[0].path))

    elif len(applications) > 1:
        album_builder = MediaGroupBuilder(caption=t(f'{module}.{tag}.document'))
        for application in applications[:10]:
            album_builder.add_document(FSInputFile(application.path))
        await message.answer_media_group(media=album_builder.build())