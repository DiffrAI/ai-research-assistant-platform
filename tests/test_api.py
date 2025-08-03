"""Essential API tests for core functionality."""

import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager

from app.core.server import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_payment_plans():
    """Test payment plans endpoint."""
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/payment/plans")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "plans" in data["data"]


@pytest.mark.asyncio
async def test_auth_registration():
    """Test user registration."""
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "newuser@example.com",
                    "full_name": "New User",
                    "password": "testpass123"
                },
            )
            assert response.status_code in (200, 201)