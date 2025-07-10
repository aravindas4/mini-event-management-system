import pytest
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from main import app
from app.core.models import Base
from app.core.database import get_primary_db
from app.events.models.event import Event
from app.events.models.attendee import Attendee

# Test database URL for SQLite (in-memory)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine and session
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_primary_db():
    """Override database dependency for testing"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_primary_db] = override_get_primary_db

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client():
    """Create test client for synchronous tests"""
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
async def async_client():
    """Create async test client for async tests"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

@pytest.fixture
def sample_event_data():
    """Sample event data for testing"""
    return {
        "name": "Tech Conference 2024",
        "location": "Convention Center, Mumbai",
        "start_time": (datetime.now() + timedelta(days=30)).isoformat(),
        "end_time": (datetime.now() + timedelta(days=30, hours=8)).isoformat(),
        "max_capacity": 100
    }

@pytest.fixture
def sample_attendee_data():
    """Sample attendee data for testing"""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com"
    }

@pytest.fixture
def sample_event(db_session):
    """Create a sample event in the database"""
    event = Event(
        name="Sample Event",
        location="Sample Location",
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=1, hours=2),
        max_capacity=50
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event

@pytest.fixture
def sample_attendee(db_session, sample_event):
    """Create a sample attendee in the database"""
    attendee = Attendee(
        event_id=sample_event.id,
        name="Sample Attendee",
        email="sample@example.com"
    )
    db_session.add(attendee)
    db_session.commit()
    db_session.refresh(attendee)
    return attendee

@pytest.fixture
def mock_event_repository():
    """Mock event repository for unit tests"""
    mock_repo = Mock()
    mock_repo.create_event = AsyncMock()
    mock_repo.get_upcoming_events = AsyncMock()
    mock_repo.get_event_by_id = AsyncMock()
    mock_repo.register_attendee = AsyncMock()
    mock_repo.get_event_attendees = AsyncMock()
    mock_repo.get_attendee_count = AsyncMock()
    return mock_repo

@pytest.fixture
def mock_event_service():
    """Mock event service for controller tests"""
    mock_service = Mock()
    mock_service.create_event = AsyncMock()
    mock_service.get_upcoming_events = AsyncMock()
    mock_service.register_attendee = AsyncMock()
    mock_service.get_event_attendees = AsyncMock()
    return mock_service

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment for each test"""
    # Set test environment variables
    import os
    os.environ.update({
        "APP_ENV": "test",
        "DEBUG": "true",
        "DATABASE_URL": TEST_DATABASE_URL,
        "MYSQL_HOST": "localhost",
        "MYSQL_USER": "test_user",
        "MYSQL_PASSWORD": "test_password",
        "MYSQL_DATABASE": "test_db",
        "MYSQL_PORT": "3306"
    })
    
    yield
    
    # Cleanup after test
    for key in ["APP_ENV", "DEBUG", "DATABASE_URL", "MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE", "MYSQL_PORT"]:
        if key in os.environ:
            del os.environ[key]