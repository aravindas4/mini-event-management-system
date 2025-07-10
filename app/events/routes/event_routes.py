from fastapi import APIRouter, Depends, Path, Query
from typing import List, Optional

from app.events.controllers.event_controller import EventController
from app.core.utils.timezone_utils import get_default_timezone
from app.events.requests.create_event_request import CreateEventRequest
from app.events.requests.register_attendee_request import RegisterAttendeeRequest
from app.events.responses.event_response import EventResponse
from app.events.responses.attendee_response import AttendeeResponse, AttendeeListResponse

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    request: CreateEventRequest,
    controller: EventController = Depends()
) -> EventResponse:
    """Create a new event"""
    return await controller.create_event(request)

@router.get("/", response_model=List[EventResponse])
async def get_events(
    limit: int = Query(default=100, ge=1, le=1000, description="Number of events to return"),
    offset: int = Query(default=0, ge=0, description="Number of events to skip"),
    timezone: Optional[str] = Query(default=None, description="Timezone for converting event times (default: Asia/Kolkata)"),
    controller: EventController = Depends()
) -> List[EventResponse]:
    """Get all upcoming events with optional timezone conversion"""
    target_timezone = timezone or get_default_timezone()
    return await controller.get_events(limit, offset, target_timezone)

@router.post("/{event_id}/register", response_model=AttendeeResponse, status_code=201)
async def register_attendee(
    event_id: int = Path(..., description="Event ID"),
    request: RegisterAttendeeRequest = ...,
    controller: EventController = Depends()
) -> AttendeeResponse:
    """Register an attendee for an event"""
    return await controller.register_attendee(event_id, request)

@router.get("/{event_id}/attendees", response_model=AttendeeListResponse)
async def get_event_attendees(
    event_id: int = Path(..., description="Event ID"),
    limit: int = Query(default=50, ge=1, le=1000, description="Number of attendees to return"),
    offset: int = Query(default=0, ge=0, description="Number of attendees to skip"),
    controller: EventController = Depends()
) -> AttendeeListResponse:
    """Get all attendees for an event"""
    return await controller.get_event_attendees(event_id, limit, offset)