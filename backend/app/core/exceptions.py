"""
Custom exception classes for the application.
"""

from typing import Any, Optional


class AppException(Exception):
    """Base exception for the application."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize exception."""
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error exception."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize validation error."""
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class NotFoundError(AppException):
    """Resource not found exception."""

    def __init__(
        self,
        message: str,
        resource_type: str = "Resource",
        resource_id: Optional[str] = None,
    ) -> None:
        """Initialize not found error."""
        details = {"resource_type": resource_type}
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class UnauthorizedError(AppException):
    """Unauthorized access exception."""

    def __init__(self, message: str = "Unauthorized access") -> None:
        """Initialize unauthorized error."""
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401,
        )


class ForbiddenError(AppException):
    """Forbidden access exception."""

    def __init__(self, message: str = "Access forbidden") -> None:
        """Initialize forbidden error."""
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=403,
        )


class ConflictError(AppException):
    """Conflict exception."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize conflict error."""
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details,
        )


class FileUploadError(AppException):
    """File upload error exception."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize file upload error."""
        super().__init__(
            message=message,
            error_code="FILE_UPLOAD_ERROR",
            status_code=400,
            details=details,
        )


class AudioProcessingError(AppException):
    """Audio processing error exception."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize audio processing error."""
        super().__init__(
            message=message,
            error_code="AUDIO_PROCESSING_ERROR",
            status_code=500,
            details=details,
        )


class TranscriptionError(AppException):
    """Transcription error exception."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize transcription error."""
        super().__init__(
            message=message,
            error_code="TRANSCRIPTION_ERROR",
            status_code=500,
            details=details,
        )


class ExportError(AppException):
    """Export error exception."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize export error."""
        super().__init__(
            message=message,
            error_code="EXPORT_ERROR",
            status_code=500,
            details=details,
        )


class RateLimitError(AppException):
    """Rate limit exceeded exception."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        """Initialize rate limit error."""
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )
