"""Enhanced entry point to run the application with improved error handling and graceful shutdown."""

import multiprocessing
import signal
import subprocess
import sys
from typing import Optional

import uvicorn
from loguru import logger

from app.core.config import AppEnvs, settings


def calculate_worker_count() -> int:
    """Calculate optimal worker count: 2 * CPU cores + 1."""
    return multiprocessing.cpu_count() * 2 + 1


def setup_signal_handlers() -> None:
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def validate_environment() -> None:
    """Validate environment configuration."""
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    logger.info(f"Host: {settings.HOST}")
    logger.info(f"Port: {settings.PORT}")
    
    if settings.ENVIRONMENT == AppEnvs.PRODUCTION:
        if settings.SECRET_KEY == "your-secret-key-change-in-production":
            logger.error("SECRET_KEY must be changed in production!")
            sys.exit(1)
        
        if settings.DEBUG:
            logger.warning("DEBUG mode is enabled in production!")


def start_development_server() -> None:
    """Start the FastAPI application with uvicorn for development."""
    try:
        worker_count = settings.WORKER_COUNT or calculate_worker_count()
        logger.info(f"🚀 Starting development server with {worker_count} worker(s)")
        
        uvicorn.run(
            app="app.core.server:app",
            host=settings.HOST,
            port=settings.PORT,
            workers=worker_count,
            reload=settings.ENVIRONMENT == "development",
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True,
        )
    except Exception as e:
        logger.error(f"Failed to start development server: {e}")
        sys.exit(1)


def start_production_server() -> None:
    """Start the FastAPI application with Gunicorn for production."""
    try:
        logger.info("✅ Production environment detected. Launching with Gunicorn...")
        
        # Validate production settings
        if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production":
            logger.error("SECRET_KEY must be set in production!")
            sys.exit(1)
        
        # Start with Gunicorn
        subprocess.run(["./start.sh"], check=True)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to start production server: {e}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error("❌ start.sh script not found!")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error starting production server: {e}")
        sys.exit(1)


def main() -> None:
    """Main application entry point with enhanced error handling."""
    try:
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers()
        
        # Validate environment configuration
        validate_environment()
        
        # Start appropriate server based on environment
        if settings.ENVIRONMENT == AppEnvs.PRODUCTION:
            start_production_server()
        else:
            start_development_server()
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
