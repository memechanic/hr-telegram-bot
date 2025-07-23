import logging
from typing import List

from sqlalchemy import select, delete

from db.models import Media
from db.setup_session import get_async_session

logger = logging.getLogger(__name__)

async def add_media(media: Media) -> bool:
    logger.debug(f"add_media: {media}")

    async with get_async_session() as session:
        session.add(media)
        try:
            await session.flush()
        except Exception as e:
            logger.error(f"add_media_error: {e}")
            return False
        else:
            return True

async def get_media(where_clause) -> List[Media]:
    logger.debug("get_media")

    async with get_async_session() as session:
        stmt = select(Media).where(where_clause)
        result = await session.scalars(stmt)
        media = [m for m in result]
        return media

async def delete_media(where_clause) -> str | None:
    logger.debug("delete_media")
    async with get_async_session() as session:
        stmt = delete(Media).where(where_clause).returning(Media.path)
        result = await session.scalars(stmt)
        path = result.first()
        return path or None