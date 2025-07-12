"""Research service for AI Research Assistant Platform."""

import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from app import cache, trace
from app.workflows.graphs.websearch import WebSearchAgentGraph
from app.workflows.graphs.websearch.components.answer_generator import AnswerGenerator
from app.workflows.graphs.websearch.components.question_rewriter import QuestionRewriter
from app.workflows.graphs.websearch.components.websearch_executor import WebSearchExecutor

from .models import (
    ExportRequest,
    ResearchRequest,
    ResearchResponse,
    ResearchResult,
    SavedResearch,
    UserSubscription,
)


class ResearchService:
    """Service for handling research logic and business rules."""

    def __init__(self):
        """Initialize the research service."""
        self.graph = WebSearchAgentGraph().compile()
        self.answer_generator = AnswerGenerator()
        self.question_rewriter = QuestionRewriter()
        self.websearch_executor = WebSearchExecutor()

    @staticmethod
    def _hash_request(payload: dict) -> str:
        """Generate a unique cache key from request payload."""
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def _check_user_limits(user_id: str) -> Tuple[bool, str]:
        """Check if user has exceeded their search limits."""
        # TODO: Implement actual user limit checking
        # For now, return True (allowed) for demo purposes
        return True, "Search allowed"

    @staticmethod
    def _increment_user_usage(user_id: str) -> None:
        """Increment user's search usage count."""
        # TODO: Implement actual usage tracking
        logger.info(f"Incrementing usage for user: {user_id}")

    @trace(name="research_service")
    async def conduct_research(
        self, user_id: str, request: ResearchRequest
    ) -> Tuple[ResearchResponse, str, int]:
        """Conduct research using AI and web search."""
        
        # Check user limits
        allowed, message = self._check_user_limits(user_id)
        if not allowed:
            return None, message, 429

        # Check cache first
        cache_key = self._hash_request(request.model_dump())
        cached_response = await cache.get(cache_key)
        if cached_response:
            logger.info("Cache hit for research query")
            return ResearchResponse.model_validate(json.loads(cached_response)), "Research completed from cache", 200

        start_time = time.time()
        
        try:
            # Prepare initial input for agent execution
            state_input = {
                "question": {"content": request.query, "type": "human"},
                "refined_question": "",
                "require_enhancement": False,
                "questions": [],
                "search_results": [],
                "messages": [{"content": request.query, "type": "human"}],
            }

            # Run the research workflow
            final_state = await self._run_research_workflow(state_input, request.max_results)
            
            # Process results
            results = self._process_search_results(final_state.get("search_results", []))
            summary = final_state.get("summary", "No summary available")
            
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
                model_used="local" if hasattr(self.answer_generator, 'llm') else "openai"
            )

            # Cache the response
            await cache.set(cache_key, response.model_dump_json(), ttl=3600)  # 1 hour cache
            
            # Increment user usage
            self._increment_user_usage(user_id)
            
            return response, "Research completed successfully", 200

        except Exception as e:
            logger.error(f"Error in research service: {e}")
            return None, f"Research failed: {str(e)}", 500

    async def _run_research_workflow(self, state_input: Dict, max_results: int) -> Dict:
        """Run the research workflow using LangGraph."""
        
        # Override max results for this search
        original_max_results = getattr(self.websearch_executor, 'max_results', 10)
        self.websearch_executor.max_results = max_results
        
        try:
            # Run the workflow
            final_state = await self.graph.ainvoke(state_input)
            return final_state
        finally:
            # Restore original max results
            self.websearch_executor.max_results = original_max_results

    def _process_search_results(self, raw_results: List[Dict]) -> List[ResearchResult]:
        """Process raw search results into structured format."""
        processed_results = []
        
        for result in raw_results:
            processed_result = ResearchResult(
                title=result.get("title", "Untitled"),
                content=result.get("content", ""),
                url=result.get("link", ""),
                source=result.get("source", "Unknown"),
                relevance_score=result.get("relevance_score")
            )
            processed_results.append(processed_result)
        
        return processed_results

    def _extract_citations(self, results: List[ResearchResult]) -> List[str]:
        """Extract citations from research results."""
        citations = []
        for i, result in enumerate(results, 1):
            citation = f"{i}. {result.title}. {result.url}"
            citations.append(citation)
        return citations

    async def save_research(
        self, user_id: str, research_response: ResearchResponse, tags: List[str] = None
    ) -> Tuple[SavedResearch, str, int]:
        """Save research results for later reference."""
        
        try:
            research_id = str(uuid.uuid4())
            now = datetime.utcnow()
            
            saved_research = SavedResearch(
                id=research_id,
                query=research_response.query,
                results=research_response.results,
                summary=research_response.summary,
                created_at=now,
                updated_at=now,
                tags=tags or []
            )
            
            # TODO: Save to database
            logger.info(f"Saved research {research_id} for user {user_id}")
            
            return saved_research, "Research saved successfully", 200
            
        except Exception as e:
            logger.error(f"Error saving research: {e}")
            return None, f"Failed to save research: {str(e)}", 500

    async def get_user_subscription(self, user_id: str) -> UserSubscription:
        """Get user's subscription information."""
        # TODO: Implement actual subscription checking
        # For demo, return a free tier subscription
        return UserSubscription(
            user_id=user_id,
            plan="free",
            searches_used=5,  # Demo value
            searches_limit=10,  # Free tier limit
            expires_at=None,
            is_active=True
        )

    async def export_research(self, request: ExportRequest) -> Tuple[bytes, str, int]:
        """Export research results in various formats."""
        
        try:
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
                content = b'{"research_id": "' + request.research_id.encode() + b'", "status": "demo"}'
                filename = f"research_{request.research_id}.json"
            else:
                return None, "Unsupported export format", 400
            
            return content, filename, 200
            
        except Exception as e:
            logger.error(f"Error exporting research: {e}")
            return None, f"Export failed: {str(e)}", 500 