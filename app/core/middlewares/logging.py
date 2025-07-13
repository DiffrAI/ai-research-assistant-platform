"""Enhanced logging middleware with request ID tracing and structured logging."""

import contextvars
import time
import uuid
from typing import Any, Dict, Optional

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import AppEnvs, settings

# Context variable to store request ID per request
request_id_ctx_var = contextvars.ContextVar("request_id", default=None)
request_start_time_ctx_var = contextvars.ContextVar("request_start_time", default=None)

# Determine the environment
APP_ENV = settings.ENVIRONMENT.lower()


def add_request_context_to_log(record: Dict[str, Any]) -> None:
    """Inject request context into log records."""
    record["extra"]["request_id"] = request_id_ctx_var.get() or "N/A"
    record["extra"]["function_id"] = record["extra"].get("function_id", "N/A")
    
    # Add request timing if available
    start_time = request_start_time_ctx_var.get()
    if start_time:
        record["extra"]["request_duration"] = time.time() - start_time


# Configure logger with context patcher
logger.configure(patcher=add_request_context_to_log)  # type: ignore

# Define enhanced log format
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level:<8}</level> | "
    "RequestID=<cyan>{extra[request_id]}</cyan> | "
    "FuncID=<magenta>{extra[function_id]}</magenta> | "
    "Duration=<yellow>{extra[request_duration]:.3f}s</yellow> | "
    "<level>{message}</level>\n"
)

# Remove default logger and add our custom configuration
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format=LOG_FORMAT,
    level=settings.LOG_LEVEL.upper(),
    enqueue=True,
    colorize=True,
    backtrace=True,
    diagnose=True,
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced middleware to log incoming HTTP requests and responses with detailed metrics."""

    def __init__(self, app, exclude_paths: Optional[list[str]] = None):
        """Initialize middleware with optional path exclusions."""
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/metrics",
            "/docs",
            "/health",
            "/openapi.json",
            "/",
            "/favicon.ico",
        ]

    def _should_skip_logging(self, path: str) -> bool:
        """Check if logging should be skipped for this path."""
        return any(path.startswith(exclude) for exclude in self.exclude_paths)

    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract comprehensive request information for logging."""
        return {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "content_type": request.headers.get("content-type", "unknown"),
            "content_length": request.headers.get("content-length", "0"),
        }

    def _extract_response_info(self, response: Response) -> Dict[str, Any]:
        """Extract response information for logging."""
        return {
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type", "unknown"),
            "content_length": response.headers.get("content-length", "0"),
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with enhanced logging."""
        # Skip logging for excluded paths
        if self._should_skip_logging(request.url.path):
            return await call_next(request)

        # Set request context
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_ctx_var.set(request_id)
        request.state.request_id = request_id

        start_time = time.time()
        request_start_time_ctx_var.set(start_time)

        # Extract request information
        request_info = self._extract_request_info(request)
        
        try:
            # Log request details in non-production environments
            if APP_ENV in {AppEnvs.DEVELOPMENT, AppEnvs.QA, AppEnvs.DEMO}:
                # Log request body if present and reasonable size
                body_bytes = await request.body()
                if body_bytes and len(body_bytes) < 1024:  # Only log small bodies
                    try:
                        body_text = body_bytes.decode("utf-8", errors="ignore").strip()
                        if body_text:
                            request_info["body"] = body_text
                    except Exception:
                        request_info["body"] = "<binary data>"

                logger.debug(
                    f"📥 Request: {request_info['method']} {request_info['path']}",
                    extra={"request_info": request_info}
                )

            # Process the request
            response = await call_next(request)

        except Exception as e:
            # Log exception with full context
            duration = time.time() - start_time
            logger.exception(
                f"❌ Error processing {request_info['method']} {request_info['path']} "
                f"(duration: {duration:.3f}s): {e!s}",
                extra={
                    "request_info": request_info,
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )
            raise

        # Calculate request duration
        duration = time.time() - start_time

        # Extract response information
        response_info = self._extract_response_info(response)

        # Attach request ID to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Request-Duration"] = f"{duration:.3f}"

        # Log response with performance metrics
        log_level = "info"
        if response.status_code >= 400:
            log_level = "warning"
        if response.status_code >= 500:
            log_level = "error"

        logger.log(
            log_level.upper(),
            f"📤 Response: {request_info['method']} {request_info['path']} → "
            f"{response.status_code} ({duration:.3f}s)",
            extra={
                "request_info": request_info,
                "response_info": response_info,
                "duration": duration,
            }
        )

        return response
