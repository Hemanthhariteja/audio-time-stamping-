"""Tests for project endpoints."""

import pytest
from fastapi.testclient import TestClient


def test_create_project(client: TestClient):
    """Test creating a project."""
    response = client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "description": "Test", "user_id": 1},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data


def test_list_projects(client: TestClient):
    """Test listing projects."""
    response = client.get(
        "/api/v1/projects?user_id=1",
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
