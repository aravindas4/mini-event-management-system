from pydantic import BaseModel, Field, field_validator
import re


class RegisterAttendeeRequest(BaseModel):
    """Request model for registering an attendee"""

    name: str = Field(..., min_length=1, max_length=255, description="Attendee name")

    email: str = Field(..., max_length=255, description="Attendee email address")

    @field_validator("name")
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Attendee name cannot be empty")
        return v.strip()

    @field_validator("email")
    def validate_email(cls, v):
        email = v.strip().lower()
        if not email:
            raise ValueError("Email cannot be empty")

        # Basic email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")

        return email

    def get(self) -> dict:
        """Get validated data as dictionary"""
        return {"name": self.name, "email": self.email}

    class Config:
        schema_extra = {
            "example": {"name": "John Doe", "email": "john.doe@example.com"}
        }
