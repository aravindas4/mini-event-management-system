from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.events.models.event import Event
from app.core.utils.timezone_utils import convert_utc_to_timezone, get_default_timezone

class EventResponse(BaseModel):
    """Response model for event data"""
    
    id: int = Field(..., description="Event ID")
    name: str = Field(..., description="Event name")
    location: str = Field(..., description="Event location")
    start_time: datetime = Field(..., description="Event start time")
    end_time: datetime = Field(..., description="Event end time")
    max_capacity: int = Field(..., description="Maximum number of attendees")
    current_attendee_count: int = Field(..., description="Current number of registered attendees")
    available_spots: int = Field(..., description="Number of available spots")
    is_full: bool = Field(..., description="Whether the event is at capacity")
    created_at: datetime = Field(..., description="Event creation time")
    updated_at: datetime = Field(..., description="Event last update time")
    
    @classmethod
    def from_domain(cls, event: Event, timezone: Optional[str] = None) -> "EventResponse":
        """Create response from domain model with optional timezone conversion"""
        target_timezone = timezone or get_default_timezone()
        
        # Convert start_time and end_time to target timezone
        start_time = convert_utc_to_timezone(event.start_time, target_timezone)
        end_time = convert_utc_to_timezone(event.end_time, target_timezone)
        
        return cls(
            id=event.id,
            name=event.name,
            location=event.location,
            start_time=start_time,
            end_time=end_time,
            max_capacity=event.max_capacity,
            current_attendee_count=event.current_attendee_count,
            available_spots=event.available_spots,
            is_full=event.is_full,
            created_at=event.created_at,
            updated_at=event.updated_at
        )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Tech Conference 2024",
                "location": "Convention Center, Mumbai",
                "start_time": "2024-12-01T10:00:00",
                "end_time": "2024-12-01T18:00:00",
                "max_capacity": 500,
                "current_attendee_count": 125,
                "available_spots": 375,
                "is_full": False,
                "created_at": "2024-11-01T09:00:00",
                "updated_at": "2024-11-01T09:00:00"
            }
        }