"""Tests for transcription service."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.transcription_service import TranscriptionService
from app.core.exceptions import AudioProcessingError


class TestTranscriptionService:
    """Test TranscriptionService functionality."""

    def test_get_device_config(self):
        """Test device configuration retrieval."""
        config = TranscriptionService._get_device_config()

        assert config is not None
        assert "device" in config
        assert "compute_type" in config
        assert "cuda_available" in config
        assert config["compute_type"] in ["float16", "int8", "cpu"]

    @patch("app.services.transcription_service.TranscriptionService._load_model")
    def test_get_model_info(self, mock_load):
        """Test model info retrieval."""
        info = TranscriptionService.get_model_info()

        assert "model_name" in info
        assert "device" in info
        assert "compute_type" in info
        assert "status" in info

    def test_get_supported_languages(self):
        """Test getting supported languages."""
        languages = TranscriptionService.get_supported_languages()

        assert isinstance(languages, dict)
        assert len(languages) > 0
        assert "en" in languages

    def test_unload_model(self):
        """Test model unloading."""
        # Set dummy model instance
        TranscriptionService._model_instance = MagicMock()
        assert TranscriptionService._model_instance is not None

        # Unload
        TranscriptionService.unload_model()
        assert TranscriptionService._model_instance is None

    @patch("app.services.transcription_service.TranscriptionService._load_model")
    def test_transcribe_file_not_found(self, mock_model):
        """Test transcription with non-existent file."""
        with pytest.raises(AudioProcessingError):
            TranscriptionService.transcribe("/non/existent/file.mp3")

    @patch("app.services.transcription_service.Path.exists")
    @patch("app.services.transcription_service.TranscriptionService._load_model")
    def test_transcribe_processing_error(self, mock_model, mock_exists):
        """Test transcription with processing error."""
        mock_exists.return_value = True
        mock_model.side_effect = Exception("Model load error")

        with pytest.raises(AudioProcessingError):
            TranscriptionService.transcribe("/some/file.mp3")
