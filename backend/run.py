#!/usr/bin/env python
"""Entry point for the application."""

import uvicorn

from app.core.config import settings
from app.main import app


def main():
    """Run the application."""
    uvicorn.run(
        "app.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
