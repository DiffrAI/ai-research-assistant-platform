"""Primary application entry point for AI Research Assistant Platform."""

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.apis import api_routers
from app.core.config import settings
from app.core.exceptions import HandleExceptions
from app.core.lifespan import lifespan
from app.core.middlewares import LoggingMiddleware


def configure_middleware() -> list[Middleware]:
    """Define and return middleware settings."""
    return [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(LoggingMiddleware),
    ]


def configure_routes(app: FastAPI) -> None:
    """Attach API routes to the application."""
    app.include_router(api_routers)


def configure_metrics(app: FastAPI) -> None:
    """Instrument and expose Prometheus metrics."""
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        excluded_handlers=[],
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)


def build_app() -> FastAPI:
    """Initialize and configure the FastAPI app instance."""
    app_instance = FastAPI(
        title="AI Research Assistant Platform",
        description="""
# AI Research Assistant Platform API

A comprehensive AI-powered research platform that combines web search capabilities with intelligent analysis and citation generation.

## 🚀 Features

- **🔍 Web Search Integration**: Powered by DuckDuckGo (free) or Tavily for comprehensive web research
- **🤖 AI Analysis**: Local model support via Ollama or OpenAI integration
- **📚 Citation Management**: Automatic citation generation and reference tracking
- **👤 User Management**: JWT-based authentication with user profiles and subscription plans
- **💳 Payment Integration**: Stripe-powered subscription management
- **📊 Research Analytics**: Usage tracking and trending topic analysis
- **💾 Research Storage**: Save and organize research sessions
- **📤 Export Capabilities**: Export research results in multiple formats

## 🔧 API Endpoints

### Authentication (`/api/v1/auth`)
- User registration and login
- JWT token management
- Subscription information

### Chat & Research (`/api/v1/chat`)
- Streaming chat responses
- Web search integration
- Background task processing

### Research (`/api/v1/research`)
- AI-powered research with citations
- Research session management
- Export functionality
- Trending topics analysis

### Payment (`/api/v1/payment`)
- Subscription plan management
- Stripe integration
- Usage tracking

### User Management (`/api/v1/user`)
- User profile management
- Account settings

## 🛠️ Technology Stack

- **Backend**: FastAPI with async/await
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **AI Models**: Local models via Ollama or OpenAI
- **Search**: DuckDuckGo (free) or Tavily
- **Payments**: Stripe
- **Monitoring**: Prometheus, Grafana, LangFuse
- **Cache**: Redis
- **Background Tasks**: Celery

## 📖 Documentation

- Interactive API docs: `/docs` (Swagger UI)
- Alternative docs: `/redoc` (ReDoc)
- Health check: `/health`
- Metrics: `/metrics`

## 🔐 Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```
""",
        version=settings.RELEASE_VERSION,
        docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
        redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
        middleware=configure_middleware(),
        lifespan=lifespan,
    )

    HandleExceptions(app=app_instance)
    configure_routes(app_instance)
    configure_metrics(app_instance)

    return app_instance


app = build_app()
