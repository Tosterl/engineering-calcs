"""Async SQLite database connection using SQLAlchemy 2.0."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.data.models import Base


# Database file path
DATABASE_DIR = Path(__file__).parent.parent.parent / "data"
DATABASE_PATH = DATABASE_DIR / "engineering_calcs.db"
DATABASE_URL = f"sqlite+aiosqlite:///{DATABASE_PATH}"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize the database by creating all tables.

    This function should be called at application startup to ensure
    all tables exist in the database.
    """
    # Ensure the data directory exists
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close the database connection.

    This function should be called at application shutdown to properly
    dispose of the engine and release resources.
    """
    await engine.dispose()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.

    This is an async context manager that provides a session for database
    operations. The session is automatically committed on success or
    rolled back on error.

    Usage:
        async with get_session() as session:
            result = await session.execute(select(Formula))
            formulas = result.scalars().all()

    Yields:
        AsyncSession: An async SQLAlchemy session.
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
