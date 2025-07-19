import logging

from asyncpg import UniqueViolationError
from sqlalchemy import insert, update, select
from sqlalchemy.exc import IntegrityError

from db.models import Pin
from db.setup_session import get_async_session

logger = logging.getLogger(__name__)

async def add_pincode(pincode: int) -> bool:
    logger.debug("add_pincode")
    async with get_async_session() as session:
        stmt = insert(Pin).values(code=pincode)
        try:
            await session.execute(stmt)
            return True
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolationError):
                logger.error(f"Pin {pincode} already exists")
                return False
            logger.error(e)
            return False

async def get_pincode(pincode: int) -> Pin:
    logger.debug("get_pincode")
    async with get_async_session() as session:
        stmt = select(Pin).where(Pin.code == pincode)
        result = await session.scalars(stmt)

        return result.first()

async def update_used_pincode(pincode: int) -> bool:
    logger.debug("update_used_pincode")
    async with get_async_session() as session:
        stmt = update(Pin).values(is_used=True).where(Pin.code == pincode)
        try:
            await session.execute(stmt)
            return True
        except Exception as e:
            logger.error(e)
            return False