"""Request/response logging middleware."""

import time
import json

from fastapi import Request
from app.core.logging import get_logger

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next):
    """Log request and response details."""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query),
        },
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": process_time,
        },
    )
    
    return response
