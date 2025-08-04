"""API router configuration."""

from fastapi import APIRouter

from .auth import router as auth_router
from .chat import router as chat_router
from .health import router as health_router
from .payment import router as payment_router
from .research import router as research_router

# Main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
api_router.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
api_router.include_router(research_router, prefix="/api/v1/research", tags=["Research"])
api_router.include_router(payment_router, prefix="/api/v1/payment", tags=["Payment"])
