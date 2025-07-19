#!/bin/bash

# Load environment variables from .env
set -a
source .env
set +a

# Default values if not set in .env
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
APP_MODULE="app.core.server:app"
# Calculate optimal worker count: 2 * CPU cores + 1. For production, consider external auto-scaling solutions.
WORKERS=$(python3 -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)")

echo "🚀 Starting FastAPI app with Gunicorn on $HOST:$PORT with $WORKERS workers..."

# Gunicorn logs to stdout/stderr, which is typically captured by container orchestration/process managers.
# For advanced logging integration (e.g., to Loki), configure the Gunicorn logger in Python or the deployment environment.
exec gunicorn "$APP_MODULE" \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "$WORKERS" \
    --bind "$HOST:$PORT"