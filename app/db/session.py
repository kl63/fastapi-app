import re
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import settings after loading environment variables
from app.core.config import settings

# We're not using async PostgreSQL in this project, so ensure we have a proper sync connection
# Convert any accidental asyncpg connection strings to standard psycopg2
if '+asyncpg' in settings.DATABASE_URL:
    settings.DATABASE_URL = re.sub(r'\+asyncpg', '', settings.DATABASE_URL)

# Create engine with appropriate connect args based on DB type
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
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
