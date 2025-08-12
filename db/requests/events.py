import logging
from typing import List

from sqlalchemy import select, delete, update

from db.models import Event, EventTypeEnum
from db.setup_session import get_async_session

logger = logging.getLogger(__name__)

async def add_event(event: Event) -> bool:
    logger.debug(f"add_event")

    async with get_async_session() as session:
        session.add(event)
        try:
            await session.flush()
        except Exception as e:
            logger.error(f"add_event: {e}")
            return False
        else:
            return True

async def get_events(where_statement) -> List[Event]:
    logger.debug(f"get_event")
    async with get_async_session() as session:
        stmt = select(Event).where(where_statement)
        result = await session.scalars(stmt)
        events = [e for e in result]
        return events

async def delete_event(where_statement):
    logger.debug(f"delete_event")
    async with get_async_session() as session:
        stmt = delete(Event).where(where_statement).returning(Event.id)
        result = await session.scalars(stmt)
        event = result.first()
        return event or None