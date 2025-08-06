"""API contract tests to verify frontend-backend endpoint alignment."""

import pytest
from fastapi.testclient import TestClient

from app.core.server import app

client = TestClient(app)


class TestPaymentAPIContract:
    """Test payment API endpoints match frontend expectations."""

    def test_get_plans_endpoint(self):
        """Test GET /api/v1/payment/plans endpoint."""
        response = client.get("/api/v1/payment/plans")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "plans" in data["data"]
        assert isinstance(data["data"]["plans"], list)
        
        # Verify plan structure matches frontend expectations
        if data["data"]["plans"]:
            plan = data["data"]["plans"][0]
            required_fields = ["plan", "price", "searches_limit", "features"]
            for field in required_fields:
                assert field in plan

    def test_checkout_endpoint_requires_auth(self):
        """Test POST /api/v1/payment/checkout endpoint requires authentication."""
        payload = {
            "plan": "pro",
            "success_url": "http://localhost:3000/success",
            "cancel_url": "http://localhost:3000/cancel"
        }
        
        response = client.post("/api/v1/payment/checkout", json=payload)
        assert response.status_code == 401

    def test_portal_endpoint_requires_auth(self):
        """Test POST /api/v1/payment/portal endpoint requires authentication."""
        payload = {
            "return_url": "http://localhost:3000/subscription"
        }
        
        response = client.post("/api/v1/payment/portal", json=payload)
        assert response.status_code == 401

    def test_subscription_endpoint_requires_auth(self):
        """Test GET /api/v1/payment/subscription endpoint requires authentication."""
        response = client.get("/api/v1/payment/subscription")
        assert response.status_code == 401


class TestChatAPIContract:
    """Test chat API endpoints match frontend expectations."""

    def test_chat_stream_endpoint_requires_auth(self):
        """Test GET /api/v1/chat/stream endpoint requires authentication."""
        params = {
            "message": "test message",
            "sleep": 0.1,
            "number": 3
        }
        
        response = client.get("/api/v1/chat/stream", params=params)
        assert response.status_code == 401

    def test_websearch_endpoint_requires_auth(self):
        """Test GET /api/v1/chat/websearch endpoint requires authentication."""
        params = {"query": "test query"}
        
        response = client.get("/api/v1/chat/websearch", params=params)
        assert response.status_code == 401

    def test_summary_endpoint_requires_auth(self):
        """Test POST /api/v1/chat/summary endpoint requires authentication."""
        payload = {"text": "This is a test text to summarize."}
        
        response = client.post("/api/v1/chat/summary", json=payload)
        assert response.status_code == 401


class TestAuthAPIContract:
    """Test auth API endpoints match frontend expectations."""

    def test_register_endpoint(self):
        """Test POST /api/v1/auth/register endpoint."""
        payload = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        
        data = response.json()
        assert "data" in data
        assert "email" in data["data"]
        assert "full_name" in data["data"]

    def test_login_endpoint(self):
        """Test POST /api/v1/auth/login endpoint."""
        # First create a user
        register_payload = {
            "email": "login_test@example.com",
            "password": "testpassword123",
            "full_name": "Login Test User"
        }
        client.post("/api/v1/auth/register", json=register_payload)
        
        # Then test login
        login_payload = {
            "email": "login_test@example.com",
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data
        assert "access_token" in data["data"]
        assert "token_type" in data["data"]
        assert "expires_in" in data["data"]

    def test_me_endpoint_requires_auth(self):
        """Test GET /api/v1/auth/me endpoint requires authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403]  # Either is acceptable for auth failure

    def test_refresh_endpoint_requires_auth(self):
        """Test POST /api/v1/auth/refresh endpoint requires authentication."""
        response = client.post("/api/v1/auth/refresh")
        assert response.status_code in [401, 403]  # Either is acceptable for auth failure

    def test_logout_endpoint(self):
        """Test POST /api/v1/auth/logout endpoint."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 200
        
        data = response.json()
        assert "data" in data


class TestAPIResponseFormat:
    """Test that all API responses follow the expected format."""

    def test_response_format_consistency(self):
        """Test that all endpoints return consistent response format."""
        # Test a few endpoints to verify response format
        endpoints_to_test = [
            ("/api/v1/payment/plans", "GET", None, None),
            ("/api/v1/auth/logout", "POST", None, None),
        ]
        
        for endpoint, method, payload, headers in endpoints_to_test:
            if method == "GET":
                response = client.get(endpoint, headers=headers)
            else:
                response = client.post(endpoint, json=payload, headers=headers)
            
            # All responses should have these fields
            data = response.json()
            assert "data" in data
            assert "message" in data
            assert "success" in data
            
            # Success should be boolean
            assert isinstance(data["success"], bool)


class TestErrorHandling:
    """Test error handling for API endpoints."""

    def test_unauthorized_access(self):
        """Test that protected endpoints return 401 without auth."""
        protected_endpoints = [
            "/api/v1/payment/subscription",
            "/api/v1/payment/checkout",
            "/api/v1/payment/portal",
            "/api/v1/auth/me",
            "/api/v1/auth/refresh",
            "/api/v1/chat/stream",
            "/api/v1/chat/websearch",
            "/api/v1/chat/summary",
        ]
        
        for endpoint in protected_endpoints:
            if endpoint in ["/api/v1/payment/checkout", "/api/v1/payment/portal", "/api/v1/chat/summary"]:
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            
            assert response.status_code == 401

    def test_invalid_endpoints(self):
        """Test that invalid endpoints return 404."""
        invalid_endpoints = [
            "/api/v1/payment/invalid",
            "/api/v1/chat/invalid",
            "/api/v1/auth/invalid",
        ]
        
        for endpoint in invalid_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 404