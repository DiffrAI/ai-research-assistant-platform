"""Essential utility functions."""

import hashlib
import json
import re
from typing import Any
from urllib.parse import urlparse


def generate_cache_key(*args: Any, **kwargs: Any) -> str:
    """Generate a consistent cache key from arguments."""
    sorted_kwargs = sorted(kwargs.items())
    data = (args, sorted_kwargs)
    return hashlib.sha256(
        json.dumps(data, default=str, sort_keys=True).encode()
    ).hexdigest()


def sanitize_url(url: str) -> str:
    """Sanitize and validate URL."""
    if not url:
        return ""
    
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        parsed = urlparse(url)
        if parsed.scheme and parsed.netloc:
            return url
    except Exception:
        pass
    
    return ""


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace and control characters
    text = re.sub(r"\s+", " ", text.strip())
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    
    return text


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))