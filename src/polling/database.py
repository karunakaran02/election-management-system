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


engine = create_async_engine(
    core.database_url,
    pool_pre_ping=True,
)

session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with session() as db:
        yield db
