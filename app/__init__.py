"""Initialize app modules"""

from app.core.config import settings

try:
    from app.core.cache import cache
    from app.core.logging_utils import trace
    from app.tasks.celery_main import celery_app

    __all__ = ["cache", "celery_app", "settings", "trace"]
except ImportError:
    __all__ = ["settings"]
