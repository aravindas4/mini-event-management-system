import logging
import pytz
from datetime import datetime
from typing import Optional, List
from fastapi import Depends, HTTPException

from app.events.repositories.event_repository import EventRepository
from app.events.models.event import Event
from app.events.models.attendee import Attendee
from app.core.exceptions import EventNotFound, CapacityExceeded, DuplicateRegistration, ValidationError
from app.core.middlewares.trace_context_middleware import get_trace_id, get_request_id, set_event_id
from app.core.utils.timezone_utils import validate_future_datetime, validate_datetime_range, ensure_timezone_aware

logger = logging.getLogger("event_management.services")

class EventService:
    """Service layer for event business logic and validation"""
    
    def __init__(self, repository: EventRepository = Depends()):
        self.repository = repository
    
    async def create_event(self, event_data: dict) -> Event:
        """Create a new event with validation"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        logger.info(
            "Creating new event",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_name": event_data.get("name"),
                "location": event_data.get("location"),
                "max_capacity": event_data.get("max_capacity")
            }
        )
        
        # Validate event data
        await self._validate_event_data(event_data)
        
        try:
            event = await self.repository.create_event(event_data)
            
            # Set event ID in context for subsequent operations
            set_event_id(str(event.id))
            
            logger.info(
                "Event created successfully",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event.id,
                    "event_name": event.name
                }
            )
            
            return event
            
        except Exception as e:
            logger.error(
                "Failed to create event",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "error": str(e),
                    "event_name": event_data.get("name")
                },
                exc_info=True
            )
            raise
    
    async def get_event_by_id(self, event_id: int) -> Event:
        """Get event by ID with validation"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        logger.debug(
            "Fetching event by ID",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_id": event_id
            }
        )
        
        event = await self.repository.get_event_by_id(event_id)
        
        if not event:
            logger.warning(
                "Event not found",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id
                }
            )
            raise EventNotFound(f"Event with ID {event_id} not found")
        
        # Set event ID in context
        set_event_id(str(event.id))
        
        logger.debug(
            "Event fetched successfully",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_id": event.id,
                "event_name": event.name
            }
        )
        
        return event
    
    async def get_upcoming_events(self, limit: int = 100, offset: int = 0) -> List[Event]:
        """Get upcoming events with pagination"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        logger.debug(
            "Fetching upcoming events",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "limit": limit,
                "offset": offset
            }
        )
        
        # Validate pagination parameters
        if limit < 1 or limit > 1000:
            raise ValidationError("Limit must be between 1 and 1000")
        
        if offset < 0:
            raise ValidationError("Offset must be non-negative")
        
        events = await self.repository.get_upcoming_events(limit, offset)
        
        logger.debug(
            "Upcoming events fetched",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "count": len(events),
                "limit": limit,
                "offset": offset
            }
        )
        
        return events
    
    async def register_attendee(self, event_id: int, attendee_data: dict) -> Attendee:
        """Register attendee with business logic validation"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        # Set event ID in context
        set_event_id(str(event_id))
        
        logger.info(
            "Registering attendee",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_id": event_id,
                "attendee_email": attendee_data.get("email"),
                "attendee_name": attendee_data.get("name")
            }
        )
        
        # Validate attendee data
        await self._validate_attendee_data(attendee_data)
        
        # Additional business logic validation
        event = await self.repository.get_event_by_id(event_id)
        if not event:
            logger.warning(
                "Attendee registration failed - event not found",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "attendee_email": attendee_data.get("email")
                }
            )
            raise EventNotFound(f"Event {event_id} not found")
        
        # Check if event has already started
        start_time_utc = ensure_timezone_aware(event.start_time)
        if start_time_utc <= datetime.now(pytz.UTC):
            logger.warning(
                "Attendee registration failed - event already started",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "event_start_time": event.start_time.isoformat(),
                    "attendee_email": attendee_data.get("email")
                }
            )
            raise ValidationError(f"Cannot register for event '{event.name}' - event has already started")
        
        try:
            attendee = await self.repository.register_attendee(event_id, attendee_data)
            
            logger.info(
                "Attendee registered successfully",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "attendee_id": attendee.id,
                    "attendee_email": attendee.email
                }
            )
            
            return attendee
            
        except (CapacityExceeded, DuplicateRegistration) as e:
            # Business logic exceptions - re-raise as-is
            logger.warning(
                "Attendee registration failed - business rule violation",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "attendee_email": attendee_data.get("email"),
                    "error": str(e)
                }
            )
            raise
        except Exception as e:
            logger.error(
                "Attendee registration failed - unexpected error",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "attendee_email": attendee_data.get("email"),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    async def get_event_attendees(self, event_id: int, limit: int = 50, offset: int = 0) -> List[Attendee]:
        """Get event attendees with pagination"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        # Set event ID in context
        set_event_id(str(event_id))
        
        logger.debug(
            "Fetching event attendees",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_id": event_id,
                "limit": limit,
                "offset": offset
            }
        )
        
        # Validate pagination parameters
        if limit < 1 or limit > 1000:
            raise ValidationError("Limit must be between 1 and 1000")
        
        if offset < 0:
            raise ValidationError("Offset must be non-negative")
        
        attendees = await self.repository.get_event_attendees(event_id, limit, offset)
        
        logger.debug(
            "Event attendees fetched",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_id": event_id,
                "count": len(attendees),
                "limit": limit,
                "offset": offset
            }
        )
        
        return attendees
    
    async def _validate_event_data(self, event_data: dict) -> None:
        """Validate event creation data"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        logger.debug(
            "Validating event data",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_name": event_data.get("name")
            }
        )
        
        # Validate required fields
        required_fields = ["name", "location", "start_time", "end_time", "max_capacity"]
        for field in required_fields:
            if field not in event_data or event_data[field] is None:
                raise ValidationError(f"Field '{field}' is required")
        
        # Validate event name
        if not event_data["name"].strip():
            raise ValidationError("Event name cannot be empty")
        
        if len(event_data["name"]) > 255:
            raise ValidationError("Event name must be less than 255 characters")
        
        # Validate location
        if not event_data["location"].strip():
            raise ValidationError("Event location cannot be empty")
        
        if len(event_data["location"]) > 255:
            raise ValidationError("Event location must be less than 255 characters")
        
        # Validate capacity
        if event_data["max_capacity"] < 1:
            raise ValidationError("Event capacity must be at least 1")
        
        if event_data["max_capacity"] > 10000:
            raise ValidationError("Event capacity cannot exceed 10,000")
        
        # Validate dates
        start_time = event_data["start_time"]
        end_time = event_data["end_time"]
        
        # Validate start time is in the future
        validate_future_datetime(start_time)
        
        # Validate datetime range and duration
        validate_datetime_range(start_time, end_time, max_days=7)
        
        logger.debug(
            "Event data validation passed",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_name": event_data.get("name")
            }
        )
    
    async def _validate_attendee_data(self, attendee_data: dict) -> None:
        """Validate attendee registration data"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        logger.debug(
            "Validating attendee data",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "attendee_email": attendee_data.get("email")
            }
        )
        
        # Validate required fields
        required_fields = ["name", "email"]
        for field in required_fields:
            if field not in attendee_data or attendee_data[field] is None:
                raise ValidationError(f"Field '{field}' is required")
        
        # Validate attendee name
        if not attendee_data["name"].strip():
            raise ValidationError("Attendee name cannot be empty")
        
        if len(attendee_data["name"]) > 255:
            raise ValidationError("Attendee name must be less than 255 characters")
        
        # Validate email format
        email = attendee_data["email"].strip().lower()
        if not email:
            raise ValidationError("Email cannot be empty")
        
        if len(email) > 255:
            raise ValidationError("Email must be less than 255 characters")
        
        # Basic email validation
        if "@" not in email or "." not in email:
            raise ValidationError("Invalid email format")
        
        # Update email in data (normalized)
        attendee_data["email"] = email
        
        logger.debug(
            "Attendee data validation passed",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "attendee_email": email
            }
        )