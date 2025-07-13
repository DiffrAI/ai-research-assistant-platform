"""Utility functions for the application."""

import hashlib
import json
import re
import time
from typing import Any, Dict, List, Optional, TypeVar
from urllib.parse import urlparse

from loguru import logger

T = TypeVar('T')


def generate_cache_key(*args: Any, **kwargs: Any) -> str:
    """Generate a consistent cache key from arguments."""
    # Sort kwargs to ensure consistent hashing
    sorted_kwargs = sorted(kwargs.items())
    data = (args, sorted_kwargs)
    return hashlib.sha256(json.dumps(data, default=str, sort_keys=True).encode()).hexdigest()


def sanitize_url(url: str) -> str:
    """Sanitize and validate URL."""
    if not url:
        return ""
    
    # Remove whitespace
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
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


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix."""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text


def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: tuple = (Exception,),
    logger_instance: Optional[Any] = None
) -> T:
    """Retry function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exceptions: Tuple of exceptions to catch and retry
        logger_instance: Logger instance to use (defaults to loguru logger)
    
    Returns:
        Result of the function call
    
    Raises:
        Last exception if all retries fail
    """
    log = logger_instance or logger
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt), max_delay)
                jitter = time.time() % 0.1 * delay
                total_delay = delay + jitter
                
                log.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {total_delay:.2f}s...")
                time.sleep(total_delay)
            else:
                log.error(f"All {max_retries} attempts failed. Last error: {e}")
    
    raise last_exception


def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength and return detailed feedback."""
    if not password:
        return {"valid": False, "errors": ["Password cannot be empty"]}
    
    errors = []
    warnings = []
    
    # Check minimum length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    elif len(password) < 12:
        warnings.append("Consider using a longer password (12+ characters)")
    
    # Check for different character types
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    if not has_lower:
        errors.append("Password must contain at least one lowercase letter")
    if not has_upper:
        errors.append("Password must contain at least one uppercase letter")
    if not has_digit:
        errors.append("Password must contain at least one digit")
    if not has_special:
        warnings.append("Consider adding special characters for better security")
    
    # Check for common patterns
    if re.search(r'(.)\1{2,}', password):
        warnings.append("Avoid repeated characters")
    
    if re.search(r'(123|abc|qwe)', password.lower()):
        warnings.append("Avoid common patterns")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "score": _calculate_password_score(password, has_lower, has_upper, has_digit, has_special)
    }


def _calculate_password_score(password: str, has_lower: bool, has_upper: bool, has_digit: bool, has_special: bool) -> int:
    """Calculate password strength score (0-100)."""
    score = 0
    
    # Length contribution
    score += min(len(password) * 4, 40)
    
    # Character type contribution
    score += sum([has_lower, has_upper, has_digit, has_special]) * 10
    
    # Complexity bonus
    if len(set(password)) > len(password) * 0.7:
        score += 10
    
    return min(score, 100)


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely parse JSON string with fallback."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries, with later dicts taking precedence."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get nested value from dictionary using dot notation."""
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> None:
    """Set nested value in dictionary using dot notation."""
    keys = path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value 