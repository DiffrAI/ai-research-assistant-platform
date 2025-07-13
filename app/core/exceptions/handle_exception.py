"""Enhanced exception handling for the FastAPI application."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from loguru import logger

from app.constants import messages
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    CustomError,
    RateLimitError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    ValidationError,
)
from app.core.responses import AppJSONResponse


class HandleExceptions:
    """Enhanced exception handler with specific error types and better logging."""

    def __init__(self, app: FastAPI) -> None:
        """Initialize exception handling with all error types."""
        self.app = app
        self._register_exception_handlers()

    def _register_exception_handlers(self) -> None:
        """Register all exception handlers."""
        self._handle_custom_exceptions()
        self._handle_pydantic_exception()
        self._handle_fastapi_http_exception()
        self._handle_default_exception()

    def _handle_custom_exceptions(self) -> None:
        """Handle all custom exception types."""

        @self.app.exception_handler(CustomError)
        async def custom_exception_handler(request: Request, exc: CustomError) -> AppJSONResponse:
            logger.error(f"Custom error: {exc.error_code} - {exc.message}", extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "details": exc.details,
                "path": request.url.path,
                "method": request.method,
            })
            return await self._create_json_response(
                status_code=exc.status_code,
                message=exc.message,
                payload=exc.payload,
                error_log=exc.error_log,
                error_code=exc.error_code,
                details=exc.details,
            )

        @self.app.exception_handler(ValidationError)
        async def validation_exception_handler(request: Request, exc: ValidationError) -> AppJSONResponse:
            logger.warning(f"Validation error: {exc.message}", extra={
                "field": exc.details.get("field"),
                "path": request.url.path,
                "method": request.method,
            })
            return await self._create_json_response(
                status_code=exc.status_code,
                message=exc.message,
                error_code=exc.error_code,
                details=exc.details,
            )

        @self.app.exception_handler(AuthenticationError)
        async def authentication_exception_handler(request: Request, exc: AuthenticationError) -> AppJSONResponse:
            logger.warning(f"Authentication error: {exc.message}", extra={
                "path": request.url.path,
                "method": request.method,
            })
            return await self._create_json_response(
                status_code=exc.status_code,
                message=exc.message,
                error_code=exc.error_code,
            )

        @self.app.exception_handler(AuthorizationError)
        async def authorization_exception_handler(request: Request, exc: AuthorizationError) -> AppJSONResponse:
            logger.warning(f"Authorization error: {exc.message}", extra={
                "path": request.url.path,
                "method": request.method,
            })
            return await self._create_json_response(
                status_code=exc.status_code,
                message=exc.message,
                error_code=exc.error_code,
            )

        @self.app.exception_handler(RateLimitError)
        async def rate_limit_exception_handler(request: Request, exc: RateLimitError) -> AppJSONResponse:
            logger.warning(f"Rate limit exceeded: {exc.message}", extra={
                "retry_after": exc.details.get("retry_after"),
                "path": request.url.path,
                "method": request.method,
            })
            return await self._create_json_response(
                status_code=exc.status_code,
                message=exc.message,
                error_code=exc.error_code,
                details=exc.details,
            )

        @self.app.exception_handler(ResourceNotFoundError)
        async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFoundError) -> AppJSONResponse:
            logger.info(f"Resource not found: {exc.message}", extra={
                "resource_type": exc.details.get("resource_type"),
                "path": request.url.path,
                "method": request.method,
            })
            return await self._create_json_response(
                status_code=exc.status_code,
                message=exc.message,
                error_code=exc.error_code,
                details=exc.details,
            )

        @self.app.exception_handler(ServiceUnavailableError)
        async def service_unavailable_exception_handler(request: Request, exc: ServiceUnavailableError) -> AppJSONResponse:
            logger.error(f"Service unavailable: {exc.message}", extra={
                "service": exc.details.get("service"),
                "path": request.url.path,
                "method": request.method,
            })
            return await self._create_json_response(
                status_code=exc.status_code,
                message=exc.message,
                error_code=exc.error_code,
                details=exc.details,
            )

    def _handle_pydantic_exception(self) -> None:
        """Handle Pydantic validation errors with detailed field information."""

        @self.app.exception_handler(RequestValidationError)
        async def pydantic_exception_handler(request: Request, exc: RequestValidationError) -> AppJSONResponse:
            # Extract field-specific errors
            field_errors = {}
            for error in exc.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                field_errors[field] = error["msg"]

            logger.warning(f"Pydantic validation error: {len(field_errors)} field(s) failed", extra={
                "field_errors": field_errors,
                "path": request.url.path,
                "method": request.method,
            })

            return await self._create_json_response(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                message=messages.PYDANTIC_VALIDATION_ERROR,
                error_code="VALIDATION_ERROR",
                error_log=exc.errors(),
                details={"field_errors": field_errors},
            )

    def _handle_fastapi_http_exception(self) -> None:
        """Handle FastAPI HTTP exceptions with rate limit support."""

        @self.app.exception_handler(HTTPException)
        async def fastapi_http_exception_handler(request: Request, exc: HTTPException) -> AppJSONResponse:
            if exc.status_code == 429:
                headers = getattr(exc, "headers", {})
                retry_after = int(headers.get("Retry-After", 60))

                logger.warning(f"Rate limit exceeded: retry after {retry_after}s", extra={
                    "retry_after": retry_after,
                    "path": request.url.path,
                    "method": request.method,
                })

                return await self._create_json_response(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    message=messages.RATE_LIMIT_ERROR.format(retry_after=retry_after),
                    error_code="RATE_LIMIT_ERROR",
                    error_log=str(exc),
                    details={"retry_after": retry_after},
                )

            logger.info(f"HTTP exception: {exc.status_code} - {exc.detail}", extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
            })

            return await self._create_json_response(
                status_code=exc.status_code,
                message=exc.detail,
                error_code=f"HTTP_{exc.status_code}",
            )

    def _handle_default_exception(self) -> None:
        """Handle all other exceptions with comprehensive logging."""

        @self.app.exception_handler(Exception)
        async def default_exception_handler(request: Request, exc: Exception) -> AppJSONResponse:
            logger.exception(f"Unhandled exception: {type(exc).__name__}: {exc}", extra={
                "exception_type": type(exc).__name__,
                "path": request.url.path,
                "method": request.method,
            })

            return await self._create_json_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=messages.INTERNAL_SERVER_ERROR,
                error_code="INTERNAL_SERVER_ERROR",
                error_log=str(exc),
            )

    async def _create_json_response(
        self,
        status_code: int,
        message: str,
        payload: Any = None,
        error_log: Any = None,
        error_code: str = "ERROR",
        details: dict = None,
    ) -> AppJSONResponse:
        """Create a JSON response for exceptions with enhanced error information."""
        if error_log:
            logger.error(f"Error details: {error_log}")

        return AppJSONResponse(
            data=payload,
            message=message,
            status_code=status_code,
            error=error_log,
            error_code=error_code,
            details=details,
        )
