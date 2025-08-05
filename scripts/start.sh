#!/bin/bash
set -e

echo "Starting FastAPI application deployment..."

# Navigate to the project directory
cd "$(dirname "$0")/.."

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Run database setup and migrations
echo "Setting up database and running migrations..."
python scripts/deploy.py

# Start the application
echo "Starting FastAPI application..."
if [ "$NODE_ENV" = "production" ]; then
    # Production mode
    uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
else
    # Development mode with reload
    uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
fi
