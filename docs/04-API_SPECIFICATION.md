# API Specification

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://api.audio-timestamping.com/api/v1
```

## Authentication

JWT tokens (prepared for future implementation, Phase 1 is public):

```
Authorization: Bearer <token>
```

## Error Response Format

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {
      "field": "specific_information"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_12345"
  }
}
```

## Common HTTP Status Codes

- `200 OK`: Successful GET/PUT/PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `409 Conflict`: Duplicate resource
- `422 Unprocessable Entity`: Validation failure
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service down

---

## Endpoints

### 1. POST /upload

Upload and preprocess audio file.

#### Request

```
POST /api/v1/upload
Content-Type: multipart/form-data

Body:
  file: <audio_file>
  project_name: "My Project" (optional, creates if not exists)
  project_id: "project-uuid" (optional, if project exists)
```

#### Response (201 Created)

```json
{
  "success": true,
  "data": {
    "project_id": "proj_550e8400-e29b-41d4-a716-446655440000",
    "project_name": "My Project",
    "audio_file_id": "audio_550e8400-e29b-41d4-a716-446655440001",
    "original_filename": "meeting.mp3",
    "stored_filename": "audio_550e8400-e29b-41d4-a716-446655440001.wav",
    "format": "MP3",
    "duration_ms": 600000,
    "file_size_bytes": 9847200,
    "status": "processing",
    "message": "File uploaded successfully. Transcription will start shortly."
  }
}
```

#### Errors

| Status | Code | Message |
|--------|------|---------|
| 400 | FILE_NOT_PROVIDED | No file provided in request |
| 400 | UNSUPPORTED_FORMAT | Format MP2 is not supported |
| 400 | FILE_TOO_LARGE | File size exceeds 200MB limit |
| 400 | AUDIO_TOO_LONG | Audio duration exceeds 10 minutes |
| 400 | CORRUPTED_AUDIO | Audio file is corrupted or unreadable |
| 422 | VALIDATION_ERROR | Project name contains invalid characters |
| 429 | RATE_LIMIT | Too many uploads. Please try again later |
| 500 | PREPROCESSING_ERROR | FFmpeg preprocessing failed |

#### Validation Rules

- **Supported formats**: MP3, WAV, M4A, AAC, OGG, FLAC, MP4
- **Max file size**: 200 MB
- **Max duration**: 10 minutes
- **Project name**: 1-255 characters, alphanumeric + spaces

---

### 2. GET /projects

List all projects for the user.

#### Request

```
GET /api/v1/projects?page=1&limit=10&sort=created_at&order=desc
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Pagination page number |
| limit | integer | 10 | Items per page (max 100) |
| sort | string | created_at | Sort field: created_at, name, updated_at |
| order | string | desc | Sort order: asc, desc |

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "projects": [
      {
        "id": "proj_550e8400-e29b-41d4-a716-446655440000",
        "name": "Meeting January 2024",
        "description": "Team standup",
        "audio_count": 3,
        "completed_count": 2,
        "processing_count": 1,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "pages": 3
    }
  }
}
```

#### Errors

| Status | Code | Message |
|--------|------|---------|
| 400 | INVALID_PAGINATION | Page must be >= 1 |
| 400 | INVALID_LIMIT | Limit must be 1-100 |
| 401 | UNAUTHORIZED | User not authenticated |

---

### 3. GET /project/{id}

Get detailed project information with audio files.

#### Request

```
GET /api/v1/project/proj_550e8400-e29b-41d4-a716-446655440000
```

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "id": "proj_550e8400-e29b-41d4-a716-446655440000",
    "name": "Meeting January 2024",
    "description": "Team standup",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "audio_files": [
      {
        "id": "audio_550e8400-e29b-41d4-a716-446655440001",
        "original_filename": "part1.mp3",
        "duration_ms": 600000,
        "file_size_bytes": 9847200,
        "status": "completed",
        "transcript_id": "trans_550e8400-e29b-41d4-a716-446655440002",
        "created_at": "2024-01-15T10:00:00Z"
      },
      {
        "id": "audio_550e8400-e29b-41d4-a716-446655440003",
        "original_filename": "part2.mp3",
        "duration_ms": 300000,
        "file_size_bytes": 4923600,
        "status": "processing",
        "transcript_id": null,
        "created_at": "2024-01-15T10:05:00Z"
      }
    ]
  }
}
```

#### Errors

| Status | Code | Message |
|--------|------|---------|
| 404 | PROJECT_NOT_FOUND | Project does not exist |
| 401 | UNAUTHORIZED | Not project owner |

---

### 4. GET /transcript/{id}

Get complete transcript with word and sentence timestamps.

#### Request

```
GET /api/v1/transcript/trans_550e8400-e29b-41d4-a716-446655440002
```

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "id": "trans_550e8400-e29b-41d4-a716-446655440002",
    "audio_file_id": "audio_550e8400-e29b-41d4-a716-446655440001",
    "project_id": "proj_550e8400-e29b-41d4-a716-446655440000",
    "full_transcript": "Welcome to the meeting. Let's discuss the quarterly goals...",
    "language": "en",
    "model_name": "faster-whisper",
    "model_version": "medium",
    "processing_time_ms": 45000,
    "created_at": "2024-01-15T10:02:00Z",
    "sentences": [
      {
        "id": "sent_550e8400-e29b-41d4-a716-446655440003",
        "sentence_index": 0,
        "text": "Welcome to the meeting.",
        "confidence": 0.98,
        "start_time_ms": 0,
        "end_time_ms": 3500,
        "words": [
          {
            "id": "word_550e8400-e29b-41d4-a716-446655440004",
            "word_index": 0,
            "text": "Welcome",
            "confidence": 0.99,
            "start_time_ms": 0,
            "end_time_ms": 800,
            "duration_ms": 800
          },
          {
            "id": "word_550e8400-e29b-41d4-a716-446655440005",
            "word_index": 1,
            "text": "to",
            "confidence": 0.97,
            "start_time_ms": 800,
            "end_time_ms": 1100,
            "duration_ms": 300
          },
          {
            "id": "word_550e8400-e29b-41d4-a716-446655440006",
            "word_index": 2,
            "text": "the",
            "confidence": 0.96,
            "start_time_ms": 1100,
            "end_time_ms": 1300,
            "duration_ms": 200
          },
          {
            "id": "word_550e8400-e29b-41d4-a716-446655440007",
            "word_index": 3,
            "text": "meeting",
            "confidence": 0.98,
            "start_time_ms": 1300,
            "end_time_ms": 2200,
            "duration_ms": 900
          }
        ]
      },
      {
        "id": "sent_550e8400-e29b-41d4-a716-446655440008",
        "sentence_index": 1,
        "text": "Let's discuss the quarterly goals.",
        "confidence": 0.96,
        "start_time_ms": 3500,
        "end_time_ms": 8200,
        "words": [
          {
            "id": "word_550e8400-e29b-41d4-a716-446655440009",
            "word_index": 4,
            "text": "Let's",
            "confidence": 0.97,
            "start_time_ms": 3500,
            "end_time_ms": 4300,
            "duration_ms": 800
          }
        ]
      }
    ]
  }
}
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| include_full_text | boolean | true | Include full_transcript field |
| sentence_detail | string | full | Level: summary, full, words_only |

#### Errors

| Status | Code | Message |
|--------|------|---------|
| 404 | TRANSCRIPT_NOT_FOUND | Transcript does not exist |
| 409 | TRANSCRIPT_PROCESSING | Transcript is still processing |
| 401 | UNAUTHORIZED | Not authorized to access |

---

### 5. GET /search

Search transcript for keywords with timestamps.

#### Request

```
GET /api/v1/search?q=quarterly%20goals&project_id=proj_550e8400-e29b-41d4-a716-446655440000&limit=20
```

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Search query |
| project_id | string | No | Limit search to project |
| transcript_id | string | No | Limit search to transcript |
| case_sensitive | boolean | No | Case-sensitive search (default: false) |
| limit | integer | No | Max results (default: 20, max: 100) |

#### Response (200 OK)

```json
{
  "success": true,
  "data": {
    "query": "quarterly goals",
    "matches": [
      {
        "match_id": "match_1",
        "transcript_id": "trans_550e8400-e29b-41d4-a716-446655440002",
        "project_id": "proj_550e8400-e29b-41d4-a716-446655440000",
        "project_name": "Meeting January 2024",
        "audio_filename": "part2.mp3",
        "sentence_index": 1,
        "sentence_text": "Let's discuss the quarterly goals.",
        "highlighted_sentence": "Let's discuss the <mark>quarterly goals</mark>.",
        "start_time_ms": 3500,
        "end_time_ms": 8200,
        "confidence": 0.96
      }
    ],
    "total_matches": 1
  }
}
```

#### Errors

| Status | Code | Message |
|--------|------|---------|
| 400 | EMPTY_QUERY | Search query cannot be empty |
| 400 | QUERY_TOO_LONG | Query exceeds 255 characters |
| 422 | INVALID_PROJECT_ID | Project does not exist |
| 429 | RATE_LIMIT | Too many searches. Please try again later |

---

### 6. POST /export

Export transcript in various formats.

#### Request

```
POST /api/v1/export
Content-Type: application/json

{
  "transcript_id": "trans_550e8400-e29b-41d4-a716-446655440002",
  "format": "srt",
  "include_confidence": true,
  "include_timings": true
}
```

#### Request Parameters

| Parameter | Type | Required | Options | Default |
|-----------|------|----------|---------|---------|
| transcript_id | string | Yes | - | - |
| format | string | Yes | txt, json, csv, srt, vtt | - |
| include_confidence | boolean | No | - | true |
| include_timings | boolean | No | - | true |

#### Response (201 Created)

```json
{
  "success": true,
  "data": {
    "export_id": "exp_550e8400-e29b-41d4-a716-446655440010",
    "transcript_id": "trans_550e8400-e29b-41d4-a716-446655440002",
    "format": "srt",
    "filename": "transcript_export_2024-01-15_10-30-00.srt",
    "file_size_bytes": 45000,
    "download_url": "/api/v1/export/exp_550e8400-e29b-41d4-a716-446655440010/download",
    "created_at": "2024-01-15T10:30:00Z",
    "expires_at": "2024-01-22T10:30:00Z"
  }
}
```

#### Export Format Examples

**SRT (SubRip)**
```
1
00:00:00,000 --> 00:00:03,500
Welcome to the meeting.

2
00:00:03,500 --> 00:00:08,200
Let's discuss the quarterly goals.
```

**VTT (WebVTT)**
```
WEBVTT

00:00:00.000 --> 00:00:03.500
Welcome to the meeting.

00:00:03.500 --> 00:00:08.200
Let's discuss the quarterly goals.
```

**JSON**
```json
{
  "transcript": {
    "id": "trans_550e8400-e29b-41d4-a716-446655440002",
    "language": "en",
    "model": "faster-whisper-medium",
    "sentences": [
      {
        "index": 0,
        "text": "Welcome to the meeting.",
        "start_ms": 0,
        "end_ms": 3500,
        "confidence": 0.98
      }
    ]
  }
}
```

**CSV**
```
sentence_index,start_time,end_time,confidence,text
0,00:00:00.000,00:00:03.500,0.98,Welcome to the meeting.
1,00:00:03.500,00:00:08.200,0.96,Let's discuss the quarterly goals.
```

**TXT (Plain text)**
```
Welcome to the meeting. Let's discuss the quarterly goals.
```

#### Errors

| Status | Code | Message |
|--------|------|---------|
| 400 | INVALID_FORMAT | Format must be txt, json, csv, srt, or vtt |
| 404 | TRANSCRIPT_NOT_FOUND | Transcript does not exist |
| 409 | TRANSCRIPT_PROCESSING | Transcript is still processing |
| 500 | EXPORT_GENERATION_ERROR | Failed to generate export file |

---

### 7. GET /export/{export_id}/download

Download exported file.

#### Request

```
GET /api/v1/export/exp_550e8400-e29b-41d4-a716-446655440010/download
```

#### Response (200 OK)

```
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Content-Disposition: attachment; filename="transcript_export_2024-01-15_10-30-00.txt"
Content-Length: 45000

[File content]
```

#### Errors

| Status | Code | Message |
|--------|------|---------|
| 404 | EXPORT_NOT_FOUND | Export does not exist or has expired |
| 410 | EXPORT_EXPIRED | Export file has expired (7 days) |

---

### 8. DELETE /project/{id}

Delete project and associated files (soft delete).

#### Request

```
DELETE /api/v1/project/proj_550e8400-e29b-41d4-a716-446655440000
```

#### Response (204 No Content)

```
HTTP/1.1 204 No Content
```

#### Errors

| Status | Code | Message |
|--------|------|---------|
| 404 | PROJECT_NOT_FOUND | Project does not exist |
| 401 | UNAUTHORIZED | Not project owner |

---

## Rate Limiting

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1705316400
```

**Limits (Phase 1)**:
- Upload: 10 requests/hour
- Transcription: 20 requests/hour
- Search: 100 requests/hour
- Export: 50 requests/hour
- General API: 1000 requests/hour

---

## Pagination

All list endpoints support pagination:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "pages": 10,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Documentation

Auto-generated Swagger documentation available at:

```
http://localhost:8000/docs
http://localhost:8000/redoc
```

