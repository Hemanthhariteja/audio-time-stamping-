"""Error handling middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger(__name__)


async def exception_handler(request: Request, exc: Exception):
    """Handle application exceptions."""
    if isinstance(exc, AppException):
        logger.error(
            f"Application error: {exc.error_code} - {exc.message}",
            extra={"error_code": exc.error_code, "details": exc.details},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "detail": exc.message,
                "details": exc.details,
            },
        )

    # Unhandled exception
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
        },
    )
