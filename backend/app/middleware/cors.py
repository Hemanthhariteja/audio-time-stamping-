"""CORS middleware configuration."""

from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def setup_cors_middleware(app):
    """Setup CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
