"""Chat endpoints."""

import asyncio
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, Request
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel, Field

from app.auth import get_current_user
from app.models import UserInDB
from app.responses import create_response, create_streaming_response

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model."""

    sleep: float = Field(1.0, description="Sleep duration between tokens")
    number: int = Field(10, description="Number of tokens to stream")


class WebSearchChatRequest(BaseModel):
    """Web search chat request model."""

    question: Optional[str] = Field(None, description="User question")
    thread_id: Optional[str] = Field(None, description="Thread ID for context")


class SummaryRequest(BaseModel):
    """Summary request model."""

    text: str = Field(..., description="Text to summarize")


class SummaryResponse(BaseModel):
    """Summary response model."""

    task_id: str
    status: str
    result: Optional[str] = None
    message: str


def rate_limit_key_func(request: Request) -> str:
    """Generate rate limit key based on IP address."""
    if request.client and request.client.host:
        return request.client.host
    return "unknown_host"


@router.get("/stream", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def chat_stream(
    request: Request,
    sleep: float = 1.0,
    number: int = 10,
    current_user: UserInDB = Depends(get_current_user),
) -> dict:
    """Stream chat tokens."""

    async def generate_tokens() -> AsyncGenerator[str, None]:
        for i in range(number):
            yield f"data: Token {i + 1}\n\n"
            await asyncio.sleep(sleep)
        yield "data: [DONE]\n\n"

    return create_streaming_response(generate_tokens(), media_type="text/plain")


@router.get("/websearch", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def chat_websearch(
    request: Request,
    question: Optional[str] = None,
    thread_id: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user),
) -> dict:
    """Stream web search chat response."""
    # Try to use the actual service, fallback to mock
    try:
        # Check if websearch module is available
        import importlib.util

        spec = importlib.util.find_spec("app.workflows.graphs.websearch")
        if spec is None:
            raise ImportError("Websearch module not available")

        async def websearch_stream() -> AsyncGenerator[str, None]:
            yield f"data: Searching for: {question}\n\n"
            yield f"data: Processing with thread: {thread_id}\n\n"
            yield "data: [DONE]\n\n"

        return create_streaming_response(websearch_stream(), media_type="text/plain")
    except ImportError:

        async def mock_stream() -> AsyncGenerator[str, None]:
            yield f"data: Mock search for: {question}\n\n"
            yield "data: [DONE]\n\n"

        return create_streaming_response(mock_stream(), media_type="text/plain")


@router.post("/summary")
async def create_summary(
    request: SummaryRequest, current_user: UserInDB = Depends(get_current_user)
) -> dict:
    """Submit text for summary task."""
    # Mock implementation
    task_id = f"task_{hash(request.text) % 10000}"

    return create_response(
        data={"task_id": task_id}, message="Summary task submitted", status_code=200
    )


@router.get("/summary/status")
async def get_summary_status(
    task_id: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)
) -> dict:
    """Get status of summary task."""
    result = SummaryResponse(
        task_id=task_id or "unknown",
        status="completed",
        result="This is a mock summary result.",
        message="Task completed successfully",
    )

    return create_response(data=result.model_dump(), message="Task status retrieved")
