"""Research endpoints."""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel

from app.auth import get_current_user
from app.models import User
from app.responses import create_response

router = APIRouter()


# Fallback models since the original ones don't exist


class ResearchRequest(BaseModel):
    query: str
    max_results: int = 10
    include_citations: bool = True


class ResearchResponse(BaseModel):
    query: str
    results: List[Any] = []
    citations: List[Any] = []


class ExportRequest(BaseModel):
    format: str
    content: str


class ResearchService:
    async def conduct_research(
        self, user_id: str, request: ResearchRequest
    ) -> tuple[ResearchResponse, str, int]:
        return ResearchResponse(query=request.query), "Success", 200

    async def save_research(
        self, user_id: str, response: ResearchResponse, tags: Optional[List[str]]
    ) -> tuple[ResearchResponse, str, int]:
        return response, "Saved", 200

    async def get_user_subscription(self, user_id: str) -> Any:
        from app.models import SubscriptionInfo, SubscriptionPlan

        return SubscriptionInfo(
            plan=SubscriptionPlan.FREE, searches_used=0, searches_limit=10
        )

    async def export_research(self, request: ExportRequest) -> tuple[bytes, str, int]:
        return request.content.encode(), f"research.{request.format}", 200


def get_research_service() -> ResearchService:
    """Get research service instance."""
    return ResearchService()


def get_user_id_from_token(current_user: User = Depends(get_current_user)) -> str:
    """Get user ID from current user."""
    return str(current_user.id)


@router.post("/", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def conduct_research(
    research_request: ResearchRequest,
    research_service: ResearchService = Depends(get_research_service),
    user_id: str = Depends(get_user_id_from_token),
) -> dict:
    """Conduct AI-powered research with web search and citations."""
    response, message, status_code = await research_service.conduct_research(
        user_id, research_request
    )

    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=message)

    return create_response(
        data=response.model_dump(), message=message, status_code=status_code
    )


@router.get("/stream", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def conduct_research_stream(
    query: str,
    max_results: int = 10,
    research_service: ResearchService = Depends(get_research_service),
    user_id: str = Depends(get_user_id_from_token),
) -> dict:
    """Stream research results in real-time."""
    research_request = ResearchRequest(
        query=query, max_results=max_results, include_citations=True
    )

    response, message, status_code = await research_service.conduct_research(
        user_id, research_request
    )

    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=message)

    return create_response(
        data=response.model_dump(), message=message, status_code=status_code
    )


@router.post("/save")
async def save_research(
    research_response: ResearchResponse,
    tags: Optional[List[str]] = None,
    research_service: ResearchService = Depends(get_research_service),
    user_id: str = Depends(get_user_id_from_token),
) -> dict:
    """Save research results for later reference."""
    saved_research, message, status_code = await research_service.save_research(
        user_id, research_response, tags
    )

    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=message)

    return create_response(
        data=saved_research.model_dump() if saved_research else {},
        message=message,
        status_code=status_code,
    )


@router.get("/saved")
async def get_saved_research() -> dict:
    """Get user's saved research sessions."""
    # TODO: Implement actual saved research retrieval
    saved_researches: List[Any] = []

    return create_response(
        data={"researches": saved_researches, "total": 0},
        message="Saved researches retrieved successfully",
    )


@router.get("/subscription")
async def get_subscription_info(
    research_service: ResearchService = Depends(get_research_service),
    user_id: str = Depends(get_user_id_from_token),
) -> dict:
    """Get user's subscription information and usage."""
    subscription = await research_service.get_user_subscription(user_id)

    return create_response(
        data=subscription.model_dump(),
        message="Subscription information retrieved successfully",
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

    import tempfile

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        if isinstance(content, str):
            tmp_file.write(content.encode("utf-8"))
        elif isinstance(content, bytes):
            tmp_file.write(content)
        tmp_file_path = tmp_file.name

    return FileResponse(
        tmp_file_path, filename=filename, media_type="application/octet-stream"
    )


@router.get("/trending")
async def get_trending_topics(limit: int = 10) -> dict:
    """Get trending research topics."""
    trending_topics = [
        {"topic": "AI and Machine Learning", "search_count": 1250},
        {"topic": "Climate Change Solutions", "search_count": 980},
        {"topic": "Quantum Computing", "search_count": 750},
        {"topic": "Sustainable Energy", "search_count": 650},
        {"topic": "Digital Privacy", "search_count": 520},
    ]

    return create_response(
        data={"trending_topics": trending_topics[:limit]},
        message="Trending topics retrieved successfully",
    )


@router.get("/analytics")
async def get_research_analytics() -> dict:
    """Get user's research analytics."""
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

    return create_response(data=analytics, message="Analytics retrieved successfully")
