import re
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

# Handle the database URL carefully to prevent connection issues
# First, parse the URL to check for missing components
db_url = settings.DATABASE_URL

# If it's a PostgreSQL URL, ensure all components are valid
if db_url.startswith("postgresql"):
    try:
        # Parse the URL to extract components
        url_parts = make_url(db_url)
        
        # If port is missing or invalid, fix it
        if not url_parts.port:
            # Get individual components
            user = url_parts.username
            password = url_parts.password if url_parts.password else ""
            host = url_parts.host if url_parts.host else "localhost"
            db_name = url_parts.database if url_parts.database else ""
            
            # Reconstruct the URL with default port 5432
            encoded_password = urllib.parse.quote_plus(password) if password else ""
            if password:
                db_url = f"postgresql://{user}:{encoded_password}@{host}:5432/{db_name}"
            else:
                db_url = f"postgresql://{user}@{host}:5432/{db_name}"
            print(f"Fixed PostgreSQL URL with default port: {db_url.replace(encoded_password, '***')}")
    except Exception as e:
        print(f"Error parsing database URL: {e}")
        # Fallback to SQLite if there's an issue with the PostgreSQL URL
        print("Falling back to SQLite database")
        db_url = "sqlite:///./app.db"

# Create engine with appropriate connect args based on DB type
engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
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
