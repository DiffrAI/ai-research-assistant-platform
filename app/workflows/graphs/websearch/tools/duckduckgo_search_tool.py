"""DuckDuckGo search tool for websearch."""

import random
import time
from typing import Any, Optional

from duckduckgo_search import DDGS
from langchain_core.tools import BaseTool
from loguru import logger
from pydantic import BaseModel, Field

from app import settings


class SearchInput(BaseModel):
    """Input schema for DuckDuckGo search tool."""

    query: str = Field(description="The search query")
    max_results: int = Field(default=10, description="Maximum number of search results")


class DuckDuckGoSearchTool(BaseTool):
    """DuckDuckGo search tool that mimics Tavily's interface with robust retry logic."""

    name: str = "duckduckgo_search"
    description: str = "Search the web using DuckDuckGo"
    max_results: int = Field(default=10, description="Maximum number of search results")

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._ddgs: Optional[DDGS] = None  # Initialize lazily
        # Store retry settings as instance variables (not Pydantic fields)
        self._max_retries = settings.SEARCH_MAX_RETRIES
        self._base_delay = settings.SEARCH_BASE_DELAY
        self._max_delay = settings.SEARCH_MAX_DELAY

    @property
    def ddgs(self) -> DDGS:
        """Lazy initialization of DDGS instance."""
        if self._ddgs is None:
            try:
                self._ddgs = DDGS()
            except Exception as e:
                logger.error(f"Failed to initialize DDGS: {e}")
                raise
        return self._ddgs

    def _exponential_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        delay = min(self._base_delay * (2**attempt), self._max_delay)
        jitter = random.uniform(0, 0.1 * delay)
        return float(delay + jitter)

    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable."""
        error_str = str(error).lower()
        retryable_patterns = [
            "rate limit",
            "too many requests",
            "timeout",
            "connection",
            "network",
            "temporary",
            "service unavailable",
            "gateway",
            "bad gateway",
            "internal server error",
            "ddgs",
        ]
        return any(pattern in error_str for pattern in retryable_patterns)

    def _run(self, query: str, max_results: int = 10) -> dict[str, Any]:
        """Execute DuckDuckGo search with robust retry logic and fallback mechanisms."""
        # Use provided max_results or fall back to instance default
        search_max_results = (
            max_results if max_results is not None else self.max_results
        )
        logger.info(
            f"DuckDuckGo search tool called with query='{query}', max_results={max_results}, using search_max_results={search_max_results}"
        )
        logger.info(f"Tool instance max_results: {self.max_results}")

        # Ensure max_results is an integer
        try:
            search_max_results = int(search_max_results)
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid max_results value: {search_max_results}, using default: {self.max_results}"
            )
            search_max_results = self.max_results

        # Limit results to the requested max_results
        logger.info(f"Will limit results to {search_max_results} items")

        for attempt in range(self._max_retries):
            try:
                logger.info(
                    f"Performing DuckDuckGo search for: '{query}' with max_results={search_max_results} (attempt {attempt + 1}/{self._max_retries})"
                )

                # Add exponential backoff delay between retries
                if attempt > 0:
                    delay = self._exponential_backoff_delay(attempt)
                    logger.info(f"Waiting {delay:.2f}s before retry {attempt + 1}")
                    time.sleep(delay)

                # Perform the search with timeout
                start_time = time.time()
                logger.info(
                    f"Calling DuckDuckGo with query='{query}' and max_results={search_max_results}"
                )
                results = list(self.ddgs.text(query, max_results=search_max_results))
                search_time = time.time() - start_time
                logger.info(f"DuckDuckGo returned {len(results)} raw results")

                # Validate results
                if not results:
                    logger.warning(
                        f"No results returned for query: '{query}' (attempt {attempt + 1})"
                    )
                    if attempt < self._max_retries - 1:
                        continue
                    return self._create_fallback_response(query, "No results found")

                # Transform results to match Tavily format
                formatted_results = []
                for result in results:
                    try:
                        formatted_result = {
                            "title": result.get("title", "Untitled"),
                            "link": result.get("link", ""),
                            "content": result.get("body", ""),
                            "source": "DuckDuckGo",
                        }
                        # Only add results with content
                        if formatted_result["content"]:
                            formatted_results.append(formatted_result)
                    except Exception as e:
                        logger.warning(f"Error formatting result: {e}")
                        continue

                # Limit results to the requested max_results
                if len(formatted_results) > search_max_results:
                    logger.info(
                        f"Limiting results from {len(formatted_results)} to {search_max_results}"
                    )
                    formatted_results = formatted_results[:search_max_results]

                logger.info(
                    f"DuckDuckGo search completed successfully with {len(formatted_results)} results in {search_time:.2f}s"
                )

                return {
                    "results": formatted_results,
                    "query": query,
                    "source": "DuckDuckGo",
                    "search_time": search_time,
                    "attempts": attempt + 1,
                }

            except Exception as e:
                error_msg = str(e)
                logger.warning(
                    f"DuckDuckGo search error (attempt {attempt + 1}): {error_msg}"
                )

                # Check if error is retryable
                if not self._is_retryable_error(e):
                    logger.error(f"Non-retryable error encountered: {error_msg}")
                    return self._create_fallback_response(
                        query, f"Non-retryable error: {error_msg}"
                    )

                # If this is the last attempt, return fallback
                if attempt == self._max_retries - 1:
                    logger.error(
                        f"All {self._max_retries} retries failed for DuckDuckGo search: {error_msg}"
                    )
                    return self._create_fallback_response(
                        query, f"All retries failed: {error_msg}"
                    )

                continue

        # This should never be reached, but add explicit return for safety
        return self._create_fallback_response(query, "Unexpected end of retry loop")

    def _create_fallback_response(self, query: str, error_msg: str) -> dict[str, Any]:
        """Create a fallback response when search fails."""
        logger.info(f"Returning fallback response for query: '{query}'")
        return {
            "results": [],
            "query": query,
            "error": error_msg,
            "source": "DuckDuckGo",
            "fallback": True,
        }

    async def _arun(self, query: str, max_results: int = 10) -> dict[str, Any]:
        """Async version of the search."""
        return self._run(query, max_results)


# Create the DuckDuckGo search tool instance
DUCKDUCKGO_SEARCH_TOOL: BaseTool = DuckDuckGoSearchTool(
    max_results=settings.DUCKDUCKGO_MAX_RESULTS
)
