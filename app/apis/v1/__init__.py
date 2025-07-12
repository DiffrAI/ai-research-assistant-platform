"""Initialize API Routers"""

from fastapi import APIRouter

from .chat.controller import router as chat_router
from .research import research_api
from .user.controller import router as user_router
from .auth.controller import router as auth_router
from .payment.controller import router as payment_router

# Define and configure versioned API routers
v1_routers = APIRouter()
v1_routers.include_router(user_router, tags=["User"])
v1_routers.include_router(chat_router, tags=["Chat"])
v1_routers.include_router(research_api, tags=["Research"])
v1_routers.include_router(auth_router, prefix="/auth", tags=["Authentication"])
v1_routers.include_router(payment_router, prefix="/payment", tags=["Payment"])

__all__ = ["v1_routers"]
