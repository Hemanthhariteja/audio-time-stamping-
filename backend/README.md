"""Backend setup and development guide."""

# AI Audio Timestamping Platform - Backend

## Overview

This is the backend service for the AI Audio Timestamping Platform. It's built with:

- **FastAPI**: Modern async Python web framework
- **SQLAlchemy**: ORM for database operations
- **Faster-Whisper**: Speech-to-text with word-level timestamps
- **FFmpeg**: Audio processing and format conversion

## Quick Start

### Prerequisites

- Python 3.10+
- FFmpeg and FFprobe
- CUDA toolkit (optional, for GPU acceleration)

### Installation

1. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Initialize database**
```bash
python -c "from app.db import init_db; init_db()"
```

5. **Run development server**
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## Project Structure

```
backend/
├── app/
│   ├── api/                 # API route definitions
│   │   └── v1/
│   │       └── endpoints/   # Endpoint handlers
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings management
│   │   ├── exceptions.py    # Custom exceptions
│   │   └── logging.py       # Logging setup
│   ├── db/                  # Database setup
│   │   └── database.py      # SQLAlchemy configuration
│   ├── models/              # Database models
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic
│   ├── schemas/             # Pydantic schemas
│   ├── utils/               # Utility functions
│   │   ├── audio_processor.py  # FFmpeg integration
│   │   └── file_manager.py     # File operations
│   ├── middleware/          # FastAPI middleware
│   └── main.py              # Application factory
├── tests/                   # Test suite
├── alembic/                 # Database migrations
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── run.py                   # Entry point
└── README.md               # This file
```

## API Endpoints

### Health Checks
- `GET /api/v1/health` - Service health status
- `GET /api/v1/health/live` - Liveness probe
- `GET /api/v1/health/ready` - Readiness probe

### Projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List user projects
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Audio Files
- `POST /api/v1/audio/upload/{project_id}` - Upload audio file
- `GET /api/v1/audio/{id}` - Get audio file details
- `POST /api/v1/audio/{id}/preprocess` - Preprocess for transcription

## Configuration

### Environment Variables

Key variables in `.env`:

```
# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=False
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///./data/audio_timestamping.db

# Upload
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=100

# Whisper
WHISPER_MODEL_NAME=medium
WHISPER_DEVICE=auto
WHISPER_COMPUTE_TYPE=auto

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

See `backend/.env.example` for complete list.

## Database

### Initialization

```bash
# Using direct import
python -c "from app.db import init_db; init_db()"

# Using Alembic (when migrations exist)
alembic upgrade head
```

### Models

The database includes 7 tables:

1. **users** - User accounts
2. **projects** - Project containers
3. **audio_files** - Uploaded audio files
4. **transcripts** - Full transcriptions
5. **transcript_sentences** - Sentence boundaries
6. **transcript_words** - Word-level details
7. **exports** - Export history

### Migrations

Alembic is configured for database version control:

```bash
# Create new migration
alembic revision --autogenerate -m "migration description"

# Apply migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Run Specific Tests

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Specific file
pytest tests/test_health.py
```

## Development

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8

# Type checking
mypy .
```

### Logging

The application uses structured logging with JSON format:

```python
from app.core import get_logger

logger = get_logger(__name__)
logger.info("Message", extra={"key": "value"})
```

## Audio Processing

### Supported Formats

- MP3
- WAV
- M4A
- AAC
- OGG
- FLAC
- MP4

### Preprocessing

Audio files are automatically converted to:
- Format: WAV (PCM 16-bit)
- Sample rate: 16kHz
- Channels: Mono (1)

### GPU Support

The system automatically detects and uses GPU if available:

```
✓ NVIDIA GPU with CUDA → Uses float16 compute type
✗ No GPU → Falls back to CPU with int8 quantization
```

## Deployment

### Docker

```bash
# Build image
docker build -t audio-timestamping-backend .

# Run container
docker run -p 8000:8000 audio-timestamping-backend
```

### Production Checklist

- [ ] Update SECRET_KEY in .env
- [ ] Set DEBUG=False
- [ ] Configure CORS_ORIGINS for frontend URL
- [ ] Setup external database (PostgreSQL recommended)
- [ ] Configure logging to file system
- [ ] Setup file storage (local or S3)
- [ ] Enable rate limiting
- [ ] Setup monitoring and alerting
- [ ] Configure backup strategy

## Troubleshooting

### FFmpeg Not Found

```bash
# Windows: Install via Windows Store or chocolatey
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg

# Set path if not in PATH
# Add to .env: FFMPEG_PATH=/path/to/ffmpeg
```

### Database Locked

Remove existing database and reinitialize:

```bash
rm data/audio_timestamping.db
python -c "from app.db import init_db; init_db()"
```

### Out of Memory

Reduce Whisper model size or use CPU:

```env
WHISPER_MODEL_NAME=base  # smaller model
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
```

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review API documentation at `http://localhost:8000/api/docs`
3. Check logs in `logs/app.log`
