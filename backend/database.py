"""
DRISHTI - Database setup
------------------------
Creates the SQLite database connection and session factory.
SQLite is used because it needs zero installation (perfect for prototypes).
For production, swap the URL below for PostgreSQL:
    postgresql://user:password@localhost/drishti
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLite database file lives next to this folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./drishti.db"

# check_same_thread=False is required only for SQLite + FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each API request gets its own DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All ORM models inherit from this Base class
Base = declarative_base()


def get_db():
    """FastAPI dependency: opens a DB session per request, closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()