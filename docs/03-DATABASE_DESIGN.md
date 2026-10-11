# Database Design & Schema

## 1. ER Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          DATABASE ENTITIES                               │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│         USERS           │
├─────────────────────────┤
│ id (PK)                 │
│ username (UNIQUE)       │
│ email (UNIQUE)          │
│ password_hash           │
│ created_at              │
│ updated_at              │
│ deleted_at (soft delete)│
└──────────────┬──────────┘
               │ 1:N
               │
┌──────────────────────────────────────────┐
│           PROJECTS                       │
├──────────────────────────────────────────┤
│ id (PK)                                  │
│ user_id (FK)                             │
│ name                                     │
│ description                              │
│ created_at                               │
│ updated_at                               │
│ deleted_at (soft delete)                 │
└──────────────┬───────────────────────────┘
               │ 1:N
               │
┌──────────────────────────────────────────────────┐
│        AUDIO_FILES                               │
├──────────────────────────────────────────────────┤
│ id (PK)                                          │
│ project_id (FK)                                  │
│ original_filename                                │
│ stored_filename (UUID-based)                     │
│ original_path                                    │
│ processed_path                                   │
│ format (MP3, WAV, M4A, etc.)                     │
│ duration_ms                                      │
│ file_size_bytes                                  │
│ status (uploaded, processing, completed, error)  │
│ error_message                                    │
│ created_at                                       │
│ updated_at                                       │
│ deleted_at (soft delete)                         │
└──────────────┬───────────────────────────────────┘
               │ 1:N
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────────────────┐  ┌──────────────────────────┐
│   TRANSCRIPTS       │  │  TRANSCRIPT_SENTENCES    │
├─────────────────────┤  ├──────────────────────────┤
│ id (PK)             │  │ id (PK)                  │
│ audio_file_id (FK)  │  │ transcript_id (FK)       │
│ full_transcript     │  │ sentence_index           │
│ language            │  │ text                     │
│ model_name          │  │ confidence               │
│ model_version       │  │ start_time_ms            │
│ processing_time_ms  │  │ end_time_ms              │
│ created_at          │  │ start_word_id (FK)       │
│ updated_at          │  │ end_word_id (FK)         │
│ deleted_at          │  │ created_at               │
└───────────┬─────────┘  └────────────┬─────────────┘
            │                         │
            │ 1:N                      │
            └─────────────────────┬───┘
                                  │
                          ┌───────▼──────────┐
                          │ TRANSCRIPT_WORDS │
                          ├──────────────────┤
                          │ id (PK)          │
                          │ transcript_id(FK)│
                          │ sentence_id (FK) │
                          │ word_index       │
                          │ text             │
                          │ confidence       │
                          │ start_time_ms    │
                          │ end_time_ms      │
                          │ duration_ms      │
                          │ created_at       │
                          └──────────────────┘

┌────────────────────────────────────────┐
│         EXPORTS                        │
├────────────────────────────────────────┤
│ id (PK)                                │
│ transcript_id (FK)                     │
│ format (TXT, JSON, CSV, SRT, VTT)      │
│ exported_filename                      │
│ file_path                              │
│ file_size_bytes                        │
│ created_at                             │
│ downloaded_at                          │
│ deleted_at (soft delete)               │
└────────────────────────────────────────┘
```

## 2. Table Definitions

### USERS Table
```sql
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    CONSTRAINT users_active CHECK (deleted_at IS NULL)
);

-- Indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

**Rationale**:
- UUID for distributed system compatibility
- UNIQUE constraint on username/email for authentication
- Soft delete for data retention and audit trails
- Timestamp tracking for audit purposes

---

### PROJECTS Table
```sql
CREATE TABLE projects (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT projects_active CHECK (deleted_at IS NULL)
);

-- Indexes
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
```

**Rationale**:
- Links audio files and transcripts to user
- Soft delete preserves project history
- Timestamp ordering for "recent projects" dashboard

---

### AUDIO_FILES Table
```sql
CREATE TABLE audio_files (
    id CHAR(36) PRIMARY KEY,
    project_id CHAR(36) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL UNIQUE,
    original_path TEXT,
    processed_path TEXT,
    format VARCHAR(20) NOT NULL,
    duration_ms INTEGER NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'uploaded',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    CONSTRAINT audio_files_active CHECK (deleted_at IS NULL),
    CONSTRAINT audio_files_status CHECK (
        status IN ('uploaded', 'processing', 'completed', 'error')
    )
);

-- Indexes
CREATE INDEX idx_audio_files_project_id ON audio_files(project_id);
CREATE INDEX idx_audio_files_status ON audio_files(status);
CREATE INDEX idx_audio_files_created_at ON audio_files(created_at DESC);
```

**Rationale**:
- Stored filename uses UUID to prevent directory traversal
- Status tracking for upload progress
- Duration stored for UI display and validation
- Error messages for debugging transcription failures

---

### TRANSCRIPTS Table
```sql
CREATE TABLE transcripts (
    id CHAR(36) PRIMARY KEY,
    audio_file_id CHAR(36) NOT NULL UNIQUE,
    full_transcript TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'en',
    model_name VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (audio_file_id) REFERENCES audio_files(id),
    CONSTRAINT transcripts_active CHECK (deleted_at IS NULL)
);

-- Indexes
CREATE INDEX idx_transcripts_audio_file_id ON transcripts(audio_file_id);
CREATE INDEX idx_transcripts_created_at ON transcripts(created_at DESC);
```

**Rationale**:
- One-to-one relationship with audio files
- Full transcript for quick retrieval without joining all words
- Model metadata for reproducibility
- Processing time for performance monitoring

---

### TRANSCRIPT_SENTENCES Table
```sql
CREATE TABLE transcript_sentences (
    id CHAR(36) PRIMARY KEY,
    transcript_id CHAR(36) NOT NULL,
    sentence_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    confidence DECIMAL(3,2),
    start_time_ms INTEGER NOT NULL,
    end_time_ms INTEGER NOT NULL,
    start_word_id CHAR(36),
    end_word_id CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transcript_id) REFERENCES transcripts(id),
    UNIQUE (transcript_id, sentence_index)
);

-- Indexes
CREATE INDEX idx_transcript_sentences_transcript_id ON transcript_sentences(transcript_id);
CREATE INDEX idx_transcript_sentences_start_time ON transcript_sentences(start_time_ms);
```

**Rationale**:
- Sentence-level timestamps for player synchronization
- Sentence index for ordering
- Confidence scores for quality assessment
- Foreign keys to word table for boundary markers

---

### TRANSCRIPT_WORDS Table
```sql
CREATE TABLE transcript_words (
    id CHAR(36) PRIMARY KEY,
    transcript_id CHAR(36) NOT NULL,
    sentence_id CHAR(36),
    word_index INTEGER NOT NULL,
    text VARCHAR(255) NOT NULL,
    confidence DECIMAL(3,2),
    start_time_ms INTEGER NOT NULL,
    end_time_ms INTEGER NOT NULL,
    duration_ms INTEGER GENERATED ALWAYS AS (end_time_ms - start_time_ms) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transcript_id) REFERENCES transcripts(id),
    FOREIGN KEY (sentence_id) REFERENCES transcript_sentences(id),
    UNIQUE (transcript_id, word_index)
);

-- Indexes
CREATE INDEX idx_transcript_words_transcript_id ON transcript_words(transcript_id);
CREATE INDEX idx_transcript_words_sentence_id ON transcript_words(sentence_id);
CREATE INDEX idx_transcript_words_start_time ON transcript_words(start_time_ms);
CREATE INDEX idx_transcript_words_text ON transcript_words(text);
```

**Rationale**:
- Word-level granularity for interactive highlighting
- Confidence scores per word
- Indexes on start_time for efficient synchronization queries
- Full-text search capability on text column (future enhancement)
- Generated column for duration (computed automatically)

---

### EXPORTS Table
```sql
CREATE TABLE exports (
    id CHAR(36) PRIMARY KEY,
    transcript_id CHAR(36) NOT NULL,
    format VARCHAR(10) NOT NULL,
    exported_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    downloaded_at TIMESTAMP NULL,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (transcript_id) REFERENCES transcripts(id),
    CONSTRAINT exports_active CHECK (deleted_at IS NULL),
    CONSTRAINT exports_format CHECK (format IN ('TXT', 'JSON', 'CSV', 'SRT', 'VTT'))
);

-- Indexes
CREATE INDEX idx_exports_transcript_id ON exports(transcript_id);
CREATE INDEX idx_exports_created_at ON exports(created_at DESC);
```

**Rationale**:
- Tracks export history
- Download tracking for analytics
- Supports multiple formats per transcript
- File path for deletion after download/expiry

---

## 3. Data Types & Constraints

| Column Type | Use Case | Example |
|------------|----------|---------|
| `CHAR(36)` | UUID primary/foreign keys | `550e8400-e29b-41d4-a716-446655440000` |
| `VARCHAR(255)` | Short strings | filenames, usernames |
| `TEXT` | Long content | full transcript, descriptions |
| `INTEGER` | Timestamps (ms), file size | `start_time_ms: 1500` |
| `DECIMAL(3,2)` | Confidence scores | `0.95` (0-1 range) |
| `TIMESTAMP` | Audit trails | `2024-01-15 10:30:00` |
| `BOOLEAN` | Flags | (future) `is_favorite: true` |

## 4. PostgreSQL Migration Path

### From SQLite to PostgreSQL
The schema is designed to migrate without changes:

```python
# SQLAlchemy connection string
# Development (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# Production (PostgreSQL)
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5432/audio_timestamping"
```

**Compatibility Notes**:
- UUIDs: SQLite uses TEXT, PostgreSQL uses native UUID type
- Soft deletes: Both support CHECK constraints
- Indexes: Identical syntax
- Generated columns: Both supported in recent versions
- Timestamps: Both support TIMESTAMP type
- Constraints: UNIQUE and FOREIGN KEY work identically

---

## 5. Query Patterns & Optimization

### Common Query Patterns

#### Find latest projects for user
```sql
SELECT p.id, p.name, COUNT(DISTINCT af.id) as audio_count
FROM projects p
LEFT JOIN audio_files af ON p.id = af.project_id
WHERE p.user_id = ? AND p.deleted_at IS NULL
GROUP BY p.id
ORDER BY p.created_at DESC
LIMIT 10;
```
**Index**: `idx_projects_user_id`, `idx_projects_created_at`

#### Get transcript with timestamps
```sql
SELECT 
    s.sentence_index,
    s.text,
    s.confidence,
    s.start_time_ms,
    s.end_time_ms,
    GROUP_CONCAT(w.text, ' ') as word_sequence
FROM transcript_sentences s
LEFT JOIN transcript_words w ON s.id = w.sentence_id
WHERE s.transcript_id = ?
GROUP BY s.id
ORDER BY s.sentence_index;
```
**Indexes**: `idx_transcript_sentences_transcript_id`, `idx_transcript_words_sentence_id`

#### Search transcript
```sql
SELECT 
    w.id,
    w.text,
    w.start_time_ms,
    s.sentence_index,
    s.text as sentence_text
FROM transcript_words w
JOIN transcript_sentences s ON w.sentence_id = s.id
WHERE w.transcript_id = ? 
  AND LOWER(w.text) LIKE LOWER(?)
ORDER BY w.word_index;
```
**Indexes**: `idx_transcript_words_text`, `idx_transcript_words_transcript_id`

#### Get words in time range (for playback sync)
```sql
SELECT id, text, start_time_ms, end_time_ms
FROM transcript_words
WHERE transcript_id = ? 
  AND start_time_ms <= ? 
  AND end_time_ms >= ?
ORDER BY start_time_ms;
```
**Index**: `idx_transcript_words_start_time`

---

## 6. Database Initialization Strategy

### Phase 1: SQLite Setup
```bash
# Initialize empty database with schema
python backend/scripts/init-db.py

# Run migrations (even if starting fresh)
alembic upgrade head

# Optional: Seed with sample data
python backend/scripts/seed-data.py
```

### Phase 2+: PostgreSQL Migration
```bash
# Export data from SQLite
python backend/scripts/export-sqlite.py

# Import to PostgreSQL
python backend/scripts/import-postgresql.py

# Verify consistency
python backend/scripts/verify-migration.py
```

---

## 7. Performance Considerations

| Operation | Complexity | Optimization |
|-----------|-----------|--------------|
| List projects | O(n) | Pagination + indexed sort |
| Get transcript | O(1) | Direct lookup by ID |
| Search words | O(m log m) | Full-text index (future) |
| Sync playback | O(1) | Binary search on indexed start_time |
| Export format | O(n) | Query with streaming |

### Future Enhancements
- Full-text search index on transcript_words.text
- Partitioning by date for large datasets
- Denormalized search cache
- Redis caching layer for popular transcripts

---

## 8. Backup & Recovery Strategy

### Backup Frequency
- **Development**: Manual before major changes
- **Production**: Daily incremental backups
- **Archive**: Monthly full backups (7-year retention)

### Recovery Points
- Point-in-time recovery enabled
- Transaction log retention: 7 days
- Backup integrity checked weekly

### Data Retention Policy
- **Active projects**: Keep indefinitely
- **Deleted (soft delete)**: 90 days before hard delete
- **Exports**: 30 days before cleanup
- **Processing logs**: 30 days

