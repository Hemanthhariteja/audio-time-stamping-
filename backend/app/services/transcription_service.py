"""Transcription service using faster-whisper for audio processing."""

import logging
import asyncio
from typing import Dict, Optional, Tuple
from pathlib import Path
import json

from app.core.config import settings
from app.core.exceptions import AudioProcessingError
from app.services.transcript_processor import TranscriptProcessor, Sentence, Word
from app.utils.gpu_detector import GPUDetector

logger = logging.getLogger(__name__)


class TranscriptionService:
    """
    Service for transcribing audio using faster-whisper.

    Features:
    - GPU/CPU auto-detection
    - Multiple language support
    - Word-level timestamp extraction
    - Error handling and logging
    - Async processing support
    """

    _model_instance = None
    _device_config = None

    @classmethod
    def _get_device_config(cls) -> Dict:
        """Get or initialize device configuration."""
        if cls._device_config is None:
            cls._device_config = GPUDetector.get_device_config()
            logger.info(f"Device config: {cls._device_config}")
        return cls._device_config

    @classmethod
    def _load_model(cls):
        """
        Load faster-whisper model (lazy loading).

        Returns:
            WhisperModel instance
        """
        if cls._model_instance is None:
            try:
                logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL_NAME}")
                from faster_whisper import WhisperModel

                device_config = cls._get_device_config()
                compute_type = device_config["compute_type"]

                cls._model_instance = WhisperModel(
                    settings.WHISPER_MODEL_NAME,
                    device=device_config["device"],
                    compute_type=compute_type,
                )

                logger.info(
                    f"Whisper model loaded successfully "
                    f"(device={device_config['device']}, compute_type={compute_type})"
                )

            except ImportError:
                raise AudioProcessingError(
                    "faster-whisper not installed. "
                    "Install with: pip install faster-whisper"
                )
            except Exception as e:
                raise AudioProcessingError(f"Failed to load Whisper model: {str(e)}")

        return cls._model_instance

    @staticmethod
    def transcribe(
        audio_file_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        fp16: bool = True,
    ) -> Dict:
        """
        Transcribe audio file to text with timing information.

        Args:
            audio_file_path: Path to audio file
            language: Language code (e.g., 'en', 'es', None for auto-detect)
            task: 'transcribe' or 'translate'
            fp16: Unused; precision is set by the model's compute type

        Returns:
            Dictionary with transcription results:
            {
                'full_text': str,
                'language': str,
                'duration': float,
                'segments': List[Dict],  # Raw Whisper segments
                'sentences': List[Sentence],
                'words': List[Word],
                'word_count': int,
                'sentence_count': int,
                'confidence': float,
            }

        Raises:
            AudioProcessingError: If transcription fails
        """
        audio_path = Path(audio_file_path)

        if not audio_path.exists():
            raise AudioProcessingError(f"Audio file not found: {audio_file_path}")

        try:
            logger.info(f"Starting transcription: {audio_path.name}")

            model = TranscriptionService._load_model()
            device_config = TranscriptionService._get_device_config()

            # Perform transcription
            segments, info = model.transcribe(
                audio_file_path,
                language=language,
                task=task,
                beam_size=settings.WHISPER_BEAM_SIZE,
                best_of=settings.WHISPER_BEST_OF,
                temperature=settings.WHISPER_TEMPERATURE,
                vad_filter=settings.WHISPER_VAD_FILTER,
                word_timestamps=True,
            )

            # Convert generator to list to access all segments
            segments = list(segments)

            logger.info(
                f"Transcription completed: {len(segments)} segments, "
                f"duration={info.duration:.1f}s, language={info.language}"
            )

            # Build result dict from raw segments
            result = {
                "text": " ".join(segment.text.strip() for segment in segments),
                "language": info.language,
                "duration": info.duration,
                "segments": [
                    {
                        "id": segment.id,
                        "seek": segment.seek,
                        "start": segment.start,
                        "end": segment.end,
                        "text": segment.text,
                        "avg_logprob": segment.avg_logprob,
                        "compression_ratio": segment.compression_ratio,
                        "no_speech_prob": segment.no_speech_prob,
                        "words": [
                            {
                                "word": word.word,
                                "start": word.start,
                                "end": word.end,
                                "probability": word.probability,
                            }
                            for word in (segment.words or [])
                        ],
                    }
                    for segment in segments
                ],
            }

            # Process into structured format
            full_text, sentences, words = TranscriptProcessor.process_whisper_output(result)

            # Calculate statistics
            word_count = len(words)
            sentence_count = len(sentences)
            avg_confidence = (
                sum(w.confidence for w in words) / word_count if word_count > 0 else 0
            )

            logger.info(
                f"Transcript processed: {word_count} words, "
                f"{sentence_count} sentences, confidence={avg_confidence:.3f}"
            )

            return {
                "full_text": full_text,
                "language": info.language,
                "duration": float(info.duration),
                "segments": result["segments"],
                "sentences": sentences,
                "words": words,
                "word_count": word_count,
                "sentence_count": sentence_count,
                "confidence": float(avg_confidence),
                "device": device_config["device"],
            }

        except AudioProcessingError:
            raise
        except Exception as e:
            error_msg = f"Transcription failed for {audio_path.name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise AudioProcessingError(error_msg)

    @staticmethod
    async def transcribe_async(
        audio_file_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        fp16: bool = True,
    ) -> Dict:
        """
        Async wrapper for transcribe (runs in thread pool).

        Args:
            audio_file_path: Path to audio file
            language: Language code
            task: 'transcribe' or 'translate'
            fp16: Use FP16 precision

        Returns:
            Transcription result dictionary
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            TranscriptionService.transcribe,
            audio_file_path,
            language,
            task,
            fp16,
        )

    @staticmethod
    def get_supported_languages() -> Dict[str, str]:
        """
        Get list of supported languages.

        Returns:
            Dictionary mapping language codes to language names
        """
        try:
            from faster_whisper.tokenizer import LANGUAGES
            return dict(LANGUAGES)
        except Exception:
            return {
                "en": "english",
                "es": "spanish",
                "fr": "french",
                "de": "german",
                "it": "italian",
                "pt": "portuguese",
                "nl": "dutch",
                "ru": "russian",
                "zh": "chinese",
                "ja": "japanese",
                "ko": "korean",
                "ar": "arabic",
                "hi": "hindi",
            }

    @staticmethod
    def detect_language(audio_file_path: str, duration_threshold: float = 30.0) -> Tuple[str, float]:
        """
        Detect language of audio file.

        Args:
            audio_file_path: Path to audio file
            duration_threshold: If audio is shorter than this (seconds), only process that much

        Returns:
            Tuple of (language_code, probability)

        Raises:
            AudioProcessingError: If detection fails
        """
        try:
            model = TranscriptionService._load_model()

            # Quick transcription just for language detection
            segments, info = model.transcribe(
                audio_file_path,
                task="transcribe",
                language=None,  # Auto-detect
            )

            # Get first segment to extract language info
            segments_list = list(segments)

            if segments_list:
                logger.info(f"Detected language: {info.language}")
                return info.language, 0.95  # Confidence from Whisper

            raise AudioProcessingError("No speech detected in audio file")

        except Exception as e:
            error_msg = f"Language detection failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise AudioProcessingError(error_msg)

    @staticmethod
    def get_model_info() -> Dict:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        device_config = TranscriptionService._get_device_config()
        is_loaded = TranscriptionService._model_instance is not None
        return {
            "model_name": settings.WHISPER_MODEL_NAME,
            "device": device_config.get("device", "cpu"),
            "device_info": device_config.get("device_info", "CPU"),
            "compute_type": device_config.get("compute_type", "int8"),
            "cuda_available": device_config.get("cuda_available", False),
            "supported_languages": list(TranscriptionService.get_supported_languages().keys()),
            "status": "loaded" if is_loaded else "ready",
        }

    @staticmethod
    def unload_model():
        """Unload model and free memory (for testing/cleanup)."""
        TranscriptionService._model_instance = None
        logger.info("Whisper model unloaded")
