"""Application lifecycle management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from loguru import logger

from .config import settings
from .database import close_db, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events."""
    logger.info("🚀 Application starting up...")
    # Initialize rate limiter if available
    try:
        logger.info("Rate limiter disabled for testing")
        # import redis.asyncio as redis
        # from fastapi_limiter import FastAPILimiter

        # redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        # redis_client = redis.from_url(
        #     redis_url, encoding="utf-8", decode_responses=True
        # )
        # await FastAPILimiter.init(redis_client)
        # logger.info("Rate limiter initialized")
    except Exception as e:
        logger.warning(f"Rate limiter not initialized: {e}")

    await init_db()
    yield
    logger.info("👋 Application shutting down...")

    # Close rate limiter if available
    try:
        from fastapi_limiter import FastAPILimiter

        await FastAPILimiter.close()
    except Exception:
        pass

    await close_db()
