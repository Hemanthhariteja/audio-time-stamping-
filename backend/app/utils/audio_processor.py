"""Audio processing utilities using FFmpeg."""

import os
import subprocess
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.exceptions import AudioProcessingError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AudioProcessor:
    """Handles audio processing using FFmpeg."""

    def __init__(self):
        """Initialize audio processor."""
        self.ffmpeg_path = settings.FFMPEG_PATH or "ffmpeg"
        self.ffprobe_path = "ffprobe"
        self._verify_ffmpeg()

    def _verify_ffmpeg(self) -> None:
        """Verify FFmpeg is installed and accessible."""
        try:
            subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                timeout=5,
                check=True,
            )
            logger.info("FFmpeg verified and accessible")
        except Exception as e:
            logger.warning(f"FFmpeg verification failed: {str(e)}. Some features may not work.")

    def convert_to_wav(
        self,
        input_file: str,
        output_file: Optional[str] = None,
    ) -> str:
        """
        Convert audio file to WAV format.

        Args:
            input_file: Path to input audio file
            output_file: Path to output WAV file (optional, auto-generated if not provided)

        Returns:
            Path to output WAV file
        """
        try:
            if not os.path.exists(input_file):
                raise AudioProcessingError(f"Input file not found: {input_file}")

            if output_file is None:
                output_file = input_file.replace(os.path.splitext(input_file)[1], ".wav")

            cmd = [
                self.ffmpeg_path,
                "-i",
                input_file,
                "-acodec",
                "pcm_s16le",
                "-ar",
                str(settings.AUDIO_SAMPLE_RATE),
                "-ac",
                str(settings.AUDIO_CHANNELS),
                "-y",  # Overwrite output
                output_file,
            ]

            logger.info(f"Converting audio: {input_file} -> {output_file}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )

            if result.returncode != 0:
                error_msg = result.stderr or "Unknown error"
                raise AudioProcessingError(
                    f"FFmpeg conversion failed: {error_msg}",
                    {"input_file": input_file, "error": error_msg},
                )

            if not os.path.exists(output_file):
                raise AudioProcessingError(f"Output file was not created: {output_file}")

            logger.info(f"Audio conversion completed: {output_file}")
            return output_file

        except AudioProcessingError:
            raise
        except Exception as e:
            logger.error(f"Audio conversion error: {str(e)}")
            raise AudioProcessingError(f"Failed to convert audio: {str(e)}")

    def get_audio_info(self, input_file: str) -> dict:
        """
        Get audio file information using ffprobe.

        Returns:
            Dictionary with audio properties
        """
        try:
            if not os.path.exists(input_file):
                raise AudioProcessingError(f"Input file not found: {input_file}")

            cmd = [
                self.ffprobe_path,
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                input_file,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                import json

                data = json.loads(result.stdout)
                stream = data.get("streams", [{}])[0]
                fmt = data.get("format", {})

                return {
                    "duration": float(fmt.get("duration", 0)),
                    "sample_rate": int(stream.get("sample_rate", 0)),
                    "channels": int(stream.get("channels", 0)),
                    "codec": stream.get("codec_name", "unknown"),
                    "bitrate": int(fmt.get("bit_rate", 0)),
                }
            else:
                raise AudioProcessingError("Could not read audio file information")

        except AudioProcessingError:
            raise
        except Exception as e:
            logger.error(f"Error getting audio info: {str(e)}")
            raise AudioProcessingError(f"Failed to get audio info: {str(e)}")

    def preprocess_audio(
        self,
        input_file: str,
        output_dir: Optional[str] = None,
    ) -> str:
        """
        Preprocess audio file for transcription.
        Converts to standardized format (WAV, 16kHz, mono).

        Args:
            input_file: Path to input audio file
            output_dir: Directory for output file (optional)

        Returns:
            Path to preprocessed audio file
        """
        try:
            if output_dir is None:
                output_dir = settings.upload_dir_path

            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Generate output filename
            base_name = Path(input_file).stem
            output_file = os.path.join(output_dir, f"{base_name}_preprocessed.wav")

            # Convert to standard format
            return self.convert_to_wav(input_file, output_file)

        except Exception as e:
            logger.error(f"Audio preprocessing error: {str(e)}")
            raise

    def get_duration(self, input_file: str) -> Optional[float]:
        """Get duration of audio file in seconds."""
        try:
            info = self.get_audio_info(input_file)
            return info.get("duration")
        except Exception as e:
            logger.warning(f"Could not get duration: {str(e)}")
            return None
