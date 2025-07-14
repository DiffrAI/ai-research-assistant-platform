"""Database configuration and session management."""

from typing import AsyncGenerator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app import settings

# Database URL
DATABASE_URL = settings.DATABASE_URL

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

# Create base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered
        from app.models.user_db import User  # noqa: F401

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Handle migration for existing databases
        await migrate_add_stripe_customer_id(conn)

        logger.info("Database tables created successfully")


async def migrate_add_stripe_customer_id(conn: AsyncConnection) -> None:
    """Add stripe_customer_id column if it doesn't exist."""
    try:
        # Check if stripe_customer_id column exists
        result = await conn.execute(text("PRAGMA table_info(users)"))
        columns = result.fetchall()
        column_names = [col[1] for col in columns]

        if "stripe_customer_id" not in column_names:
            await conn.execute(
                text("ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR")
            )
            logger.info("Added stripe_customer_id column to users table")
    except Exception as e:
        logger.warning(f"Migration warning (this is normal for new databases): {e}")


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    logger.info("Database connections closed")
