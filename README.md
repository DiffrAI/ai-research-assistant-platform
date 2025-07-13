# AI Research Assistant Platform

A full-stack AI research platform with FastAPI backend and React frontend, featuring user authentication, subscription management, AI-powered research, and modern UI/UX.

---

## ✨ Features

### 🔐 **Authentication & User Management**
- **JWT-based authentication** with secure token handling
- **User registration and login** with email validation
- **Subscription management** with Stripe integration
- **Role-based access control** (User, Admin)
- **Password security** with bcrypt hashing

### 🧠 **AI-Powered Research**
- **Local LLM support** via Ollama (free, privacy-focused)
- **OpenAI integration** as fallback option
- **Real-time web search** with DuckDuckGo (free) and Tavily
- **Intelligent research workflows** with citation generation
- **Export functionality** (PDF, Markdown, structured formats)

### 💳 **Subscription & Payments**
- **Stripe integration** for secure payment processing
- **Multiple subscription tiers** (Free, Pro, Academic, Enterprise)
- **Usage tracking** and analytics
- **Webhook handling** for payment events

### 🎨 **Modern Frontend**
- **React with TypeScript** for type safety
- **Tailwind CSS** for responsive, modern design
- **Zustand** for state management
- **React Hook Form** for form handling
- **Toast notifications** for user feedback

### 📊 **Monitoring & Observability**
- **Prometheus** for metrics collection
- **Grafana** for visualization and dashboards
- **LangFuse** for LLM observability
- **Structured logging** with request tracing
- **Health checks** and monitoring endpoints

### ⚡ **Performance & Scalability**
- **Redis caching** with fallback to in-memory
- **Rate limiting** with configurable thresholds
- **Background tasks** with Celery
- **Async/await** throughout the stack
- **Horizontal scaling** ready

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │◄──►│  FastAPI Backend │◄──►│   SQLite/PostgreSQL │
│   (TypeScript)   │    │   (Python 3.9+) │    │     Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
        │   Ollama/    │ │  Web Search│ │   Stripe    │
        │   OpenAI     │ │DuckDuckGo/ │ │  Payments   │
        │   LLMs       │ │   Tavily   │ │             │
        └──────────────┘ └────────────┘ └─────────────┘
                │               │               │
        ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
        │   Redis      │ │  Celery   │ │  Prometheus │
        │   Cache      │ │  Workers  │ │   Grafana   │
        └──────────────┘ └────────────┘ └─────────────┘
```

### **Key Components:**
- **API Versioning:** `/api/v1/`
- **Standardized responses:** JSON with consistent structure
- **Modular architecture:** `app/apis/`, `app/core/`, `app/models/`, `app/services/`, `app/workflows/`
- **Environment-based config:** Development, staging, production

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git
- Docker (optional)

### 1. Clone & Setup
```bash
git clone https://github.com/mahiuddinalkamal/ai-research-assistant-platform.git
cd ai-research-assistant-platform
```

### 2. Backend Setup
```bash
# Install dependencies
uv sync

# Copy environment file
cp docs/example.env .env

# Edit .env with your configuration
# Required: SECRET_KEY, USE_LOCAL_MODEL=true, LOCAL_MODEL_NAME
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Start Development Servers

#### Option A: Dev Script (Recommended)
```bash
chmod +x start-dev.sh
./start-dev.sh
```

#### Option B: Manual
```bash
# Backend (Terminal 1)
source .venv/bin/activate
python main.py

# Frontend (Terminal 2)
cd frontend
npm start
```

#### Option C: Docker Compose
```bash
docker-compose up --build
```

### 5. Access the Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8002
- **API Docs:** http://localhost:8002/docs
- **Grafana:** http://localhost:3000 (admin/supersecurepassword)

---

## 📚 Documentation

### 🛠️ **Setup & Configuration**
- [📋 Environment Variables](docs/envs.md) - Complete configuration guide
- [🧠 Local Model Setup](docs/local_model_setup.md) - Ollama configuration
- [🐳 Docker Setup](docs/docker-compose.md) - Container deployment
- [📝 Contributing Guide](docs/CONTRIBUTING.md) - Development guidelines

### 🔧 **Technical Documentation**
- [🧠 Cache Configuration](docs/cache.md) - Redis and in-memory caching
- [🛡️ Rate Limiting](docs/rate_limit.md) - Request throttling
- [📝 Logging](docs/logging.md) - Structured logging
- [🔍 Trace Decorator](docs/trace.md) - Function tracing

### 📊 **Business & Planning**
- [💼 Business Plan](docs/business-plan.md) - Market analysis and strategy
- [📈 LangFuse Setup](docs/langfuse.md) - LLM observability

---

## 🧪 Testing & Quality Assurance

### Running Tests
```bash
# All tests
.venv/bin/python3 -m pytest tests/ -v

# Specific test file
.venv/bin/python3 -m pytest tests/test_user.py -v

# With coverage
make test
```

### Code Quality Checks
```bash
# Lint and format
make lint

# Type checking
make type-check

# Security checks
make security-check

# All checks
make ci
```

### Test Coverage
- ✅ **User Management** - Registration, login, authentication
- ✅ **Research Functionality** - Web search, AI processing
- ✅ **Local Model Integration** - Ollama client testing
- ✅ **Web Search** - DuckDuckGo and Tavily integration
- ✅ **Chat Endpoints** - Streaming and web search

---

## 🐳 Docker & Deployment

### Development
```bash
docker-compose up --build
```

### Production (with monitoring)
```bash
docker-compose -f docker-compose-langfuse.yaml up --build
```

### Services Included
- **FastAPI Application** - Main backend service
- **Celery Worker** - Background task processing
- **Redis** - Caching and task queue
- **RedisInsight** - Redis management UI
- **Prometheus** - Metrics collection
- **Grafana** - Monitoring dashboards
- **Loki & Promtail** - Log aggregation

---

## 🛠️ Troubleshooting

### Common Issues

#### **Port Conflicts**
```bash
# Kill processes on ports
lsof -ti:3000 | xargs kill -9  # Frontend
lsof -ti:8002 | xargs kill -9  # Backend
```

#### **Database Issues**
```bash
# Reset database
rm ai_research.db && python main.py
```

#### **Ollama Connection**
```bash
# Check if Ollama is running
curl http://127.0.0.1:11434/api/tags

# Start Ollama
ollama serve

# Verify model
ollama list
```

#### **Environment Issues**
```bash
# Check environment
cat .env | grep LOCAL_MODEL_NAME

# Reinstall dependencies
rm -rf .venv
uv sync
```

#### **Stripe Integration**
- Verify API keys in `.env`
- Check webhook configuration
- Ensure test mode for development

#### **Redis/Celery**
- Ensure Redis is running for cache and background tasks
- Check Celery worker logs for task processing

#### **Web Search Issues**
- Adjust retry/delay settings in `.env`
- Switch between DuckDuckGo and Tavily
- Check internet connectivity

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Quick Contribution Steps
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'feat: add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Use conventional commit messages
- Run `make ci` before pushing

---

## 🗺️ Roadmap

### ✅ **Completed (MVP)**
- [x] User authentication and management
- [x] AI-powered research with local models
- [x] Web search integration (DuckDuckGo/Tavily)
- [x] Subscription management with Stripe
- [x] Export functionality (PDF, Markdown)
- [x] Modern React frontend with Tailwind
- [x] Comprehensive testing suite
- [x] Monitoring and observability
- [x] Docker containerization
- [x] Rate limiting and caching

### 🔄 **In Progress**
- [ ] User profile management and password reset
- [ ] Dark mode implementation
- [ ] Enhanced mobile responsiveness
- [ ] Advanced analytics dashboard

### 📋 **Next 3 Months**
- [ ] Collaboration tools and shared projects
- [ ] Advanced export formats (Word, PowerPoint)
- [ ] Team features and multi-user accounts
- [ ] API marketplace and third-party integrations
- [ ] Mobile app (React Native or PWA)

### 🚀 **Future Features**
- [ ] Internationalization (i18n)
- [ ] Advanced research analytics
- [ ] SSO/OAuth integration
- [ ] Multi-tenancy support
- [ ] Enterprise white-label solutions

---

## 📊 Project Status

**Current Status:** ✅ **MVP Complete - Ready for Beta Launch**

### **Technical Metrics**
- **Test Coverage:** 9 passing tests across all major components
- **Code Quality:** Ruff linting, MyPy type checking, security scans
- **Performance:** Redis caching, rate limiting, async operations
- **Security:** JWT authentication, bcrypt hashing, input validation

### **Feature Completeness**
- **Backend:** 100% - All core APIs implemented
- **Frontend:** 95% - Modern UI with all major features
- **Infrastructure:** 100% - Docker, monitoring, CI/CD
- **Documentation:** 100% - Comprehensive guides and examples

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** for the excellent async web framework
- **React** and **Tailwind CSS** for the modern frontend
- **Ollama** for local LLM support
- **Stripe** for payment processing
- **Redis** for caching and task queues
- **Docker** for containerization

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/mahiuddinalkamal/ai-research-assistant-platform/issues)
- **Discussions:** [GitHub Discussions](https://github.com/mahiuddinalkamal/ai-research-assistant-platform/discussions)
- **Documentation:** [docs/](docs/) folder

---

**Built with ❤️ for researchers, students, and professionals worldwide.**
