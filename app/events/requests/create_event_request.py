from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.core.utils.timezone_utils import (
    validate_future_datetime,
    validate_datetime_range,
)


class CreateEventRequest(BaseModel):
    """Request model for creating a new event"""

    name: str = Field(..., min_length=1, max_length=255, description="Event name")

    location: str = Field(
        ..., min_length=1, max_length=255, description="Event location"
    )

    start_time: datetime = Field(..., description="Event start time (ISO format)")

    end_time: datetime = Field(..., description="Event end time (ISO format)")

    max_capacity: int = Field(
        ..., ge=1, le=10000, description="Maximum number of attendees"
    )

    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Event name cannot be empty")
        return v.strip()

    @field_validator("location")
    def validate_location(cls, v):
        if not v.strip():
            raise ValueError("Event location cannot be empty")
        return v.strip()

    @field_validator("start_time")
    def validate_start_time(cls, v):
        validate_future_datetime(v)
        return v

    @field_validator("end_time")
    def validate_end_time(cls, v, info):
        # Get start_time from validation context
        if info.data and "start_time" in info.data:
            start_time = info.data["start_time"]
            validate_datetime_range(start_time, v, max_days=7)
        return v

    def get(self) -> dict:
        """Get validated data as dictionary"""
        return {
            "name": self.name,
            "location": self.location,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "max_capacity": self.max_capacity,
        }

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        schema_extra = {
            "example": {
                "name": "Tech Conference 2024",
                "location": "Convention Center, Mumbai",
                "start_time": "2024-12-01T10:00:00",
                "end_time": "2024-12-01T18:00:00",
                "max_capacity": 500,
            }
        }
