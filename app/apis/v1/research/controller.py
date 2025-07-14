"""Research controller for AI Research Assistant Platform."""

from typing import Any, List

from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.routing import APIRouter
from fastapi_limiter.depends import RateLimiter

from app.apis.v1.auth.controller import get_current_user
from app.core.responses import AppJSONResponse
from app.models.user import User

from .models import (
    ExportRequest,
    ResearchRequest,
    ResearchResponse,
)
from .service import ResearchService

router = APIRouter()


def get_research_service() -> ResearchService:
    """Dependency to get research service."""
    return ResearchService()


def get_user_id_from_token(current_user: User = Depends(get_current_user)) -> str:
    """Get user ID from JWT token."""
    return str(current_user.id)


def write_temp_file(content: bytes | str | None) -> str:
    import tempfile

    tmp_file_path = ""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        if isinstance(content, str):
            tmp_file.write(content.encode("utf-8"))
        elif isinstance(content, bytes):
            tmp_file.write(content)
        else:
            tmp_file.write(b"")
        tmp_file_path = tmp_file.name
    return tmp_file_path


@router.post(
    "/research",
    response_model=ResearchResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def conduct_research(
    research_request: ResearchRequest,
    research_service: ResearchService = Depends(get_research_service),
    user_id: str = Depends(get_user_id_from_token),
) -> AppJSONResponse:
    """Conduct AI-powered research with web search and citations."""
    response, message, status_code = await research_service.conduct_research(
        user_id,
        research_request,
    )

    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=message)

    return AppJSONResponse(
        data=response.model_dump(),
        message=message,
        status_code=status_code,
    )


@router.get(
    "/research/stream",
    dependencies=[Depends(RateLimiter(times=5, seconds=60))],
)
async def conduct_research_stream(
    query: str,
    max_results: int = 10,
    research_service: ResearchService = Depends(get_research_service),
    user_id: str = Depends(get_user_id_from_token),
) -> AppJSONResponse:
    """Stream research results in real-time."""
    research_request = ResearchRequest(
        query=query,
        max_results=max_results,
        include_citations=True,
    )

    response, message, status_code = await research_service.conduct_research(
        user_id,
        research_request,
    )

    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=message)

    return AppJSONResponse(
        data=response.model_dump(),
        message=message,
        status_code=status_code,
    )


@router.post("/research/save")
async def save_research(
    research_response: ResearchResponse,
    tags: list[str] | None = None,
    research_service: ResearchService = Depends(get_research_service),
    user_id: str = Depends(get_user_id_from_token),
) -> AppJSONResponse:
    """Save research results for later reference."""
    saved_research, message, status_code = await research_service.save_research(
        user_id,
        research_response,
        tags,
    )

    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=message)

    return AppJSONResponse(
        data=saved_research.model_dump() if saved_research else {},
        message=message,
        status_code=status_code,
    )


@router.get("/research/saved")
async def get_saved_research() -> AppJSONResponse:
    """Get user's saved research sessions."""
    # TODO: Implement actual saved research retrieval
    # For demo, return empty list
    saved_researches: List[Any] = []

    return AppJSONResponse(
        data={"researches": saved_researches, "total": 0},
        message="Saved researches retrieved successfully",
        status_code=200,
    )


@router.get("/subscription")
async def get_subscription_info(
    research_service: ResearchService = Depends(get_research_service),
    user_id: str = Depends(get_user_id_from_token),
) -> AppJSONResponse:
    """Get user's subscription information and usage."""
    subscription = await research_service.get_user_subscription(user_id)

    return AppJSONResponse(
        data=subscription.model_dump(),
        message="Subscription information retrieved successfully",
        status_code=200,
    )


@router.post("/export")
async def export_research(
    export_request: ExportRequest,
    research_service: ResearchService = Depends(get_research_service),
) -> FileResponse:
    """Export research results in various formats."""
    content, filename, status_code = await research_service.export_research(
        export_request
    )

    if status_code != 200 or content is None:
        raise HTTPException(status_code=status_code, detail=filename)

    tmp_file_path = write_temp_file(content)
    return FileResponse(
        tmp_file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.get("/research/trending")
async def get_trending_topics(
    limit: int = 10,
) -> AppJSONResponse:
    """Get trending research topics."""
    # TODO: Implement trending topics analysis
    # For demo, return sample trending topics
    trending_topics = [
        {"topic": "AI and Machine Learning", "search_count": 1250},
        {"topic": "Climate Change Solutions", "search_count": 980},
        {"topic": "Quantum Computing", "search_count": 750},
        {"topic": "Sustainable Energy", "search_count": 650},
        {"topic": "Digital Privacy", "search_count": 520},
    ]

    return AppJSONResponse(
        data={"trending_topics": trending_topics[:limit]},
        message="Trending topics retrieved successfully",
        status_code=200,
    )


@router.get("/research/analytics")
async def get_research_analytics() -> AppJSONResponse:
    """Get user's research analytics."""
    # TODO: Implement actual analytics
    # For demo, return sample analytics
    analytics = {
        "total_searches": 45,
        "saved_researches": 12,
        "most_searched_topics": [
            {"topic": "Python Programming", "count": 8},
            {"topic": "Machine Learning", "count": 6},
            {"topic": "Web Development", "count": 4},
        ],
        "average_search_time": 2.3,
        "export_count": 5,
    }

    return AppJSONResponse(
        data=analytics,
        message="Analytics retrieved successfully",
        status_code=200,
    )
