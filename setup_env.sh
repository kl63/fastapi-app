#!/bin/bash
# Environment variables setup script for FastAPI PostgreSQL database
# Run this script on your server with: bash setup_env.sh

echo "Setting up environment variables in .env file..."

# Prompt for database credentials
read -p "Enter PostgreSQL username: " POSTGRES_USER
read -s -p "Enter PostgreSQL password: " POSTGRES_PASSWORD
echo ""
read -p "Enter PostgreSQL database name: " POSTGRES_DB
read -p "Enter PostgreSQL host (default: localhost): " POSTGRES_HOST
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
read -p "Enter PostgreSQL port (default: 5432): " POSTGRES_PORT
POSTGRES_PORT=${POSTGRES_PORT:-5432}

# URL encode the password for DATABASE_URL
ENCODED_PASSWORD=$(python3 -c "import urllib.parse; print(urllib.parse.quote_plus('$POSTGRES_PASSWORD'))")

# Generate .env file
cat > .env << EOF
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=$POSTGRES_DB
POSTGRES_HOST=$POSTGRES_HOST
POSTGRES_PORT=$POSTGRES_PORT
DATABASE_URL=postgresql://$POSTGRES_USER:$ENCODED_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB
SECRET_KEY=supersecretkey
API_VERSION=1.0.0
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
EOF

# Set proper permissions for .env file
chmod 600 .env

echo "✅ Environment variables have been set up in .env file"
echo "You can now run the database setup script: bash setup_database.sh"
