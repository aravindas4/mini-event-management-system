import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from app.events.services.event_service import EventService
from app.events.models.event import Event
from app.events.models.attendee import Attendee
from app.core.exceptions import (
    EventNotFound,
    CapacityExceeded,
    DuplicateRegistration,
    ValidationError,
)


class TestEventService:
    """Test cases for EventService"""

    @pytest.fixture
    def mock_repository(self):
        """Mock repository for service tests"""
        mock_repo = Mock()
        mock_repo.create_event = AsyncMock()
        mock_repo.get_upcoming_events = AsyncMock()
        mock_repo.get_event_by_id = AsyncMock()
        mock_repo.register_attendee = AsyncMock()
        mock_repo.get_event_attendees = AsyncMock()
        mock_repo.get_attendee_count = AsyncMock()
        return mock_repo

    @pytest.fixture
    def service(self, mock_repository):
        """Create service instance with mocked repository"""
        return EventService(repository=mock_repository)

    @pytest.mark.asyncio
    async def test_create_event_success(self, service, mock_repository):
        """Test successful event creation"""
        # Arrange
        event_data = {
            "name": "Tech Conference",
            "location": "Mumbai",
            "start_time": datetime.now() + timedelta(days=30),
            "end_time": datetime.now() + timedelta(days=30, hours=8),
            "max_capacity": 100,
        }

        expected_event = Event(**event_data)
        expected_event.id = 1
        expected_event.created_at = datetime.now()
        expected_event.updated_at = datetime.now()
        mock_repository.create_event.return_value = expected_event

        # Act
        result = await service.create_event(event_data)

        # Assert
        mock_repository.create_event.assert_called_once_with(event_data)
        assert result == expected_event
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_create_event_validation_error(self, service, mock_repository):
        """Test event creation with validation error"""
        # Arrange
        event_data = {
            "name": "",  # Invalid empty name
            "location": "Mumbai",
            "start_time": datetime.now() + timedelta(days=30),
            "end_time": datetime.now() + timedelta(days=30, hours=8),
            "max_capacity": 100,
        }

        # Act & Assert
        with pytest.raises(ValidationError, match="Event name cannot be empty"):
            await service.create_event(event_data)

    @pytest.mark.asyncio
    async def test_create_event_start_time_in_past(self, service, mock_repository):
        """Test event creation with start time in past"""
        # Arrange
        event_data = {
            "name": "Tech Conference",
            "location": "Mumbai",
            "start_time": datetime.now() - timedelta(days=1),  # Past date
            "end_time": datetime.now() + timedelta(hours=8),
            "max_capacity": 100,
        }

        # Act & Assert
        with pytest.raises(
            ValidationError, match="Event start time cannot be in the past"
        ):
            await service.create_event(event_data)

    @pytest.mark.asyncio
    async def test_create_event_end_before_start(self, service, mock_repository):
        """Test event creation with end time before start time"""
        # Arrange
        event_data = {
            "name": "Tech Conference",
            "location": "Mumbai",
            "start_time": datetime.now() + timedelta(days=30),
            "end_time": datetime.now() + timedelta(days=29),  # Before start
            "max_capacity": 100,
        }

        # Act & Assert
        with pytest.raises(
            ValidationError, match="Event end time must be after start time"
        ):
            await service.create_event(event_data)

    @pytest.mark.asyncio
    async def test_get_upcoming_events_success(self, service, mock_repository):
        """Test successful retrieval of upcoming events"""
        # Arrange
        event1 = Event(
            id=1,
            name="Event 1",
            location="Location 1",
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=2),
            max_capacity=50,
        )
        event1.created_at = datetime.now()
        event1.updated_at = datetime.now()

        event2 = Event(
            id=2,
            name="Event 2",
            location="Location 2",
            start_time=datetime.now() + timedelta(days=2),
            end_time=datetime.now() + timedelta(days=2, hours=2),
            max_capacity=100,
        )
        event2.created_at = datetime.now()
        event2.updated_at = datetime.now()

        expected_events = [event1, event2]
        mock_repository.get_upcoming_events.return_value = expected_events

        # Act
        result = await service.get_upcoming_events(limit=10, offset=0)

        # Assert
        mock_repository.get_upcoming_events.assert_called_once_with(limit=10, offset=0)
        assert result == expected_events
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_register_attendee_success(self, service, mock_repository):
        """Test successful attendee registration"""
        # Arrange
        event_id = 1
        attendee_data = {"name": "John Doe", "email": "john@example.com"}

        expected_attendee = Attendee(id=1, event_id=event_id, **attendee_data)
        expected_attendee.registered_at = datetime.now()
        mock_repository.register_attendee.return_value = expected_attendee

        # Act
        result = await service.register_attendee(event_id, attendee_data)

        # Assert
        mock_repository.register_attendee.assert_called_once_with(
            event_id, attendee_data
        )
        assert result == expected_attendee
        assert result.event_id == event_id

    @pytest.mark.asyncio
    async def test_register_attendee_event_not_found(self, service, mock_repository):
        """Test attendee registration for non-existent event"""
        # Arrange
        event_id = 999
        attendee_data = {"name": "John Doe", "email": "john@example.com"}

        mock_repository.register_attendee.side_effect = EventNotFound(
            f"Event with id {event_id} not found"
        )

        # Act & Assert
        with pytest.raises(EventNotFound):
            await service.register_attendee(event_id, attendee_data)

    @pytest.mark.asyncio
    async def test_register_attendee_capacity_exceeded(self, service, mock_repository):
        """Test attendee registration when capacity is exceeded"""
        # Arrange
        event_id = 1
        attendee_data = {"name": "John Doe", "email": "john@example.com"}

        mock_repository.register_attendee.side_effect = CapacityExceeded(
            "Event is at maximum capacity"
        )

        # Act & Assert
        with pytest.raises(CapacityExceeded):
            await service.register_attendee(event_id, attendee_data)

    @pytest.mark.asyncio
    async def test_register_attendee_duplicate_registration(
        self, service, mock_repository
    ):
        """Test duplicate attendee registration"""
        # Arrange
        event_id = 1
        attendee_data = {"name": "John Doe", "email": "john@example.com"}

        mock_repository.register_attendee.side_effect = DuplicateRegistration(
            "Attendee already registered for this event"
        )

        # Act & Assert
        with pytest.raises(DuplicateRegistration):
            await service.register_attendee(event_id, attendee_data)

    @pytest.mark.asyncio
    async def test_get_event_attendees_success(self, service, mock_repository):
        """Test successful retrieval of event attendees"""
        # Arrange
        event_id = 1
        attendee1 = Attendee(
            id=1, event_id=event_id, name="John Doe", email="john@example.com"
        )
        attendee1.registered_at = datetime.now()

        attendee2 = Attendee(
            id=2, event_id=event_id, name="Jane Smith", email="jane@example.com"
        )
        attendee2.registered_at = datetime.now()

        expected_attendees = [attendee1, attendee2]
        mock_repository.get_event_attendees.return_value = expected_attendees

        # Act
        result = await service.get_event_attendees(event_id, limit=50, offset=0)

        # Assert
        mock_repository.get_event_attendees.assert_called_once_with(
            event_id, limit=50, offset=0
        )
        assert result == expected_attendees
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_event_attendees_event_not_found(self, service, mock_repository):
        """Test getting attendees for non-existent event"""
        # Arrange
        event_id = 999
        mock_repository.get_event_attendees.side_effect = EventNotFound(
            f"Event with id {event_id} not found"
        )

        # Act & Assert
        with pytest.raises(EventNotFound):
            await service.get_event_attendees(event_id, limit=50, offset=0)
