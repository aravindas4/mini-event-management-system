import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from app.events.controllers.event_controller import EventController
from app.events.models.event import Event
from app.events.models.attendee import Attendee
from app.events.requests.create_event_request import CreateEventRequest
from app.events.requests.register_attendee_request import RegisterAttendeeRequest
from app.core.exceptions import EventNotFound, CapacityExceeded, DuplicateRegistration, ValidationError


class TestEventController:
    """Test cases for EventController"""

    @pytest.fixture
    def mock_service(self):
        """Mock service for controller tests"""
        mock_service = Mock()
        mock_service.create_event = AsyncMock()
        mock_service.get_upcoming_events = AsyncMock()
        mock_service.register_attendee = AsyncMock()
        mock_service.get_event_attendees = AsyncMock()
        mock_service.repository = Mock()
        mock_service.repository.get_attendee_count = AsyncMock()
        return mock_service

    @pytest.fixture
    def controller(self, mock_service):
        """Create controller instance with mocked service"""
        return EventController(service=mock_service)

    @pytest.mark.asyncio
    @patch('app.events.controllers.event_controller.get_trace_id')
    @patch('app.events.controllers.event_controller.get_request_id')
    async def test_create_event_success(self, mock_get_request_id, mock_get_trace_id, controller, mock_service):
        """Test successful event creation"""
        # Arrange
        mock_get_trace_id.return_value = "trace-123"
        mock_get_request_id.return_value = "request-456"
        
        event_data = {
            "name": "Tech Conference",
            "location": "Mumbai",
            "start_time": datetime.now() + timedelta(days=30),
            "end_time": datetime.now() + timedelta(days=30, hours=8),
            "max_capacity": 100
        }
        
        expected_event = Event(**event_data)
        expected_event.id = 1
        expected_event.created_at = datetime.now()
        expected_event.updated_at = datetime.now()
        mock_service.create_event.return_value = expected_event
        
        request = CreateEventRequest(**event_data)
        
        # Act
        result = await controller.create_event(request)
        
        # Assert
        mock_service.create_event.assert_called_once_with(request.get())
        assert result.id == 1
        assert result.name == event_data["name"]

    @pytest.mark.asyncio
    @patch('app.events.controllers.event_controller.get_trace_id')
    @patch('app.events.controllers.event_controller.get_request_id')
    async def test_create_event_validation_error(self, mock_get_request_id, mock_get_trace_id, controller, mock_service):
        """Test event creation with validation error"""
        # Arrange
        mock_get_trace_id.return_value = "trace-123"
        mock_get_request_id.return_value = "request-456"
        
        event_data = {
            "name": "Tech Conference",
            "location": "Mumbai",
            "start_time": datetime.now() + timedelta(days=30),
            "end_time": datetime.now() + timedelta(days=30, hours=8),
            "max_capacity": 100
        }
        
        mock_service.create_event.side_effect = ValidationError("Event name cannot be empty")
        request = CreateEventRequest(**event_data)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await controller.create_event(request)
        
        assert exc_info.value.status_code == 422
        assert "Event name cannot be empty" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    @patch('app.events.controllers.event_controller.get_trace_id')
    @patch('app.events.controllers.event_controller.get_request_id')
    async def test_create_event_internal_error(self, mock_get_request_id, mock_get_trace_id, controller, mock_service):
        """Test event creation with internal server error"""
        # Arrange
        mock_get_trace_id.return_value = "trace-123"
        mock_get_request_id.return_value = "request-456"
        
        event_data = {
            "name": "Tech Conference",
            "location": "Mumbai",
            "start_time": datetime.now() + timedelta(days=30),
            "end_time": datetime.now() + timedelta(days=30, hours=8),
            "max_capacity": 100
        }
        
        mock_service.create_event.side_effect = Exception("Database connection failed")
        request = CreateEventRequest(**event_data)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await controller.create_event(request)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Internal server error"

    @pytest.mark.asyncio
    @patch('app.events.controllers.event_controller.get_trace_id')
    @patch('app.events.controllers.event_controller.get_request_id')
    async def test_get_events_success(self, mock_get_request_id, mock_get_trace_id, controller, mock_service):
        """Test successful retrieval of events"""
        # Arrange
        mock_get_trace_id.return_value = "trace-123"
        mock_get_request_id.return_value = "request-456"
        
        event1 = Event(id=1, name="Event 1", location="Location 1", start_time=datetime.now() + timedelta(days=1), 
                      end_time=datetime.now() + timedelta(days=1, hours=2), max_capacity=50)
        event1.created_at = datetime.now()
        event1.updated_at = datetime.now()
        
        event2 = Event(id=2, name="Event 2", location="Location 2", start_time=datetime.now() + timedelta(days=2), 
                      end_time=datetime.now() + timedelta(days=2, hours=2), max_capacity=100)
        event2.created_at = datetime.now()
        event2.updated_at = datetime.now()
        
        expected_events = [event1, event2]
        mock_service.get_upcoming_events.return_value = expected_events
        
        # Act
        result = await controller.get_events(limit=100, offset=0, timezone="Asia/Kolkata")
        
        # Assert
        mock_service.get_upcoming_events.assert_called_once_with(100, 0)
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2

    @pytest.mark.asyncio
    @patch('app.events.controllers.event_controller.get_trace_id')
    @patch('app.events.controllers.event_controller.get_request_id')
    async def test_register_attendee_success(self, mock_get_request_id, mock_get_trace_id, controller, mock_service):
        """Test successful attendee registration"""
        # Arrange
        mock_get_trace_id.return_value = "trace-123"
        mock_get_request_id.return_value = "request-456"
        
        event_id = 1
        attendee_data = {"name": "John Doe", "email": "john@example.com"}
        
        expected_attendee = Attendee(id=1, event_id=event_id, **attendee_data)
        expected_attendee.registered_at = datetime.now()
        mock_service.register_attendee.return_value = expected_attendee
        
        request = RegisterAttendeeRequest(**attendee_data)
        
        # Act
        result = await controller.register_attendee(event_id, request)
        
        # Assert
        mock_service.register_attendee.assert_called_once_with(event_id, request.get())
        assert result.id == 1
        assert result.event_id == event_id

    @pytest.mark.asyncio
    @patch('app.events.controllers.event_controller.get_trace_id')
    @patch('app.events.controllers.event_controller.get_request_id')
    async def test_register_attendee_event_not_found(self, mock_get_request_id, mock_get_trace_id, controller, mock_service):
        """Test attendee registration for non-existent event"""
        # Arrange
        mock_get_trace_id.return_value = "trace-123"
        mock_get_request_id.return_value = "request-456"
        
        event_id = 999
        attendee_data = {"name": "John Doe", "email": "john@example.com"}
        
        mock_service.register_attendee.side_effect = EventNotFound(f"Event with id {event_id} not found")
        request = RegisterAttendeeRequest(**attendee_data)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await controller.register_attendee(event_id, request)
        
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    @patch('app.events.controllers.event_controller.get_trace_id')
    @patch('app.events.controllers.event_controller.get_request_id')
    async def test_register_attendee_capacity_exceeded(self, mock_get_request_id, mock_get_trace_id, controller, mock_service):
        """Test attendee registration when capacity is exceeded"""
        # Arrange
        mock_get_trace_id.return_value = "trace-123"
        mock_get_request_id.return_value = "request-456"
        
        event_id = 1
        attendee_data = {"name": "John Doe", "email": "john@example.com"}
        
        mock_service.register_attendee.side_effect = CapacityExceeded("Event is at maximum capacity")
        request = RegisterAttendeeRequest(**attendee_data)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await controller.register_attendee(event_id, request)
        
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    @patch('app.events.controllers.event_controller.get_trace_id')
    @patch('app.events.controllers.event_controller.get_request_id')
    async def test_register_attendee_duplicate_registration(self, mock_get_request_id, mock_get_trace_id, controller, mock_service):
        """Test duplicate attendee registration"""
        # Arrange
        mock_get_trace_id.return_value = "trace-123"
        mock_get_request_id.return_value = "request-456"
        
        event_id = 1
        attendee_data = {"name": "John Doe", "email": "john@example.com"}
        
        mock_service.register_attendee.side_effect = DuplicateRegistration("Attendee already registered for this event")
        request = RegisterAttendeeRequest(**attendee_data)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await controller.register_attendee(event_id, request)
        
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    @patch('app.events.controllers.event_controller.get_trace_id')
    @patch('app.events.controllers.event_controller.get_request_id')
    async def test_get_event_attendees_success(self, mock_get_request_id, mock_get_trace_id, controller, mock_service):
        """Test successful retrieval of event attendees"""
        # Arrange
        mock_get_trace_id.return_value = "trace-123"
        mock_get_request_id.return_value = "request-456"
        
        event_id = 1
        attendee1 = Attendee(id=1, event_id=event_id, name="John Doe", email="john@example.com")
        attendee1.registered_at = datetime.now()
        
        attendee2 = Attendee(id=2, event_id=event_id, name="Jane Smith", email="jane@example.com")  
        attendee2.registered_at = datetime.now()
        
        expected_attendees = [attendee1, attendee2]
        mock_service.get_event_attendees.return_value = expected_attendees
        mock_service.repository.get_attendee_count.return_value = 2
        
        # Act
        result = await controller.get_event_attendees(event_id, limit=50, offset=0)
        
        # Assert
        mock_service.get_event_attendees.assert_called_once_with(event_id, 50, 0)
        mock_service.repository.get_attendee_count.assert_called_once_with(event_id)
        assert len(result.attendees) == 2
        assert result.total_count == 2
        assert result.limit == 50
        assert result.offset == 0

    @pytest.mark.asyncio
    @patch('app.events.controllers.event_controller.get_trace_id')
    @patch('app.events.controllers.event_controller.get_request_id')
    async def test_get_event_attendees_event_not_found(self, mock_get_request_id, mock_get_trace_id, controller, mock_service):
        """Test getting attendees for non-existent event"""
        # Arrange
        mock_get_trace_id.return_value = "trace-123"
        mock_get_request_id.return_value = "request-456"
        
        event_id = 999
        mock_service.get_event_attendees.side_effect = EventNotFound(f"Event with id {event_id} not found")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await controller.get_event_attendees(event_id, limit=50, offset=0)
        
        assert exc_info.value.status_code == 404