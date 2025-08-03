[![Release Pipeline](https://github.com/DiffrAI/ai-research-assistant-platform/actions/workflows/release-pipeline.yml/badge.svg)](https://github.com/DiffrAI/ai-research-assistant-platform/actions/workflows/release-pipeline.yml)

# AI Research Assistant Platform

A modern, full-stack platform for AI-powered research. Built with FastAPI and React, it offers robust user management, subscription handling, real-time web search, and seamless integration with local and cloud LLMs. Designed for researchers, students, and professionals who want a reliable, extensible research assistant.

---

## Features
- **Secure authentication** (JWT, roles, password hashing)
- **Subscription management** (Stripe, usage tracking)
- **AI research workflows** (local LLMs, OpenAI fallback, web search)
- **Modern frontend** (React, Tailwind, responsive UI)
- **Export options** (PDF, Markdown)
- **Monitoring** (Prometheus, Grafana, LangFuse)
- **Performance** (async, Redis cache, rate limiting, Celery tasks)
- **Production-ready** (Docker, CI/CD, health checks)

---

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git
- Docker (Optional)
- Docker Compose (Optional)

### 1. Clone & Install
```bash
git clone https://github.com/DiffrAI/ai-research-assistant-platform
cd ai-research-assistant-platform
uv sync
cp .env.sample .env
# Edit .env as needed
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

### 3. Run (Dev)
```bash
# Backend
uv run python main.py
# Frontend (in another terminal)
cd frontend
npm start
```

### 4. Access
- Frontend: http://localhost:3000
- API: http://localhost:8002
- Docs: http://localhost:8002/docs

---

## Architecture

### Backend Structure
```
app/
├── api/                    # API endpoints
│   ├── auth.py            # Authentication endpoints
│   ├── chat.py            # Chat & streaming endpoints
│   ├── research.py        # Research endpoints
│   ├── payment.py         # Payment & subscription endpoints
│   └── health.py          # Health check endpoints
├── core/                  # Core infrastructure
│   ├── config.py          # Configuration management
│   ├── database.py        # Database setup & connections
│   ├── server.py          # FastAPI application setup
│   └── lifespan.py        # Application lifecycle management
├── models/                # Data models
│   └── models.py          # Unified Pydantic & SQLAlchemy models
├── workflows/             # AI workflow components
│   └── graphs/websearch/  # Web search AI workflows
├── tasks/                 # Background task processing
├── auth.py               # Authentication logic & utilities
├── payment.py            # Payment service integration
├── responses.py          # Response formatting utilities
├── exceptions.py         # Custom exception handling
└── utils.py              # Essential utility functions
```

### Technology Stack
- **Backend:** FastAPI (Python), async, modular, simplified architecture
- **Frontend:** React (TypeScript), Tailwind CSS, Zustand state
- **Database:** SQLite (dev), PostgreSQL (prod-ready)
- **AI:** Local LLMs (Ollama), OpenAI fallback
- **Web Search:** DuckDuckGo, Tavily
- **Payments:** Stripe
- **Monitoring:** Prometheus, Grafana, LangFuse
- **Background Tasks:** Celery, Redis

---

## Testing & Quality

- **Run all tests:**
  ```bash
  uv run pytest tests/
  ```
- **Lint & type check:**
  ```bash
  uv run ruff check .
  uv run mypy app/
  ```
- **Security:**
  ```bash
  uv run bandit -r app/
  uv run safety check
  ```
- **CI/CD:** All PRs and releases must pass lint, type, security, and test checks (see `.github/workflows/`).

---

## Deployment

- **Docker Compose (all services):**
  ```bash
  docker compose up --build
  ```
- **Production (with monitoring):**
  ```bash
  docker compose -f docker-compose-langfuse.yaml up --build
  ```

---

## Documentation & Support


- **Contributing:** See `CONTRIBUTING.md`
- **Issues:** [GitHub Issues](https://github.com/DiffrAI/ai-research-assistant-platform/issues)

---

## License
MIT License. See [LICENSE](LICENSE).

---

**Built for real-world research. Contributions welcome.**
