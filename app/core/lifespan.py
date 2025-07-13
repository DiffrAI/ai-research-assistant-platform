"""Application lifecycle management."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from loguru import logger

from .database import close_db, init_db
from .middlewares.rate_limiter import init_rate_limiter


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events."""
    logger.info("🚀 Application starting up...")
    await init_rate_limiter()
    await init_db()
    yield
    logger.info("👋 Application shutting down...")
    await close_db()
