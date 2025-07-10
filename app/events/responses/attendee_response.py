from datetime import datetime
from pydantic import BaseModel, Field

from app.events.models.attendee import Attendee


class AttendeeResponse(BaseModel):
    """Response model for attendee data"""

    id: int = Field(..., description="Attendee ID")
    name: str = Field(..., description="Attendee name")
    email: str = Field(..., description="Attendee email")
    event_id: int = Field(..., description="Event ID")
    registered_at: datetime = Field(..., description="Registration timestamp")

    @classmethod
    def from_domain(cls, attendee: Attendee) -> "AttendeeResponse":
        """Create response from domain model"""
        return cls(
            id=attendee.id,
            name=attendee.name,
            email=attendee.email,
            event_id=attendee.event_id,
            registered_at=attendee.registered_at,
        )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "event_id": 1,
                "registered_at": "2024-11-15T14:30:00",
            }
        }


class AttendeeListResponse(BaseModel):
    """Response model for paginated attendee list"""

    attendees: list[AttendeeResponse] = Field(..., description="List of attendees")
    total_count: int = Field(..., description="Total number of attendees")
    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Number of items skipped")
    has_more: bool = Field(..., description="Whether there are more items")

    @classmethod
    def from_domain_list(
        cls, attendees: list[Attendee], total_count: int, limit: int, offset: int
    ) -> "AttendeeListResponse":
        """Create response from domain model list"""
        return cls(
            attendees=[
                AttendeeResponse.from_domain(attendee) for attendee in attendees
            ],
            total_count=total_count,
            limit=limit,
            offset=offset,
            has_more=offset + len(attendees) < total_count,
        )

    class Config:
        schema_extra = {
            "example": {
                "attendees": [
                    {
                        "id": 1,
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "event_id": 1,
                        "registered_at": "2024-11-15T14:30:00",
                    }
                ],
                "total_count": 125,
                "limit": 50,
                "offset": 0,
                "has_more": True,
            }
        }
