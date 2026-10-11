"""Project API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db import get_db
from app.repositories import TranscriptRepository, TranscriptSentenceRepository
from app.schemas import (
    AudioFileResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services import AudioFileService, ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None,
):
    """Create a new project."""
    try:
        resolved_user_id = user_id if user_id is not None else getattr(project_data, "user_id", None)
        if resolved_user_id is None:
            raise HTTPException(status_code=422, detail="user_id is required")

        service = ProjectService(db)
        return service.create_project(resolved_user_id, project_data)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    user_id: Optional[int] = None,  # TODO: Get from JWT token
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List all projects for a user."""
    try:
        resolved_user_id = user_id if user_id is not None else 1
        service = ProjectService(db)
        projects, _ = service.get_user_projects(resolved_user_id, skip, limit)
        return projects
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Get project details."""
    try:
        service = ProjectService(db)
        return service.get_project(project_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    """Update a project."""
    try:
        service = ProjectService(db)
        return service.update_project(project_id, project_data)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{project_id}/audio", response_model=List[AudioFileResponse])
async def list_project_audio_files(
    project_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List audio files attached to a project."""
    try:
        service = AudioFileService(db)
        files, _ = service.get_project_audio_files(project_id, skip, limit)
        return files
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{project_id}/transcript", response_model=dict)
async def get_project_transcript(
    project_id: int,
    audio_file_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Return the transcript for the given audio file, or the first transcribed file in a project."""
    try:
        audio_service = AudioFileService(db)
        audio_files, _ = audio_service.get_project_audio_files(project_id, 0, 100)

        if not audio_files:
            return {"id": None, "text": "", "language": "unknown", "sentences": [], "words": []}

        transcript_repo = TranscriptRepository(db)
        sentence_repo = TranscriptSentenceRepository(db)

        for audio_file in audio_files:
            if audio_file_id is not None and audio_file.id != audio_file_id:
                continue
            transcript = transcript_repo.get_by_audio_file_id(audio_file.id)
            if not transcript:
                continue

            sentences = sentence_repo.get_transcript_sentences(transcript.id)
            return {
                "id": transcript.id,
                "text": transcript.full_text,
                "language": transcript.language_code,
                "sentences": [
                    {
                        "id": sentence.id,
                        "text": sentence.sentence_text,
                        "start_time": sentence.start_time,
                        "end_time": sentence.end_time,
                        "words": [
                            {
                                "id": word.id,
                                "text": word.word_text,
                                "start_time": word.start_time,
                                "end_time": word.end_time,
                            }
                            for word in sentence.words
                        ],
                    }
                    for sentence in sentences
                ],
                "words": [
                    {
                        "id": word.id,
                        "text": word.word_text,
                        "start_time": word.start_time,
                        "end_time": word.end_time,
                    }
                    for sentence in sentences
                    for word in sentence.words
                ],
            }

        return {"id": None, "text": "", "language": "unknown", "sentences": [], "words": []}
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Delete a project."""
    try:
        service = ProjectService(db)
        service.delete_project(project_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
