import logging
from typing import List

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

async def get_media(stmt) -> List[Media]:
    logger.debug("get_media")

    async with get_async_session() as session:
        stmt = stmt
        result = await session.scalars(stmt)
        media = [m for m in result]
        return media
