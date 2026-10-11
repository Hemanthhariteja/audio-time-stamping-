# Project Folder Structure

## Complete Directory Layout

```
audio-timestamping/
│
├── frontend/                          # Next.js Application
│   ├── app/                           # Next.js App Router
│   │   ├── layout.tsx                 # Root layout with providers
│   │   ├── page.tsx                   # Home/Dashboard page
│   │   ├── globals.css                # Global styles
│   │   ├── (dashboard)/               # Dashboard routes group
│   │   │   ├── layout.tsx             # Dashboard layout with sidebar
│   │   │   ├── page.tsx               # Dashboard page
│   │   │   ├── upload/
│   │   │   │   ├── page.tsx           # Upload page
│   │   │   │   └── components/
│   │   │   │       └── UploadZone.tsx
│   │   │   ├── transcript/[id]/
│   │   │   │   ├── page.tsx           # Transcript viewer
│   │   │   │   └── components/
│   │   │   │       ├── Player.tsx
│   │   │   │       ├── Transcript.tsx
│   │   │   │       ├── Search.tsx
│   │   │   │       └── ExportMenu.tsx
│   │   │   └── project/[id]/
│   │   │       ├── page.tsx           # Project details
│   │   │       └── components/
│   │   │           └── ProjectInfo.tsx
│   │   └── api/                       # API Routes (optional, for proxy)
│   │       └── proxy/[...path]/
│   │
│   ├── components/                    # Reusable UI Components
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── audio/
│   │   │   ├── Waveform.tsx
│   │   │   ├── AudioPlayer.tsx
│   │   │   └── PlaybackControls.tsx
│   │   ├── transcript/
│   │   │   ├── TranscriptViewer.tsx
│   │   │   ├── TranscriptLine.tsx
│   │   │   ├── WordHighlight.tsx
│   │   │   └── SentenceHighlight.tsx
│   │   └── layouts/
│   │       ├── MainLayout.tsx
│   │       └── AuthLayout.tsx
│   │
│   ├── hooks/                         # Custom React Hooks
│   │   ├── useProject.ts
│   │   ├── useTranscript.ts
│   │   ├── useAudioPlayer.ts
│   │   ├── useUpload.ts
│   │   └── useSearch.ts
│   │
│   ├── services/                      # API Client Services
│   │   ├── api.ts                     # Axios/fetch configuration
│   │   ├── projectService.ts
│   │   ├── transcriptService.ts
│   │   ├── uploadService.ts
│   │   └── exportService.ts
│   │
│   ├── types/                         # TypeScript Type Definitions
│   │   ├── index.ts
│   │   ├── api.ts
│   │   ├── models.ts
│   │   └── forms.ts
│   │
│   ├── utils/                         # Utility Functions
│   │   ├── format.ts                  # Time formatting, etc.
│   │   ├── validation.ts
│   │   ├── error-handler.ts
│   │   └── constants.ts
│   │
│   ├── context/                       # React Context (if needed)
│   │   └── AppContext.tsx
│   │
│   ├── public/                        # Static assets
│   │   ├── icons/
│   │   ├── images/
│   │   └── fonts/
│   │
│   ├── .env.local                     # Local environment variables
│   ├── .env.example                   # Example environment file
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── package.json
│   └── README.md
│
├── backend/                           # FastAPI Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app initialization
│   │   │
│   │   ├── api/                       # API Routes
│   │   │   ├── __init__.py
│   │   │   ├── router.py              # Main router combining all routes
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── upload.py          # POST /upload
│   │   │   │   ├── transcription.py   # POST /transcribe
│   │   │   │   ├── projects.py        # GET/DELETE /projects
│   │   │   │   ├── transcript.py      # GET /transcript/{id}
│   │   │   │   ├── search.py          # GET /search
│   │   │   │   └── export.py          # POST /export
│   │   │   └── dependencies.py        # Dependency injection
│   │   │
│   │   ├── services/                  # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── upload_service.py      # File upload & validation
│   │   │   ├── transcription_service.py # Whisper integration
│   │   │   ├── export_service.py      # Export handling
│   │   │   ├── project_service.py     # Project management
│   │   │   ├── search_service.py      # Transcript search
│   │   │   └── audio_processor.py     # FFmpeg preprocessing
│   │   │
│   │   ├── repositories/              # Data Access Layer
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py     # Base CRUD operations
│   │   │   ├── user_repository.py
│   │   │   ├── project_repository.py
│   │   │   ├── audio_file_repository.py
│   │   │   ├── transcript_repository.py
│   │   │   └── export_repository.py
│   │   │
│   │   ├── models/                    # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base model class
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── audio_file.py
│   │   │   ├── transcript.py
│   │   │   ├── transcript_sentence.py
│   │   │   ├── transcript_word.py
│   │   │   └── export.py
│   │   │
│   │   ├── schemas/                   # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── user_schema.py
│   │   │   ├── project_schema.py
│   │   │   ├── audio_file_schema.py
│   │   │   ├── transcript_schema.py
│   │   │   ├── search_schema.py
│   │   │   └── export_schema.py
│   │   │
│   │   ├── utils/                     # Utility Functions
│   │   │   ├── __init__.py
│   │   │   ├── logger.py              # Logging configuration
│   │   │   ├── file_manager.py        # File operations
│   │   │   ├── error_handler.py       # Custom exceptions
│   │   │   ├── validators.py          # Input validation
│   │   │   └── constants.py           # App constants
│   │   │
│   │   ├── config/                    # Configuration
│   │   │   ├── __init__.py
│   │   │   ├── settings.py            # Environment-based settings
│   │   │   ├── database.py            # Database configuration
│   │   │   ├── model_config.py        # Whisper model settings
│   │   │   └── app_config.yaml        # Application configuration file
│   │   │
│   │   ├── middleware/                # Custom Middleware
│   │   │   ├── __init__.py
│   │   │   ├── error_middleware.py    # Global error handler
│   │   │   ├── logging_middleware.py  # Request/response logging
│   │   │   └── rate_limit.py          # Rate limiting
│   │   │
│   │   └── core/                      # Core Infrastructure
│   │       ├── __init__.py
│   │       ├── database.py            # SQLAlchemy setup
│   │       ├── security.py            # Security utilities
│   │       └── events.py              # Startup/shutdown events
│   │
│   ├── migrations/                    # Database Migrations (Alembic)
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 001_initial_schema.py
│   │       ├── 002_add_transcript_tables.py
│   │       └── ...
│   │
│   ├── tests/                         # Backend Tests
│   │   ├── __init__.py
│   │   ├── conftest.py                # Pytest fixtures
│   │   ├── unit/
│   │   │   ├── test_audio_processor.py
│   │   │   ├── test_transcription_service.py
│   │   │   ├── test_export_service.py
│   │   │   └── test_validators.py
│   │   ├── integration/
│   │   │   ├── test_upload_api.py
│   │   │   ├── test_transcription_api.py
│   │   │   ├── test_search_api.py
│   │   │   └── test_export_api.py
│   │   └── fixtures/
│   │       ├── sample_audio.mp3
│   │       └── sample_data.json
│   │
│   ├── .env.local                     # Local environment
│   ├── .env.example
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── pytest.ini
│   ├── README.md
│   └── alembic.ini
│
├── docker/                            # Docker Configuration
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── docs/                              # Documentation
│   ├── 01-ARCHITECTURE.md
│   ├── 02-FOLDER_STRUCTURE.md (this file)
│   ├── 03-DATABASE_DESIGN.md
│   ├── 04-API_SPECIFICATION.md
│   ├── 05-IMPLEMENTATION_ROADMAP.md
│   ├── 06-INSTALLATION_GUIDE.md
│   ├── 07-DEPLOYMENT_GUIDE.md
│   ├── ER_DIAGRAM.md
│   └── API_DOCUMENTATION.md
│
├── project-config/                    # Project Configuration
│   ├── .eslintrc.json                 # Frontend linting
│   ├── .prettierrc                    # Code formatting
│   ├── settings.yml                   # App-wide settings
│   └── model_config.yml               # Whisper model configuration
│
├── scripts/                           # Utility Scripts
│   ├── setup.sh                       # Development setup
│   ├── init-db.py                     # Database initialization
│   ├── seed-data.py                   # Sample data insertion
│   └── check-env.py                   # Environment validation
│
├── .github/                           # GitHub Actions
│   └── workflows/
│       ├── ci.yml                     # CI/CD pipeline
│       ├── tests.yml                  # Test automation
│       └── deploy.yml                 # Deployment automation
│
├── uploads/                           # Runtime upload directory
│   ├── .gitkeep
│   └── processed/
│
├── .gitignore
├── .env.example                       # Root environment template
├── README.md                          # Project README
├── CONTRIBUTING.md                    # Contribution guidelines
└── LICENSE
```

## Folder Purpose Guide

### Frontend (`frontend/`)
- Contains the Next.js application
- Organized by feature/route
- Components folder for reusable UI elements
- Services layer for API communication
- Custom hooks for logic reuse

### Backend (`backend/`)
- Python FastAPI application
- Layered architecture (routes → services → repositories → models)
- Database migrations folder
- Comprehensive test suite
- Configuration management

### Docker (`docker/`)
- Separate Dockerfiles for frontend and backend
- Docker Compose for local development
- Ready for production deployment

### Docs (`docs/`)
- Architecture decisions
- Database schema
- API specifications
- Installation and deployment guides
- ER diagrams

### Project Config (`project-config/`)
- Centralized configuration files
- Linting and formatting rules
- Application settings
- Model configuration (easy switching)

### Tests
- **Backend Tests**: `backend/tests/` with PyTest structure
- **Frontend Tests**: Will be `frontend/__tests__/` with Jest
- **E2E Tests**: Will be `frontend/e2e/` with Playwright

## Key Design Principles

### Separation of Concerns
- Clear boundaries between frontend and backend
- Services don't directly access database
- Repositories handle all data access
- API endpoints only handle HTTP concerns

### Scalability
- Folder structure allows adding more services
- Database models can be extended
- Component-based frontend allows feature isolation
- Configuration externalizes system settings

### Maintainability
- Consistent folder naming conventions
- Type safety throughout (TypeScript + Python type hints)
- Tests alongside code
- Documentation at multiple levels

### Modularity
- Each feature is self-contained
- Minimal coupling between components
- Services can be tested independently
- Easy to add new export formats, search capabilities, etc.

