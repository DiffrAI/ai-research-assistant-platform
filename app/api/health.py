"""Health check endpoints."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.responses import create_response

router = APIRouter()


@router.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return create_response(
        data={
            "status": "healthy",
            "version": settings.release_version,
            "environment": settings.environment.value,
        },
        message="Service is healthy",
    )


@router.get("/")
async def root() -> JSONResponse:
    """Root endpoint."""
    return create_response(
        data={"name": "AI Research Assistant Platform"},
        message="Welcome to AI Research Assistant Platform",
    )
