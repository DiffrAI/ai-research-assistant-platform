"""Enhanced response module for application-level API responses."""

from typing import Any, Dict, Literal, Optional

from fastapi.responses import JSONResponse


class AppJSONResponse(JSONResponse):
    """Enhanced JSON response structure for the entire application.

    This class standardizes all API responses to follow a consistent structure,
    making it easier for frontend clients and developers to interpret results.
    """

    def __init__(
        self,
        data: Any = None,
        message: str = "Success",
        status: Literal["success", "error"] = "success",
        error: Optional[str | Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
    ):
        """Initialize the AppJSONResponse with enhanced error handling.

        Args:
            data: The actual payload to return in the 'data' key
            message: A human-readable message describing the result
            status: Status of the response; typically 'success' or 'error'
            error: Optional error details, either a string or a dictionary
            error_code: Optional error code for programmatic error handling
            details: Optional additional details or metadata
            status_code: HTTP status code for the response
        """
        content = {
            "status": status,
            "message": message,
            "data": data,
        }
        
        # Add error information if present
        if error is not None:
            content["error"] = error
            
        if error_code is not None:
            content["error_code"] = error_code
            
        if details is not None:
            content["details"] = details

        super().__init__(
            content=content,
            status_code=status_code,
            media_type="application/json",
        )
