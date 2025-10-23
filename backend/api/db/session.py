"""Database session management and connection."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import NullPool
from typing import Generator

# Database URL from environment variable - NO HARDCODED CREDENTIALS
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set it in your .env file or environment."
    )

# Create engine
# For development, use NullPool to avoid connection issues with Docker
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool if os.getenv("ENV") == "development" else None,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    future=True,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

# Base class for declarative models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database sessions.

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database - create all tables."""
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Drop all database tables. WARNING: Use with caution!"""
    Base.metadata.drop_all(bind=engine)
