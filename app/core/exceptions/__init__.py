"""Init module for Exceptions"""

from .base import (
    AuthenticationError,
    AuthorizationError,
    CustomError,
    ErrorDetails,
    RateLimitError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    ValidationError,
)
from .handle_exception import HandleExceptions

__all__ = [
    "CustomError",
    "ValidationError", 
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "ResourceNotFoundError",
    "ServiceUnavailableError",
    "ErrorDetails",
    "HandleExceptions",
]
