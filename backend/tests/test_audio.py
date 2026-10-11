"""Tests for audio file endpoints."""

import pytest
from fastapi.testclient import TestClient


import io

def test_upload_audio_file(client: TestClient):
    """Test uploading an audio file."""
    fake_audio = io.BytesIO(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
    response = client.post(
        "/api/v1/audio/upload/1",
        files={"file": ("test_sample.wav", fake_audio, "audio/wav")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == "test_sample.wav"
    assert data["upload_status"] == "ready"
