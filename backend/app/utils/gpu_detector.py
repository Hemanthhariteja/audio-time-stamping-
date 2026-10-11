"""GPU and CUDA detection utilities for Whisper transcription."""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class GPUDetector:
    """Detect GPU availability and configuration for audio processing."""

    @staticmethod
    def detect_cuda() -> Tuple[bool, str]:
        """
        Detect CUDA availability.

        Returns:
            Tuple of (cuda_available, device_info)
        """
        try:
            import torch

            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                current_device = torch.cuda.current_device()
                device_name = torch.cuda.get_device_name(current_device)
                memory_gb = torch.cuda.get_device_properties(current_device).total_memory / (
                    1024 ** 3
                )

                info = (
                    f"CUDA enabled: {device_name} ({device_count} device(s), "
                    f"{memory_gb:.1f} GB memory)"
                )
                logger.info(f"GPU detected: {info}")
                return True, info
            else:
                logger.info("CUDA not available, will use CPU")
                return False, "CPU only"
        except ImportError:
            logger.warning("torch not installed, cannot detect CUDA")
            return False, "CPU only"
        except Exception as e:
            logger.warning(f"Error detecting CUDA: {e}")
            return False, f"CPU only (error: {str(e)})"

    @staticmethod
    def get_compute_type() -> str:
        """
        Determine optimal compute type for faster-whisper.

        Returns:
            Compute type: "float16" on GPU, "int8" on CPU
        """
        cuda_available, _ = GPUDetector.detect_cuda()

        if cuda_available:
            return "float16"
        else:
            # Use int8 quantization on CPU for better performance
            return "int8"

    @staticmethod
    def get_device_config() -> dict:
        """
        Get complete device configuration for transcription.

        Returns:
            Dict with device, compute_type, and other settings
        """
        cuda_available, device_info = GPUDetector.detect_cuda()
        compute_type = GPUDetector.get_compute_type()

        return {
            "cuda_available": cuda_available,
            "device_info": device_info,
            "compute_type": compute_type,
            "device": "cuda" if cuda_available else "cpu",
        }
