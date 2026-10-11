"""Database connection and session management."""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create engine with appropriate settings for SQLite or PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
)

# For SQLite, enable foreign keys
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        """Enable foreign keys for SQLite."""
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Declarative base for ORM models
Base = declarative_base()

# Import models to ensure tables are registered with metadata before initialization.
from app.models import models  # noqa: F401,E402


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database by creating all tables and a default user for local development."""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)

    from sqlalchemy.orm import Session
    from app.models import User

    with Session(bind=engine) as session:
        existing_user = session.query(User).filter(User.email == "demo@example.com").first()
        if not existing_user:
            session.add(
                User(
                    email="demo@example.com",
                    full_name="Demo User",
                    hashed_password="demo-password",
                    is_active=1,
                )
            )
            session.commit()
            logger.info("Seeded default demo user")

    logger.info("Database initialized successfully")


def drop_all_tables() -> None:
    """Drop all tables (use with caution)."""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All tables dropped")
