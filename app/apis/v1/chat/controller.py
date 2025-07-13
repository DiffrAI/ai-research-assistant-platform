"""Route for chat streaming and summary task."""

from fastapi import Depends, Request
from fastapi.routing import APIRouter
from fastapi_limiter.depends import RateLimiter
from fastapi_utils.cbv import cbv

from app.core.responses import AppJSONResponse, AppStreamingResponse

from .models import ChatRequest, SummaryRequest, WebSearchChatRequest
from .service import ChatService

router = APIRouter()

def common_dependency():
    """Common dependency."""
    return {"msg": "This is a dependency"}

@cbv(router)
class ChatRoute:
    """Chat-related routes."""

    def __init__(self):
        self.common_dep = common_dependency()
        self.service = ChatService()

    @router.get(
        "/chat",
        response_class=AppStreamingResponse,
        dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    )
    async def chat(
        self,
        request: Request,
        sleep: float = 1,
        number: int = 10,
    ):
        """Stream chat tokens based on query parameters."""
        sleep = request.query_params.get("sleep", sleep)
        number = request.query_params.get("number", number)
        chat_request = ChatRequest(sleep=float(sleep), number=int(number))
        data = await self.service.chat_service(request_params=chat_request)
        return AppStreamingResponse(data_stream=data)

    @router.get(
        "/chat/websearch",
        response_class=AppStreamingResponse,
        dependencies=[Depends(RateLimiter(times=5, seconds=60))],
    )
    async def chat_websearch(
        self,
        request: Request,
        question: str = None,
        thread_id: str = None,
    ):
        """Stream chat tokens based on query parameters."""
        question = request.query_params.get("question", question)
        thread_id = request.query_params.get("thread_id", thread_id)
        chat_request = WebSearchChatRequest(question=question, thread_id=thread_id)
        data = await self.service.chat_websearch_service(request_params=chat_request)
        return AppStreamingResponse(data_stream=data)

    @router.post("/celery/summary")
    async def celery_summary(self, request_params: SummaryRequest):
        """Submit text for summary task."""
        data, message, status_code = await self.service.submit_summary_task(
            text=request_params.text,
        )
        return AppJSONResponse(data=data, message=message, status_code=status_code)

    @router.get("/celery/summary/status")
    async def celery_summary_status(
        self,
        task_id: str = None,
    ):
        """Get status and result of a Celery summary task."""
        data, message, status_code = await self.service.summary_status(task_id=task_id)
        return AppJSONResponse(data=data, message=message, status_code=status_code)
