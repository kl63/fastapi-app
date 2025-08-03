import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.core.config import settings

# Determine if we're using an async URL
is_async = '+asyncpg' in settings.DATABASE_URL

# Create appropriate engine based on URL
if is_async:
    # For async connections
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    
    # Also create a synchronous URL for the health check
    sync_url = re.sub(r'\+asyncpg', '', settings.DATABASE_URL)
    engine = create_engine(
        sync_url,
        pool_pre_ping=True,
        pool_size=3,  # Smaller pool for health checks
    )
else:
    # For synchronous connections
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    async_engine = None

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
