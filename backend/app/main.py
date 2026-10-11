"""Main FastAPI application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db import init_db
from app.middleware.cors import setup_cors_middleware
from app.middleware.error_handler import exception_handler
from app.core.exceptions import AppException

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Setup logging
    setup_logging()
    
    # Create app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered audio transcription platform with word and sentence-level timestamps",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url="/api/redoc",
    )
    
    # Setup CORS
    setup_cors_middleware(app)
    
    # Setup exception handler
    app.add_exception_handler(AppException, exception_handler)
    
    # Mount static uploads directory for frontend audio access
    settings.upload_dir_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir_path)), name="uploads")

    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize database and app on startup."""
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Database: {settings.DATABASE_URL}")
        
        try:
            init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        logger.info(f"Shutting down {settings.APP_NAME}")
    
    return app


# Create app instance
app = create_app()
