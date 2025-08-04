"""
Database initialization script.
Run this manually to create tables if Alembic migrations fail.
"""
import sys
import os
import urllib.parse
import logging
from pathlib import Path

# Add the parent directory to sys.path to ensure proper imports
root_path = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(root_path))

from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# We need to manually handle database connection due to possible import issues
def get_database_connection():
    try:
        # First try to import settings
        from app.core.config import settings
        logger.info(f"Using database URL from settings")
        return settings.DATABASE_URL
    except Exception as e:
        logger.error(f"Error importing settings: {e}")
        
        # Try to load from environment variables
        logger.info("Falling back to environment variables")
        from dotenv import load_dotenv
        load_dotenv()
        
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432") 
        db = os.getenv("POSTGRES_DB")
        
        if all([user, password, host, db]):
            # URL encode the password
            encoded_password = urllib.parse.quote_plus(password)
            db_url = f"postgresql://{user}:{encoded_password}@{host}:{port}/{db}"
            logger.info(f"Created database URL from environment variables")
            return db_url
        
        # Final fallback to SQLite
        logger.warning("Falling back to SQLite database")
        return "sqlite:///./app.db"

# Create database engine and session
def get_session():
    db_url = get_database_connection()
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {},
        pool_pre_ping=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def init_db() -> None:
    """Initialize the database with tables if they don't exist."""
    db = get_session()
    try:
        # Check if the user table exists
        try:
            logger.info("Checking if user table exists...")
            db.execute(text("SELECT 1 FROM \"user\" LIMIT 1"))
            logger.info("User table already exists, skipping creation.")
        except Exception as e:
            logger.info(f"User table does not exist ({str(e)}), creating it...")
            # Create user table
            logger.info("Creating user table...")
            db.execute(text("""
            CREATE TABLE IF NOT EXISTS "user" (
                id VARCHAR(36) PRIMARY KEY,
                email VARCHAR(100) NOT NULL UNIQUE,
                username VARCHAR(100) NOT NULL UNIQUE,
                hashed_password VARCHAR(100) NOT NULL,
                full_name VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE
            );
            """))
            
            # Create indexes separately to handle cases where table exists but indexes don't
            try:
                logger.info("Creating indexes...")
                db.execute(text("CREATE INDEX IF NOT EXISTS user_email_idx ON \"user\" (email)"))
                db.execute(text("CREATE INDEX IF NOT EXISTS user_username_idx ON \"user\" (username)"))
            except Exception as idx_error:
                logger.warning(f"Error creating indexes: {idx_error}")
            
            db.commit()
            logger.info("User table created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main() -> None:
    """Main function to initialize the database."""
    logger.info("Creating database tables")
    init_db()
    logger.info("Database tables created")

if __name__ == "__main__":
    main()
