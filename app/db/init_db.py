"""
Database initialization script.
Run this manually to create tables if Alembic migrations fail.
"""
import sys
import os
from pathlib import Path
import logging

# Add the parent directory to sys.path to ensure proper imports
root_path = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(root_path))

from sqlalchemy import text
from app.db.session import SessionLocal
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize the database with tables if they don't exist."""
    db = SessionLocal()
    try:
        # Check if the user table exists
        try:
            db.execute(text("SELECT 1 FROM user LIMIT 1"))
            logger.info("User table already exists, skipping creation.")
        except Exception:
            logger.info("Creating user table...")
            # Create user table
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
            
            CREATE INDEX IF NOT EXISTS user_email_idx ON "user" (email);
            CREATE INDEX IF NOT EXISTS user_username_idx ON "user" (username);
            """))
            
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
