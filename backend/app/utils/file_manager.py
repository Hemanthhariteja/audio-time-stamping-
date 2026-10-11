"""File management utilities."""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.exceptions import FileUploadError
from app.core.logging import get_logger

logger = get_logger(__name__)


class FileManager:
    """Manages file operations for uploads and exports."""

    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """Generate a unique filename based on timestamp and original name."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        name, ext = os.path.splitext(original_filename)
        return f"{timestamp}_{name[:50]}{ext}"

    @staticmethod
    def validate_file_format(filename: str, allowed_formats: list[str]) -> bool:
        """Validate file format."""
        ext = os.path.splitext(filename)[1].lstrip(".").lower()
        return ext in allowed_formats

    @staticmethod
    def validate_file_size(file_size: int, max_size: int = settings.MAX_UPLOAD_SIZE_BYTES) -> bool:
        """Validate file size."""
        return file_size <= max_size

    @staticmethod
    def save_upload_file(
        file_content: bytes,
        original_filename: str,
        subfolder: str = "audio",
    ) -> tuple[str, str]:
        """
        Save uploaded file to disk.

        Returns:
            Tuple of (stored_filename, file_path)
        """
        try:
            # Validate format
            if not FileManager.validate_file_format(
                original_filename, settings.ALLOWED_AUDIO_FORMATS
            ):
                raise FileUploadError(
                    f"File format not supported. Allowed formats: {', '.join(settings.ALLOWED_AUDIO_FORMATS)}"
                )

            # Validate size
            if not FileManager.validate_file_size(len(file_content)):
                raise FileUploadError(
                    f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
                )

            # Generate unique filename
            stored_filename = FileManager.generate_unique_filename(original_filename)

            # Create subfolder
            upload_dir = settings.upload_dir_path / subfolder
            upload_dir.mkdir(parents=True, exist_ok=True)

            # Save file
            file_path = upload_dir / stored_filename
            with open(file_path, "wb") as f:
                f.write(file_content)

            logger.info(f"File saved: {file_path}")
            return stored_filename, str(file_path)

        except FileUploadError:
            raise
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise FileUploadError(f"Failed to save file: {str(e)}")

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Delete a file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes."""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.error(f"Error getting file size: {str(e)}")
            return 0

    @staticmethod
    def get_file_duration(file_path: str) -> Optional[float]:
        """Get audio file duration using ffprobe, falling back to PyAV."""
        if shutil.which("ffprobe") is None:
            return FileManager._get_duration_with_av(file_path)

        try:
            import subprocess

            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    file_path,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                duration = float(result.stdout.strip())
                return duration
            else:
                logger.warning(f"Could not get duration for {file_path}")
                return FileManager._get_duration_with_av(file_path)

        except Exception as e:
            logger.error(f"Error getting file duration: {str(e)}")
            return FileManager._get_duration_with_av(file_path)

    @staticmethod
    def _get_duration_with_av(file_path: str) -> Optional[float]:
        """Get audio file duration using PyAV (bundled with faster-whisper)."""
        try:
            import av

            with av.open(file_path) as container:
                if container.duration is not None:
                    return float(container.duration) / av.time_base
                stream = container.streams.audio[0]
                if stream.duration is not None and stream.time_base is not None:
                    return float(stream.duration * stream.time_base)
            return None

        except Exception as e:
            logger.warning(f"Could not get duration for {file_path}: {str(e)}")
            return None

    @staticmethod
    def cleanup_old_files(
        directory: str,
        days_old: int = 30,
    ) -> int:
        """Delete files older than specified days."""
        try:
            count = 0
            cutoff_time = datetime.utcnow().timestamp() - (days_old * 24 * 3600)

            for file_path in Path(directory).glob("**/*"):
                if file_path.is_file():
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        count += 1

            logger.info(f"Cleaned up {count} files from {directory}")
            return count

        except Exception as e:
            logger.error(f"Error cleaning up files: {str(e)}")
            return 0
