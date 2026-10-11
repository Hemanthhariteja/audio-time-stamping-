# Phases 3-4 Implementation Plan

## Phase 3: Whisper Transcription Integration (Production-Ready)

### Backend Components
1. **TranscriptionService** - Core transcription orchestration
   - Model loading with GPU/CPU auto-detection
   - Full transcription pipeline (audio → text → structured output)
   - Error handling and retry logic
   - Async processing with job tracking
   - Logging and monitoring

2. **TranscriptProcessor** - Extract structured data
   - Sentence boundary detection and extraction
   - Word-level timestamp extraction
   - Confidence score calculation
   - Language detection

3. **TranscriptExporter** - Multi-format export
   - TXT (plain text)
   - JSON (structured with timestamps)
   - CSV (tabular with word/sentence data)
   - SRT (SubRip format for video)
   - VTT (WebVTT format for web)

4. **API Endpoints** (8 endpoints)
   - POST /api/v1/audio/{id}/transcribe - Start transcription
   - GET /api/v1/transcript/{id} - Retrieve full transcript
   - GET /api/v1/transcript/{id}/sentences - Get sentences with timing
   - GET /api/v1/transcript/{id}/words - Get words with timing
   - POST /api/v1/transcript/{id}/search - Full-text search
   - POST /api/v1/transcript/{id}/export/{format} - Export transcript
   - GET /api/v1/transcription-status/{audio_file_id} - Job status
   - DELETE /api/v1/transcript/{id} - Delete transcript

5. **Database Support**
   - TranscriptionJob table (optional, for async tracking)
   - Store results in existing Transcript/TranscriptSentence/TranscriptWord

6. **Configuration**
   - WHISPER_MODEL_NAME (base by default)
   - ENABLE_GPU (auto-detect CUDA)
   - AUDIO_CHUNK_DURATION (for long files)
   - TRANSCRIPTION_TIMEOUT

### Files to Create (Phase 3)
- app/services/transcription_service.py
- app/services/transcript_processor.py
- app/services/transcript_exporter.py
- app/api/v1/endpoints/transcripts.py
- app/utils/gpu_detector.py
- tests/test_transcription.py
- tests/test_transcript_export.py

**Phase 3 Total: 7 files | ~2,500 lines of code**

---

## Phase 4: Frontend Development (Production-Ready)

### Project Structure
```
frontend/
├── app/
│   ├── page.tsx                    # Home/dashboard
│   ├── projects/
│   │   ├── page.tsx               # Projects list
│   │   └── [id]/
│   │       ├── page.tsx           # Project detail
│   │       └── files/
│   │           └── [fileId]/
│   │               └── page.tsx   # Transcript viewer
│   └── layout.tsx
├── components/
│   ├── Dashboard.tsx
│   ├── ProjectList.tsx
│   ├── ProjectForm.tsx
│   ├── FileUpload.tsx
│   ├── AudioPlayer.tsx
│   ├── TranscriptViewer.tsx
│   ├── WordTimeline.tsx
│   ├── SearchBar.tsx
│   ├── ExportMenu.tsx
│   └── ...layout & UI components
├── hooks/
│   ├── useProjects.ts
│   ├── useAudioFile.ts
│   ├── useTranscript.ts
│   ├── useTranscriptSearch.ts
│   └── useAudioPlayer.ts
├── services/
│   ├── api.ts
│   └── apiClient.ts
├── types/
│   └── index.ts                   # TypeScript interfaces
├── styles/
│   └── globals.css
└── package.json
```

### React Components (12 components)
1. **Dashboard** - Project overview and quick actions
2. **ProjectList** - List all user projects
3. **ProjectForm** - Create/edit project modal
4. **FileUpload** - Drag-and-drop audio upload
5. **AudioPlayer** - WaveSurfer.js audio player
6. **TranscriptViewer** - Synchronized transcript display
7. **WordTimeline** - Word-level highlighting with playback sync
8. **SearchBar** - Full-text transcript search
9. **ExportMenu** - Format selector for export
10. **Layout** - Navigation and page wrapper
11. **LoadingSpinner** - Loading states
12. **ErrorBoundary** - Error handling

### Key Features
- **Audio Playback**: WaveSurfer.js with waveform visualization
- **Transcript Sync**: Click word → jump to audio position
- **Search**: Full-text search with highlighting
- **Export**: Download in 5 formats
- **Responsive**: Mobile-friendly design
- **State Management**: React Query + Context API
- **Type Safety**: Full TypeScript coverage

### Dependencies
- Next.js 14 (React 19)
- TypeScript 5.x
- React Query (v5)
- WaveSurfer.js
- Tailwind CSS
- shadcn/ui (component library)
- axios (HTTP client)

### Files to Create (Phase 4)
**Pages (5):**
- app/page.tsx
- app/projects/page.tsx
- app/projects/[id]/page.tsx
- app/projects/[id]/files/[fileId]/page.tsx
- app/layout.tsx

**Components (12):**
- components/Dashboard.tsx
- components/ProjectList.tsx
- components/ProjectForm.tsx
- components/FileUpload.tsx
- components/AudioPlayer.tsx
- components/TranscriptViewer.tsx
- components/WordTimeline.tsx
- components/SearchBar.tsx
- components/ExportMenu.tsx
- components/Layout.tsx
- components/LoadingSpinner.tsx
- components/ErrorBoundary.tsx

**Hooks (5):**
- hooks/useProjects.ts
- hooks/useAudioFile.ts
- hooks/useTranscript.ts
- hooks/useTranscriptSearch.ts
- hooks/useAudioPlayer.ts

**Services/Types (3):**
- services/api.ts
- services/apiClient.ts
- types/index.ts

**Config (3):**
- package.json
- tsconfig.json
- next.config.js

**Phase 4 Total: 28 files | ~4,500 lines of code**

---

## Implementation Sequence

1. **Phase 3 First** (faster-whisper integration)
   - Install ML dependencies (faster-whisper, torch, librosa)
   - Create TranscriptionService with GPU detection
   - Build transcript processing pipeline
   - Create export functionality
   - Add API endpoints for transcription workflow
   - Test with sample audio files

2. **Phase 4 Second** (frontend)
   - Initialize Next.js project
   - Setup React Query and API client
   - Build core components (Dashboard, Upload, Player)
   - Integrate WaveSurfer.js audio player
   - Build transcript viewer with sync
   - Add search functionality
   - Create export interface
   - Full TypeScript coverage

## Timeline
- Phase 3: 5-7 days
- Phase 4: 6-8 days
- **Total: 11-15 days of work → compressed into this session**

## Success Criteria
- ✅ Phase 3: All 8 transcription API endpoints working
- ✅ Transcription produces word-level timestamps
- ✅ All 5 export formats functional
- ✅ Phase 4: Frontend components render correctly
- ✅ Audio player syncs with transcript
- ✅ Search functionality working
- ✅ Zero build errors
- ✅ Full TypeScript coverage

---

## Next: Begin Phase 3 Implementation
Starting with TranscriptionService and supporting infrastructure...
