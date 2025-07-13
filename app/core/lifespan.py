"""Application lifecycle management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from .middlewares.rate_limiter import init_rate_limiter
from .database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    logger.info("🚀 Application starting up...")
    await init_rate_limiter()
    await init_db()
    yield
    logger.info("👋 Application shutting down...")
    await close_db()
