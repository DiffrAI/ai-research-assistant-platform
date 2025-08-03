"""Tests for the /chat streaming endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.core.server import app
from asgi_lifespan import LifespanManager
import asyncio

@pytest.mark.asyncio
async def test_stream_chat():
    """Test the /chat streaming endpoint."""
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Register a user (ignore if already exists)
            reg_resp = await client.post(
                "/api/v1/auth/register",
                json={
                    "email": "testuser@example.com",
                    "full_name": "Test User",
                    "password": "testpass123"
                },
            )
            assert reg_resp.status_code in (201, 400)
            await asyncio.sleep(0.1)
            # Login to get token
            login_resp = await client.post(
                "/api/v1/auth/login",
                json={"email": "testuser@example.com", "password": "testpass123"},
            )
            token = login_resp.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get("/api/v1/chat/stream?sleep=0.01&number=3", headers=headers)
            assert response.status_code == 200
