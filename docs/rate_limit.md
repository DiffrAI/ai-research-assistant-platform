# 🛡️ Rate Limiting with fastapi-limiter

This project uses [**fastapi-limiter**](https://github.com/long2ice/fastapi-limiter) to implement scalable, Redis-based rate limiting in your FastAPI app. It protects against abuse, brute force attempts, and excessive traffic by enforcing flexible request thresholds.

---

## 🚀 Features

- 🔗 Redis-backed distributed rate limiting
- 🧠 IP or token-based client identification
- 🪝 Decorator-free, dependency-based integration
- 🧾 Automatic `429 Too Many Requests` responses
- 🕒 Native `Retry-After` header support
- ⚙️ Customizable via `Bearer` tokens, IPs, headers, or API keys

---

## ⚙️ Configuration

### 🔧 Backend Initialization

Rate limiter is initialized in `app/core/middlewares/rate_limiter.py`:

```python
"""Rate limiter configuration using fastapi-limiter."""

import fakeredis.aioredis
import redis.asyncio as redis
from fastapi import Request
from fastapi_limiter import FastAPILimiter

from app.core.config import RateLimitBackend, settings


async def token_or_ip_key(request: Request) -> str:
    """Use Bearer token if available, fallback to client IP."""
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        if token:
            return token
    return request.client.host


async def init_rate_limiter():
    """Initialize FastAPI limiter with Redis or local memory (fakeredis)."""

    if settings.RATE_LIMIT_BACKEND == RateLimitBackend.LOCAL:
        fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
        await FastAPILimiter.init(redis=fake_redis, identifier=token_or_ip_key)

    elif settings.RATE_LIMIT_BACKEND == RateLimitBackend.REDIS:
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        if settings.REDIS_PASSWORD:
            redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}"

        redis_client = redis.from_url(redis_url, decode_responses=True)
        await FastAPILimiter.init(redis=redis_client, identifier=token_or_ip_key)

    else:
        raise ValueError(
            f"Unsupported RATE_LIMIT_BACKEND: {settings.RATE_LIMIT_BACKEND}"
        )
```

### ⚡ Lifespan Hook

Call it inside your app's `lifespan` startup:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .middlewares.rate_limiter import init_rate_limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_rate_limiter()
    yield
```

---

## 🧩 Usage in Routes

### ✅ Basic Rate Limiting

Use the `RateLimiter` dependency in route decorators:

```python
from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

router = APIRouter()

@router.get("/ping", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def ping():
    return {"message": "pong"}
```

This will limit requests to **10 per 60 seconds** per token or IP.

### 🔐 Authentication-Specific Limits

```python
@router.post("/login", dependencies=[Depends(RateLimiter(times=5, seconds=300))])
async def login(credentials: LoginRequest):
    """Limit login attempts to 5 per 5 minutes per IP."""
    return await auth_service.authenticate(credentials)

@router.post("/register", dependencies=[Depends(RateLimiter(times=3, seconds=3600))])
async def register(user_data: RegisterRequest):
    """Limit registrations to 3 per hour per IP."""
    return await auth_service.register_user(user_data)
```

### 📊 Research Endpoint Limits

```python
@router.post("/research", dependencies=[Depends(RateLimiter(times=50, seconds=3600))])
async def conduct_research(request: ResearchRequest, user: User = Depends(get_current_user)):
    """Allow 50 research requests per hour per user."""
    return await research_service.conduct_research(request, user)

@router.get("/research/history", dependencies=[Depends(RateLimiter(times=100, seconds=3600))])
async def get_research_history(user: User = Depends(get_current_user)):
    """Allow 100 history requests per hour per user."""
    return await research_service.get_user_history(user.id)
```

### 💳 Payment Endpoint Limits

```python
@router.post("/payment/create", dependencies=[Depends(RateLimiter(times=10, seconds=3600))])
async def create_payment(payment_data: PaymentRequest, user: User = Depends(get_current_user)):
    """Limit payment creation to 10 per hour per user."""
    return await payment_service.create_payment(payment_data, user)

@router.get("/payment/history", dependencies=[Depends(RateLimiter(times=20, seconds=3600))])
async def get_payment_history(user: User = Depends(get_current_user)):
    """Allow 20 payment history requests per hour per user."""
    return await payment_service.get_user_payments(user.id)
```

### 🔍 Search-Specific Limits

```python
@router.get("/search", dependencies=[Depends(RateLimiter(times=100, seconds=3600))])
async def search(query: str, user: User = Depends(get_current_user)):
    """Allow 100 searches per hour per user."""
    return await search_service.search(query, user)

@router.get("/search/advanced", dependencies=[Depends(RateLimiter(times=30, seconds=3600))])
async def advanced_search(request: AdvancedSearchRequest, user: User = Depends(get_current_user)):
    """Limit advanced searches to 30 per hour per user."""
    return await search_service.advanced_search(request, user)
```

### 📤 Export Endpoint Limits

```python
@router.post("/export/pdf", dependencies=[Depends(RateLimiter(times=20, seconds=3600))])
async def export_pdf(request: ExportRequest, user: User = Depends(get_current_user)):
    """Limit PDF exports to 20 per hour per user."""
    return await export_service.export_pdf(request, user)

@router.post("/export/markdown", dependencies=[Depends(RateLimiter(times=50, seconds=3600))])
async def export_markdown(request: ExportRequest, user: User = Depends(get_current_user)):
    """Allow 50 markdown exports per hour per user."""
    return await export_service.export_markdown(request, user)
```

---

## 🧠 Custom Key Strategies

### API Key-Based Limiting

```python
async def api_key_or_ip(request: Request) -> str:
    """Use X-API-KEY header or fallback to IP."""
    api_key = request.headers.get("X-API-KEY")
    if api_key:
        return f"api_key:{api_key}"
    return f"ip:{request.client.host}"

# Initialize with custom key function
await FastAPILimiter.init(redis=redis_client, identifier=api_key_or_ip)
```

### User-Based Limiting

```python
async def user_or_ip(request: Request) -> str:
    """Use user ID from JWT token or fallback to IP."""
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                return f"user:{user_id}"
        except JWTError:
            pass
    return f"ip:{request.client.host}"
```

### Subscription-Based Limiting

```python
async def subscription_based_key(request: Request) -> str:
    """Use subscription plan for different rate limits."""
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id:
                # Get user's subscription plan
                user = await get_user_by_id(user_id)
                if user:
                    return f"subscription:{user.subscription_plan}:{user_id}"
        except JWTError:
            pass
    return f"ip:{request.client.host}"
```

### Dynamic Rate Limiting

```python
from fastapi import Depends, Request
from fastapi_limiter.depends import RateLimiter

def get_rate_limiter_for_user(user: User):
    """Return rate limiter based on user's subscription plan."""
    limits = {
        "free": RateLimiter(times=10, seconds=3600),
        "pro": RateLimiter(times=100, seconds=3600),
        "academic": RateLimiter(times=500, seconds=3600),
        "enterprise": RateLimiter(times=1000, seconds=3600)
    }
    return limits.get(user.subscription_plan, limits["free"])

@router.post("/research")
async def conduct_research(
    request: ResearchRequest,
    user: User = Depends(get_current_user),
    rate_limiter: RateLimiter = Depends(get_rate_limiter_for_user)
):
    """Apply rate limiting based on user's subscription."""
    return await research_service.conduct_research(request, user)
```

---

## 🛑 Handling 429 Responses

A `429 Too Many Requests` response is returned automatically, but you can customize it inside your app's exception handlers:

```python
def _handle_fastapi_http_exception(self):
        """Handle FastAPI HTTP exceptions."""

    @self.app.exception_handler(HTTPException)
    async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
        if exc.status_code == 429:
            headers = getattr(exc, "headers", {})
            retry_after = int(headers["Retry-After"])

            return await self._create_json_response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                message=messages.RATE_LIMIT_ERROR.format(retry_after=retry_after),
                error_log=str(exc),
            )

        return await self._create_json_response(
            status_code=exc.status_code, message=exc.detail
        )
```

### Custom 429 Response

```python
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 429:
        headers = getattr(exc, "headers", {})
        retry_after = headers.get("Retry-After", 60)
        
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Please try again in {retry_after} seconds.",
                "retry_after": retry_after,
                "limit_type": "user_based" if "Bearer" in request.headers.get("authorization", "") else "ip_based"
            },
            headers={"Retry-After": str(retry_after)}
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )
```

---

## 🐳 Redis Setup for Local Dev

You can use Docker to run Redis locally:

```bash
docker run -d --name dev-redis -p 6379:6379 redis:7-alpine
```

### Optional: RedisInsight for UI

```bash
docker run -d -p 8001:8001 --name redis-insight \
  --link dev-redis:redis \
  redis/redisinsight:latest
```

Access at: [http://localhost:8001](http://localhost:8001)

---

## 🧪 Testing Without Redis

Use `fakeredis` as a memory backend for tests/dev:

```env
RATE_LIMIT_BACKEND=LOCAL
```

### Testing Rate Limits

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_rate_limiting():
    """Test that rate limiting works correctly."""
    # Make requests up to the limit
    for i in range(10):
        response = client.get("/ping")
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.get("/ping")
    assert response.status_code == 429
    assert "Retry-After" in response.headers
```

---

## 🧠 Best Practices

### Rate Limit Tiers

```python
# Free tier: Very restrictive
FREE_TIER_LIMITS = {
    "research": RateLimiter(times=5, seconds=3600),      # 5/hour
    "search": RateLimiter(times=20, seconds=3600),       # 20/hour
    "export": RateLimiter(times=3, seconds=3600),        # 3/hour
}

# Pro tier: Moderate limits
PRO_TIER_LIMITS = {
    "research": RateLimiter(times=50, seconds=3600),     # 50/hour
    "search": RateLimiter(times=200, seconds=3600),      # 200/hour
    "export": RateLimiter(times=20, seconds=3600),       # 20/hour
}

# Enterprise tier: High limits
ENTERPRISE_TIER_LIMITS = {
    "research": RateLimiter(times=500, seconds=3600),    # 500/hour
    "search": RateLimiter(times=1000, seconds=3600),     # 1000/hour
    "export": RateLimiter(times=100, seconds=3600),      # 100/hour
}
```

### Security Considerations

- ✅ Use token-based keys for user-based throttling
- ✅ Apply stricter limits on sensitive routes like `/login`, `/register`
- ✅ Always return `Retry-After` to guide clients
- ✅ Use namespaces or DB separation in Redis for staging vs prod
- ✅ Monitor rate limit violations for security threats

### Monitoring Rate Limits

```python
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

async def log_rate_limit_violation(request: Request, user_id: str = None):
    """Log rate limit violations for monitoring."""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    
    logger.warning(
        f"Rate limit violation - IP: {client_ip}, "
        f"User: {user_id}, User-Agent: {user_agent}"
    )
```

---

## 📚 References

- 📘 [fastapi-limiter GitHub](https://github.com/long2ice/fastapi-limiter)
- 📘 [Redis Docs](https://redis.io/docs/)
- 📘 [RedisInsight UI](https://redis.com/redis-enterprise/redis-insight/)
