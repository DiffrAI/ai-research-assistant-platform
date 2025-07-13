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
   - ✅ Research endpoints (with some configuration issues)

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
   - ⚠️ LangGraph workflow configuration issues
   - ⚠️ Missing LangFuse environment variables
   - ⚠️ Research endpoint returns configuration errors

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

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./ai_research.db

# Security
SECRET_KEY=your-secret-key-change-in-production

# AI Services
OPENAI_API_KEY=your-openai-key
TAVILY_API_KEY=your-tavily-key

# Payment (Stripe)
STRIPE_SECRET_KEY=your-stripe-secret
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable

# Monitoring (LangFuse)
LANGFUSE_HOST=your-langfuse-host
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
```

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

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## 🎯 Next Steps

1. Fix frontend startup issues
2. Configure LangFuse for research service
3. Add proper error handling for research workflows
4. Implement saved research functionality
5. Add analytics and trending topics
6. Set up proper environment variables

## 📄 License

This project is licensed under the MIT License.
