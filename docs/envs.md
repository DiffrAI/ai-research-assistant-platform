# 🌍 Environment Variables

Application configuration is fully managed through a `.env` file using `pydantic.BaseSettings`. This approach ensures environment-specific settings can be easily managed without hardcoding values.

---

## ✅ Complete `.env` Configuration

```env
# =============================================================================
# CORE APPLICATION SETTINGS
# =============================================================================
ENVIRONMENT=development         # Options: development | qa | demo | production
LOG_LEVEL=DEBUG                # Options: TRACE | DEBUG | INFO | WARNING | ERROR
RELEASE_VERSION=0.0.1

# Server Configuration
HOST=0.0.0.0
PORT=8002
WORKER_COUNT=4                 # Auto-detected if not set
DEBUG=true

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_URL=sqlite+aiosqlite:///./ai_research.db
# For PostgreSQL: postgresql+asyncpg://user:pass@localhost/dbname

# =============================================================================
# SECURITY & AUTHENTICATION
# =============================================================================
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# =============================================================================
# AI MODEL CONFIGURATION
# =============================================================================
# Local Model (Ollama) - Recommended for development
USE_LOCAL_MODEL=true
LOCAL_MODEL_URL=http://127.0.0.1:11434
LOCAL_MODEL_NAME=qwen2.5:7b    # Must match the model loaded in Ollama

# OpenAI (Alternative to local model)
OPENAI_API_KEY=your_openai_api_key_here

# =============================================================================
# WEB SEARCH CONFIGURATION
# =============================================================================
# Search Provider (DuckDuckGo is free, Tavily is paid)
SEARCH_PROVIDER=duckduckgo      # Options: duckduckgo | tavily
DUCKDUCKGO_MAX_RESULTS=10
SEARCH_MAX_RETRIES=3           # Number of retries for web search
SEARCH_BASE_DELAY=1.0          # Base delay (seconds) for exponential backoff
SEARCH_MAX_DELAY=10.0          # Max delay (seconds) for exponential backoff

# Tavily (Alternative to DuckDuckGo)
TAVILY_API_KEY=your_tavily_api_key_here

# =============================================================================
# CACHE & RATE LIMITING
# =============================================================================
# Cache Backend
CACHE_BACKEND=local            # Options: local | redis
RATE_LIMIT_BACKEND=local       # Options: local | redis

# Redis Configuration (for cache and rate limiting)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# =============================================================================
# PAYMENT & SUBSCRIPTION (Stripe)
# =============================================================================
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# =============================================================================
# MONITORING & OBSERVABILITY
# =============================================================================
# LangFuse (Optional - for LLM observability)
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key

# Grafana (Optional - for metrics)
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=supersecurepassword
```

---

## ⚙️ Configuration Categories

### 🔐 **Security Variables**
- `SECRET_KEY`: **Required** - Used for JWT token signing
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiry (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiry (default: 7)

### 🧠 **AI Model Configuration**
- `USE_LOCAL_MODEL`: Set to `true` for Ollama, `false` for OpenAI
- `LOCAL_MODEL_URL`: Ollama server URL (default: http://127.0.0.1:11434)
- `LOCAL_MODEL_NAME`: Model name in Ollama (e.g., qwen2.5:7b)
- `OPENAI_API_KEY`: Required if `USE_LOCAL_MODEL=false`

### 🌐 **Web Search Configuration**
- `SEARCH_PROVIDER`: Choose between `duckduckgo` (free) or `tavily` (paid)
- `DUCKDUCKGO_MAX_RESULTS`: Maximum search results (default: 10)
- `SEARCH_MAX_RETRIES`: Retry attempts for failed searches (default: 3)
- `SEARCH_BASE_DELAY` & `SEARCH_MAX_DELAY`: Exponential backoff settings

### 💳 **Payment Configuration**
- `STRIPE_SECRET_KEY`: Stripe secret key for payment processing
- `STRIPE_PUBLISHABLE_KEY`: Stripe publishable key for frontend
- `STRIPE_WEBHOOK_SECRET`: Webhook secret for payment events

### 📊 **Monitoring Configuration**
- `LANGFUSE_*`: LangFuse configuration for LLM observability
- `GF_SECURITY_*`: Grafana admin credentials

---

## 🔒 Security Best Practices

* **Never commit** your `.env` file to version control
* Use `.env.sample` to share required variables with your team
* For production, use secret management tools (Docker secrets, AWS SSM, HashiCorp Vault)
* Rotate `SECRET_KEY` and API keys regularly
* Use environment-specific configurations (dev/staging/prod)

---

## 🚨 Required vs Optional Variables

### **Required for Basic Functionality:**
- `SECRET_KEY`
- `DATABASE_URL`
- `USE_LOCAL_MODEL` + `LOCAL_MODEL_URL` + `LOCAL_MODEL_NAME` (or `OPENAI_API_KEY`)
- `SEARCH_PROVIDER`

### **Required for Production:**
- All security variables
- `STRIPE_*` keys (for payments)
- `REDIS_*` (if using Redis for cache/rate limiting)

### **Optional (Development):**
- `LANGFUSE_*` (for LLM observability)
- `GF_SECURITY_*` (for Grafana monitoring)
- `TAVILY_API_KEY` (if using Tavily search)

---

## 🔧 Environment-Specific Configurations

### **Development:**
```env
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CACHE_BACKEND=local
RATE_LIMIT_BACKEND=local
```

### **Production:**
```env
ENVIRONMENT=production
LOG_LEVEL=INFO
CACHE_BACKEND=redis
RATE_LIMIT_BACKEND=redis
DEBUG=false
```

---

## 🐳 Docker Environment Variables

When using Docker Compose, you can override environment variables:

```yaml
services:
  app:
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/app
      - REDIS_HOST=redis
      - REDIS_PORT=6379
```
