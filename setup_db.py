"""
Standalone database setup script with hardcoded PostgreSQL connection.
This bypasses environment variables and SQLAlchemy URL parsing issues.
"""
import os
import sys
import psycopg2
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_database():
    """Create database tables directly using psycopg2."""
    # Hardcode database connection parameters - these will be replaced during deployment
    db_params = {
        'host': '__POSTGRES_HOST__',
        'port': '5432',  # Always use default PostgreSQL port
        'user': '__POSTGRES_USER__',
        'password': '__POSTGRES_PASSWORD__',
        'dbname': '__POSTGRES_DB__'
    }

    try:
        logger.info("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        logger.info("Creating user table if it doesn't exist...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS "user" (
            id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(100) NOT NULL UNIQUE,
            username VARCHAR(100) NOT NULL UNIQUE,
            hashed_password VARCHAR(100) NOT NULL,
            full_name VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE,
            is_admin BOOLEAN DEFAULT FALSE
        );
        """)
        
        # Create indexes
        logger.info("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS user_email_idx ON \"user\" (email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS user_username_idx ON \"user\" (username)")
        
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    setup_database()
