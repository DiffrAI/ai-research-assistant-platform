from unittest.mock import MagicMock, patch


# Patch ChatOpenAI at import time for all tests
@patch("app.workflows.graphs.websearch.local_model_client.ChatOpenAI")
def test_local_model_client_success(mock_chat_openai):
    mock_instance = MagicMock()
    mock_instance.invoke.return_value = MagicMock(content="Hello!")
    mock_chat_openai.return_value = mock_instance
    from app.workflows.graphs.websearch.local_model_client import LocalModelClient
    client = LocalModelClient()
    result = client.invoke([{"role": "user", "content": "Hi"}])
    assert "Hello" in result

@patch("app.workflows.graphs.websearch.local_model_client.ChatOpenAI")
def test_local_model_client_error(mock_chat_openai):
    mock_instance = MagicMock()
    mock_instance.invoke.side_effect = Exception("Ollama error")
    mock_chat_openai.return_value = mock_instance
    from app.workflows.graphs.websearch.local_model_client import LocalModelClient
    client = LocalModelClient()
    result = client.invoke([{"role": "user", "content": "Hi"}])
    assert "I apologize" in result or "error" in result.lower()

@patch("app.workflows.graphs.websearch.local_model_client.settings")
@patch("app.workflows.graphs.websearch.local_model_client.ChatOpenAI")
def test_local_model_client_uses_model_name_from_config(mock_chat_openai, mock_settings):
    mock_settings.LOCAL_MODEL_URL = "http://localhost:11434"
    mock_settings.LOCAL_MODEL_NAME = "qwen2.5:7b"
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance
    from app.workflows.graphs.websearch.local_model_client import LocalModelClient
    client = LocalModelClient()
    assert client.model_name == "qwen2.5:7b"
