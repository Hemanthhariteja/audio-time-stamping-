# Environment Variables Reference

## Backend (.env for backend/)

```bash
# Application
APP_NAME=Audio Timestamping Platform
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./app.db
# For production: postgresql://user:password@localhost:5432/audio_timestamping

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
CORS_ALLOW_CREDENTIALS=true

# File Storage
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=200
MAX_AUDIO_DURATION_MINUTES=10

# Whisper Configuration
WHISPER_MODEL_NAME=medium
WHISPER_MODEL_CACHE=./models
WHISPER_LANGUAGE=en
WHISPER_DEVICE=auto
WHISPER_COMPUTE_TYPE=auto

# Audio Processing
FFMPEG_PATH=ffmpeg
FFMPEG_TIMEOUT_SECONDS=600

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_PERIOD_SECONDS=3600

# Authentication (for future use)
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Logging
LOG_FORMAT=json
LOG_FILE=./logs/app.log
LOG_MAX_SIZE_MB=100
LOG_BACKUP_COUNT=5
```

## Frontend (.env.local for frontend/)

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=Audio Timestamping
NEXT_PUBLIC_APP_VERSION=1.0.0

# Features
NEXT_PUBLIC_ENABLE_DARK_MODE=true
NEXT_PUBLIC_ENABLE_EXPORT=true
NEXT_PUBLIC_ENABLE_SEARCH=true

# Audio Settings
NEXT_PUBLIC_MAX_AUDIO_DURATION_MINUTES=10
NEXT_PUBLIC_MAX_FILE_SIZE_MB=200

# UI Configuration
NEXT_PUBLIC_ITEMS_PER_PAGE=10
NEXT_PUBLIC_TOAST_DURATION_MS=3000
NEXT_PUBLIC_POLLING_INTERVAL_MS=1000

# Development
NEXT_PUBLIC_DEBUG=true
```

## Environment Configuration Strategy

### Development (.env.local)
- Local API endpoints
- Debug logging enabled
- SQLite database
- Shorter timeouts for testing
- Mock data available

### Staging (.env.staging)
- Staging API endpoints
- Info logging
- PostgreSQL database
- Production-like timeouts
- Real data samples

### Production (.env.production)
- Production API endpoints
- Error logging only
- PostgreSQL database
- Standard timeouts
- Real data only

## Required System Environment

### Python (Backend)
```bash
# Check Python version
python --version  # Should be 3.10+

# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Node.js (Frontend)
```bash
# Check Node version
node --version  # Should be 18+
npm --version   # Should be 9+

# Install dependencies
npm install

# Set up environment
cp .env.example .env.local
```

### FFmpeg (System)
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows (via Chocolatey)
choco install ffmpeg

# Verify installation
ffmpeg -version
```

### CUDA (Optional, for GPU support)
```bash
# Check if installed
nvidia-smi

# If not installed, download from:
# https://developer.nvidia.com/cuda-toolkit
```

## Configuration Files Reference

### `backend/app/config/settings.py`
Pydantic BaseSettings for environment variable validation
- Loads from .env file
- Provides typed access to all configuration
- Validates on startup

### `backend/app/config/app_config.yaml`
Application-level configuration
```yaml
application:
  name: Audio Timestamping Platform
  version: 1.0.0
  environment: development

logging:
  level: INFO
  format: json
  file: logs/app.log
```

### `backend/app/config/model_config.yaml`
Machine learning model configuration
```yaml
model:
  name: faster-whisper
  size: medium
  language: en

inference:
  device: auto  # cuda or cpu
  compute_type: auto
  beam_size: 5
  best_of: 5
  temperature: 0
  word_timestamps: true
  vad_filter: true

hardware_detection:
  check_cuda: true
  check_memory: true
  fallback_to_cpu: true
```

## Secrets Management Strategy

### Development
- Use .env.local files (NOT committed to git)
- Secrets in plain text (for local testing only)
- Reset after each session

### Production
- Use environment variables
- Use Docker secrets or managed secrets service
- Rotate secrets regularly
- Never commit to repository

### Tools
- `.env.example` - template file (committed)
- `.env.local` - local secrets (NOT committed)
- `.gitignore` - prevents accidental commits

## Validation Checklist

Before starting Phase 2, ensure:

### Backend Requirements
- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] FFmpeg installed and in PATH
- [ ] CUDA toolkit installed (if GPU available)
- [ ] `.env.local` created from template
- [ ] All environment variables validated

### Frontend Requirements
- [ ] Node.js 18+ installed
- [ ] npm 9+ installed
- [ ] `.env.local` created from template
- [ ] API_BASE_URL points to backend

### System Requirements
- [ ] 20GB storage available
- [ ] 8GB RAM (16GB recommended)
- [ ] Stable internet connection
- [ ] Git configured

## Quick Reference

### Start Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:3000
```

### View API Docs
http://localhost:8000/docs

### Database
```bash
# Initialize
python backend/scripts/init-db.py

# Migrate
cd backend
alembic upgrade head

# Check status
alembic current
```

