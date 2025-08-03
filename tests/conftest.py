import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base, get_db
from app.core.server import app
import os
from fastapi_limiter import FastAPILimiter
import fakeredis.aioredis
from app.apis.v1.auth.controller import get_current_user
from app.models.user import User, SubscriptionPlan, UserRole
from datetime import datetime

# Use an in-memory SQLite database with shared cache for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:?cache=shared"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def fastapi_limiter_init():
    fake_redis = fakeredis.aioredis.FakeRedis()
    await FastAPILimiter.init(redis=fake_redis)
    yield
    await FastAPILimiter.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(test_engine):
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture(scope="function", autouse=True)
async def setup_app_db(db_session):
    async def override_get_db():
        async with db_session as session:
            yield session
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_auth():
    def override_get_current_user():
        now = datetime.utcnow()
        return User(
            id=1,
            email="testuser@example.com",
            full_name="Test User",
            is_active=True,
            role=UserRole.USER,
            subscription_plan=SubscriptionPlan.FREE,
            searches_used_this_month=0,
            searches_limit=10,
            subscription_expires_at=None,
            created_at=now,
            updated_at=now,
        )
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear() 