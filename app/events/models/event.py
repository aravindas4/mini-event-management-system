import pytz

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
from app.core.models import Base


class Event(Base):
    """Event model with timezone support"""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    max_capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now(pytz.UTC))
    updated_at = Column(
        DateTime, default=datetime.now(pytz.UTC), onupdate=datetime.now(pytz.UTC)
    )

    # Relationship with attendees
    attendees = relationship(
        "Attendee", back_populates="event", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_start_time", "start_time"),
        Index("idx_name", "name"),
    )

    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', location='{self.location}')>"

    @property
    def current_attendee_count(self) -> int:
        """Get current number of attendees"""
        return len(self.attendees) if self.attendees else 0

    @property
    def is_full(self) -> bool:
        """Check if event is at capacity"""
        return self.current_attendee_count >= self.max_capacity

    @property
    def available_spots(self) -> int:
        """Get number of available spots"""
        return self.max_capacity - self.current_attendee_count
