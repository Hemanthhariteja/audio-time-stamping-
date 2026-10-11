# Project Quick Reference Card

## 🎯 AI Audio Timestamping Platform - At a Glance

### Project Scope
Convert English audio (up to 10 minutes) into transcripts with word-level and sentence-level timestamps using Faster-Whisper, FFmpeg, and modern web technologies.

### Target Hardware
- Intel i5 + GTX 1650 (4GB) + 8GB RAM
- Auto-detects CUDA; falls back to CPU

---

## 🏗️ Architecture

```
Next.js Frontend ↔ FastAPI Backend ↔ SQLite Database
       ↓                ↓                   ↓
React Components    Services            7 Tables
+ Tailwind CSS      Repositories        Normalized
+ React Query       Business Logic      3NF
```

---

## 📦 Core Technologies

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js + TypeScript + Tailwind |
| Backend | Python + FastAPI |
| Database | SQLite → PostgreSQL |
| ML | Faster-Whisper Medium |
| Audio | FFmpeg |
| Testing | Jest, PyTest, Playwright |

---

## 📊 Database (7 Tables)

```
Users ← Projects ← AudioFiles
                      ↓
                  Transcripts
                      ↓
          ┌───────────┴───────────┐
          ↓                       ↓
  TranscriptSentences    TranscriptWords
          
Exports (separate)
```

---

## 🔌 8 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /upload | POST | Upload & preprocess audio |
| /projects | GET | List user projects |
| /project/{id} | GET | Project details |
| /transcript/{id} | GET | Full transcript + timestamps |
| /search | GET | Search transcripts |
| /export | POST | Export in 5 formats |
| /project/{id} | DELETE | Delete project |
| /health | GET | Health check |

---

## 🎵 Supported Formats

**Audio**: MP3, WAV, M4A, AAC, OGG, FLAC, MP4  
**Export**: TXT, JSON, CSV, SRT, VTT  
**Constraints**: Max 200MB, 10 minutes

---

## 🚀 5-Phase Roadmap

| Phase | Duration | Focus |
|-------|----------|-------|
| 1 | 2-3 days | Architecture & Design ✓ |
| 2 | 4-5 days | Backend Setup |
| 3 | 5-7 days | Whisper Integration |
| 4 | 6-8 days | Frontend Development |
| 5 | 5-7 days | Testing & Deployment |
| **Total** | **22-30 days** | **Production Ready** |

---

## 📋 Requirements Coverage

- [x] Audio upload with validation
- [x] FFmpeg preprocessing (7 formats)
- [x] Faster-Whisper transcription
- [x] Word-level timestamps
- [x] Sentence-level timestamps
- [x] Interactive playback synchronization
- [x] Full-text search
- [x] Multi-format export
- [x] Project management
- [x] Dark mode UI
- [x] Responsive design
- [x] Comprehensive error handling
- [x] Security (input validation, rate limiting)
- [x] Testing (unit, integration, E2E)
- [x] Docker containerization

---

## 💻 Setup Checklist

### Prerequisites
```bash
Python 3.10+
Node.js 18+
FFmpeg (system)
CUDA toolkit (optional, for GPU)
8GB RAM (16GB recommended)
```

### Backend Start
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend Start
```bash
cd frontend
npm install
npm run dev  # http://localhost:3000
```

### API Documentation
```
http://localhost:8000/docs
```

---

## 🔒 Security Features

- ✓ Input validation (Pydantic)
- ✓ File upload security (UUID filenames)
- ✓ SQL injection prevention (SQLAlchemy ORM)
- ✓ XSS prevention (React + validation)
- ✓ Rate limiting (per-endpoint)
- ✓ CORS configuration
- ✓ JWT architecture (ready for Phase 2+)

---

## 🧪 Testing Strategy

| Framework | Layer | Target Coverage |
|-----------|-------|-----------------|
| PyTest | Backend | >80% |
| Jest | Frontend | >70% |
| Playwright | E2E | All workflows |

---

## 📈 Performance Targets

- Transcription: < 1x audio duration
- Search: < 500ms response
- UI: < 200ms response
- Memory: < 4GB for 10-min audio
- GPU: 70-90% utilization

---

## 🗂️ File Organization

```
audio-timestamping/
├── docs/                   (8 design documents)
├── backend/               (FastAPI app - Phase 2)
├── frontend/              (Next.js app - Phase 2)
├── docker/                (Docker config - Phase 5)
├── scripts/               (Setup scripts - Phase 2)
├── project-config/        (Configuration files)
├── .github/               (CI/CD workflows - Phase 5)
├── uploads/               (Runtime directory)
├── README.md              (Project overview)
└── .env.example           (Config template)
```

---

## 🎯 Success Criteria

### Phase 1 ✓
- [x] Architecture finalized
- [x] Database designed
- [x] API specified
- [ ] Awaiting approval

### Phase 2
- [ ] Backend functional
- [ ] Upload working
- [ ] Tests passing

### Phase 3
- [ ] Transcription complete
- [ ] Timestamps accurate

### Phase 4
- [ ] Frontend complete
- [ ] UI/UX polished

### Phase 5
- [ ] All tests pass
- [ ] Docker working
- [ ] Production ready

---

## 📚 Documentation Index

| Document | Purpose | Pages |
|----------|---------|-------|
| 01-ARCHITECTURE.md | System design | 11 |
| 02-FOLDER_STRUCTURE.md | Directory layout | 8 |
| 03-DATABASE_DESIGN.md | Schema & queries | 12 |
| 04-API_SPECIFICATION.md | Endpoints & examples | 18 |
| 05-IMPLEMENTATION_ROADMAP.md | Tasks & timeline | 14 |
| 06-PROJECT_SUMMARY.md | Executive summary | 10 |
| ENVIRONMENT_SETUP.md | Configuration | 6 |
| PHASE1_CHECKLIST.md | Requirements validation | 10 |
| README.md | Quick start | 5 |
| **TOTAL** | **~95 KB of documentation** | **94 pages** |

---

## 🔑 Key Decision Points

### Why Faster-Whisper?
4x faster than Whisper, word timestamps, GPU support

### Why Next.js?
Built-in routing, SSR, TypeScript, modern framework

### Why FastAPI?
Async support, auto-docs, ML-friendly, fast

### Why SQLite then PostgreSQL?
Lightweight for Phase 1, prepared for scaling

### Why Clean Architecture?
Maintainability, testability, scalability

---

## ⚡ Quick Commands

```bash
# Initialize backend
cd backend && python scripts/init-db.py && alembic upgrade head

# Start backend
python -m uvicorn app.main:app --reload --port 8000

# Start frontend
cd frontend && npm run dev

# Run tests
pytest backend/tests/
npm test --prefix frontend

# Build Docker
docker-compose build

# Deploy
docker-compose up -d
```

---

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| FFmpeg not found | Install: `apt install ffmpeg` or `brew install ffmpeg` |
| GPU not detected | Install CUDA toolkit, check with `nvidia-smi` |
| Port 8000 in use | Change `SERVER_PORT` in .env |
| Database locked | Delete `app.db` and reinitialize |
| CORS errors | Check `CORS_ORIGINS` in .env |

---

## 📞 Support Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/
- **Faster-Whisper**: https://github.com/guillaumekln/faster-whisper
- **SQLAlchemy**: https://www.sqlalchemy.org/

---

## ✅ Phase 1 Sign-Off

| Approval | Status |
|----------|--------|
| Architecture | ✓ Complete |
| Design | ✓ Complete |
| Planning | ✓ Complete |
| **Awaiting** | **Stakeholder Review** |

---

**Generated**: 2024-01-15  
**Version**: 1.0.0  
**Status**: Phase 1 Complete - Ready for Review

---

*Print this card and share with your team!*

