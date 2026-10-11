"""Middleware module."""

from app.middleware.cors import setup_cors_middleware
from app.middleware.error_handler import exception_handler

__all__ = ["setup_cors_middleware", "exception_handler"]
