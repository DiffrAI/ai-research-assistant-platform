"""Application exceptions."""

from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(HTTPException):
    """Base application exception."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ValidationError(AppException):
    """Validation error."""

    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


class AuthenticationError(AppException):
    """Authentication error."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(AppException):
    """Authorization error."""

    def __init__(self, detail: str = "Access denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundError(AppException):
    """Resource not found error."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class RateLimitError(AppException):
    """Rate limit exceeded error."""

    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class ServiceUnavailableError(AppException):
    """Service unavailable error."""

    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


def create_error_response(
    status_code: int, message: str, details: Any = None
) -> JSONResponse:
    """Create a standardized error response."""
    content = {"status": "error", "message": message, "status_code": status_code}
    if details:
        content["details"] = details

    return JSONResponse(status_code=status_code, content=content)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application exceptions with enhanced error messages."""
    logger.error(f"Application error on {request.method} {request.url.path}: {exc.detail}")
    
    # Provide specific error messages for different types
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        message = "Authentication required. Please provide a valid Bearer token."
        if "token" in exc.detail.lower():
            message = "Invalid or expired authentication token. Please login again."
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        message = "Access denied. You don't have permission to access this resource."
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        message = f"Resource not found: {exc.detail}"
    elif exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        message = "Rate limit exceeded. Please wait before making more requests."
    else:
        message = exc.detail
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "data": None,
            "message": message,
            "success": False,
            "status_code": exc.status_code,
            "endpoint": f"{request.method} {request.url.path}"
        }
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation exceptions with detailed parameter information."""
    logger.error(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
    
    # Create user-friendly error messages
    error_details = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_type = error["type"]
        
        # Create more descriptive error messages
        if error_type == "missing":
            user_message = f"Required parameter '{field}' is missing"
        elif error_type == "type_error":
            user_message = f"Parameter '{field}' has invalid type: {message}"
        elif error_type == "value_error":
            user_message = f"Parameter '{field}' has invalid value: {message}"
        else:
            user_message = f"Parameter '{field}': {message}"
        
        error_details.append({
            "field": field,
            "message": user_message,
            "type": error_type,
            "input": error.get("input")
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "data": None,
            "message": "Request validation failed. Please check the required parameters.",
            "success": False,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "errors": error_details,
            "endpoint": f"{request.method} {request.url.path}"
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions with consistent error format."""
    logger.exception(f"Unexpected error on {request.method} {request.url.path}: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "data": None,
            "message": "An unexpected error occurred. Please try again later.",
            "success": False,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "endpoint": f"{request.method} {request.url.path}"
        }
    )
