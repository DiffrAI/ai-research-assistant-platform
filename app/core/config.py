"""Enhanced configuration settings for the application."""

import enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, enum.Enum):
    """Defines available logging levels for application monitoring and debugging."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    TRACE = "TRACE"


class CacheBackend(str, enum.Enum):
    """Supported cache backends."""

    REDIS = "redis"
    LOCAL = "local"


class RateLimitBackend(str, enum.Enum):
    """Supported rate-limit backends."""

    REDIS = "redis"
    LOCAL = "local"


class AppEnvs(str, enum.Enum):
    """Application environments."""

    DEVELOPMENT = "development"
    QA = "qa"
    DEMO = "demo"
    PRODUCTION = "production"


class SearchProvider(str, enum.Enum):
    """Supported search providers."""

    DUCKDUCKGO = "duckduckgo"
    TAVILY = "tavily"


class DatabaseConfig(BaseModel):
    """Database configuration settings."""

    url: str = Field(
        default="sqlite+aiosqlite:///./ai_research.db",
        description="Database connection URL",
    )
    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(
        default=20, ge=0, le=100, description="Maximum overflow connections"
    )
    pool_timeout: int = Field(
        default=30, ge=1, le=300, description="Connection pool timeout in seconds"
    )
    pool_recycle: int = Field(
        default=3600,
        ge=60,
        le=7200,
        description="Connection pool recycle time in seconds",
    )


class RedisConfig(BaseModel):
    """Redis configuration settings."""

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    password: Optional[str] = Field(default=None, description="Redis password")
    db: int = Field(default=0, ge=0, le=15, description="Redis database number")
    max_connections: int = Field(
        default=10, ge=1, le=100, description="Maximum Redis connections"
    )


class LocalModelConfig(BaseModel):
    """Local model configuration settings."""

    url: str = Field(
        default="http://127.0.0.1:11434", description="Local model API URL"
    )
    name: str = Field(default="qwen2.5:7b", description="Local model name")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Model temperature"
    )
    max_tokens: int = Field(
        default=2000, ge=1, le=10000, description="Maximum tokens per response"
    )
    timeout: int = Field(
        default=30, ge=1, le=300, description="Request timeout in seconds"
    )


class SearchConfig(BaseModel):
    """Search configuration settings."""

    provider: SearchProvider = Field(
        default=SearchProvider.DUCKDUCKGO, description="Search provider"
    )
    max_results: int = Field(
        default=10, ge=1, le=50, description="Maximum search results"
    )
    max_retries: int = Field(
        default=5, ge=1, le=10, description="Maximum search retries"
    )
    base_delay: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Base delay for exponential backoff"
    )
    max_delay: float = Field(
        default=10.0,
        ge=1.0,
        le=60.0,
        description="Maximum delay for exponential backoff",
    )
    timeout: int = Field(default=30, ge=5, le=120, description="Search request timeout")


class SecurityConfig(BaseModel):
    """Security configuration settings."""

    secret_key: str = Field(
        default="your-secret-key-change-in-production", description="JWT secret key"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, ge=1, le=1440, description="Access token expiry in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, ge=1, le=365, description="Refresh token expiry in days"
    )
    password_min_length: int = Field(
        default=8, ge=6, le=128, description="Minimum password length"
    )


class AppConfig(BaseSettings):
    """Enhanced primary configuration settings for the application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application settings
    log_level: LogLevel = LogLevel.TRACE
    release_version: str = "0.0.1"
    environment: AppEnvs = AppEnvs.DEVELOPMENT
    host: str = "0.0.0.0"
    port: int = Field(default=8002, ge=1, le=65535)
    worker_count: Optional[int] = Field(default=None, ge=1, le=32)
    debug: bool = True

    # Cache and rate limiting
    cache_backend: CacheBackend = CacheBackend.LOCAL
    rate_limit_backend: RateLimitBackend = RateLimitBackend.LOCAL

    # Database configuration
    database: DatabaseConfig = DatabaseConfig()

    # Redis configuration
    redis: RedisConfig = RedisConfig()

    # Local model configuration
    local_model: LocalModelConfig = LocalModelConfig()
    use_local_model: bool = False

    # Search configuration
    search: SearchConfig = SearchConfig()
    search_timeout: int = Field(
        default=30, ge=5, le=120, description="Global search request timeout"
    )

    # Security configuration
    security: SecurityConfig = SecurityConfig()

    # External API keys
    openai_api_key: str = ""
    tavily_api_key: str = ""

    # Stripe configuration
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""

    # LangFuse configuration
    langfuse_host: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""

    # Legacy compatibility properties
    @property
    def LOG_LEVEL(self) -> LogLevel:
        return self.log_level

    @property
    def RELEASE_VERSION(self) -> str:
        return self.release_version

    @property
    def ENVIRONMENT(self) -> AppEnvs:
        return self.environment

    @property
    def HOST(self) -> str:
        return self.host

    @property
    def PORT(self) -> int:
        return self.port

    @property
    def WORKER_COUNT(self) -> Optional[int]:
        return self.worker_count

    @property
    def DEBUG(self) -> bool:
        return self.debug

    @property
    def CACHE_BACKEND(self) -> CacheBackend:
        return self.cache_backend

    @property
    def RATE_LIMIT_BACKEND(self) -> RateLimitBackend:
        return self.rate_limit_backend

    @property
    def REDIS_HOST(self) -> str:
        return self.redis.host

    @property
    def REDIS_PORT(self) -> str:
        return str(self.redis.port)

    @property
    def REDIS_PASSWORD(self) -> str:
        return self.redis.password or ""

    @property
    def OPENAI_API_KEY(self) -> str:
        return self.openai_api_key

    @property
    def TAVILY_API_KEY(self) -> str:
        return self.tavily_api_key

    @property
    def LOCAL_MODEL_URL(self) -> str:
        return self.local_model.url

    @property
    def LOCAL_MODEL_NAME(self) -> str:
        return self.local_model.name

    @property
    def USE_LOCAL_MODEL(self) -> bool:
        return self.use_local_model

    @property
    def SEARCH_PROVIDER(self) -> str:
        return self.search.provider.value

    @property
    def DUCKDUCKGO_MAX_RESULTS(self) -> int:
        return self.search.max_results

    @property
    def SEARCH_MAX_RETRIES(self) -> int:
        return self.search.max_retries

    @property
    def SEARCH_BASE_DELAY(self) -> float:
        return self.search.base_delay

    @property
    def SEARCH_MAX_DELAY(self) -> float:
        return self.search.max_delay

    @property
    def SEARCH_TIMEOUT(self) -> int:
        return self.search_timeout

    @property
    def SECRET_KEY(self) -> str:
        return self.security.secret_key

    @property
    def ALGORITHM(self) -> str:
        return self.security.algorithm

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.security.access_token_expire_minutes

    @property
    def REFRESH_TOKEN_EXPIRE_DAYS(self) -> int:
        return self.security.refresh_token_expire_days

    @property
    def STRIPE_SECRET_KEY(self) -> str:
        return self.stripe_secret_key

    @property
    def STRIPE_PUBLISHABLE_KEY(self) -> str:
        return self.stripe_publishable_key

    @property
    def STRIPE_WEBHOOK_SECRET(self) -> str:
        return self.stripe_webhook_secret

    @property
    def DATABASE_URL(self) -> str:
        return self.database.url

    @property
    def LANGFUSE_HOST(self) -> str:
        return self.langfuse_host

    @property
    def LANGFUSE_PUBLIC_KEY(self) -> str:
        return self.langfuse_public_key

    @property
    def LANGFUSE_SECRET_KEY(self) -> str:
        return self.langfuse_secret_key

    @field_validator("worker_count", mode="before")
    @classmethod
    def validate_worker_count(cls, v: Optional[int]) -> int:
        """Validate worker count based on environment."""
        if v is None:
            import multiprocessing

            return multiprocessing.cpu_count() * 2 + 1
        return v

    @field_validator("security")
    @classmethod
    def validate_secret_key(cls, v: "SecurityConfig", info: Any) -> "SecurityConfig":
        """Ensure secret key is changed in production."""
        if (
            info.data.get("environment") == AppEnvs.PRODUCTION
            and v.secret_key == "your-secret-key-change-in-production"
        ):
            raise ValueError("SECRET_KEY must be changed in production!")
        return v

    @field_validator(
        "openai_api_key",
        "tavily_api_key",
        "stripe_secret_key",
        "stripe_publishable_key",
        "stripe_webhook_secret",
        "langfuse_host",
        "langfuse_public_key",
        "langfuse_secret_key",
    )
    @classmethod
    def validate_production_keys(cls, v: str, info: Any) -> str:
        """Ensure critical API keys are set in production."""
        if info.data.get("environment") == AppEnvs.PRODUCTION and not v:
            raise ValueError(f"{info.field_name.upper()} must be set in production!")
        return v


# Initialize configuration settings
settings = AppConfig()
