"""Initial migration for Event and Attendee models

Revision ID: 001
Revises:
Create Date: 2024-11-15 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create Event and Attendee tables"""
    # Create events table
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("max_capacity", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("max_capacity > 0", name="check_max_capacity_positive"),
        sa.CheckConstraint("start_time < end_time", name="check_start_before_end"),
    )

    # Create attendees table
    op.create_table(
        "attendees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column(
            "registered_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["event_id"], ["events.id"], name="fk_attendees_event_id"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "email", name="unique_email_per_event"),
    )

    # Create indexes for better performance
    op.create_index("idx_events_start_time", "events", ["start_time"])
    op.create_index("idx_attendees_event_id", "attendees", ["event_id"])
    op.create_index("idx_attendees_email", "attendees", ["email"])


def downgrade() -> None:
    """Drop Event and Attendee tables"""
    op.drop_index("idx_attendees_email", table_name="attendees")
    op.drop_index("idx_attendees_event_id", table_name="attendees")
    op.drop_index("idx_events_start_time", table_name="events")
    op.drop_table("attendees")
    op.drop_table("events")
