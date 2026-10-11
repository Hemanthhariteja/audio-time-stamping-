"""
Configuration management for the application.
Supports environment-based configuration with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "AI Audio Timestamping Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # Server
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # API Configuration
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "*",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    # Database
    DATABASE_URL: str = "sqlite:///D:/audio time stamping/data/audio_timestamping.db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 100  # 100MB max
    MAX_UPLOAD_SIZE_BYTES: int = 100 * 1024 * 1024
    ALLOWED_AUDIO_FORMATS: list[str] = [
        "mp3",
        "wav",
        "m4a",
        "aac",
        "ogg",
        "flac",
        "mp4",
    ]

    # Audio Processing
    FFMPEG_PATH: Optional[str] = None  # Auto-detect if not specified
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHANNELS: int = 1  # Mono
    AUDIO_BITRATE: str = "128k"

    # Whisper Model
    WHISPER_MODEL_NAME: str = "medium"  # base, small, medium, large
    WHISPER_DEVICE: str = "auto"  # auto, cuda, cpu
    WHISPER_COMPUTE_TYPE: str = "auto"  # auto, float16, int8
    WHISPER_NUM_WORKERS: int = 1
    WHISPER_BEAM_SIZE: int = 5
    WHISPER_BEST_OF: int = 5
    WHISPER_TEMPERATURE: float = 0.0
    WHISPER_VAD_FILTER: bool = True

    # Export Configuration
    EXPORT_DIR: str = "exports"
    ALLOWED_EXPORT_FORMATS: list[str] = ["txt", "json", "csv", "srt", "vtt"]
    EXPORT_RETENTION_DAYS: int = 30  # Auto-delete exports after 30 days

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or standard
    LOG_FILE: Optional[str] = "logs/app.log"

    # Performance
    WORKER_THREADS: int = 4
    PROCESSING_TIMEOUT_SECONDS: int = 300  # 5 minutes
    UPLOAD_CLEANUP_INTERVAL_HOURS: int = 24

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True

    @property
    def database_url_for_alembic(self) -> str:
        """Return database URL for Alembic migrations."""
        if self.DATABASE_URL.startswith("sqlite"):
            # SQLite doesn't support async, use sync URL
            return self.DATABASE_URL
        return self.DATABASE_URL

    @property
    def upload_dir_path(self) -> Path:
        """Return upload directory as Path object."""
        return Path(self.UPLOAD_DIR)

    @property
    def export_dir_path(self) -> Path:
        """Return export directory as Path object."""
        return Path(self.EXPORT_DIR)

    @property
    def log_dir_path(self) -> Optional[Path]:
        """Return log directory as Path object."""
        if self.LOG_FILE:
            return Path(self.LOG_FILE).parent
        return None

    def __init__(self, **data):
        """Initialize settings and create necessary directories."""
        super().__init__(**data)
        
        # Create necessary directories
        self.upload_dir_path.mkdir(parents=True, exist_ok=True)
        self.export_dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create log directory if needed
        if self.log_dir_path:
            self.log_dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create data directory for SQLite
        if self.DATABASE_URL.startswith("sqlite"):
            db_path = Path(self.DATABASE_URL.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
