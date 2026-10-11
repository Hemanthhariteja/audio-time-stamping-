# AI Audio Timestamping Platform

> A modern, production-ready web application for converting English audio into accurate transcripts with precise word-level and sentence-level timestamps.

## 🎯 Project Overview

This project builds a complete transcription platform combining:
- **Modern Frontend**: Next.js + TypeScript + React
- **Powerful Backend**: Python + FastAPI
- **State-of-the-art ML**: Faster-Whisper for speech recognition
- **Professional UI**: Dark mode, responsive, interactive waveform
- **Production Ready**: Docker, CI/CD, comprehensive testing

## 📋 Features

### Current Progress
- ✓ Architecture documentation
- ✓ Database schema design
- ✓ Backend API and services
- ✓ Whisper transcription integration foundation
- ✓ Next.js frontend shell and project workflow
- ✓ Docker and CI/CD scaffolding
- ⏳ Full end-to-end transcription run validated in a development environment

### Planned Features
- Audio upload with drag-and-drop
- Live transcription with progress tracking
- Interactive transcript viewer with timestamps
- Audio player with waveform synchronization
- Full-text search across transcripts
- Export to TXT, JSON, CSV, SRT, VTT formats
- Project management and upload history
- Dark mode support
- Responsive design for all devices

## 🏗️ Architecture

### Clean Architecture Layers
```
Presentation Layer (Next.js Components)
    ↓
API Gateway Layer (FastAPI Routes)
    ↓
Business Logic Layer (Services)
    ↓
Data Access Layer (Repositories)
    ↓
Database Layer (SQLite/PostgreSQL)
```

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, React Query |
| Backend | Python 3.10+, FastAPI, SQLAlchemy |
| Database | SQLite (→ PostgreSQL) |
| ML Model | Faster-Whisper Medium |
| Audio Processing | FFmpeg |
| Testing | Jest, PyTest, Playwright |
| Containerization | Docker, Docker Compose |

## 📊 Database Design

7 normalized tables with efficient relationships:
- **Users**: User accounts and authentication
- **Projects**: Project grouping
- **AudioFiles**: Uploaded audio metadata
- **Transcripts**: Full transcript storage
- **TranscriptSentences**: Sentence-level timestamps
- **TranscriptWords**: Word-level timestamps and confidence
- **Exports**: Export history and formats

## 🔌 API Endpoints

- `POST /upload` - Upload and preprocess audio
- `GET /projects` - List user projects
- `GET /project/{id}` - Get project details
- `GET /transcript/{id}` - Get full transcript with timestamps
- `GET /search` - Search transcripts
- `POST /export` - Export in multiple formats
- `DELETE /project/{id}` - Delete project
- `GET /health` - Health check

## 📈 Implementation Roadmap

### Phase 1: Requirements & Architecture ✓
- Architecture design
- Database schema
- API specification
- Folder structure
- Estimated: 2-3 days

### Phase 2: Backend Setup ⏳
- FastAPI application
- Database layer
- Upload API
- FFmpeg preprocessing
- Estimated: 4-5 days

### Phase 3: Transcription Engine
- Faster-Whisper integration
- Timestamp extraction
- Database storage
- Background processing
- Estimated: 5-7 days

### Phase 4: Frontend Development
- Dashboard
- Upload interface
- Transcript viewer
- Audio player
- Search & export
- Estimated: 6-8 days

### Phase 5: Testing & Deployment
- E2E testing
- Performance optimization
- Docker setup
- CI/CD pipeline
- Production deployment
- Estimated: 5-7 days

**Total Timeline**: 22-30 days (full-time development)

## 💻 Hardware Requirements

### Minimum (Target System)
- Intel i5 processor
- NVIDIA GTX 1650 (4GB VRAM)
- 8GB RAM
- 20GB storage

### Optimal
- Intel i7 or newer
- NVIDIA RTX 3060+ (8GB+ VRAM)
- 16GB RAM
- 50GB storage

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- FFmpeg (system dependency)
- NVIDIA CUDA Toolkit (for GPU support, optional)

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd audio-timestamping

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database initialization
python scripts/init-db.py
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --port 8000

# In another terminal - Frontend setup
cd ../frontend
npm install
npm run dev  # Runs on http://localhost:3000
```

### Docker Setup

```bash
docker-compose up --build
```

The API will be available on http://localhost:8000 and the frontend on http://localhost:3000.

## 📖 Documentation

All documentation is in the `docs/` folder:

- **[01-ARCHITECTURE.md](docs/01-ARCHITECTURE.md)** - System architecture and design patterns
- **[02-FOLDER_STRUCTURE.md](docs/02-FOLDER_STRUCTURE.md)** - Complete directory layout
- **[03-DATABASE_DESIGN.md](docs/03-DATABASE_DESIGN.md)** - ER diagram and schema
- **[04-API_SPECIFICATION.md](docs/04-API_SPECIFICATION.md)** - All 8 endpoints with examples
- **[05-IMPLEMENTATION_ROADMAP.md](docs/05-IMPLEMENTATION_ROADMAP.md)** - Detailed task breakdown
- **[06-PROJECT_SUMMARY.md](docs/06-PROJECT_SUMMARY.md)** - Executive summary

## 🧪 Testing Strategy

### Backend Testing (PyTest)
- Unit tests for services and utilities
- Integration tests for APIs
- Fixtures for test data
- Target: >80% coverage

### Frontend Testing (Jest + React Testing Library)
- Component tests
- Hook tests
- Integration tests
- Target: >70% coverage

### E2E Testing (Playwright)
- Full user workflows
- Cross-browser compatibility
- Responsive design validation

## 🔒 Security

- Input validation on all endpoints
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (React + Pydantic)
- Rate limiting on all endpoints
- Secure file upload handling
- JWT architecture prepared (Phase 1)

## 🚦 Supported Audio Formats

- MP3
- WAV
- M4A
- AAC
- OGG
- FLAC
- MP4 (audio extracted)

**Constraints**:
- Maximum file size: 200 MB
- Maximum duration: 10 minutes

## ⚙️ Configuration

Configuration is externalized in:
- `app_config.yaml` - Application settings
- `model_config.yaml` - Whisper model configuration
- `.env` - Environment variables

Example `model_config.yaml`:
```yaml
model:
  name: faster-whisper
  size: medium
  language: en
  
inference:
  device: auto  # cuda or cpu (auto-detected)
  compute_type: auto  # float16 for GPU, int8 for CPU
  beam_size: 5
  best_of: 5
  temperature: 0
  word_timestamps: true
  vad_filter: true
```

## 📊 Performance Targets

- **Transcription**: < 1x audio duration
- **Search**: < 500ms response
- **UI Response**: < 200ms
- **Memory**: < 4GB for 10-min audio
- **GPU Utilization**: 70-90%

## 🐳 Docker Support

Complete Docker setup with:
- Separate Dockerfiles for frontend and backend
- Docker Compose for local development
- Multi-stage builds for optimization
- Volume mounting for development
- Ready for production deployment

## 🔄 CI/CD Pipeline

GitHub Actions workflows (Phase 5):
- Automated testing on push
- Linting and code quality checks
- Security scanning
- Automated deployment

## 📝 Code Quality Standards

- **Type Safety**: Full TypeScript (frontend), Type hints (backend)
- **SOLID Principles**: All layers follow SOLID
- **Clean Code**: Meaningful names, single responsibility
- **Testing**: Comprehensive test coverage
- **Documentation**: Inline comments for complex logic

## 🤝 Contributing

(Guidelines to be added)

## 📄 License

(License to be determined)

## 🎓 Architecture Principles

1. **Clean Architecture**: Separation of concerns across layers
2. **Dependency Injection**: Loose coupling via DI
3. **Repository Pattern**: Data abstraction for potential multi-DB support
4. **Soft Deletes**: Data retention and audit trails
5. **PostgreSQL Ready**: SQLite schema is PostgreSQL-compatible
6. **Scalability**: Design allows adding caching, queuing, microservices

## 📞 Support

### Phase 1 Status
- ✓ Requirements validated
- ✓ Architecture finalized
- ✓ Database designed
- ✓ API specified
- ⏳ Awaiting approval to proceed to Phase 2

### Documentation
See the `docs/` folder for complete technical documentation.

---

**Current Version**: 1.0.0 (Phase 1 - Design)  
**Last Updated**: 2024-01-15  
**Status**: ✓ Ready for Review

