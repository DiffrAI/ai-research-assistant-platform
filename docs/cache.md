# 🧠 Flexible Caching with aiocache

This project supports both **Redis** and **in-memory** caching backends via `aiocache`. It enables request-level caching, background task result storage, and general performance boosts with minimal effort.

---

## ✅ Features

* 🔄 **Pluggable cache backend** (Redis or in-memory)
* 📦 **JSON serialization**
* 🕒 **TTL (Time-to-Live)** support
* 🧱 **Namespace isolation**
* 🔐 **Password-protected Redis support**
* ⚡ Fully async + compatible with FastAPI

---

## ⚙️ Configuration

Caching is configured in `app/core/cache/cache.py` using the `CacheBackend` enum:

```python
"""Simple cache setup using aiocache with support for Redis and in-memory backends."""

from aiocache import Cache
from aiocache.serializers import JsonSerializer

from app.core.config import settings
from app.core.enums import CacheBackend

if settings.CACHE_BACKEND == CacheBackend.REDIS:
    cache = Cache(
        cache_class=Cache.REDIS,  # type: ignore
        endpoint=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        ttl=300,
        namespace="fastapi_cache",
        serializer=JsonSerializer(),
        db=1,
    )
elif settings.CACHE_BACKEND == CacheBackend.LOCAL:
    cache = Cache(
        cache_class=Cache.MEMORY,
        ttl=300,
        namespace="fastapi_cache",
        serializer=JsonSerializer(),
    )
else:
    raise ValueError(f"Unsupported cache backend: {settings.CACHE_BACKEND}")
```

---

## 🧾 .env Configuration

Make sure to set up the `.env` file accordingly:

```env
# General Cache Backend
CACHE_BACKEND=redis  # or "local"

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=yourpassword
```

---

## 🧪 Usage Examples

### Basic Caching

```python
from app.core.cache.cache import cache

@router.get("/cached")
async def get_cached_response():
    result = await cache.get("my_cache_key")
    if result:
        return {"cached": True, "data": result}

    result = expensive_function()
    await cache.set("my_cache_key", result)
    return {"cached": False, "data": result}
```

### Research Result Caching

```python
from app.core.cache.cache import cache
import hashlib
import json

class ResearchService:
    @staticmethod
    def _hash_request(payload: dict) -> str:
        """Generate a unique cache key from request payload."""
        sorted_payload = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(sorted_payload.encode()).hexdigest()

    async def conduct_research(self, request: ResearchRequest) -> ResearchResponse:
        # Check cache first
        cache_key = self._hash_request(request.model_dump())
        cached_response = await cache.get(cache_key)
        
        if cached_response:
            logger.info("Cache hit for research query")
            return ResearchResponse.model_validate(json.loads(cached_response))

        # Perform expensive research
        result = await self._perform_research(request)
        
        # Cache the result
        await cache.set(cache_key, result.model_dump_json())
        
        return result
```

### User Session Caching

```python
from app.core.cache.cache import cache

class AuthService:
    async def get_cached_user(self, user_id: int) -> User | None:
        cache_key = f"user:{user_id}"
        cached_user = await cache.get(cache_key)
        
        if cached_user:
            return User.model_validate(cached_user)
        
        # Fetch from database
        user = await self._get_user_from_db(user_id)
        if user:
            await cache.set(cache_key, user.model_dump(), ttl=3600)  # 1 hour
        
        return user

    async def invalidate_user_cache(self, user_id: int):
        """Invalidate user cache when user data changes."""
        cache_key = f"user:{user_id}"
        await cache.delete(cache_key)
```

### API Response Caching

```python
from app.core.cache.cache import cache
from fastapi import Depends

async def get_cached_api_response(
    endpoint: str,
    params: dict,
    ttl: int = 300
) -> dict:
    """Cache API responses with configurable TTL."""
    cache_key = f"api:{endpoint}:{hash(str(params))}"
    
    cached_response = await cache.get(cache_key)
    if cached_response:
        return cached_response
    
    # Make API call
    response = await make_api_call(endpoint, params)
    
    # Cache response
    await cache.set(cache_key, response, ttl=ttl)
    
    return response
```

### Background Task Result Caching

```python
from app.core.cache.cache import cache
from celery import shared_task

@shared_task
async def process_large_dataset(dataset_id: str):
    """Process large dataset and cache results."""
    cache_key = f"dataset:{dataset_id}"
    
    # Check if already processed
    cached_result = await cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Process dataset
    result = await expensive_processing(dataset_id)
    
    # Cache for 24 hours
    await cache.set(cache_key, result, ttl=86400)
    
    return result
```

### Cache Invalidation Patterns

```python
from app.core.cache.cache import cache

class CacheManager:
    @staticmethod
    async def invalidate_user_related_cache(user_id: int):
        """Invalidate all cache entries related to a user."""
        patterns = [
            f"user:{user_id}",
            f"user_subscription:{user_id}",
            f"user_research:{user_id}:*"
        ]
        
        for pattern in patterns:
            await cache.delete_pattern(pattern)
    
    @staticmethod
    async def invalidate_research_cache(query_hash: str):
        """Invalidate specific research cache entry."""
        cache_key = f"research:{query_hash}"
        await cache.delete(cache_key)
    
    @staticmethod
    async def clear_all_cache():
        """Clear all cache (use with caution)."""
        await cache.clear()
```

### Cache Statistics and Monitoring

```python
from app.core.cache.cache import cache

class CacheMonitor:
    @staticmethod
    async def get_cache_stats() -> dict:
        """Get cache statistics for monitoring."""
        try:
            # Get cache info (Redis only)
            if hasattr(cache, 'redis'):
                info = await cache.redis.info()
                return {
                    "total_connections_received": info.get("total_connections_received", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "used_memory_human": info.get("used_memory_human", "0B"),
                    "connected_clients": info.get("connected_clients", 0)
                }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def get_cache_hit_rate() -> float:
        """Calculate cache hit rate."""
        stats = await CacheMonitor.get_cache_stats()
        
        hits = stats.get("keyspace_hits", 0)
        misses = stats.get("keyspace_misses", 0)
        total = hits + misses
        
        return (hits / total * 100) if total > 0 else 0.0
```

---

## 🔐 Security Best Practices

* Enable **password authentication** on production Redis servers
* Use **namespaces** to isolate cache domains
* Normalize or hash cache keys to prevent brute-force key flooding:
  ```python
  import hashlib

  def hashed_key(raw_key: str) -> str:
      return hashlib.sha256(raw_key.encode()).hexdigest()
  ```

---

## 🐳 Docker Redis Setup

The project includes Redis and RedisInsight for local development in `docker-compose.yml`:

| Service      | URL                                            | Port |
| ------------ | ---------------------------------------------- | ---- |
| Redis        | redis://localhost:6379                         | 6379 |
| RedisInsight | [http://localhost:8001](http://localhost:8001) | 8001 |

---

## 🧠 Best Practices

### Cache Key Design
```python
# Good: Descriptive, namespaced keys
"user:123:profile"
"research:abc123:results"
"subscription:456:limits"

# Bad: Generic keys
"data"
"result"
"info"
```

### TTL Strategy
```python
# Short TTL for frequently changing data
await cache.set("user_session:123", session_data, ttl=300)  # 5 minutes

# Medium TTL for moderately stable data
await cache.set("user_profile:123", profile_data, ttl=3600)  # 1 hour

# Long TTL for static data
await cache.set("static_config", config_data, ttl=86400)  # 24 hours
```

### Cache Invalidation
```python
# Invalidate on data change
async def update_user_profile(user_id: int, new_data: dict):
    # Update database
    await db.update_user(user_id, new_data)
    
    # Invalidate cache
    await cache.delete(f"user:{user_id}:profile")
```

### Error Handling
```python
async def safe_cache_get(key: str, default=None):
    """Safely get from cache with error handling."""
    try:
        return await cache.get(key)
    except Exception as e:
        logger.error(f"Cache get error for key {key}: {e}")
        return default

async def safe_cache_set(key: str, value, ttl=300):
    """Safely set cache with error handling."""
    try:
        await cache.set(key, value, ttl=ttl)
    except Exception as e:
        logger.error(f"Cache set error for key {key}: {e}")
```

---

## 📚 References

* [aiocache Docs](https://aiocache.readthedocs.io/)
* [RedisInsight](https://redis.com/redis-enterprise/redis-insight/)
* [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
