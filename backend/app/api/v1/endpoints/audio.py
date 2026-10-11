"""Audio file API endpoints."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db import get_db
from app.schemas import AudioFileResponse
from app.services import AudioFileService

router = APIRouter(prefix="/audio", tags=["audio"])


@router.post("/upload/{project_id}", response_model=AudioFileResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio_file(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload an audio file.

    Supported formats: MP3, WAV, M4A, AAC, OGG, FLAC, MP4
    Maximum file size: 100MB
    """
    try:
        # Read file content
        file_content = await file.read()

        # Upload
        service = AudioFileService(db)
        return service.upload_audio_file(
            project_id=project_id,
            original_filename=file.filename,
            file_content=file_content,
        )

    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/{audio_file_id}", response_model=AudioFileResponse)
async def get_audio_file(
    audio_file_id: int,
    db: Session = Depends(get_db),
):
    """Get audio file details."""
    try:
        service = AudioFileService(db)
        return service.get_audio_file(audio_file_id)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{audio_file_id}/preprocess", status_code=status.HTTP_202_ACCEPTED)
async def preprocess_audio_file(
    audio_file_id: int,
    db: Session = Depends(get_db),
):
    """Preprocess audio file for transcription."""
    try:
        service = AudioFileService(db)
        service.preprocess_audio(audio_file_id)
        return {"status": "preprocessing"}
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
