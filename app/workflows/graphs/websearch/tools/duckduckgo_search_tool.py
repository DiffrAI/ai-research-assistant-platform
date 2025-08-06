"""DuckDuckGo search tool for websearch."""

import asyncio
import random
import time
from typing import Any, Optional
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup
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
        self.base_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # Store retry settings as instance variables (not Pydantic fields)
        self._max_retries = settings.SEARCH_MAX_RETRIES
        self._base_delay = settings.SEARCH_BASE_DELAY
        self._max_delay = settings.SEARCH_MAX_DELAY

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

        # Ensure max_results is an integer
        try:
            search_max_results = int(search_max_results)
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid max_results value: {search_max_results}, using default: {self.max_results}"
            )
            search_max_results = self.max_results

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
                
                # Use httpx for the search
                with httpx.Client(timeout=30.0) as client:
                    params = {
                        "q": query,
                        "kl": "wt-wt",
                    }
                    
                    response = client.get(
                        self.base_url, 
                        params=params, 
                        headers=self.headers,
                        follow_redirects=True
                    )
                    response.raise_for_status()

                    # Parse the HTML response
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = self._parse_results(soup, search_max_results)
                
                search_time = time.time() - start_time
                logger.info(f"DuckDuckGo returned {len(results)} results")

                # Validate results
                if not results:
                    logger.warning(
                        f"No results returned for query: '{query}' (attempt {attempt + 1})"
                    )
                    if attempt < self._max_retries - 1:
                        continue
                    return self._create_fallback_response(query, "No results found")

                logger.info(
                    f"DuckDuckGo search completed successfully with {len(results)} results in {search_time:.2f}s"
                )

                return {
                    "results": results,
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

    def _parse_results(self, soup: BeautifulSoup, max_results: int) -> list[dict[str, Any]]:
        """Parse search results from HTML."""
        results = []
        
        # Find result containers
        result_containers = soup.find_all('div', class_='result')
        
        for container in result_containers[:max_results]:
            try:
                # Extract title and link
                title_elem = container.find('a', class_='result__a')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                
                # Extract snippet
                snippet_elem = container.find('a', class_='result__snippet')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                # Clean up the link (DuckDuckGo sometimes uses redirect URLs)
                if link.startswith('/l/?uddg='):
                    # Extract the actual URL from DuckDuckGo's redirect
                    import urllib.parse
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
                    if 'uddg' in parsed:
                        link = urllib.parse.unquote(parsed['uddg'][0])
                
                if title and link and snippet:
                    results.append({
                        "title": title,
                        "link": link,
                        "content": snippet,
                        "source": "DuckDuckGo",
                    })
                    
            except Exception as e:
                logger.warning(f"Error parsing search result: {e}")
                continue
                
        return results

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
