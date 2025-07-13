"""Defines custom exceptions for detailed error handling."""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class ErrorDetails(BaseModel):
    """Structured error details for better error handling."""
    
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class CustomError(Exception):
    """Custom exception with detailed attributes and structured error handling."""

    def __init__(
        self,
        message: str,
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        payload: Optional[Any] = None,
        error_log: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.payload = payload
        self.error_log = error_log
        self.details = details or {}

    def __str__(self) -> str:
        return (
            f"CustomError: {self.message} (Status: {self.status_code}, "
            f"Code: {self.error_code}, Details: {self.details})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the exception."""
        return {
            "message": self.message,
            "status_code": self.status_code,
            "error_code": self.error_code,
            "payload": self.payload,
            "error_log": self.error_log,
            "details": self.details,
        }

    def to_error_details(self) -> ErrorDetails:
        """Convert to structured error details."""
        return ErrorDetails(
            code=self.error_code,
            message=self.message,
            details=self.details,
        )


class ValidationError(CustomError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"field": field} if field else {},
            **kwargs
        )


class AuthenticationError(CustomError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            **kwargs
        )


class AuthorizationError(CustomError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            **kwargs
        )


class RateLimitError(CustomError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            **kwargs
        )


class ResourceNotFoundError(CustomError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found", resource_type: Optional[str] = None, **kwargs):
        details = {"resource_type": resource_type} if resource_type else {}
        super().__init__(
            message=message,
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            details=details,
            **kwargs
        )


class ServiceUnavailableError(CustomError):
    """Raised when an external service is unavailable."""
    
    def __init__(self, message: str = "Service temporarily unavailable", service: Optional[str] = None, **kwargs):
        details = {"service": service} if service else {}
        super().__init__(
            message=message,
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
            details=details,
            **kwargs
        )
