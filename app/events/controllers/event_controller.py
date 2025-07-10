import logging
from typing import List
from fastapi import Depends, HTTPException, Query

from app.events.services.event_service import EventService
from app.events.requests.create_event_request import CreateEventRequest
from app.events.requests.register_attendee_request import RegisterAttendeeRequest
from app.events.responses.event_response import EventResponse
from app.events.responses.attendee_response import AttendeeResponse, AttendeeListResponse
from app.core.exceptions import EventNotFound, CapacityExceeded, DuplicateRegistration, ValidationError
from app.core.middlewares.trace_context_middleware import get_trace_id, get_request_id, get_event_id
from app.core.utils.timezone_utils import validate_timezone

logger = logging.getLogger("event_management.controllers")

class EventController:
    """Controller for event-related HTTP endpoints"""
    
    def __init__(self, service: EventService = Depends()):
        self.service = service
    
    async def create_event(self, request: CreateEventRequest) -> EventResponse:
        """Create event endpoint"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        logger.debug(
            "Event creation request received",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "endpoint": "POST /events",
                "request_data": request.dict()
            }
        )
        
        try:
            event = await self.service.create_event(request.get())
            response = EventResponse.from_domain(event)
            
            logger.debug(
                "Event creation response sent",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event.id,
                    "status_code": 201
                }
            )
            
            return response
            
        except ValidationError as e:
            logger.warning(
                "Event creation validation error",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "endpoint": "POST /events",
                    "error": str(e)
                }
            )
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(
                "Event creation endpoint failed",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "endpoint": "POST /events",
                    "error": str(e)
                },
                exc_info=True
            )
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_events(
        self, 
        limit: int,
        offset: int,
        timezone: str
    ) -> List[EventResponse]:
        """Get upcoming events endpoint with timezone conversion"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        logger.debug(
            "Get events request received",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "endpoint": "GET /events",
                "limit": limit,
                "offset": offset,
                "timezone": timezone
            }
        )
        
        try:
            # Validate timezone
            if not validate_timezone(timezone):
                raise ValidationError(f"Invalid timezone: {timezone}")
                
            events = await self.service.get_upcoming_events(limit, offset)
            response = [EventResponse.from_domain(event, timezone) for event in events]
            
            logger.debug(
                "Get events response sent",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "count": len(response),
                    "timezone": timezone,
                    "status_code": 200
                }
            )
            
            return response
            
        except ValidationError as e:
            logger.warning(
                "Get events validation error",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "endpoint": "GET /events",
                    "error": str(e)
                }
            )
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(
                "Get events endpoint failed",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "endpoint": "GET /events",
                    "error": str(e)
                },
                exc_info=True
            )
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def register_attendee(self, event_id: int, request: RegisterAttendeeRequest) -> AttendeeResponse:
        """Register attendee endpoint with ContextVar-based logging"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        logger.debug(
            "Attendee registration request received",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_id": event_id,
                "endpoint": f"POST /events/{event_id}/register"
            }
        )
        
        try:
            attendee = await self.service.register_attendee(event_id, request.get())
            response = AttendeeResponse.from_domain(attendee)
            
            logger.debug(
                "Attendee registration response sent",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "attendee_id": attendee.id,
                    "status_code": 201
                }
            )
            
            return response
            
        except EventNotFound as e:
            logger.warning(
                "Attendee registration - event not found",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "error": str(e)
                }
            )
            raise HTTPException(status_code=404, detail=str(e))
        except (CapacityExceeded, DuplicateRegistration) as e:
            logger.warning(
                "Attendee registration - conflict",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "error": str(e)
                }
            )
            raise HTTPException(status_code=409, detail=str(e))
        except ValidationError as e:
            logger.warning(
                "Attendee registration validation error",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "error": str(e)
                }
            )
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(
                "Attendee registration endpoint failed",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "endpoint": f"POST /events/{event_id}/register",
                    "error": str(e)
                },
                exc_info=True
            )
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_event_attendees(
        self, 
        event_id: int,
        limit: int = Query(default=50, ge=1, le=1000, description="Number of attendees to return"),
        offset: int = Query(default=0, ge=0, description="Number of attendees to skip")
    ) -> AttendeeListResponse:
        """Get event attendees endpoint with pagination"""
        trace_id = get_trace_id()
        request_id = get_request_id()
        
        logger.debug(
            "Get event attendees request received",
            extra={
                "trace_id": trace_id,
                "request_id": request_id,
                "event_id": event_id,
                "endpoint": f"GET /events/{event_id}/attendees",
                "limit": limit,
                "offset": offset
            }
        )
        
        try:
            attendees = await self.service.get_event_attendees(event_id, limit, offset)
            
            # Get total count for pagination
            total_count = await self.service.repository.get_attendee_count(event_id)
            
            response = AttendeeListResponse.from_domain_list(attendees, total_count, limit, offset)
            
            logger.debug(
                "Get event attendees response sent",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "count": len(attendees),
                    "total_count": total_count,
                    "status_code": 200
                }
            )
            
            return response
            
        except EventNotFound as e:
            logger.warning(
                "Get event attendees - event not found",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "error": str(e)
                }
            )
            raise HTTPException(status_code=404, detail=str(e))
        except ValidationError as e:
            logger.warning(
                "Get event attendees validation error",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "error": str(e)
                }
            )
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(
                "Get event attendees endpoint failed",
                extra={
                    "trace_id": trace_id,
                    "request_id": request_id,
                    "event_id": event_id,
                    "endpoint": f"GET /events/{event_id}/attendees",
                    "error": str(e)
                },
                exc_info=True
            )
            raise HTTPException(status_code=500, detail="Internal server error")