import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config_reader import config

logger = logging.getLogger(__name__)

async_engine = create_async_engine(
    config.database_url.get_secret_value(),
    echo=False
)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)

@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    logger.debug('get_async_session')
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(e)