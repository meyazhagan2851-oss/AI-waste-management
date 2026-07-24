"""
database.py
------------
Database connection and session management using SQLAlchemy.
Defaults to SQLite (zero-config, file-based) but DATABASE_URL can be
swapped for PostgreSQL/MySQL in production via the .env file.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# connect_args is required only for SQLite to allow multi-threaded access
# (FastAPI can handle requests on different threads)
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# Each instance of SessionLocal will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our ORM models will inherit from
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request
    and guarantees it is closed afterwards, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables. Called once on application startup."""
    # Import models here to ensure they are registered with Base before creating tables
    from app.models import db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
