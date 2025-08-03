"""Test research endpoint functionality."""

import pytest
from fastapi.testclient import TestClient
from app.core.server import app
from app.apis.v1.auth.controller import get_current_user


# Use context manager to ensure lifespan is triggered (for app.state setup)
def test_research_unauthenticated():
    """Test that unauthenticated research requests are rejected."""
    # Remove the mock_auth override for this test
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/research", json={"query": "What is the latest news about AI?"}
        )
        # Should get 403 forbidden because authentication is required
        assert response.status_code == 403
        data = response.json()
        assert data["status"] == "success" or data["status"] == "error"
        # Check for 'not authenticated' message
        assert "not authenticated" in data["message"].lower()


# To test authenticated requests, you would need to:
# 1. Register a test user
# 2. Login to get a token
# 3. Use the token in the Authorization header
# Example:
# def test_research_authenticated():
#     """Test that authenticated research requests work."""
#     with TestClient(app) as client:
#         # Register
#         client.post("/api/v1/auth/register", json={
#             "email": "testuser@example.com",
#             "full_name": "Test User",
#             "password": "testpass123"
#         })
#         # Login
#         login_resp = client.post("/api/v1/auth/login", json={
#             "email": "testuser@example.com",
#             "password": "testpass123"
#         })
#         token = login_resp.json()["data"]["access_token"]
#         # Research
#         headers = {"Authorization": f"Bearer {token}"}
#         response = client.post("/api/v1/research", json={"query": "What is the latest news about AI?"}, headers=headers)
#         assert response.status_code == 200
#         data = response.json()
#         assert data["status"] == "success"
#         assert "data" in data
#         # Optionally check for expected keys in data["data"]
