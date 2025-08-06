"""Middleware for API endpoint validation and helpful error messages."""

import logging
from typing import Dict, List
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.responses import create_response

logger = logging.getLogger(__name__)


class EndpointValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to detect common endpoint mismatches and provide helpful suggestions."""

    def __init__(self, app):
        super().__init__(app)
        # Common endpoint mismatches and their corrections
        self.endpoint_suggestions: Dict[str, str] = {
            # Payment API mismatches
            "/api/v1/payment/create-checkout-session": "/api/v1/payment/checkout",
            "/api/v1/payment/create-portal-session": "/api/v1/payment/portal",
            "/api/v1/payment/usage": "/api/v1/payment/subscription",
            
            # Chat API mismatches
            "/api/v1/chat/chat": "/api/v1/chat/stream",
            "/api/v1/chat/celery/summary": "/api/v1/chat/summary",
            
            # Common variations
            "/api/v1/payment/create_checkout_session": "/api/v1/payment/checkout",
            "/api/v1/payment/create_portal_session": "/api/v1/payment/portal",
            "/api/v1/chat/celery_summary": "/api/v1/chat/summary",
        }
        
        # Valid endpoints for fuzzy matching
        self.valid_endpoints: List[str] = [
            # Auth endpoints
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/me",
            "/api/v1/auth/subscription",
            "/api/v1/auth/logout",
            "/api/v1/auth/refresh",
            
            # Payment endpoints
            "/api/v1/payment/plans",
            "/api/v1/payment/checkout",
            "/api/v1/payment/portal",
            "/api/v1/payment/subscription",
            
            # Chat endpoints
            "/api/v1/chat/stream",
            "/api/v1/chat/websearch",
            "/api/v1/chat/summary",
            "/api/v1/chat/summary/status",
            
            # Research endpoints
            "/api/v1/research",
            "/api/v1/research/stream",
            "/api/v1/research/save",
            "/api/v1/research/saved",
            "/api/v1/research/export",
            "/api/v1/research/subscription",
            "/api/v1/research/trending",
            "/api/v1/research/analytics",
        ]

    async def dispatch(self, request: Request, call_next):
        """Process the request and provide helpful error messages for mismatched endpoints."""
        response = await call_next(request)
        
        # Only handle 404 errors for API endpoints
        if (response.status_code == 404 and 
            request.url.path.startswith("/api/v1/")):
            
            # Log the mismatch for monitoring
            logger.warning(
                f"API endpoint mismatch: {request.method} {request.url.path} "
                f"from {request.client.host if request.client else 'unknown'}"
            )
            
            # Check for exact matches in our suggestions
            if request.url.path in self.endpoint_suggestions:
                suggested_endpoint = self.endpoint_suggestions[request.url.path]
                return JSONResponse(
                    status_code=404,
                    content=create_response(
                        data={
                            "requested_endpoint": request.url.path,
                            "suggested_endpoint": suggested_endpoint,
                            "method": request.method
                        },
                        message=f"Endpoint not found. Did you mean '{suggested_endpoint}'?",
                        status_code=404
                    )
                )
            
            # Try fuzzy matching for similar endpoints
            suggestions = self._find_similar_endpoints(request.url.path)
            if suggestions:
                return JSONResponse(
                    status_code=404,
                    content=create_response(
                        data={
                            "requested_endpoint": request.url.path,
                            "suggested_endpoints": suggestions[:3],  # Limit to top 3
                            "method": request.method
                        },
                        message=f"Endpoint not found. Similar endpoints: {', '.join(suggestions[:3])}",
                        status_code=404
                    )
                )
            
            # Generic 404 with available endpoints for the same service
            service_endpoints = self._get_service_endpoints(request.url.path)
            if service_endpoints:
                return JSONResponse(
                    status_code=404,
                    content=create_response(
                        data={
                            "requested_endpoint": request.url.path,
                            "available_endpoints": service_endpoints,
                            "method": request.method
                        },
                        message=f"Endpoint not found. Available endpoints for this service: {', '.join(service_endpoints)}",
                        status_code=404
                    )
                )
        
        return response

    def _find_similar_endpoints(self, requested_path: str) -> List[str]:
        """Find similar endpoints using simple string matching."""
        suggestions = []
        requested_parts = requested_path.lower().split('/')
        
        for endpoint in self.valid_endpoints:
            endpoint_parts = endpoint.lower().split('/')
            
            # Calculate similarity score
            common_parts = len(set(requested_parts) & set(endpoint_parts))
            if common_parts >= 3:  # At least 3 common parts (api, v1, service)
                suggestions.append(endpoint)
        
        return suggestions

    def _get_service_endpoints(self, requested_path: str) -> List[str]:
        """Get all endpoints for the same service (auth, payment, chat, research)."""
        path_parts = requested_path.split('/')
        if len(path_parts) < 4:
            return []
        
        service = path_parts[3]  # e.g., 'auth', 'payment', 'chat'
        service_prefix = f"/api/v1/{service}/"
        
        return [ep for ep in self.valid_endpoints if ep.startswith(service_prefix)]


def log_endpoint_mismatch(request: Request, suggested_endpoint: str = None):
    """Log endpoint mismatches for monitoring and debugging."""
    log_data = {
        "timestamp": "now",
        "method": request.method,
        "requested_path": request.url.path,
        "suggested_path": suggested_endpoint,
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown")
    }
    
    logger.info(f"Endpoint mismatch logged: {log_data}")