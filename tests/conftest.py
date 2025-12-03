import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_db

# Use a separate SQLite DB for tests so you don't touch dev/prod data.
TEST_DATABASE_URL = "sqlite:///./test.db"

# SQLite-specific connect_args
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Create a fresh schema for tests
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override the app's DB dependency to use the test database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply the override globally for all tests
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client using the test database."""
    return TestClient(app)
