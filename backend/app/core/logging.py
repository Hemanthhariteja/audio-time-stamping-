"""
Logging configuration for the application.
"""

import json
import logging
import logging.handlers
from typing import Optional

from app.core.config import settings


def setup_logging() -> None:
    """Configure logging for the application."""
    
    # Create logger
    logger = logging.getLogger("app")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Create formatters
    if settings.LOG_FORMAT == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if configured)
    if settings.LOG_FILE:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=settings.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance by name."""
    return logging.getLogger(name)
