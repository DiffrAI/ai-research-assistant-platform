#!/bin/bash

# Kill any existing processes on ports 3000 and 8002
echo "Killing existing processes..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8002 | xargs kill -9 2>/dev/null || true

# Wait a moment for processes to be killed
sleep 2

# Start backend
echo "Starting FastAPI backend..."
source .venv/bin/activate
uv run python main.py &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8002/health > /dev/null; then
    echo "Backend is running on http://localhost:8002"
else
    echo "Backend failed to start"
    exit 1
fi

# Start frontend
echo "Starting React frontend..."
cd frontend
PORT=3000 npm start &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "Frontend is running on http://localhost:3000"
else
    echo "Frontend may still be starting..."
fi

echo ""
echo "🎉 Development environment started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8002"
echo "API Docs: http://localhost:8002/docs"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user to stop
wait 