"""Middleware for monitoring API endpoint usage and performance."""

import time
import logging
from typing import Dict, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json

logger = logging.getLogger(__name__)


class APIMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor API endpoint usage, performance, and errors."""

    def __init__(self, app):
        super().__init__(app)
        self.endpoint_stats: Dict[str, Dict] = {}

    async def dispatch(self, request: Request, call_next):
        """Monitor API requests and responses."""
        start_time = time.time()
        endpoint_key = f"{request.method} {request.url.path}"
        
        # Extract user info if available
        user_id = None
        if hasattr(request.state, 'user'):
            user_id = getattr(request.state.user, 'id', None)
        
        # Process the request
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Log API usage
        self._log_api_usage(
            request=request,
            response=response,
            process_time=process_time,
            user_id=user_id
        )
        
        # Update endpoint statistics
        self._update_endpoint_stats(endpoint_key, response.status_code, process_time)
        
        # Add monitoring headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Endpoint"] = endpoint_key
        
        return response

    def _log_api_usage(
        self, 
        request: Request, 
        response: Response, 
        process_time: float,
        user_id: Optional[str] = None
    ):
        """Log API usage for monitoring and analytics."""
        log_data = {
            "timestamp": time.time(),
            "method": request.method,
            "endpoint": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "user_id": user_id,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "query_params": dict(request.query_params) if request.query_params else None,
        }
        
        # Log successful requests at INFO level
        if 200 <= response.status_code < 400:
            logger.info(f"API_SUCCESS: {json.dumps(log_data)}")
        
        # Log client errors (4xx) at WARNING level
        elif 400 <= response.status_code < 500:
            log_data["error_type"] = "client_error"
            logger.warning(f"API_CLIENT_ERROR: {json.dumps(log_data)}")
        
        # Log server errors (5xx) at ERROR level
        elif response.status_code >= 500:
            log_data["error_type"] = "server_error"
            logger.error(f"API_SERVER_ERROR: {json.dumps(log_data)}")

    def _update_endpoint_stats(self, endpoint_key: str, status_code: int, process_time: float):
        """Update endpoint statistics for monitoring."""
        if endpoint_key not in self.endpoint_stats:
            self.endpoint_stats[endpoint_key] = {
                "total_requests": 0,
                "success_count": 0,
                "error_count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "status_codes": {}
            }
        
        stats = self.endpoint_stats[endpoint_key]
        stats["total_requests"] += 1
        stats["total_time"] += process_time
        stats["avg_time"] = stats["total_time"] / stats["total_requests"]
        stats["min_time"] = min(stats["min_time"], process_time)
        stats["max_time"] = max(stats["max_time"], process_time)
        
        # Count status codes
        status_str = str(status_code)
        stats["status_codes"][status_str] = stats["status_codes"].get(status_str, 0) + 1
        
        # Count success vs errors
        if 200 <= status_code < 400:
            stats["success_count"] += 1
        else:
            stats["error_count"] += 1

    def get_endpoint_stats(self) -> Dict[str, Dict]:
        """Get current endpoint statistics."""
        return self.endpoint_stats.copy()

    def reset_stats(self):
        """Reset endpoint statistics."""
        self.endpoint_stats.clear()


# Global instance for accessing stats
monitoring_middleware = None


def get_monitoring_stats() -> Dict[str, Dict]:
    """Get current monitoring statistics."""
    if monitoring_middleware:
        return monitoring_middleware.get_endpoint_stats()
    return {}


def log_authentication_failure(request: Request, reason: str):
    """Log authentication failures for security monitoring."""
    log_data = {
        "timestamp": time.time(),
        "event": "auth_failure",
        "reason": reason,
        "endpoint": request.url.path,
        "method": request.method,
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
    }
    
    logger.warning(f"AUTH_FAILURE: {json.dumps(log_data)}")


def log_rate_limit_exceeded(request: Request, user_id: Optional[str] = None):
    """Log rate limit violations."""
    log_data = {
        "timestamp": time.time(),
        "event": "rate_limit_exceeded",
        "endpoint": request.url.path,
        "method": request.method,
        "user_id": user_id,
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
    }
    
    logger.warning(f"RATE_LIMIT: {json.dumps(log_data)}")


def log_endpoint_mismatch(request: Request, suggested_endpoint: Optional[str] = None):
    """Log endpoint mismatches for debugging."""
    log_data = {
        "timestamp": time.time(),
        "event": "endpoint_mismatch",
        "requested_endpoint": request.url.path,
        "method": request.method,
        "suggested_endpoint": suggested_endpoint,
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
    }
    
    logger.info(f"ENDPOINT_MISMATCH: {json.dumps(log_data)}")