import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from crawl4ai_scraper.backend.database import get_db
from crawl4ai_scraper.backend.main import app

# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = Session(engine)
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create test database and tables."""
    SQLModel.metadata.create_all(engine)
    yield
    os.remove("./test.db")


@pytest.fixture
def client():
    """Create test client with database override."""
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_db():
    """Get test database session."""
    return Session(engine)
