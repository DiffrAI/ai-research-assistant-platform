"""Monitoring endpoints for API usage and health."""

from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.models import User, UserRole
from app.responses import create_response
from app.middleware.api_monitoring import get_monitoring_stats

router = APIRouter()


@router.get("/stats")
async def get_api_stats(current_user: User = Depends(get_current_user)) -> dict:
    """Get API endpoint usage statistics (admin only)."""
    # Only allow admin users to view stats
    if current_user.role != UserRole.ADMIN:
        return create_response(
            data=None,
            message="Access denied. Admin privileges required.",
            status_code=403
        )
    
    stats = get_monitoring_stats()
    
    # Calculate summary statistics
    total_requests = sum(stat["total_requests"] for stat in stats.values())
    total_errors = sum(stat["error_count"] for stat in stats.values())
    avg_response_time = sum(stat["avg_time"] for stat in stats.values()) / len(stats) if stats else 0
    
    summary = {
        "total_endpoints": len(stats),
        "total_requests": total_requests,
        "total_errors": total_errors,
        "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
        "avg_response_time_ms": round(avg_response_time * 1000, 2)
    }
    
    return create_response(
        data={
            "summary": summary,
            "endpoint_stats": stats
        },
        message="API statistics retrieved successfully"
    )


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint for monitoring systems."""
    return create_response(
        data={
            "status": "healthy",
            "service": "AI Research Assistant Platform",
            "version": "1.0.0"
        },
        message="Service is healthy"
    )


@router.get("/endpoints")
async def list_endpoints() -> dict:
    """List all available API endpoints."""
    endpoints = {
        "auth": [
            "POST /api/v1/auth/register",
            "POST /api/v1/auth/login",
            "GET /api/v1/auth/me",
            "GET /api/v1/auth/subscription",
            "POST /api/v1/auth/logout",
            "POST /api/v1/auth/refresh"
        ],
        "payment": [
            "GET /api/v1/payment/plans",
            "POST /api/v1/payment/checkout",
            "POST /api/v1/payment/portal",
            "GET /api/v1/payment/subscription"
        ],
        "chat": [
            "GET /api/v1/chat/stream",
            "GET /api/v1/chat/websearch",
            "POST /api/v1/chat/summary",
            "GET /api/v1/chat/summary/status"
        ],
        "research": [
            "POST /api/v1/research",
            "GET /api/v1/research/stream",
            "POST /api/v1/research/save",
            "GET /api/v1/research/saved",
            "POST /api/v1/research/export",
            "GET /api/v1/research/subscription",
            "GET /api/v1/research/trending",
            "GET /api/v1/research/analytics"
        ],
        "monitoring": [
            "GET /api/v1/monitoring/stats",
            "GET /api/v1/monitoring/health",
            "GET /api/v1/monitoring/endpoints"
        ]
    }
    
    return create_response(
        data={"endpoints": endpoints},
        message="Available endpoints retrieved successfully"
    )