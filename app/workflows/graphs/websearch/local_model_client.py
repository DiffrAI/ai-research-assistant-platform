"""Enhanced local model client for Ollama integration with robust error handling."""

import json
import re
import time
from typing import Any, Dict, List, Optional, Type, TypeVar, cast

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, SecretStr, ValidationError

from app import settings
from app.core.exceptions import ServiceUnavailableError

T = TypeVar("T", bound=BaseModel)


class LocalModelClient:
    """Enhanced client for interacting with local Ollama model with robust error handling."""

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """Initialize the local model client.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
        """
        self.model_name = settings.LOCAL_MODEL_NAME
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        logger.info(
            f"Initializing LocalModelClient with URL: {settings.LOCAL_MODEL_URL}/v1"
        )
        logger.info(f"Using model: {self.model_name}")

        self.client = ChatOpenAI(
            base_url=settings.LOCAL_MODEL_URL + "/v1",
            api_key=SecretStr("not-needed"),  # Ollama doesn't require API key
            model=self.model_name,
            temperature=settings.local_model.temperature,
            timeout=settings.local_model.timeout,
        )

    def _exponential_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        delay = min(self.retry_delay * (2**attempt), 10.0)
        jitter = time.time() % 0.1 * delay
        return delay + jitter

    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable."""
        error_str = str(error).lower()
        retryable_patterns = [
            "timeout",
            "connection",
            "network",
            "temporary",
            "service unavailable",
            "gateway",
            "bad gateway",
            "internal server error",
            "rate limit",
        ]
        return any(pattern in error_str for pattern in retryable_patterns)

    def invoke(self, messages: List[BaseMessage]) -> str:
        """Invoke the local model with messages and retry logic."""
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"Invoking local model (attempt {attempt + 1}/{self.max_retries})"
                )

                # Add delay between retries
                if attempt > 0:
                    delay = self._exponential_backoff_delay(attempt)
                    logger.debug(f"Waiting {delay:.2f}s before retry {attempt + 1}")
                    time.sleep(delay)

                response = self.client.invoke(messages)
                content = str(response.content)  # Ensure content is string

                if not content or content.strip() == "":
                    logger.warning("Empty response from local model")
                    return "I apologize, but I received an empty response. Please try again."

                logger.debug(f"Local model response received (length: {len(content)})")
                return content

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Local model invocation error (attempt {attempt + 1}): {e}"
                )

                if not self._is_retryable_error(e):
                    logger.error(f"Non-retryable error encountered: {e}")
                    break

                if attempt == self.max_retries - 1:
                    logger.error(
                        f"All {self.max_retries} retries failed for local model"
                    )
                    break

        # If we get here, all retries failed
        error_msg = f"Failed to invoke local model after {self.max_retries} attempts"
        if last_error:
            error_msg += f": {last_error}"

        logger.error(error_msg)
        raise ServiceUnavailableError(
            message="Local model is currently unavailable",
            service="ollama",
            details={"model": self.model_name, "attempts": self.max_retries},
        )

    def invoke_with_structured_output(
        self, messages: List[BaseMessage], schema: Type[T]
    ) -> T:
        """Invoke the local model with structured output parsing."""
        try:
            # Get raw response
            content = self.invoke(messages)

            # Parse structured response
            return self._parse_structured_response(content, schema)

        except Exception as e:
            logger.error(f"Error in structured output invocation: {e}")
            # Return default instance
            return schema.model_validate({})

    def _parse_structured_response(self, content: str, schema: Type[T]) -> T:
        """Parse the model response to extract structured data with multiple strategies."""
        content = content.strip()

        # Strategy 1: Try to extract JSON directly
        try:
            # Look for JSON object in the response
            json_match = re.search(
                r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content, re.DOTALL
            )
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.debug(f"JSON parsing failed: {e}")

        # Strategy 2: Try to extract key-value pairs
        try:
            data = self._extract_key_value_pairs(content, schema)
            if data:
                return schema.model_validate(data)
        except ValidationError as e:
            logger.debug(f"Key-value extraction failed: {e}")

        # Strategy 3: Try to extract from markdown-like format
        try:
            data = self._extract_from_markdown(content, schema)
            if data:
                return schema.model_validate(data)
        except ValidationError as e:
            logger.debug(f"Markdown extraction failed: {e}")

        # Strategy 4: Fallback - try to infer from content
        try:
            data = self._infer_from_content(content, schema)
            return schema.model_validate(data)
        except ValidationError as e:
            logger.warning(f"All structured parsing strategies failed: {e}")
            return schema.model_validate({})

    def _extract_key_value_pairs(self, content: str, schema: Type[T]) -> Dict[str, Any]:
        """Extract key-value pairs from text content."""
        data: Dict[str, Any] = {}
        schema_fields = list(schema.model_fields.keys())

        # Look for patterns like "key: value" or "key = value"
        for field in schema_fields:
            patterns = [
                rf"{field}:\s*([^\n]+)",
                rf"{field}\s*=\s*([^\n]+)",
                rf'"{field}":\s*("[^"]+")',
                rf'"{field}":\s*([^,\s\}}]+)',
            ]

            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Try to convert to appropriate type
                    try:
                        field_type = schema.model_fields[field].annotation
                        if field_type is bool:
                            data[field] = cast(
                                Any, bool(value.lower() in ("true", "yes", "1"))
                            )
                        elif field_type is int:
                            data[field] = cast(Any, int(value))
                        elif field_type is float:
                            data[field] = cast(Any, float(value))
                        else:
                            data[field] = cast(Any, value)
                    except (ValueError, TypeError):
                        data[field] = value
                    break

        return data

    def _extract_from_markdown(self, content: str, schema: Type[T]) -> Dict[str, Any]:
        """Extract structured data from markdown-like format."""
        data: Dict[str, Any] = {}
        schema_fields = list(schema.model_fields.keys())

        # Look for markdown headers and lists
        lines = content.split("\n")
        current_field = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for headers
            for field in schema_fields:
                if re.match(rf"^#+\s*{field}", line, re.IGNORECASE):
                    current_field = field
                    break

            # Check for list items
            if current_field and line.startswith(("-", "*", "•")):
                value = line[1:].strip()
                if current_field not in data:
                    data[current_field] = []
                data[current_field].append(value)

            # Check for key-value in line
            for field in schema_fields:
                if f"{field}:" in line.lower():
                    value = line.split(":", 1)[1].strip()
                    data[field] = value
                    break

        return data

    def _infer_from_content(self, content: str, schema: Type[T]) -> Dict[str, Any]:
        """Infer structured data from content using heuristics."""
        data: Dict[str, Any] = {}
        schema_fields = list(schema.model_fields.keys())

        # Simple heuristics based on content
        content_lower = content.lower()

        for field in schema_fields:
            # Look for field mentions in content
            if field.lower() in content_lower:
                # Extract surrounding text as value
                field_index = content_lower.find(field.lower())
                start = max(0, field_index - 50)
                end = min(len(content), field_index + len(field) + 50)
                context = content[start:end]

                # Try to extract value from context
                value_match = re.search(
                    rf"{field.lower()}[:\s]+([^\n,;]+)", context, re.IGNORECASE
                )
                if value_match:
                    data[field] = value_match.group(1).strip()

        return data
