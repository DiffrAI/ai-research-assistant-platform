"""Root router"""

from fastapi import APIRouter

from app import settings
from app.core.responses import AppJSONResponse

health_router = APIRouter()


@health_router.get(
    "/health",
    response_class=AppJSONResponse,
    summary="Health Check",
    description="Check the health status of the AI Research Assistant Platform API",
    response_description="JSON response with service status and version information.",
)
async def health_check() -> AppJSONResponse:
    """Health check endpoint for the AI Research Assistant Platform."""
    return AppJSONResponse(
        data={
            "message": "AI Research Assistant Platform",
            "version": settings.RELEASE_VERSION,
        },
        message="Service root endpoint",
        status="success",
        status_code=200,
    )
