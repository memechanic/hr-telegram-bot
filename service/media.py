import logging
from datetime import datetime
from os import remove as rm_file
from pathlib import Path
from typing import List, Dict

from aiogram import Bot
from aiogram.types import PhotoSize, Video, Document, FSInputFile

from db.models import SourceTypeEnum, Media
from db.requests.media import add_media, get_media, delete_media, update_media

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

async def delete_media_by_id(media_id: int) -> bool:
    logger.debug("delete_media_by_id")
    w = Media.id == media_id
    path = await delete_media(w)
    if path: rm_file(path)
    return bool(path)

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

    data = {
        'file_id': doc.file_id,
        'type': doc_type,
        'tag': tag,
        'source_type': SourceTypeEnum.telegram
    }
    media = Media(**data)
    media_id = await add_media(media)

    new_filename = f"{str(media_id)}_{filename}"
    path = _MEDIA_PATH / tag / new_filename
    update_data = {
        'filename': new_filename,
        'path': str(path),
    }
    result = await update_media(media_id, **update_data)
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
    w = Media.tag == tag
    result = await get_media(w)
    return result

async def get_media_input_files(tag: str) -> Dict[str, List[FSInputFile]] | None:
    logger.debug("send_media")

    media = await get_media_by_tag(tag)
    photos_raw = list(filter(lambda p: p.type.startswith('image'), media))
    videos_raw = list(filter(lambda p: p.type.startswith('video'), media))
    applications_raw = list(filter(lambda p: p.type.startswith('application'), media))

    files = {
        'photos': [],
        'videos': [],
        'applications': [],
    }

    if len(photos_raw) == 0 and len(videos_raw) == 0 and len(applications_raw) == 0:
        return files

    if len(photos_raw):
        for photo in photos_raw:
            files['photos'].append(FSInputFile(photo.path))

    if len(videos_raw):
        for video in videos_raw:
            files['videos'].append(FSInputFile(video.path))

    if len(applications_raw):
        for app in applications_raw:
            files['applications'].append(FSInputFile(app.path))

    return files