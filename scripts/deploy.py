#!/usr/bin/env python3
"""
Deployment script for FastAPI application
Handles database creation, migrations, and application startup
"""
import os
import sys
import logging
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse, quote_plus
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the parent directory to sys.path
root_path = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(root_path))

from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_database_if_not_exists():
    """
    Create the database if it doesn't exist (PostgreSQL only)
    """
    if not settings.DATABASE_URL or not settings.DATABASE_URL.startswith('postgresql'):
        logger.info("Not using PostgreSQL, skipping database creation")
        return True
    
    try:
        # Parse the database URL
        parsed = urlparse(settings.DATABASE_URL)
        dbname = parsed.path.lstrip('/')
        user = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 5432
        
        logger.info(f"Checking if database '{dbname}' exists on {host}:{port}")
        
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Check if database exists
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        exists = cur.fetchone()
        
        if not exists:
            logger.info(f"Database '{dbname}' does not exist. Creating it...")
            cur.execute(f'CREATE DATABASE "{dbname}"')
            logger.info(f"Database '{dbname}' created successfully")
        else:
            logger.info(f"Database '{dbname}' already exists")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False


def run_alembic_migrations():
    """
    Run Alembic migrations to update database schema
    """
    try:
        logger.info("Running Alembic migrations...")
        
        # Change to the project root directory
        os.chdir(root_path)
        
        # First, try to run migrations normally
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("Alembic migrations completed successfully")
            logger.info(f"Migration output: {result.stdout}")
            return True
        
        # If migration failed due to existing tables, try to stamp the database
        if "already exists" in result.stderr or "DuplicateTable" in result.stderr:
            logger.info("Tables already exist. Stamping database with current migration...")
            
            # Get the latest migration revision
            revision_result = subprocess.run(
                ["alembic", "heads"],
                capture_output=True,
                text=True
            )
            
            if revision_result.returncode == 0:
                revision_output = revision_result.stdout.strip()
                # Extract just the revision ID (first part before space or parentheses)
                revision = revision_output.split()[0] if revision_output else "head"
                logger.info(f"Stamping database with revision: {revision}")
                
                # Stamp the database with the current revision
                stamp_result = subprocess.run(
                    ["alembic", "stamp", revision],
                    capture_output=True,
                    text=True
                )
                
                if stamp_result.returncode == 0:
                    logger.info("Database stamped successfully")
                    return True
                else:
                    logger.error(f"Failed to stamp database: {stamp_result.stderr}")
            
        logger.error(f"Alembic migration failed: {result.stderr}")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error running migrations: {e}")
        return False


def check_database_connection():
    """
    Check if we can connect to the database
    """
    try:
        from app.db.session import SessionLocal
        from sqlalchemy import text
        
        logger.info("Testing database connection...")
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def create_initial_migration_if_needed():
    """
    Create initial migration if no migrations exist
    """
    try:
        versions_dir = root_path / "alembic" / "versions"
        migration_files = [f for f in versions_dir.glob("*.py") if not f.name.startswith("__")]
        
        if not migration_files:
            logger.info("No migrations found. Creating initial migration...")
            
            result = subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
                capture_output=True,
                text=True,
                cwd=root_path
            )
            
            if result.returncode == 0:
                logger.info("Initial migration created successfully")
                return True
            else:
                logger.error(f"Failed to create initial migration: {result.stderr}")
                return False
        else:
            logger.info(f"Found {len(migration_files)} existing migration(s)")
            return True
            
    except Exception as e:
        logger.error(f"Error checking/creating migrations: {e}")
        return False


def main():
    """
    Main deployment function
    """
    logger.info("Starting deployment process...")
    
    # Step 1: Create database if it doesn't exist
    if not create_database_if_not_exists():
        logger.error("Failed to create database. Exiting.")
        sys.exit(1)
    
    # Step 2: Create initial migration if needed
    if not create_initial_migration_if_needed():
        logger.error("Failed to create initial migration. Exiting.")
        sys.exit(1)
    
    # Step 3: Run migrations
    if not run_alembic_migrations():
        logger.error("Failed to run migrations. Exiting.")
        sys.exit(1)
    
    # Step 4: Test database connection
    if not check_database_connection():
        logger.error("Database connection test failed. Exiting.")
        sys.exit(1)
    
    logger.info("Deployment completed successfully!")
    logger.info("Database is ready for the application.")


if __name__ == "__main__":
    main()
