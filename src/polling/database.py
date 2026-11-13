from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from polling.core.config import core


class Base(DeclarativeBase):
    pass


connect_args = {}
if "asyncpg" in core.database_url:
    # Required for connection poolers (e.g. Supabase Supavisor / PgBouncer)
    connect_args["statement_cache_size"] = 0

engine = create_async_engine(
    core.database_url,
    pool_pre_ping=True,
    connect_args=connect_args,
)

session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session() as db:
        yield db
