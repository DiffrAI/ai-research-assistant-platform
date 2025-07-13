"""Root router"""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

root_router = APIRouter()


@root_router.get(
    "/",
    include_in_schema=False,
    summary="API Documentation Redirect",
    description="Redirects the root path to the interactive API documentation for the AI Research Assistant Platform.",
    response_description="Redirect response to the Swagger UI documentation",
)
async def root() -> RedirectResponse:
    """Redirects to the AI Research Assistant Platform API documentation."""
    return RedirectResponse(url="/docs")
