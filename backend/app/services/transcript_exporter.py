"""Export transcripts in multiple formats: TXT, JSON, CSV, SRT, VTT."""

import json
import csv
import logging
from io import StringIO
from typing import List, Dict, Literal
from datetime import datetime

from app.services.transcript_processor import Sentence, Word

logger = logging.getLogger(__name__)


class TranscriptExporter:
    """Export transcript data in multiple formats."""

    SUPPORTED_FORMATS = ("txt", "json", "csv", "srt", "vtt")

    @staticmethod
    def _format_timestamp_srt(seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _format_timestamp_vtt(seconds: float) -> str:
        """Convert seconds to VTT timestamp format (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    @staticmethod
    def to_txt(full_text: str, sentences: List[Sentence]) -> str:
        """
        Export to plain text format.

        Args:
            full_text: Complete transcript text
            sentences: List of Sentence objects

        Returns:
            Plain text transcript
        """
        return full_text

    @staticmethod
    def to_json(
        full_text: str,
        sentences: List[Sentence],
        metadata: Dict = None,
    ) -> str:
        """
        Export to JSON format with full metadata.

        Args:
            full_text: Complete transcript text
            sentences: List of Sentence objects
            metadata: Additional metadata (timestamp, audio_duration, etc.)

        Returns:
            JSON string
        """
        if metadata is None:
            metadata = {}

        data = {
            "text": full_text,
            "metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "total_words": sum(len(s.words) for s in sentences),
                "total_sentences": len(sentences),
                **metadata,
            },
            "sentences": [
                {
                    "index": i,
                    "text": sentence.text,
                    "start_time": round(sentence.start, 2),
                    "end_time": round(sentence.end, 2),
                    "confidence": round(sentence.confidence, 3),
                    "word_count": len(sentence.words),
                    "words": [
                        {
                            "text": word.text,
                            "start_time": round(word.start, 2),
                            "end_time": round(word.end, 2),
                            "confidence": round(word.confidence, 3),
                        }
                        for word in sentence.words
                    ],
                }
                for i, sentence in enumerate(sentences, 1)
            ],
        }

        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def to_csv(full_text: str, sentences: List[Sentence]) -> str:
        """
        Export to CSV format (word-level).

        Args:
            full_text: Complete transcript text
            sentences: List of Sentence objects

        Returns:
            CSV string
        """
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "Sentence #",
                "Word #",
                "Word",
                "Start Time (s)",
                "End Time (s)",
                "Duration (s)",
                "Confidence",
                "Sentence Text",
            ]
        )

        # Write word rows
        for sent_idx, sentence in enumerate(sentences, 1):
            for word_idx, word in enumerate(sentence.words, 1):
                duration = round(word.end - word.start, 3)
                writer.writerow(
                    [
                        sent_idx,
                        word_idx,
                        word.text,
                        round(word.start, 3),
                        round(word.end, 3),
                        duration,
                        round(word.confidence, 3),
                        sentence.text,
                    ]
                )

        return output.getvalue()

    @staticmethod
    def to_srt(sentences: List[Sentence]) -> str:
        """
        Export to SRT subtitle format.

        Args:
            sentences: List of Sentence objects

        Returns:
            SRT formatted string
        """
        srt_lines = []

        for i, sentence in enumerate(sentences, 1):
            start_time = TranscriptExporter._format_timestamp_srt(sentence.start)
            end_time = TranscriptExporter._format_timestamp_srt(sentence.end)

            srt_lines.append(str(i))
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(sentence.text)
            srt_lines.append("")  # Blank line between entries

        return "\n".join(srt_lines)

    @staticmethod
    def to_vtt(sentences: List[Sentence]) -> str:
        """
        Export to VTT (WebVTT) subtitle format.

        Args:
            sentences: List of Sentence objects

        Returns:
            VTT formatted string
        """
        vtt_lines = ["WEBVTT\n"]

        for sentence in sentences:
            start_time = TranscriptExporter._format_timestamp_vtt(sentence.start)
            end_time = TranscriptExporter._format_timestamp_vtt(sentence.end)

            vtt_lines.append(f"{start_time} --> {end_time}")
            vtt_lines.append(sentence.text)
            vtt_lines.append("")  # Blank line between entries

        return "\n".join(vtt_lines)

    @staticmethod
    def export(
        format: Literal["txt", "json", "csv", "srt", "vtt"],
        full_text: str,
        sentences: List[Sentence],
        metadata: Dict = None,
    ) -> str:
        """
        Export transcript in specified format.

        Args:
            format: Export format (txt, json, csv, srt, vtt)
            full_text: Complete transcript text
            sentences: List of Sentence objects
            metadata: Optional metadata for JSON export

        Returns:
            Formatted transcript string

        Raises:
            ValueError: If format is not supported
        """
        format = format.lower()

        if format not in TranscriptExporter.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format '{format}'. "
                f"Supported formats: {', '.join(TranscriptExporter.SUPPORTED_FORMATS)}"
            )

        logger.info(f"Exporting transcript to {format.upper()} format")

        if format == "txt":
            return TranscriptExporter.to_txt(full_text, sentences)
        elif format == "json":
            return TranscriptExporter.to_json(full_text, sentences, metadata)
        elif format == "csv":
            return TranscriptExporter.to_csv(full_text, sentences)
        elif format == "srt":
            return TranscriptExporter.to_srt(sentences)
        elif format == "vtt":
            return TranscriptExporter.to_vtt(sentences)

    @staticmethod
    def get_file_extension(format: str) -> str:
        """Get file extension for export format."""
        extensions = {
            "txt": ".txt",
            "json": ".json",
            "csv": ".csv",
            "srt": ".srt",
            "vtt": ".vtt",
        }
        return extensions.get(format.lower(), f".{format}")

    @staticmethod
    def get_content_type(format: str) -> str:
        """Get MIME type for export format."""
        content_types = {
            "txt": "text/plain",
            "json": "application/json",
            "csv": "text/csv",
            "srt": "application/x-subrip",
            "vtt": "text/vtt",
        }
        return content_types.get(format.lower(), "text/plain")
