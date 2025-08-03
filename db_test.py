"""
Database connection diagnostic script.
Run this on the server to test PostgreSQL connectivity.
"""
import os
import sys
import psycopg2
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Try to load environment variables
print("Loading .env file...")
load_dotenv()

# Get database URL from environment
db_url = os.getenv("DATABASE_URL")
print(f"Database URL from environment: {db_url}")

if not db_url:
    print("ERROR: DATABASE_URL environment variable not found!")
    sys.exit(1)

# Test direct psycopg2 connection
print("\n--- Testing psycopg2 direct connection ---")
try:
    # Parse the DATABASE_URL to extract components
    if db_url.startswith("postgresql://"):
        connection_parts = db_url[len("postgresql://"):].split("@")
        user_pass = connection_parts[0].split(":")
        host_db = connection_parts[1].split("/")
        
        username = user_pass[0]
        password = user_pass[1] if len(user_pass) > 1 else None
        host = host_db[0].split(":")[0]  # Split out port if exists
        dbname = host_db[1] if len(host_db) > 1 else None
        
        print(f"Username: {username}")
        print(f"Password: {'*' * len(password) if password else 'None or Empty'}")
        print(f"Host: {host}")
        print(f"Database: {dbname}")
    else:
        print(f"WARNING: Unexpected database URL format: {db_url}")
    
    # Try to connect
    conn = psycopg2.connect(db_url)
    print("psycopg2 connection successful!")
    conn.close()
except Exception as e:
    print(f"psycopg2 connection failed: {e}")

# Test SQLAlchemy connection
print("\n--- Testing SQLAlchemy connection ---")
try:
    engine = create_engine(db_url)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(f"SQLAlchemy connection successful! Result: {result.scalar()}")
except Exception as e:
    print(f"SQLAlchemy connection failed: {e}")

print("\n--- Checking PostgreSQL service ---")
try:
    import subprocess
    result = subprocess.run(["systemctl", "status", "postgresql"], 
                           capture_output=True, text=True)
    print(result.stdout)
except Exception as e:
    print(f"Could not check PostgreSQL service: {e}")
