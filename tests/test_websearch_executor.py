from unittest.mock import MagicMock, patch

from app.workflows.graphs.websearch.components.websearch_executor import (
    WebSearchExecutor,
)


def test_websearch_executor_fallback_to_refined_question():
    executor = WebSearchExecutor()
    state = {
        "question": MagicMock(content="original question"),
        "refined_question": "refined question",
        # 'refined_questions' missing
    }
    with patch(
        "app.workflows.graphs.websearch.components.websearch_executor.SEARCH_TOOL"
    ) as mock_tool:
        mock_tool.invoke.return_value = [
            {
                "title": "Result",
                "link": "url",
                "content": "Some content",
                "source": "DuckDuckGo",
            }
        ]
        result = executor.search(state)
        assert "search_results" in result
        assert isinstance(result["search_results"], list)
        assert result["search_results"][0]["title"] == "Result"


def test_websearch_executor_retry_logic():
    executor = WebSearchExecutor()
    state = {
        "question": MagicMock(content="original question"),
        "refined_question": "refined question",
    }
    # Fail twice, then succeed
    call_count = {"count": 0}

    def flaky_invoke(_):
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
        mock_tool.invoke.side_effect = flaky_invoke
        result = executor.search(state)
        assert any(r["title"] == "Recovered" for r in result["search_results"])
        assert call_count["count"] == 2


def test_websearch_executor_failed_queries():
    executor = WebSearchExecutor()
    state = {
        "question": MagicMock(content="original question"),
        "refined_question": "refined question",
    }
    with patch(
        "app.workflows.graphs.websearch.components.websearch_executor.SEARCH_TOOL"
    ) as mock_tool:
        mock_tool.invoke.side_effect = Exception("Always fails")
        result = executor.search(state)
        assert result["search_results"] == []
