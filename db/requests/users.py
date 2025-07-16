import logging

from sqlalchemy import insert, update, select

from db.models import User
from db.setup_session import get_async_session

async def get_user(tg_id: int) -> User:
    async with get_async_session() as session:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await session.scalars(stmt)
        return result.first()
