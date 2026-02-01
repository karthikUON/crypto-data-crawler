"""Database connection and session management."""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from crawler.config import settings
from db.models import Base

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,  # Number of connections to maintain in the pool
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database by creating all tables."""
    try:
        logger.info("Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db():
    """
    Dependency function for FastAPI to get database session.

    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        connection = engine.connect()
        connection.close()
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
