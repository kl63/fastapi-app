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
    """Create database and tables directly using psycopg2."""
    # Hardcode database connection parameters - these will be replaced during deployment
    db_host = '__POSTGRES_HOST__'
    db_port = '5432'  # Always use default PostgreSQL port
    db_user = '__POSTGRES_USER__'
    db_password = '__POSTGRES_PASSWORD__'
    db_name = '__POSTGRES_DB__'
    
    # First, connect to the default postgres database to create our app database if needed
    try:
        logger.info("Connecting to default PostgreSQL database to create application database...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname='postgres'  # Connect to default database first
        )
        conn.autocommit = True  # Important for creating database
        cursor = conn.cursor()
        
        # Check if our database exists, if not create it
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}';")
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database '{db_name}'...")
            # Escape any quotes in the database name
            safe_db_name = db_name.replace("'", "'''")
            cursor.execute(f"CREATE DATABASE \"{safe_db_name}\";")
            logger.info(f"Database '{db_name}' created.")
        else:
            logger.info(f"Database '{db_name}' already exists.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        sys.exit(1)

    # Now connect to our application database to create tables
    try:
        logger.info(f"Connecting to application database '{db_name}'...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
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
        logger.error(f"Error setting up database tables: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    setup_database()
