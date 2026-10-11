"""Repository classes for database operations."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import (
    AudioFile,
    Export,
    Project,
    Transcript,
    TranscriptSentence,
    TranscriptWord,
    User,
)
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, db: Session):
        """Initialize user repository."""
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_active_by_email(self, email: str) -> Optional[User]:
        """Get active user by email."""
        return (
            self.db.query(User)
            .filter(and_(User.email == email, User.deleted_at.is_(None)))
            .first()
        )


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project model."""

    def __init__(self, db: Session):
        """Initialize project repository."""
        super().__init__(Project, db)

    def get_user_projects(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """Get all projects for a user."""
        return (
            self.db.query(Project)
            .filter(
                and_(Project.user_id == user_id, Project.deleted_at.is_(None))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_user_projects(self, user_id: int) -> int:
        """Count active projects for a user."""
        return (
            self.db.query(Project)
            .filter(
                and_(Project.user_id == user_id, Project.deleted_at.is_(None))
            )
            .count()
        )


class AudioFileRepository(BaseRepository[AudioFile]):
    """Repository for AudioFile model."""

    def __init__(self, db: Session):
        """Initialize audio file repository."""
        super().__init__(AudioFile, db)

    def get_project_audio_files(
        self, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[AudioFile]:
        """Get all audio files for a project."""
        return (
            self.db.query(AudioFile)
            .filter(
                and_(
                    AudioFile.project_id == project_id,
                    AudioFile.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_stored_filename(self, filename: str) -> Optional[AudioFile]:
        """Get audio file by stored filename."""
        return (
            self.db.query(AudioFile)
            .filter(AudioFile.stored_filename == filename)
            .first()
        )

    def get_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> List[AudioFile]:
        """Get audio files by upload status."""
        return (
            self.db.query(AudioFile)
            .filter(AudioFile.upload_status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )


class TranscriptRepository(BaseRepository[Transcript]):
    """Repository for Transcript model."""

    def __init__(self, db: Session):
        """Initialize transcript repository."""
        super().__init__(Transcript, db)

    def get_by_audio_file_id(self, audio_file_id: int) -> Optional[Transcript]:
        """Get transcript by audio file ID."""
        return (
            self.db.query(Transcript)
            .filter(Transcript.audio_file_id == audio_file_id)
            .first()
        )

    def search_by_text(
        self, query: str, skip: int = 0, limit: int = 100
    ) -> List[Transcript]:
        """Search transcripts by text content."""
        search_pattern = f"%{query}%"
        return (
            self.db.query(Transcript)
            .filter(Transcript.full_text.ilike(search_pattern))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Transcript]:
        """Get transcripts by processing status."""
        return (
            self.db.query(Transcript)
            .filter(Transcript.processing_status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )


class TranscriptSentenceRepository(BaseRepository[TranscriptSentence]):
    """Repository for TranscriptSentence model."""

    def __init__(self, db: Session):
        """Initialize transcript sentence repository."""
        super().__init__(TranscriptSentence, db)

    def get_transcript_sentences(self, transcript_id: int) -> List[TranscriptSentence]:
        """Get all sentences for a transcript."""
        return (
            self.db.query(TranscriptSentence)
            .filter(TranscriptSentence.transcript_id == transcript_id)
            .order_by(TranscriptSentence.sentence_index)
            .all()
        )

    def search_by_text(self, transcript_id: int, query: str) -> List[TranscriptSentence]:
        """Search for text in sentences within a transcript."""
        search_pattern = f"%{query}%"
        return (
            self.db.query(TranscriptSentence)
            .filter(
                and_(
                    TranscriptSentence.transcript_id == transcript_id,
                    TranscriptSentence.sentence_text.ilike(search_pattern),
                )
            )
            .all()
        )


class TranscriptWordRepository(BaseRepository[TranscriptWord]):
    """Repository for TranscriptWord model."""

    def __init__(self, db: Session):
        """Initialize transcript word repository."""
        super().__init__(TranscriptWord, db)

    def get_sentence_words(self, sentence_id: int) -> List[TranscriptWord]:
        """Get all words for a sentence."""
        return (
            self.db.query(TranscriptWord)
            .filter(TranscriptWord.sentence_id == sentence_id)
            .all()
        )

    def search_in_transcript(self, transcript_id: int, query: str) -> List[dict]:
        """Search for words in a transcript."""
        search_pattern = f"%{query}%"
        results = (
            self.db.query(TranscriptWord, TranscriptSentence)
            .join(
                TranscriptSentence,
                TranscriptWord.sentence_id == TranscriptSentence.id,
            )
            .join(
                Transcript,
                TranscriptSentence.transcript_id == Transcript.id,
            )
            .filter(
                and_(
                    Transcript.id == transcript_id,
                    TranscriptWord.word_text.ilike(search_pattern),
                )
            )
            .all()
        )
        return results


class ExportRepository(BaseRepository[Export]):
    """Repository for Export model."""

    def __init__(self, db: Session):
        """Initialize export repository."""
        super().__init__(Export, db)

    def get_transcript_exports(
        self, transcript_id: int, skip: int = 0, limit: int = 100
    ) -> List[Export]:
        """Get all exports for a transcript."""
        return (
            self.db.query(Export)
            .filter(
                and_(
                    Export.transcript_id == transcript_id,
                    Export.deleted_at.is_(None),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_expired_exports(self) -> List[Export]:
        """Get all expired exports."""
        return (
            self.db.query(Export)
            .filter(
                and_(
                    Export.expires_at.isnot(None),
                    Export.expires_at <= datetime.utcnow(),
                    Export.deleted_at.is_(None),
                )
            )
            .all()
        )
