import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import settings after loading environment variables
from app.core.config import settings

# Get DB URL from settings
db_url = settings.DATABASE_URL

if db_url.startswith("postgresql"):
    try:
        # Parse the URL
        url_parts = make_url(db_url)

        user = url_parts.username
        password = url_parts.password or ""
        host = url_parts.host or "localhost"
        port = url_parts.port or 5432
        db_name = url_parts.database or ""

        # Always encode the password
        encoded_password = urllib.parse.quote_plus(password)

        # Rebuild the URL with the encoded password
        db_url = f"postgresql://{user}:{encoded_password}@{host}:{port}/{db_name}"

        # Debug log (hides password)
        print("DEBUG: Final DB URL ->", db_url.replace(encoded_password, "***"))
    except Exception as e:
        print(f"Error parsing database URL: {e}")
        print("Falling back to SQLite database")
        db_url = "sqlite:///./app.db"

# Create SQLAlchemy engine
engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create session factory
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
