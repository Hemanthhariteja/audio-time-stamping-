# AI Audio Timestamping Platform - Architecture Design

## 1. System Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer (Next.js)                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Dashboard │ Upload │ Transcript │ Player │ Search │Export│   │
│  └──────────────────────────────────────────────────────────┘   │
│                      React Components + Tailwind CSS             │
└─────────────────────────────────────────────────────────────────┘
                              ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer (FastAPI)                 │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Route Handlers │ Middleware │ Error Handling │ Logging │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Service Layer (Business Logic)               │
│  ┌──────────────┬──────────────┬──────────────────────────┐     │
│  │ Upload       │ Transcription │ Export Service          │     │
│  │ Service      │ Service       │                         │     │
│  └──────────────┴──────────────┴──────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 Repository/Data Access Layer                     │
│  ┌──────────────┬──────────────┬──────────────────────────┐     │
│  │ User Repo    │ Project Repo  │ Transcript Repo         │     │
│  └──────────────┴──────────────┴──────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Database Layer (SQLite/PostgreSQL)            │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Users │ Projects │ AudioFiles │ Transcript Tables   │       │
│  └──────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   External Services & Utilities                  │
│  ┌──────────────┬──────────────┬──────────────────────────┐     │
│  │ FFmpeg       │ Faster-Whisper  │ File Storage (Local) │     │
│  └──────────────┴──────────────┴──────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Clean Architecture Layers

### Frontend Layer
- **Presentation Components**: UI components (Dashboard, Upload, Player, etc.)
- **State Management**: React Query for server state, React Hook Form for form state
- **Type Safety**: Full TypeScript implementation
- **Styling**: Tailwind CSS with component composition

### API Gateway Layer (FastAPI)
- **Route Handlers**: HTTP endpoints for all operations
- **Request/Response Validation**: Pydantic models
- **Middleware**: CORS, logging, error handling, rate limiting
- **Dependency Injection**: FastAPI dependency system

### Service Layer (Business Logic)
- **UploadService**: File validation, preprocessing coordination
- **TranscriptionService**: Whisper pipeline coordination
- **ExportService**: Multi-format export handling
- **SearchService**: Transcript searching
- **ProjectService**: Project management

### Repository Layer (Data Access)
- **UserRepository**: User data persistence
- **ProjectRepository**: Project CRUD operations
- **AudioFileRepository**: Audio file metadata
- **TranscriptRepository**: Transcript and timestamp storage
- **ExportRepository**: Export history tracking

### Models Layer (Domain)
- **User**: User account data
- **Project**: Project metadata
- **AudioFile**: Audio file information
- **Transcript**: Transcript data structures
- **TranscriptWord**: Word-level timing data
- **TranscriptSentence**: Sentence-level timing data

### Utilities Layer
- **Logger**: Structured logging
- **Config Manager**: Configuration loading and management
- **Error Handlers**: Custom exceptions and error responses
- **FFmpeg Helper**: Audio preprocessing commands
- **File Manager**: File operations (upload, storage, cleanup)

### Infrastructure Layer
- **Database**: SQLite connection and session management
- **File Storage**: Local file system management
- **Audio Processing**: FFmpeg subprocess management
- **Model Loading**: Faster-Whisper model initialization

## 3. Data Flow

### Upload & Transcription Flow
```
1. User selects/drags audio file
2. Frontend validates file type and size
3. Frontend sends to POST /upload
4. Backend validates file
5. Backend preprocesses with FFmpeg:
   - Convert to WAV
   - Convert to Mono
   - Resample to 16 kHz
   - Normalize volume
6. Backend stores processed audio
7. Backend creates Project & AudioFile records
8. Frontend polls GET /project/{id} for status
9. Backend runs Faster-Whisper transcription
10. Extracts word & sentence timestamps
11. Stores transcript data in database
12. Frontend receives transcript
```

### Playback Synchronization Flow
```
1. User plays audio
2. Audio player updates current time
3. Frontend uses WebSocket or polling to sync
4. Highlights current sentence in transcript
5. Highlights current word in transcript
6. Auto-scrolls transcript to current position
```

### Search & Export Flow
```
1. User searches text
2. Frontend sends GET /search?query={text}&project_id={id}
3. Backend searches TranscriptWords table
4. Returns matching timestamps
5. User clicks result
6. Audio jumps to timestamp
7. For export: POST /export with format type
8. Backend generates file and returns download
```

## 4. Technology Stack Rationale

### Frontend: Next.js + TypeScript
- **Why**: Server-side rendering, static generation, API routes, excellent TypeScript support
- **Alternatives Considered**: React (lacks built-in routing), Vue (smaller ecosystem)
- **Decision**: Next.js provides production-ready structure with minimal overhead

### Backend: Python + FastAPI
- **Why**: Fast, modern, perfect for ML/AI workloads, easy to integrate Faster-Whisper
- **Alternatives Considered**: Node.js (lacks ML library ecosystem), Go (overkill for this scale)
- **Decision**: Python native support for Faster-Whisper eliminates layer complexity

### Database: SQLite (PostgreSQL-ready)
- **Why**: Single file, no server dependency for personal computers, sufficient for 10-minute audio limit
- **Design**: Normalized schema designed to migrate to PostgreSQL without changes
- **Alternatives Considered**: PostgreSQL (overkill for Phase 1), MongoDB (poor for timestamping queries)
- **Migration Path**: Connection string configuration allows PostgreSQL drop-in replacement

### ML Model: Faster-Whisper Medium
- **Why**: Balance between accuracy and speed, supports word-level timestamps, GPU-optimized
- **Hardware Detection**: Automatic CUDA detection with fallback to CPU
- **Configuration**: Externalized in config file for easy model switching

### Audio Processing: FFmpeg
- **Why**: Industry standard, supports all required formats, reliable preprocessing
- **Alternative**: pydub (less efficient for batch operations)
- **Decision**: FFmpeg is more performant and battle-tested

### Frontend UI Libraries
- **React Query**: Server state management (transcripts, projects)
- **React Hook Form**: Form validation and submission
- **WaveSurfer.js**: Interactive waveform display and playback
- **Tailwind CSS**: Utility-first CSS for consistent, responsive design

## 5. Scalability & Performance Considerations

### Phase 1 (Personal Computer)
- Single CPU/GPU transcription
- SQLite file-based database
- Local file storage
- Synchronous upload + background transcription

### Future Scaling (Phase 2+)
- Queue system (Celery, RabbitMQ) for concurrent transcriptions
- PostgreSQL for multi-user support
- S3/cloud storage for files
- Redis for caching and session management
- Kubernetes orchestration
- Model serving with TensorRT

### Hardware Optimization
```
Detected: Intel i5 + GTX 1650 + 8GB RAM
├─ CPU: 4-8 cores available
├─ GPU: CUDA compute 7.1, 4GB VRAM
├─ RAM: 8GB total
│   ├─ OS: ~2GB
│   ├─ Whisper Medium: ~3GB
│   ├─ FFmpeg: ~500MB
│   └─ FastAPI/Database: ~1GB
└─ Conclusion: 10-minute audio processing is feasible
```

## 6. Error Handling Strategy

### Error Categories
1. **File Validation Errors** (400 Bad Request)
   - Unsupported format
   - File too large
   - Duration exceeds 10 minutes

2. **Processing Errors** (500 Internal Server Error)
   - FFmpeg failure
   - Whisper failure
   - Disk space issues

3. **Database Errors** (500 Internal Server Error)
   - Query failures
   - Migration failures

4. **Network Errors** (503 Service Unavailable)
   - Timeouts
   - Connection failures

### Error Response Format
```json
{
  "error": {
    "code": "AUDIO_FORMAT_UNSUPPORTED",
    "message": "The audio format MP2 is not supported",
    "details": {
      "supported_formats": ["MP3", "WAV", "M4A", "AAC", "OGG", "FLAC"],
      "provided_format": "MP2"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## 7. Security Architecture

### Input Validation
- File type validation (whitelist approach)
- File size validation (max 200MB)
- Duration validation (max 10 minutes)
- Filename sanitization (remove special chars, use UUID)

### Database Security
- SQL injection prevention: SQLAlchemy ORM (parameterized queries)
- XSS prevention: Input validation + output encoding
- CORS configuration: Restrict to specific origins

### File Security
- Store uploaded files outside web root
- Use UUID-based filenames
- Implement file cleanup after processing
- Virus scanning consideration for future

### Authentication (Architecture only, not Phase 1)
- JWT token structure designed
- Bearer token middleware ready
- User identification in API endpoints

## 8. Logging & Monitoring

### Logging Levels
- **DEBUG**: Detailed processing steps (Whisper inference, FFmpeg commands)
- **INFO**: Successful operations (upload completed, transcription started)
- **WARNING**: Recoverable issues (retries, fallbacks)
- **ERROR**: Failures requiring user action (file corruption, timeout)

### Logging Points
- API request/response
- File upload start/end
- Preprocessing start/end
- Transcription start/end
- Database operations
- Error stack traces

## 9. Testing Strategy

### Backend Testing (PyTest)
- **Unit Tests**: Service layer, repository layer, utilities
- **Integration Tests**: API endpoints with database
- **Fixture Tests**: Mock FFmpeg, mock Whisper

### Frontend Testing (Jest + React Testing Library)
- **Component Tests**: UI components in isolation
- **Integration Tests**: User flows (upload → playback)
- **Hook Tests**: React hooks and state management

### E2E Testing (Playwright)
- Full user workflows
- Cross-browser testing
- Audio playback synchronization verification

## 10. Deployment Architecture

### Development Environment
```
Local Machine
├─ Frontend: `npm run dev` (port 3000)
├─ Backend: `python -m uvicorn app.main:app --reload` (port 8000)
├─ Database: SQLite (local file)
└─ File Storage: Local ./uploads directory
```

### Production Environment (Docker)
```
Docker Container
├─ Frontend: Next.js (static export + node server)
├─ Backend: FastAPI (Uvicorn + Gunicorn)
├─ Database: SQLite mounted volume (prepared for PostgreSQL)
└─ File Storage: Volume mount (prepared for S3)
```

### Environment Configuration
- `.env.local`: Development secrets
- `.env.production`: Production secrets
- `config/settings.yml`: Model and processing configuration
- Docker Compose: Orchestration definition

## 11. Architecture Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend Framework | Next.js | Built-in routing, SSR, TypeScript support |
| Backend Framework | FastAPI | Modern, async, ML-friendly, auto-docs |
| Database | SQLite | Lightweight, no server, PostgreSQL-compatible schema |
| ML Model | Faster-Whisper Medium | Speed/accuracy balance, GPU-optimized |
| Audio Processing | FFmpeg | Industry standard, all formats, reliable |
| ORM | SQLAlchemy | Type-safe queries, migration support (Alembic) |
| Frontend State | React Query + RTK | Separation of concerns, server/client state |
| Styling | Tailwind CSS | Responsive, consistent, minimal bundle |
| Authentication | JWT (designed) | Stateless, scalable, industry standard |
| File Storage | Local FS (PostgreSQL-ready) | Simple for Phase 1, S3 for Phase 2+ |

