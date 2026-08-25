"""
DRISHTI - Database setup
------------------------
LOCAL DEVELOPMENT: SQLite (zero installation, perfect for prototypes).
HOSTED / PRODUCTION: set the DATABASE_URL environment variable to any
PostgreSQL connection string — Supabase, Neon, Render Postgres all work:

    DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxx.supabase.co:5432/postgres

This IS the famous "one-line SQLite -> PostgreSQL migration": every query in
the codebase goes through SQLAlchemy, so nothing else has to change.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Env var wins when present (Render/Supabase); otherwise local SQLite file.
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./drishti.db")

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # check_same_thread=False is required only for SQLite + FastAPI
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # pool_pre_ping=True drops dead pooled connections (managed Postgres
    # providers like Supabase close idle connections aggressively).
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

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