"""Web search component that retrieves search results for enhanced or rephrased questions."""

import random
import time
from typing import Any

from loguru import logger

from app import settings
from app.workflows.graphs.websearch.states import AgentState
from app.workflows.graphs.websearch.tools import SEARCH_TOOL


class WebSearchExecutor:
    """Agent component responsible for executing web searches based on refined or enhanced questions."""

    def __init__(self):
        self.max_results = 10
        # Store retry settings as instance variables
        self._max_retries = settings.SEARCH_MAX_RETRIES
        self._base_delay = settings.SEARCH_BASE_DELAY

    def _exponential_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        delay = min(self._base_delay * (2 ** attempt), settings.SEARCH_MAX_DELAY)
        jitter = random.uniform(0, 0.1 * delay)
        return delay + jitter

    def search(self, state: AgentState) -> dict[str, list[dict[str, Any]]]:
        """Executes web search queries using available questions in the state with robust error handling.
        """
        # Handle both enhanced questions (from question_enhancer) and single refined question (from question_rewriter)
        questions = []

        # Check for refined_questions first (from question_enhancer)
        if "refined_questions" in state and state["refined_questions"]:
            questions = state["refined_questions"]
        # Fallback to refined_question (from question_rewriter)
        elif "refined_question" in state and state["refined_question"]:
            questions = [state["refined_question"]]
        # Final fallback to original question
        elif "question" in state and state["question"] and hasattr(state["question"], "content"):
            questions = [state["question"].content]
        else:
            logger.warning("No questions available for web search")
            return {"search_results": []}

        results = []
        failed_queries = []

        for query in questions:
            if not query or not query.strip():
                logger.warning("Skipping empty query")
                continue

            logger.info(f"Performing web search for: '{query}'")

            # Try multiple times for each query
            for attempt in range(self._max_retries):
                try:
                    # Add delay between retries
                    if attempt > 0:
                        delay = self._exponential_backoff_delay(attempt)
                        logger.info(f"Retrying search for '{query}' (attempt {attempt + 1}/{self._max_retries}) after {delay:.2f}s")
                        time.sleep(delay)

                    # Invoke the search tool
                    search_response = SEARCH_TOOL.invoke({"query": query})

                    # Handle different response formats
                    if isinstance(search_response, dict):
                        if "error" in search_response:
                            logger.warning(f"Search tool returned error for '{query}': {search_response['error']}")
                            if attempt < self._max_retries - 1:
                                continue
                            failed_queries.append(query)
                            break

                        search_results = search_response.get("results", [])
                    else:
                        # Handle case where tool returns results directly
                        search_results = search_response if isinstance(search_response, list) else []

                    # Process each result
                    query_results = []
                    for item in search_results:
                        if isinstance(item, dict):
                            try:
                                # Ensure we have the required fields
                                processed_item = {
                                    "title": item.get("title", "Untitled"),
                                    "link": item.get("link", ""),
                                    "content": item.get("content", item.get("body", "")),
                                    "source": item.get("source", "Unknown"),
                                }
                                # Only add if we have content
                                if processed_item["content"]:
                                    query_results.append(processed_item)
                            except Exception as e:
                                logger.warning(f"Error processing search result: {e}")
                                continue

                    logger.info(f"Successfully processed {len(query_results)} results for query: '{query}'")
                    results.extend(query_results)
                    break  # Success, exit retry loop

                except Exception as e:
                    error_msg = str(e)
                    logger.warning(f"Error during web search for query '{query}' (attempt {attempt + 1}): {error_msg}")

                    if attempt == self._max_retries - 1:
                        logger.error(f"All retries failed for query '{query}': {error_msg}")
                        failed_queries.append(query)
                    continue

        # Log summary
        total_queries = len(questions)
        successful_queries = total_queries - len(failed_queries)
        logger.info(f"Web search completed: {successful_queries}/{total_queries} queries successful, {len(results)} total results")

        if failed_queries:
            logger.warning(f"Failed queries: {failed_queries}")

        return {"search_results": results}
