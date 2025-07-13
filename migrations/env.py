from __future__ import annotations

import asyncio
from logging.config import fileConfig
from pathlib import Path

from alembic import context

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from sqlalchemy import pool

from config_reader import config
from db.models import Base

alembic_cfg = context.config

if alembic_cfg.config_file_name:
    fileConfig(alembic_cfg.config_file_name)

target_metadata = Base.metadata

async_engine: AsyncEngine = create_async_engine(
    config.database_url.get_secret_value(),
    poolclass=pool.NullPool,
    future=True
)

def run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def async_run_migrations():
    async with async_engine.begin() as connection:
        await connection.run_sync(run_migrations)

if context.is_offline_mode():
    raise SystemExit("Оффлайн режим не поддерживается с AsyncEngine")

asyncio.run(async_run_migrations())