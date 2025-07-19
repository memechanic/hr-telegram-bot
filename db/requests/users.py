import logging

from sqlalchemy import insert, update, select

from db.models import User
from db.setup_session import get_async_session

logger = logging.getLogger(__name__)

async def get_user(tg_id: int) -> User | None:
    logger.debug("get_user")
    async with get_async_session() as session:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await session.scalars(stmt)
        user = result.first()
        logger.debug(f"get_user result: {user}")
        return user


async def add_user(user: User) -> bool:
    logger.debug("add_user")
    async with get_async_session() as session:
        session.add(user)
        try:
            await session.flush()
        except Exception as e:
            logger.error(e)
            return False
        else:
            return True


async def update_user(tg_id: int, **kwargs) -> bool:
    logger.debug("update_user")
    async with get_async_session() as session:
        try:
            stmt = update(User).where(User.tg_id == tg_id).values(**kwargs)
            await session.execute(stmt)
        except Exception as e:
            logger.error(e)
            return False
        else:
            return True

async def get_admin() -> User:
    logger.debug("get_admin")
    async with get_async_session() as session:
        stmt = select(User).where(User.is_admin == True)
        result = await session.scalars(stmt)
        return result.first()