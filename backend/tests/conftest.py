"""Test configuration and fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_db():
    """Create test database."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield SessionLocal
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Create test database session."""
    session = test_db()
    yield session
    session.close()


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)
