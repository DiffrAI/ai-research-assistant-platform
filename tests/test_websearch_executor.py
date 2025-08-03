import pytest
from unittest.mock import MagicMock, patch

from app.workflows.graphs.websearch.components.websearch_executor import (
    WebSearchExecutor,
)


# REPLACE ALL TESTS WITH ASYNC VERSIONS
@pytest.mark.asyncio
async def test_websearch_executor_fallback_to_refined_question():
    executor = WebSearchExecutor()
    state = {
        "question": MagicMock(content="original question"),
        "refined_question": "refined question",
        # 'refined_questions' missing
    }
    async def mock_ainvoke(params):
        return {"results": [
            {
                "title": "Result",
                "link": "url",
                "content": "Some content",
                "source": "DuckDuckGo",
            }
        ]}
    with patch(
        "app.workflows.graphs.websearch.components.websearch_executor.SEARCH_TOOL"
    ) as mock_tool:
        mock_tool.ainvoke.side_effect = mock_ainvoke
        result = await executor.search(state)
        assert "search_results" in result
        assert isinstance(result["search_results"], list)
        assert result["search_results"][0]["title"] == "Result"

@pytest.mark.asyncio
async def test_websearch_executor_retry_logic():
    executor = WebSearchExecutor()
    state = {
        "question": MagicMock(content="original question"),
        "refined_question": "refined question",
    }
    # Fail twice, then succeed
    call_count = {"count": 0}

    async def flaky_ainvoke(_):
        if call_count["count"] < 2:
            call_count["count"] += 1
            raise Exception("Temporary error")
        return [
            {
                "title": "Recovered",
                "link": "url",
                "content": "Recovered content",
                "source": "DuckDuckGo",
            }
        ]

    with patch(
        "app.workflows.graphs.websearch.components.websearch_executor.SEARCH_TOOL"
    ) as mock_tool:
        mock_tool.ainvoke.side_effect = flaky_ainvoke
        result = await executor.search(state)
        assert any(r["title"] == "Recovered" for r in result["search_results"])
        assert call_count["count"] == 2

@pytest.mark.asyncio
async def test_websearch_executor_failed_queries():
    executor = WebSearchExecutor()
    state = {
        "question": MagicMock(content="original question"),
        "refined_question": "refined question",
    }
    async def always_fail(_):
        raise Exception("Always fails")
    with patch(
        "app.workflows.graphs.websearch.components.websearch_executor.SEARCH_TOOL"
    ) as mock_tool:
        mock_tool.ainvoke.side_effect = always_fail
        result = await executor.search(state)
        assert result["search_results"] == []
