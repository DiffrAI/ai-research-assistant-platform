"""Response utilities."""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import status
from fastapi.responses import JSONResponse, StreamingResponse


def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def create_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK,
    **kwargs
) -> JSONResponse:
    """Create a standardized JSON response."""
    content = {
        "status": "success",
        "message": message,
        "status_code": status_code
    }
    
    if data is not None:
        content["data"] = data
    
    content.update(kwargs)
    
    # Convert to JSON string first to handle datetime objects
    json_content = json.loads(json.dumps(content, default=json_serializer))
    
    return JSONResponse(status_code=status_code, content=json_content)


def create_streaming_response(
    content,
    media_type: str = "text/plain",
    headers: Optional[Dict[str, str]] = None
) -> StreamingResponse:
    """Create a streaming response."""
    return StreamingResponse(
        content,
        media_type=media_type,
        headers=headers or {}
    )