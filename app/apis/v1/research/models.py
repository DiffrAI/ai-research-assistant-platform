"""Data models for AI Research Assistant Platform."""

from datetime import datetime

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """Request model for research queries."""

    query: str = Field(..., description="Research query or question")
    max_results: int = Field(default=10, description="Maximum number of search results")
    include_citations: bool = Field(default=True, description="Include citations in response")
    export_format: str | None = Field(default=None, description="Export format (pdf, docx, markdown)")


class ResearchResult(BaseModel):
    """Model for individual research result."""

    title: str = Field(..., description="Title of the source")
    content: str = Field(..., description="Content or summary")
    url: str = Field(..., description="Source URL")
    source: str = Field(..., description="Source name (e.g., DuckDuckGo)")
    relevance_score: float | None = Field(default=None, description="Relevance score")


class ResearchResponse(BaseModel):
    """Response model for research results."""

    query: str = Field(..., description="Original research query")
    results: list[ResearchResult] = Field(..., description="Research results")
    summary: str = Field(..., description="AI-generated summary")
    citations: list[str] = Field(..., description="Citation list")
    total_results: int = Field(..., description="Total number of results")
    search_time: float = Field(..., description="Search execution time in seconds")
    model_used: str = Field(..., description="AI model used for generation")


class SavedResearch(BaseModel):
    """Model for saved research sessions."""

    id: str = Field(..., description="Unique research session ID")
    query: str = Field(..., description="Original research query")
    results: list[ResearchResult] = Field(..., description="Research results")
    summary: str = Field(..., description="AI-generated summary")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    tags: list[str] = Field(default=[], description="User-defined tags")


class UserSubscription(BaseModel):
    """Model for user subscription information."""

    user_id: str = Field(..., description="User ID")
    plan: str = Field(..., description="Subscription plan (free, pro, enterprise)")
    searches_used: int = Field(..., description="Number of searches used this month")
    searches_limit: int = Field(..., description="Monthly search limit")
    expires_at: datetime | None = Field(default=None, description="Subscription expiry date")
    is_active: bool = Field(..., description="Whether subscription is active")


class ExportRequest(BaseModel):
    """Request model for exporting research results."""

    research_id: str = Field(..., description="Research session ID to export")
    format: str = Field(..., description="Export format (pdf, docx, markdown, json)")
    include_citations: bool = Field(default=True, description="Include citations in export")
    include_summary: bool = Field(default=True, description="Include AI summary in export")
