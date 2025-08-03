from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    # Connect args for SQLite - remove if using PostgreSQL
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    # For PostgreSQL, let's add some engine configuration for better performance
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create SessionLocal class for dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function to get DB session
    
    Yields:
        db (Session): SQLAlchemy Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
