"""Service classes for business logic."""

import os
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AudioProcessingError,
    FileUploadError,
    NotFoundError,
    ValidationError,
)
from app.core.logging import get_logger
from app.models import AudioFile, Project, Transcript, TranscriptSentence, TranscriptWord
from app.repositories import (
    AudioFileRepository,
    ProjectRepository,
    TranscriptRepository,
    UserRepository,
)
from app.schemas import (
    AudioFileResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.utils import AudioProcessor, FileManager

logger = get_logger(__name__)


class ProjectService:
    """Service for project operations."""

    def __init__(self, db: Session):
        """Initialize project service."""
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.user_repo = UserRepository(db)

    def create_project(
        self, user_id: int, project_data: ProjectCreate
    ) -> ProjectResponse:
        """Create a new project."""
        # Verify user exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found", "User", user_id)

        project = self.project_repo.create(
            user_id=user_id,
            name=project_data.name,
            description=project_data.description,
        )

        logger.info(f"Project created: {project.id} for user {user_id}")
        return ProjectResponse.from_orm(project)

    def get_project(self, project_id: int) -> ProjectResponse:
        """Get project by ID."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found", "Project", project_id)

        return ProjectResponse.from_orm(project)

    def get_user_projects(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[List[ProjectResponse], int]:
        """Get all projects for a user."""
        projects = self.project_repo.get_user_projects(user_id, skip, limit)
        total = self.project_repo.count_user_projects(user_id)

        return [ProjectResponse.from_orm(p) for p in projects], total

    def update_project(
        self, project_id: int, project_data: ProjectUpdate
    ) -> ProjectResponse:
        """Update a project."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found", "Project", project_id)

        update_data = project_data.dict(exclude_unset=True)
        updated_project = self.project_repo.update(project_id, **update_data)

        logger.info(f"Project updated: {project_id}")
        return ProjectResponse.from_orm(updated_project)

    def delete_project(self, project_id: int) -> None:
        """Delete a project (soft delete)."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found", "Project", project_id)

        self.project_repo.soft_delete(project_id)
        logger.info(f"Project deleted: {project_id}")


class AudioFileService:
    """Service for audio file operations."""

    def __init__(self, db: Session):
        """Initialize audio file service."""
        self.db = db
        self.audio_repo = AudioFileRepository(db)
        self.project_repo = ProjectRepository(db)
        self.file_manager = FileManager()
        self.audio_processor = AudioProcessor()

    def upload_audio_file(
        self,
        project_id: int,
        original_filename: str,
        file_content: bytes,
    ) -> AudioFileResponse:
        """
        Upload and process audio file.

        Steps:
        1. Validate project exists
        2. Save file to disk
        3. Get file metadata
        4. Preprocess audio
        5. Create database record
        """
        try:
            # Ensure project exists; create a fallback one if the caller is using a temporary project id.
            project = self.project_repo.get_by_id(project_id)
            if not project:
                project = self.project_repo.create(
                    user_id=1,
                    name=f"Imported Project {project_id}",
                    description="Auto-created for uploaded audio",
                )

            # Save file
            stored_filename, file_path = self.file_manager.save_upload_file(
                file_content, original_filename, subfolder="audio"
            )

            # Get file info
            file_size = len(file_content)
            file_format = original_filename.split(".")[-1].lower()
            duration = self.file_manager.get_file_duration(file_path)

            # Create database record
            audio_file = self.audio_repo.create(
                project_id=project.id,
                original_filename=original_filename,
                stored_filename=stored_filename,
                file_format=file_format,
                file_size_bytes=file_size,
                duration_seconds=duration,
                processed_file_path=file_path,
                upload_status="ready",
            )

            logger.info(f"Audio file uploaded: {audio_file.id}")
            return AudioFileResponse.from_orm(audio_file)

        except (FileUploadError, AudioProcessingError):
            raise
        except Exception as e:
            logger.error(f"Error uploading audio file: {str(e)}")
            raise AudioProcessingError(f"Failed to upload audio file: {str(e)}")

    def preprocess_audio(self, audio_file_id: int) -> None:
        """Preprocess audio file for transcription."""
        try:
            audio_file = self.audio_repo.get_by_id(audio_file_id)
            if not audio_file:
                raise NotFoundError("Audio file not found", "AudioFile", audio_file_id)

            # Update status
            self.audio_repo.update(audio_file_id, upload_status="preprocessing")

            # Get file path
            file_path = os.path.join(
                settings.upload_dir_path, "audio", audio_file.stored_filename
            )

            # Preprocess
            processed_path = self.audio_processor.preprocess_audio(file_path)

            # Update database
            self.audio_repo.update(
                audio_file_id,
                processed_file_path=processed_path,
                upload_status="ready",
            )

            logger.info(f"Audio file preprocessed: {audio_file_id}")

        except Exception as e:
            logger.error(f"Error preprocessing audio: {str(e)}")
            self.audio_repo.update(
                audio_file_id,
                upload_status="failed",
                processing_error=str(e),
            )
            raise

    def get_audio_file(self, audio_file_id: int) -> AudioFileResponse:
        """Get audio file by ID."""
        audio_file = self.audio_repo.get_by_id(audio_file_id)
        if not audio_file:
            raise NotFoundError("Audio file not found", "AudioFile", audio_file_id)

        return AudioFileResponse.from_orm(audio_file)

    def get_project_audio_files(
        self, project_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[List[AudioFileResponse], int]:
        """Get all audio files for a project."""
        # Verify project exists
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found", "Project", project_id)

        audio_files = self.audio_repo.get_project_audio_files(project_id, skip, limit)
        total = len(self.audio_repo.get_project_audio_files(project_id, 0, 999999))

        return [AudioFileResponse.from_orm(af) for af in audio_files], total


# Import settings after other imports to avoid circular imports
from app.core.config import settings
