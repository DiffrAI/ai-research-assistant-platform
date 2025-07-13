# AI Research Assistant Platform

A full-stack AI research platform with FastAPI backend and React frontend, featuring user authentication, SQLite database, and AI-powered research capabilities.

## 🚀 Quick Start

### Option 1: Using the Development Script (Recommended)

```bash
# Make the script executable
chmod +x start-dev.sh

# Start both backend and frontend
./start-dev.sh
```

This will:
- Kill any existing processes on ports 3000 and 8002
- Start the FastAPI backend on port 8002
- Start the React frontend on port 3000
- Check that both services are running

### Option 2: Manual Start

#### Backend
```bash
# Activate virtual environment
source .venv/bin/activate

# Start backend
python main.py
```

#### Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (if not already done)
npm install

# Start frontend
PORT=3000 npm start
```

### Option 3: Docker Compose

```bash
# Build and start both services
docker-compose up --build
```

## 📊 Current Status

### ✅ Working Components

1. **Backend (FastAPI)**
   - ✅ Running on port 8002
   - ✅ SQLite database with user management
   - ✅ JWT authentication system
   - ✅ User registration and login APIs
   - ✅ Chat endpoint (streaming)
   - ✅ Payment endpoints
   - ✅ Research endpoints (with robust web search and local LLM integration)

2. **Database**
   - ✅ SQLite database (`ai_research.db`)
   - ✅ User table with proper schema
   - ✅ User data storage and retrieval
   - ✅ Database initialization working

3. **API Endpoints**
   - ✅ Authentication: `/api/v1/auth/*`
   - ✅ User management
   - ✅ Chat: `/api/v1/chat`
   - ✅ Payment: `/api/v1/payment/*`
   - ✅ Research: `/api/v1/research/*`

### ⚠️ Known Issues

1. **Frontend Startup**
   - ⚠️ React app sometimes has port conflicts
   - ⚠️ Use `PORT=3000` to force port 3000
   - ⚠️ Kill existing processes if needed

2. **Research Service**
   - ⚠️ Ensure Ollama is running and the correct model is loaded (see docs/local_model_setup.md)
   - ⚠️ DuckDuckGo may occasionally rate limit; robust retry logic is built-in and configurable

## 🔧 API Testing

### Test User Registration
```bash
curl -X POST http://localhost:8002/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","full_name":"Test User","password":"testpass123"}'
```

### Test User Login
```bash
curl -X POST http://localhost:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### Test Chat API
```bash
curl "http://localhost:8002/api/v1/chat?message=hello"
```

## 🗄️ Database

The application uses SQLite for development. The database file is `ai_research.db` in the root directory.

### View Database
```bash
sqlite3 ai_research.db
```

### Check Users
```sql
SELECT id, email, full_name, role, subscription_plan FROM users;
```

## 🐳 Docker Setup

### Development with Docker Compose

```bash
# Start both services
docker-compose up --build

# Stop services
docker-compose down
```

### Production Setup

```bash
# Use the production docker-compose
docker-compose -f docker-compose-langfuse.yaml up --build
```

## 📁 Project Structure

```
fastapi-genai-boilerplate/
├── app/                    # Backend application
│   ├── apis/              # API routes
│   ├── core/              # Core configuration
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── workflows/         # AI workflows
├── frontend/              # React frontend
│   ├── src/               # Source code
│   ├── public/            # Public assets
│   └── package.json       # Dependencies
├── docker-compose.yml     # Docker setup
├── start-dev.sh          # Development script
└── ai_research.db        # SQLite database
```

## 🔑 Environment Variables

Create a `.env` file in the root directory. See [`docs/envs.md`](docs/envs.md) and [`docs/example.env`](docs/example.env) for a full list and details.

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./ai_research.db

# Security
SECRET_KEY=your-secret-key-change-in-production

# Local Model (Ollama)
USE_LOCAL_MODEL=true
LOCAL_MODEL_URL=http://127.0.0.1:11434
LOCAL_MODEL_NAME=qwen2.5:7b  # Must match the model loaded in Ollama

# Web Search (DuckDuckGo)
SEARCH_PROVIDER=duckduckgo
DUCKDUCKGO_MAX_RESULTS=10
SEARCH_MAX_RETRIES=3         # Number of retries for DuckDuckGo search
SEARCH_BASE_DELAY=1.0        # Base delay (seconds) for exponential backoff
SEARCH_MAX_DELAY=10.0        # Max delay (seconds) for exponential backoff

# Optional: OpenAI (if not using local model)
# OPENAI_API_KEY=your-openai-key

# Optional: Tavily (if you want to use Tavily search)
# TAVILY_API_KEY=your-tavily-key

# Payment (Stripe)
STRIPE_SECRET_KEY=your-stripe-secret
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable

# Monitoring (LangFuse)
LANGFUSE_HOST=your-langfuse-host
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
```

## 🌐 Local Model Setup (Ollama)

- Ollama is the only supported local LLM backend. LM Studio is not supported.
- See [`docs/local_model_setup.md`](docs/local_model_setup.md) for full instructions.
- Make sure `LOCAL_MODEL_NAME` matches the model you have loaded in Ollama (e.g., `qwen2.5:7b`).

## 🌍 Web Search Integration

- DuckDuckGo is the default and recommended web search provider.
- Robust retry logic and exponential backoff are built-in and configurable via `.env`.
- See [`docs/local_model_setup.md`](docs/local_model_setup.md) for details and troubleshooting.

## 🚨 Troubleshooting

### Frontend Not Starting
```bash
# Kill processes on port 3000
lsof -ti:3000 | xargs kill -9

# Start with specific port
PORT=3000 npm start
```

### Backend Not Starting
```bash
# Kill processes on port 8002
lsof -ti:8002 | xargs kill -9

# Activate virtual environment
source .venv/bin/activate

# Start backend
python main.py
```

### Database Issues
```bash
# Remove database and restart
rm ai_research.db
python main.py
```

### Local Model Issues
- Ensure Ollama is running on `LOCAL_MODEL_URL` (default: `http://127.0.0.1:11434`)
- Ensure the model name in `LOCAL_MODEL_NAME` matches the model loaded in Ollama
- See [`docs/local_model_setup.md`](docs/local_model_setup.md) for more

### Web Search Issues
- DuckDuckGo is robust but may occasionally rate limit; retry logic is built-in
- Adjust `SEARCH_MAX_RETRIES`, `SEARCH_BASE_DELAY`, and `SEARCH_MAX_DELAY` in `.env` as needed
- For more reliable/structured search, you can switch to Tavily (paid)

## 🚀 CI/CD Pipeline

This project includes a comprehensive CI/CD pipeline that runs on every push to the main branch.

### Pipeline Features
- ✅ **Multi-Python Testing**: Tests on Python 3.11 and 3.12
- ✅ **Code Quality**: Linting with Ruff, type checking with MyPy
- ✅ **Security**: Bandit for security checks, Safety for dependency vulnerabilities
- ✅ **Coverage**: Test coverage reporting with pytest-cov
- ✅ **Build Verification**: Package building and Docker image testing
- ✅ **Pre-commit Hooks**: Local checks before commits

### Local Development
```bash
# Run all CI checks locally
make ci

# Run individual checks
make lint          # Linting
make type-check    # Type checking
make test          # Tests with coverage
make security-check # Security checks
make build         # Build package

# Install pre-commit hooks
make pre-commit

# Run pre-commit on all files
make pre-commit-run
```

### CI/CD Configuration Files
- `.github/workflows/ci.yml` - GitHub Actions workflow
- `ruff.toml` - Ruff linting configuration
- `mypy.ini` - MyPy type checking configuration
- `.bandit` - Bandit security configuration
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `Makefile` - Local development commands

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## 📄 License

This project is licensed under the MIT License.
