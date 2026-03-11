#!/bin/bash
# Manual database setup script for FastAPI PostgreSQL database
# Run this script on your server with: bash setup_database.sh

# Load environment variables from .env file
if [ -f .env ]; then
  echo "Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
else
  echo "Error: .env file not found!"
  exit 1
fi

# Check if required environment variables are set
if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ] || [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_HOST" ]; then
  echo "Error: Required database environment variables not set in .env file!"
  echo "Please ensure POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, and POSTGRES_HOST are set."
  exit 1
fi

# Set default port if not specified
POSTGRES_PORT=${POSTGRES_PORT:-5432}
echo "Using PostgreSQL port: $POSTGRES_PORT"

# Export password for psql commands
export PGPASSWORD="$POSTGRES_PASSWORD"

echo "Connecting to PostgreSQL server at $POSTGRES_HOST..."

# First, create database if it doesn't exist
echo "Creating database '$POSTGRES_DB' if it doesn't exist..."
psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE \"$POSTGRES_DB\";" || {
  echo "Note: Database '$POSTGRES_DB' might already exist, continuing..."
}

# Then create tables and indexes
echo "Creating tables and indexes in '$POSTGRES_DB' database..."
psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" << EOF
-- Create user table if it doesn't exist
CREATE TABLE IF NOT EXISTS "user" (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(100) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS user_email_idx ON "user" (email);
CREATE INDEX IF NOT EXISTS user_username_idx ON "user" (username);

-- Add any other tables or schema changes below
EOF

if [ $? -eq 0 ]; then
  echo "Database setup completed successfully!"
else
  echo "Error: Failed to create tables and indexes."
  exit 1
fi

# Try to run Alembic migrations if available (optional)
if [ -d 'alembic' ]; then
  echo "Attempting to run Alembic migrations..."
  alembic upgrade head || echo "⚠️ Alembic migrations failed, but the database is already set up directly."
fi

echo "✅ Database setup complete!"
