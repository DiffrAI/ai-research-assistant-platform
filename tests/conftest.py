"""Test configuration."""

import asyncio

import fakeredis.aioredis
import pytest
from fastapi_limiter import FastAPILimiter
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.server import app

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:?cache=shared"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_environment():
    """Setup test environment with database and rate limiter."""
    # Setup test database
    engine = create_async_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Setup test session maker
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # Override database dependency
    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Setup fake redis for rate limiter
    fake_redis = fakeredis.aioredis.FakeRedis()
    await FastAPILimiter.init(redis=fake_redis)

    yield

    # Cleanup
    await FastAPILimiter.close()
    await engine.dispose()
    app.dependency_overrides.clear()
