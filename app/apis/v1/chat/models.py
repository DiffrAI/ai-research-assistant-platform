"""Request module for chat streaming API."""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for configuring chat token streaming."""

    sleep: float = Field(
        1,
        json_schema_extra={
            "description": "Sleep duration (in seconds) between streamed tokens.",
        },
    )
    number: int = Field(
        10,
        json_schema_extra={"description": "Total number of tokens to stream."},
    )


class WebSearchChatRequest(BaseModel):
    """Request model for initiating a web search-based chat response."""

    question: Optional[str] = Field(
        None,
        description="The user's input question to be processed for web search and answer generation.",
    )
    thread_id: Optional[str] = Field(
        None,
        description="Unique identifier for the chat thread to maintain context across requests.",
    )


class SummaryRequest(BaseModel):
    """Request model for submitting text to the summary task."""

    text: str = Field(
        ...,
        json_schema_extra={"description": "The text content to summarize."},
    )


class SummaryTaskResponse(BaseModel):
    """Response model for summary task submission."""

    task_id: str = Field(..., description="The ID of the submitted Celery task.")
    status: str = Field(..., description="The status of the task.")
    message: str = Field(..., description="A descriptive message.")


class SummaryTaskStatusResponse(BaseModel):
    """Response model for summary task status and result."""

    task_id: str = Field(..., description="The ID of the Celery task.")
    status: str = Field(..., description="The current status of the task.")
    result: Optional[str] = Field(
        None, description="The result of the task, if completed."
    )
    message: str = Field(..., description="A descriptive message.")
