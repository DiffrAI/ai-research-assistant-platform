"""Research API module for AI Research Assistant Platform."""

from fastapi import APIRouter

from .controller import router as research_router

# Define research API router
research_api = APIRouter()
research_api.include_router(research_router, tags=["Research"])

__all__ = ["research_api"]
