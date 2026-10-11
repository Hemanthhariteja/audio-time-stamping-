"""Transcript API endpoints for transcription, retrieval, search, and export."""

import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.core.exceptions import (
    NotFoundError,
    AudioProcessingError,
    ValidationError,
    ConflictError,
)
from app.repositories import (
    TranscriptRepository,
    TranscriptSentenceRepository,
    TranscriptWordRepository,
    AudioFileRepository,
    ExportRepository,
)
from app.services.transcription_service import TranscriptionService
from app.services.transcript_exporter import TranscriptExporter
from app.schemas import (
    TranscriptResponse,
    TranscriptDetailedResponse,
    TranscriptSentenceResponse,
    TranscriptWordResponse,
    ExportRequest,
    ExportResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.models import AudioFile, Transcript, TranscriptSentence, TranscriptWord, Export

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/transcripts", tags=["transcripts"])
exports_router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("/audio/{audio_file_id}/transcribe", status_code=202, response_model=dict)
def start_transcription(
    audio_file_id: int,
    language: Optional[str] = Query(None, description="Language code (e.g., 'en', 'es')"),
    db: Session = Depends(get_db),
):
    """
    Start transcription of an audio file.

    Runs the transcription in a worker thread and returns once it is complete.

    Args:
        audio_file_id: ID of audio file to transcribe
        language: Optional language code for transcription
        db: Database session

    Returns:
        Job status with transcript ID and processing status
    """
    try:
        # Get audio file
        audio_repo = AudioFileRepository(db)
        audio_file = audio_repo.get_by_id(audio_file_id)

        if not audio_file:
            raise NotFoundError(f"Audio file {audio_file_id} not found")

        if audio_file.upload_status != "ready":
            raise ValidationError(
                f"Audio file not ready for transcription. Status: {audio_file.upload_status}"
            )

        # Check if transcript already exists
        transcript_repo = TranscriptRepository(db)
        existing = transcript_repo.get_by_audio_file_id(audio_file_id)
        if existing:
            raise ConflictError(f"Transcript already exists for audio file {audio_file_id}")

        logger.info(f"Starting transcription for audio file {audio_file_id}")

        if not audio_file.processed_file_path:
            raise ValidationError("Audio file has no stored media to transcribe")

        # Perform transcription (synchronously for now, could be async job)
        result = TranscriptionService.transcribe(audio_file.processed_file_path, language=language)

        # Save transcript with its sentences and words in a single transaction
        transcript = Transcript(
            audio_file_id=audio_file_id,
            full_text=result["full_text"],
            language_code=result["language"],
            confidence_score=result["confidence"],
            processing_status="completed",
            sentences=[
                TranscriptSentence(
                    sentence_index=idx,
                    sentence_text=sentence.text,
                    start_time=sentence.start,
                    end_time=sentence.end,
                    confidence_score=sentence.confidence,
                    words=[
                        TranscriptWord(
                            word_index=word_idx,
                            word_text=word.text[:255],
                            start_time=word.start,
                            end_time=word.end,
                            confidence_score=word.confidence,
                        )
                        for word_idx, word in enumerate(sentence.words)
                    ],
                )
                for idx, sentence in enumerate(result["sentences"])
            ],
        )
        db.add(transcript)

        # Update audio file status
        audio_file.upload_status = "ready"
        if not audio_file.duration_seconds:
            audio_file.duration_seconds = result["duration"]
        db.commit()
        db.refresh(transcript)

        logger.info(
            f"Transcription completed for audio file {audio_file_id}: "
            f"{transcript.id} (status=completed)"
        )

        return {
            "status": "accepted",
            "transcript_id": transcript.id,
            "audio_file_id": audio_file_id,
            "processing_status": "completed",
            "word_count": result["word_count"],
            "sentence_count": result["sentence_count"],
            "duration": result["duration"],
            "language": result["language"],
        }

    except (NotFoundError, ValidationError, ConflictError):
        raise
    except AudioProcessingError as e:
        logger.error(f"Transcription error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during transcription: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Transcription failed")


@router.get("/{transcript_id}", response_model=TranscriptDetailedResponse)
def get_transcript(transcript_id: int, db: Session = Depends(get_db)):
    """
    Get complete transcript with all details.

    Args:
        transcript_id: ID of transcript
        db: Database session

    Returns:
        Detailed transcript with sentences and statistics
    """
    try:
        transcript_repo = TranscriptRepository(db)
        transcript = transcript_repo.get_by_id(transcript_id)

        if not transcript:
            raise NotFoundError(f"Transcript {transcript_id} not found")

        # Get sentences
        sentence_repo = TranscriptSentenceRepository(db)
        sentences = sentence_repo.get_transcript_sentences(transcript_id)

        return TranscriptDetailedResponse(
            id=transcript.id,
            audio_file_id=transcript.audio_file_id,
            full_text=transcript.full_text,
            language_code=transcript.language_code,
            confidence_score=transcript.confidence_score,
            processing_status=transcript.processing_status,
            sentence_count=len(sentences),
            word_count=sum(len(s.words) for s in sentences) if sentences else 0,
            sentences=[
                TranscriptSentenceResponse(
                    id=s.id,
                    sentence_index=s.sentence_index,
                    sentence_text=s.sentence_text,
                    start_time=s.start_time,
                    end_time=s.end_time,
                    confidence_score=s.confidence_score,
                    words=[
                        TranscriptWordResponse(
                            id=w.id,
                            word_index=w.word_index,
                            word_text=w.word_text,
                            start_time=w.start_time,
                            end_time=w.end_time,
                            confidence_score=w.confidence_score,
                        )
                        for w in s.words
                    ],
                )
                for s in sentences
            ],
            created_at=transcript.created_at,
            updated_at=transcript.updated_at,
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transcript: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve transcript")


@router.get("/{transcript_id}/sentences", response_model=list[TranscriptSentenceResponse])
def get_sentences(transcript_id: int, db: Session = Depends(get_db)):
    """
    Get sentences for a transcript with timing information.

    Args:
        transcript_id: ID of transcript
        db: Database session

    Returns:
        List of sentences with word-level timestamps
    """
    try:
        transcript_repo = TranscriptRepository(db)
        transcript = transcript_repo.get_by_id(transcript_id)

        if not transcript:
            raise NotFoundError(f"Transcript {transcript_id} not found")

        sentence_repo = TranscriptSentenceRepository(db)
        sentences = sentence_repo.get_transcript_sentences(transcript_id)

        return [
            TranscriptSentenceResponse(
                id=s.id,
                sentence_index=s.sentence_index,
                sentence_text=s.sentence_text,
                start_time=s.start_time,
                end_time=s.end_time,
                confidence_score=s.confidence_score,
                words=[
                    TranscriptWordResponse(
                        id=w.id,
                        word_index=w.word_index,
                        word_text=w.word_text,
                        start_time=w.start_time,
                        end_time=w.end_time,
                        confidence_score=w.confidence_score,
                    )
                    for w in s.words
                ],
            )
            for s in sentences
        ]

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving sentences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sentences")


@router.get("/{transcript_id}/words", response_model=list[TranscriptWordResponse])
def get_words(transcript_id: int, db: Session = Depends(get_db)):
    """
    Get all words for a transcript with timing information.

    Args:
        transcript_id: ID of transcript
        db: Database session

    Returns:
        List of words with precise timing
    """
    try:
        transcript_repo = TranscriptRepository(db)
        transcript = transcript_repo.get_by_id(transcript_id)

        if not transcript:
            raise NotFoundError(f"Transcript {transcript_id} not found")

        sentence_repo = TranscriptSentenceRepository(db)
        sentences = sentence_repo.get_transcript_sentences(transcript_id)

        words = []
        for sentence in sentences:
            for word in sentence.words:
                words.append(
                    TranscriptWordResponse(
                        id=word.id,
                        word_index=word.word_index,
                        word_text=word.word_text,
                        start_time=word.start_time,
                        end_time=word.end_time,
                        confidence_score=word.confidence_score,
                    )
                )

        return words

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error retrieving words: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve words")


@router.post("/{transcript_id}/search", response_model=SearchResponse)
def search_transcript(
    transcript_id: int,
    query: str = Query(..., min_length=1),
    case_sensitive: bool = Query(False),
    db: Session = Depends(get_db),
):
    """
    Full-text search within a transcript.

    Args:
        transcript_id: ID of transcript
        query: Search query
        case_sensitive: Whether search is case-sensitive
        db: Database session

    Returns:
        Search results with context and timestamps
    """
    try:
        transcript_repo = TranscriptRepository(db)
        transcript = transcript_repo.get_by_id(transcript_id)

        if not transcript:
            raise NotFoundError(f"Transcript {transcript_id} not found")

        # Perform search
        sentence_repo = TranscriptSentenceRepository(db)
        results = sentence_repo.search_by_text(transcript_id, query)

        search_results = []
        for result in results:
            match_text = result.sentence_text
            if not case_sensitive:
                search_results.append(
                    SearchResult(
                        sentence_id=result.id,
                        sentence_text=match_text,
                        start_time=result.start_time,
                        end_time=result.end_time,
                        context=match_text,
                    )
                )
            else:
                if query in match_text:
                    search_results.append(
                        SearchResult(
                            sentence_id=result.id,
                            sentence_text=match_text,
                            start_time=result.start_time,
                            end_time=result.end_time,
                            context=match_text,
                        )
                    )

        return SearchResponse(
            query=query, total_results=len(search_results), results=search_results
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error searching transcript: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/{transcript_id}/export/{export_format}", status_code=201, response_model=dict)
def export_transcript(
    transcript_id: int,
    export_format: str,
    db: Session = Depends(get_db),
):
    """
    Export transcript in specified format.

    Supported formats: txt, json, csv, srt, vtt

    Args:
        transcript_id: ID of transcript
        export_format: Format to export (txt, json, csv, srt, vtt)
        db: Database session

    Returns:
        Export metadata and download URL
    """
    try:
        if export_format not in TranscriptExporter.SUPPORTED_FORMATS:
            raise ValidationError(
                f"Unsupported export format '{export_format}'. "
                f"Supported: {', '.join(TranscriptExporter.SUPPORTED_FORMATS)}"
            )

        # Get transcript with sentences/words
        transcript_repo = TranscriptRepository(db)
        transcript = transcript_repo.get_by_id(transcript_id)

        if not transcript:
            raise NotFoundError(f"Transcript {transcript_id} not found")

        sentence_repo = TranscriptSentenceRepository(db)
        sentences = sentence_repo.get_transcript_sentences(transcript_id)

        # Convert ORM objects to processor format
        from app.services.transcript_processor import Sentence, Word

        sentences_data = [
            Sentence(
                text=s.sentence_text,
                start=s.start_time,
                end=s.end_time,
                words=[
                    Word(
                        text=w.word_text,
                        start=w.start_time,
                        end=w.end_time,
                        confidence=w.confidence_score,
                    )
                    for w in s.words
                ],
                confidence=s.confidence_score,
            )
            for s in sentences
        ]

        # Export in requested format
        content = TranscriptExporter.export(
            format=export_format,
            full_text=transcript.full_text,
            sentences=sentences_data,
            metadata={
                "transcript_id": transcript_id,
                "audio_file_id": transcript.audio_file_id,
                "language": transcript.language_code,
                "duration": getattr(transcript.audio_file, "duration_seconds", None),
            },
        )

        # Save export record
        export_repo = ExportRepository(db)
        export_file_path = (
            f"{settings.EXPORT_DIR}/{transcript_id}_{export_format}"
            f"{TranscriptExporter.get_file_extension(export_format)}"
        )

        # Write file
        from pathlib import Path

        export_path = Path(export_file_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(content, encoding="utf-8")

        export = export_repo.create(
            transcript_id=transcript_id,
            export_format=export_format,
            file_path=str(export_path),
            file_size_bytes=len(content.encode("utf-8")),
        )

        logger.info(f"Exported transcript {transcript_id} to {export_format}")

        return {
            "export_id": export.id,
            "transcript_id": transcript_id,
            "format": export_format,
            "file_path": str(export_path),
            "file_size_bytes": export.file_size_bytes,
            "download_url": f"/api/v1/exports/{export.id}/download",
            "created_at": export.created_at.isoformat(),
        }

    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error exporting transcript: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/transcription-status/{audio_file_id}", response_model=dict)
def get_transcription_status(audio_file_id: int, db: Session = Depends(get_db)):
    """
    Get transcription status for an audio file.

    Args:
        audio_file_id: ID of audio file
        db: Database session

    Returns:
        Status indicating whether transcription is pending, in progress, or complete
    """
    try:
        transcript_repo = TranscriptRepository(db)
        transcript = transcript_repo.get_by_audio_file_id(audio_file_id)

        if not transcript:
            return {
                "audio_file_id": audio_file_id,
                "status": "pending",
                "transcript_id": None,
            }

        return {
            "audio_file_id": audio_file_id,
            "status": transcript.processing_status,
            "transcript_id": transcript.id,
            "completed_at": transcript.updated_at.isoformat() if transcript.updated_at else None,
        }

    except Exception as e:
        logger.error(f"Error getting transcription status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get status")


@router.delete("/{transcript_id}", status_code=204)
def delete_transcript(transcript_id: int, db: Session = Depends(get_db)):
    """
    Delete a transcript and associated data.

    Args:
        transcript_id: ID of transcript to delete
        db: Database session
    """
    try:
        transcript_repo = TranscriptRepository(db)
        transcript = transcript_repo.get_by_id(transcript_id)

        if not transcript:
            raise NotFoundError(f"Transcript {transcript_id} not found")

        # Soft delete
        transcript_repo.soft_delete(transcript_id)

        logger.info(f"Deleted transcript {transcript_id}")

        return None

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting transcript: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete transcript")


@exports_router.get("/{export_id}/download")
def download_export(export_id: int, db: Session = Depends(get_db)):
    """
    Download a previously generated export file.

    Args:
        export_id: ID of export
        db: Database session
    """
    export_repo = ExportRepository(db)
    export = export_repo.get_by_id(export_id)

    if not export or not Path(export.file_path).exists():
        raise NotFoundError(f"Export {export_id} not found")

    export_repo.update(export_id, download_count=export.download_count + 1)

    return FileResponse(
        export.file_path,
        media_type="application/octet-stream",
        filename=f"transcript_{export.transcript_id}{Path(export.file_path).suffix}",
    )
