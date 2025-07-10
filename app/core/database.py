from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.database import db_settings

"""
Primary MySQL
Connects to MySQL database for event management
"""
engine_primary = create_engine(db_settings.primary.url(), echo=True)
SessionLocalPrimary = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_primary
)


def get_primary_db() -> Session:
    """Get a database session for the primary MySQL database"""
    db = SessionLocalPrimary()
    try:
        yield db
    finally:
        db.close()
