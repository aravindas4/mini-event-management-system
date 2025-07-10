import pytz

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.core.models import Base


class Attendee(Base):
    """Attendee model with email validation and event relationship"""

    __tablename__ = "attendees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    registered_at = Column(DateTime, default=datetime.now(pytz.UTC))

    # Relationship with event
    event = relationship("Event", back_populates="attendees")

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("event_id", "email", name="unique_email_per_event"),
        Index("idx_event_id", "event_id"),
        Index("idx_email", "email"),
    )

    def __repr__(self):
        return f"<Attendee(id={self.id}, name='{self.name}', email='{self.email}', event_id={self.event_id})>"
