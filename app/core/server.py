"""Primary application entry point for AI Research Assistant Platform."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import api_router
from app.core.config import settings
from app.core.lifespan import lifespan
from app.exceptions import (
    AppException,
    app_exception_handler,
    general_exception_handler,
    validation_exception_handler,
)
from app.middleware.endpoint_validation import EndpointValidationMiddleware
from app.middleware.api_monitoring import APIMonitoringMiddleware


def configure_middleware(app: FastAPI) -> None:
    """Configure middleware for the application."""
    # Add monitoring middleware first to capture all requests
    app.add_middleware(APIMonitoringMiddleware)
    
    # Add endpoint validation middleware
    app.add_middleware(EndpointValidationMiddleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_routes(app: FastAPI) -> None:
    """Attach API routes to the application."""
    app.include_router(api_router)


def configure_exception_handlers(app: FastAPI) -> None:
    """Configure exception handlers."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)


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

## Features

- **Web Search Integration**: Powered by DuckDuckGo (free) or Tavily for comprehensive web research
- **AI Analysis**: Local model support via Ollama or OpenAI integration
- **Citation Management**: Automatic citation generation and reference tracking
- **User Management**: JWT-based authentication with user profiles and subscription plans
- **Payment Integration**: Stripe-powered subscription management
- **Research Analytics**: Usage tracking and trending topic analysis
- **Research Storage**: Save and organize research sessions
- **Export Capabilities**: Export research results in multiple formats

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

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```
""",
        version=settings.RELEASE_VERSION,
        docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
        redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
        lifespan=lifespan,
    )

    configure_middleware(app_instance)
    configure_exception_handlers(app_instance)
    configure_routes(app_instance)
    configure_metrics(app_instance)

    return app_instance


app = build_app()
