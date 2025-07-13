"""Enhanced research service for AI Research Assistant Platform."""

import hashlib
import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from app import cache, trace
from app.core.exceptions import (
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
)
from app.workflows.graphs.websearch import WebSearchAgentGraph
from app.workflows.graphs.websearch.components.answer_generator import AnswerGenerator
from app.workflows.graphs.websearch.components.websearch_executor import (
    WebSearchExecutor,
)

from .models import (
    ExportRequest,
    ResearchRequest,
    ResearchResponse,
    ResearchResult,
    SavedResearch,
    UserSubscription,
)


class ResearchService:
    """Enhanced service for handling research logic and business rules."""

    @staticmethod
    def _hash_request(payload: Dict[str, Any]) -> str:
        """Generate a unique cache key from request payload."""
        # Sort keys to ensure consistent hashing
        sorted_payload = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(sorted_payload.encode()).hexdigest()

    @staticmethod
    def _validate_research_request(request: ResearchRequest) -> None:
        """Validate research request parameters."""
        if not request.query or not request.query.strip():
            raise ValidationError("Query cannot be empty", field="query")

        if len(request.query.strip()) < 3:
            raise ValidationError(
                "Query must be at least 3 characters long", field="query"
            )

        if len(request.query.strip()) > 1000:
            raise ValidationError("Query too long (max 1000 characters)", field="query")

        if request.max_results < 1 or request.max_results > 50:
            raise ValidationError(
                "Max results must be between 1 and 50", field="max_results"
            )

    @staticmethod
    def _check_user_limits(user_id: str) -> Tuple[bool, str]:
        """Check if user has exceeded their search limits."""
        # TODO: Implement actual user limit checking with database
        # For now, return True (allowed) for demo purposes
        return True, "Search allowed"

    @staticmethod
    def _increment_user_usage(user_id: str) -> None:
        """Increment user's search usage count."""
        # TODO: Implement actual usage tracking with database
        logger.info(f"Incrementing usage for user: {user_id}")

    @trace(name="research_service")
    async def conduct_research(
        self,
        user_id: str,
        request: ResearchRequest,
    ) -> Tuple[Optional[ResearchResponse], str, int]:
        """Conduct research using AI and web search with enhanced error handling."""
        try:
            # Validate request
            self._validate_research_request(request)

            # Check user limits
            allowed, message = self._check_user_limits(user_id)
            if not allowed:
                raise RateLimitError(
                    message=message,
                    retry_after=60,
                    details={"user_id": user_id, "limit_type": "search_quota"},
                )

            # Check cache first
            cache_key = self._hash_request(request.model_dump())
            cached_response = await cache.get(cache_key)
            if cached_response:
                logger.info("Cache hit for research query")
                return (
                    ResearchResponse.model_validate(json.loads(cached_response)),
                    "Research completed from cache",
                    200,
                )

            start_time = time.time()

            # Prepare initial input for agent execution
            from langchain_core.messages import HumanMessage

            state_input = {
                "question": HumanMessage(content=request.query),
                "refined_question": "",
                "require_enhancement": False,
                "refined_questions": [],
                "search_results": [],
                "messages": [HumanMessage(content=request.query)],
            }

            # Create a new WebSearchExecutor with the desired max_results
            searcher = WebSearchExecutor(max_results=request.max_results)

            # Create a new graph with the searcher
            graph = WebSearchAgentGraph(searcher=searcher).compile()

            # Run the research workflow
            final_state = await graph.ainvoke(
                state_input,
                config={"configurable": {"thread_id": user_id}},
            )

            # Process results
            results = self._process_search_results(
                final_state.get("search_results", [])
            )

            # Extract summary from messages
            summary = self._extract_summary_from_messages(
                final_state.get("messages", [])
            )

            # Calculate search time
            search_time = time.time() - start_time

            # Create response
            response = ResearchResponse(
                query=request.query,
                results=results,
                summary=summary,
                citations=self._extract_citations(results),
                total_results=len(results),
                search_time=search_time,
                model_used="local" if hasattr(AnswerGenerator(), "llm") else "openai",
            )

            # Cache the response with appropriate TTL
            cache_ttl = (
                3600 if len(results) > 0 else 300
            )  # 1 hour for good results, 5 min for empty
            await cache.set(cache_key, response.model_dump_json(), ttl=cache_ttl)

            # Increment user usage
            self._increment_user_usage(user_id)

            logger.info(
                f"Research completed successfully in {search_time:.2f}s with {len(results)} results"
            )
            return response, "Research completed successfully", 200

        except (ValidationError, RateLimitError) as e:
            # Re-raise validation and rate limit errors
            raise e
        except Exception as e:
            logger.exception(f"Error in research service: {e}")
            raise ServiceUnavailableError(
                message="Research service temporarily unavailable",
                service="research",
                details={"error": str(e)},
            ) from e

    def _process_search_results(
        self, raw_results: List[Dict[str, Any]]
    ) -> List[ResearchResult]:
        """Process raw search results into structured format with validation."""
        processed_results = []

        for i, result in enumerate(raw_results):
            try:
                processed_result = ResearchResult(
                    title=result.get("title", "Untitled"),
                    content=result.get("content", ""),
                    url=result.get("link", ""),
                    source=result.get("source", "Unknown"),
                    relevance_score=result.get("relevance_score"),
                )
                processed_results.append(processed_result)
            except Exception as e:
                logger.warning(f"Error processing search result {i}: {e}")
                continue

        return processed_results

    def _extract_summary_from_messages(self, messages: List[Any]) -> str:
        """Extract summary from messages with fallback."""
        if not messages:
            return "No summary available"

        # Get the last AI message which should contain the summary
        for message in reversed(messages):
            if hasattr(message, "content") and message.content:
                content = message.content.strip()
                if content and len(content) > 10:  # Ensure meaningful content
                    return content

        return "No summary available"

    def _extract_citations(self, results: List[ResearchResult]) -> List[str]:
        """Extract citations from research results with validation."""
        citations = []
        for i, result in enumerate(results, 1):
            if result.url and result.title:
                citation = f"{i}. {result.title}. {result.url}"
                citations.append(citation)
        return citations

    async def save_research(
        self,
        user_id: str,
        research_response: ResearchResponse,
        tags: Optional[List[str]] = None,
    ) -> Tuple[Optional[SavedResearch], str, int]:
        """Save research results for later reference with validation."""
        try:
            if not research_response.query:
                raise ValidationError(
                    "Cannot save research without a query", field="query"
                )

            if not research_response.results:
                raise ValidationError(
                    "Cannot save research without results", field="results"
                )

            research_id = str(uuid.uuid4())
            now = datetime.utcnow()

            saved_research = SavedResearch(
                id=research_id,
                query=research_response.query,
                results=research_response.results,
                summary=research_response.summary,
                created_at=now,
                updated_at=now,
                tags=tags or [],
            )

            # TODO: Save to database
            logger.info(f"Saved research {research_id} for user {user_id}")

            return saved_research, "Research saved successfully", 200

        except ValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"Error saving research: {e}")
            raise ServiceUnavailableError(
                message="Failed to save research",
                service="database",
                details={"error": str(e)},
            ) from e

    async def get_user_subscription(self, user_id: str) -> UserSubscription:
        """Get user's subscription information with validation."""
        if not user_id:
            raise ValidationError("User ID is required", field="user_id")

        # TODO: Implement actual subscription checking
        # For demo, return a free tier subscription
        return UserSubscription(
            user_id=user_id,
            plan="free",
            searches_used=5,  # Demo value
            searches_limit=10,  # Free tier limit
            expires_at=None,
            is_active=True,
        )

    async def export_research(
        self, request: ExportRequest
    ) -> Tuple[Optional[bytes], str, int]:
        """Export research results in various formats with validation."""
        try:
            if not request.research_id:
                raise ValidationError("Research ID is required", field="research_id")

            if request.format not in ["pdf", "docx", "markdown", "json"]:
                raise ValidationError("Unsupported export format", field="format")

            # TODO: Implement actual research retrieval and export
            # For now, return a demo export

            if request.format == "pdf":
                content = b"PDF export demo content"
                filename = f"research_{request.research_id}.pdf"
            elif request.format == "docx":
                content = b"DOCX export demo content"
                filename = f"research_{request.research_id}.docx"
            elif request.format == "markdown":
                content = b"# Research Results\n\nDemo markdown export"
                filename = f"research_{request.research_id}.md"
            elif request.format == "json":
                content = (
                    b'{"research_id": "'
                    + request.research_id.encode()
                    + b'", "status": "demo"}'
                )
                filename = f"research_{request.research_id}.json"
            else:
                raise ValidationError("Unsupported export format", field="format")

            return content, filename, 200

        except ValidationError as e:
            raise e
        except Exception as e:
            logger.error(f"Error exporting research: {e}")
            raise ServiceUnavailableError(
                message="Export failed", service="export", details={"error": str(e)}
            ) from e
