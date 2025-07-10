import logging
import pytz
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from fastapi import Depends

from app.core.database import get_primary_db
from app.events.models.event import Event
from app.events.models.attendee import Attendee
from app.core.exceptions import EventNotFound, CapacityExceeded, DuplicateRegistration
from app.core.middlewares.trace_context_middleware import get_trace_id, get_request_id, set_event_id

logger = logging.getLogger("event_management.repositories")

class EventRepository:
    """Repository for Event-related database operations with business logic"""
    
    def __init__(self, db: Session = Depends(get_primary_db)):
        self.db = db
    
    async def create_event(self, event_data: dict) -> Event:
        """Create a new event"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        logger.info(
            "Creating event in database",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_name": event_data.get("name"),
                "location": event_data.get("location")
            }
        )

        # Remove timezone from start_time and end_time
        if event_data["start_time"].tzinfo is not None:
            event_data["start_time"] = event_data["start_time"].replace(tzinfo=None)

        if event_data["end_time"].tzinfo is not None:
            event_data["end_time"] = event_data["end_time"].replace(tzinfo=None)
        
        event = Event(
            name=event_data["name"],
            location=event_data["location"],
            start_time=event_data["start_time"],
            end_time=event_data["end_time"],
            max_capacity=event_data["max_capacity"]
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        
        # Set event ID in context
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
    
    async def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get event by ID"""
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
        
        event = self.db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            logger.warning(
                "Event not found",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id
                }
            )
            return None
        
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
        """Get upcoming events (future events only)"""
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
        
        now = datetime.now(pytz.UTC)
        events = (
            self.db.query(Event)
            .filter(Event.start_time > now)
            .order_by(Event.start_time.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        
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
    
    async def get_attendee_count(self, event_id: int) -> int:
        """Get current attendee count for an event"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        logger.debug(
            "Getting attendee count",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_id": event_id
            }
        )
        
        count = self.db.query(func.count(Attendee.id)).filter(Attendee.event_id == event_id).scalar()
        
        logger.debug(
            "Attendee count retrieved",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_id": event_id,
                "count": count
            }
        )
        
        return count or 0
    
    async def register_attendee(self, event_id: int, attendee_data: dict) -> Attendee:
        """Register an attendee for an event with capacity and duplicate checks"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
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
        
        # Get the event
        event = await self.get_event_by_id(event_id)
        if not event:
            raise EventNotFound(f"Event with ID {event_id} not found")
        
        # Check for duplicate registration
        existing_attendee = (
            self.db.query(Attendee)
            .filter(
                and_(
                    Attendee.event_id == event_id,
                    Attendee.email == attendee_data["email"]
                )
            )
            .first()
        )
        
        if existing_attendee:
            logger.warning(
                "Duplicate registration attempt",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "attendee_email": attendee_data["email"],
                    "existing_attendee_id": existing_attendee.id
                }
            )
            raise DuplicateRegistration(
                f"Email {attendee_data['email']} is already registered for this event"
            )
        
        # Check capacity
        current_count = await self.get_attendee_count(event_id)
        if current_count >= event.max_capacity:
            logger.warning(
                "Capacity exceeded",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "current_count": current_count,
                    "max_capacity": event.max_capacity,
                    "attendee_email": attendee_data["email"]
                }
            )
            raise CapacityExceeded(
                f"Event '{event.name}' is at full capacity ({event.max_capacity} attendees)"
            )
        
        # Create attendee
        attendee = Attendee(
            event_id=event_id,
            name=attendee_data["name"],
            email=attendee_data["email"]
        )
        
        self.db.add(attendee)
        self.db.commit()
        self.db.refresh(attendee)
        
        logger.info(
            "Attendee registered successfully",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_id": event_id,
                "attendee_id": attendee.id,
                "attendee_email": attendee.email,
                "new_count": current_count + 1,
                "max_capacity": event.max_capacity
            }
        )
        
        return attendee
    
    async def get_event_attendees(self, event_id: int, limit: int = 50, offset: int = 0) -> List[Attendee]:
        """Get attendees for an event with pagination"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
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
        
        # Verify event exists
        event = await self.get_event_by_id(event_id)
        if not event:
            raise EventNotFound(f"Event with ID {event_id} not found")
        
        attendees = (
            self.db.query(Attendee)
            .filter(Attendee.event_id == event_id)
            .order_by(Attendee.registered_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        
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