"""Request and response schemas using Pydantic."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """User response schema."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    """Base project schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project creation schema."""

    user_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    """Project update schema."""

    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response schema."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# Audio File Schemas
class AudioFileBase(BaseModel):
    """Base audio file schema."""

    original_filename: str
    file_format: str
    file_size_bytes: int
    duration_seconds: Optional[float] = None


class AudioFileResponse(AudioFileBase):
    """Audio file response schema."""

    id: int
    project_id: int
    stored_filename: str
    upload_status: str
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class AudioFileUploadResponse(BaseModel):
    """Audio file upload response schema."""

    id: int
    original_filename: str
    stored_filename: str
    upload_status: str
    created_at: datetime


# Transcript Schemas
class TranscriptWordResponse(BaseModel):
    """Transcript word response schema."""

    id: int
    word_text: str
    start_time: float
    end_time: float
    confidence_score: Optional[float] = None
    word_index: int

    class Config:
        """Pydantic config."""

        from_attributes = True


class TranscriptSentenceResponse(BaseModel):
    """Transcript sentence response schema."""

    id: int
    sentence_text: str
    start_time: float
    end_time: float
    confidence_score: Optional[float] = None
    sentence_index: int
    words: list[TranscriptWordResponse] = []

    class Config:
        """Pydantic config."""

        from_attributes = True


class TranscriptResponse(BaseModel):
    """Transcript response schema."""

    id: int
    audio_file_id: int
    full_text: str
    language_code: str
    confidence_score: Optional[float] = None
    processing_status: str
    sentences: list[TranscriptSentenceResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class TranscriptDetailedResponse(TranscriptResponse):
    """Detailed transcript response with all words."""

    pass


# Export Schemas
class ExportRequest(BaseModel):
    """Export request schema."""

    export_format: str = Field(..., pattern="^(txt|json|csv|srt|vtt)$")


class ExportResponse(BaseModel):
    """Export response schema."""

    id: int
    transcript_id: int
    export_format: str
    file_path: str
    file_size_bytes: int
    download_count: int
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# Search Schemas
class SearchRequest(BaseModel):
    """Search request schema."""

    query: str = Field(..., min_length=1, max_length=255)


class SearchResult(BaseModel):
    """Search result schema."""

    sentence_id: int
    sentence_text: str
    start_time: float
    end_time: float
    context: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response schema."""

    query: str
    total_results: int
    results: list[SearchResult]


# Error Response Schemas
class ErrorDetail(BaseModel):
    """Error detail schema."""

    error_code: str
    message: str
    details: Optional[dict] = None


class ValidationErrorResponse(BaseModel):
    """Validation error response schema."""

    errors: list[dict]


# Pagination Schemas
class PaginationParams(BaseModel):
    """Pagination parameters."""

    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    total: int
    skip: int
    limit: int
    items: list
