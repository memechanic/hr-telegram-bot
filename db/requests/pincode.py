import logging

from asyncpg import UniqueViolationError
from sqlalchemy import insert, update, select
from sqlalchemy.exc import IntegrityError

from db.models import Pin
from db.setup_session import get_async_session


async def add_pincode(pincode: int) -> bool:
    async with get_async_session() as session:
        stmt = insert(Pin).values(code=pincode)
        try:
            await session.execute(stmt)
            return True
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolationError):
                logging.error(f"Pin {pincode} already exists")
                return False
            logging.error(e)
            return False

async def get_pincode(pincode: int) -> Pin:
    async with get_async_session() as session:
        stmt = select(Pin).where(Pin.code == pincode)
        result = await session.scalars(stmt)

        return result.first()

async def update_used_pincode(pincode: int) -> bool:
    async with get_async_session() as session:
        stmt = update(Pin).values(is_used=True).where(Pin.code == pincode)
        try:
            await session.execute(stmt)
            return True
        except Exception as e:
            logging.error(e)
            return False