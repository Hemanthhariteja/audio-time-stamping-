"""Tests for transcript export functionality."""

import pytest
import json
from app.services.transcript_exporter import TranscriptExporter
from app.services.transcript_processor import Sentence, Word


@pytest.fixture
def sample_transcript():
    """Create sample transcript data for testing."""
    words = [
        Word(text="Hello", start=0.0, end=0.5, confidence=0.99),
        Word(text="world", start=0.6, end=1.1, confidence=0.98),
        Word(text="This", start=2.0, end=2.3, confidence=0.97),
        Word(text="is", start=2.4, end=2.6, confidence=0.99),
        Word(text="a", start=2.7, end=2.9, confidence=0.95),
        Word(text="test.", start=3.0, end=3.5, confidence=0.96),
    ]

    sentences = [
        Sentence(
            text="Hello world",
            start=0.0,
            end=1.1,
            words=[words[0], words[1]],
            confidence=0.985,
        ),
        Sentence(
            text="This is a test.",
            start=2.0,
            end=3.5,
            words=[words[2], words[3], words[4], words[5]],
            confidence=0.970,
        ),
    ]

    return {
        "full_text": "Hello world This is a test.",
        "sentences": sentences,
    }


class TestTranscriptExporter:
    """Test TranscriptExporter functionality."""

    def test_export_to_txt(self, sample_transcript):
        """Test exporting to plain text."""
        result = TranscriptExporter.to_txt(
            sample_transcript["full_text"],
            sample_transcript["sentences"],
        )

        assert isinstance(result, str)
        assert "Hello world" in result
        assert "This is a test." in result

    def test_export_to_json(self, sample_transcript):
        """Test exporting to JSON."""
        result = TranscriptExporter.to_json(
            sample_transcript["full_text"],
            sample_transcript["sentences"],
        )

        data = json.loads(result)
        assert "text" in data
        assert "sentences" in data
        assert "metadata" in data
        assert len(data["sentences"]) == 2
        assert data["metadata"]["total_words"] == 6

    def test_export_to_csv(self, sample_transcript):
        """Test exporting to CSV."""
        result = TranscriptExporter.to_csv(
            sample_transcript["full_text"],
            sample_transcript["sentences"],
        )

        assert isinstance(result, str)
        lines = result.strip().split("\n")
        assert len(lines) > 1  # Header + data
        assert "Sentence #" in lines[0]
        assert "Word #" in lines[0]
        assert "Hello" in result

    def test_export_to_srt(self, sample_transcript):
        """Test exporting to SRT subtitle format."""
        result = TranscriptExporter.to_srt(sample_transcript["sentences"])

        assert isinstance(result, str)
        assert "00:00:00,000 --> 00:00:01,100" in result
        assert "Hello world" in result
        assert "00:00:02,000 --> 00:00:03,500" in result
        assert "This is a test." in result

    def test_export_to_vtt(self, sample_transcript):
        """Test exporting to VTT subtitle format."""
        result = TranscriptExporter.to_vtt(sample_transcript["sentences"])

        assert isinstance(result, str)
        assert "WEBVTT" in result
        assert "00:00:00.000 --> 00:00:01.100" in result
        assert "Hello world" in result
        assert "00:00:02.000 --> 00:00:03.500" in result
        assert "This is a test." in result

    def test_export_unsupported_format(self, sample_transcript):
        """Test exporting with unsupported format."""
        with pytest.raises(ValueError):
            TranscriptExporter.export(
                format="pdf",
                full_text=sample_transcript["full_text"],
                sentences=sample_transcript["sentences"],
            )

    def test_get_file_extension(self):
        """Test getting file extension for formats."""
        assert TranscriptExporter.get_file_extension("txt") == ".txt"
        assert TranscriptExporter.get_file_extension("json") == ".json"
        assert TranscriptExporter.get_file_extension("csv") == ".csv"
        assert TranscriptExporter.get_file_extension("srt") == ".srt"
        assert TranscriptExporter.get_file_extension("vtt") == ".vtt"

    def test_get_content_type(self):
        """Test getting MIME type for formats."""
        assert TranscriptExporter.get_content_type("txt") == "text/plain"
        assert TranscriptExporter.get_content_type("json") == "application/json"
        assert TranscriptExporter.get_content_type("csv") == "text/csv"
        assert TranscriptExporter.get_content_type("srt") == "application/x-subrip"
        assert TranscriptExporter.get_content_type("vtt") == "text/vtt"

    def test_format_timestamp_srt(self):
        """Test SRT timestamp formatting."""
        assert TranscriptExporter._format_timestamp_srt(0.0) == "00:00:00,000"
        assert TranscriptExporter._format_timestamp_srt(61.5) == "00:01:01,500"
        assert TranscriptExporter._format_timestamp_srt(3661.123) == "01:01:01,123"

    def test_format_timestamp_vtt(self):
        """Test VTT timestamp formatting."""
        assert TranscriptExporter._format_timestamp_vtt(0.0) == "00:00:00.000"
        assert TranscriptExporter._format_timestamp_vtt(61.5) == "00:01:01.500"
        assert TranscriptExporter._format_timestamp_vtt(3661.123) == "01:01:01.123"
