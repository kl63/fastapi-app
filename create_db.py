import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database connection parameters
host = "127.0.0.1"
port = 5432
user = "kevinlin192003"
password = "@Basketball1234"
dbname = "fastapi_db"

# Connect to PostgreSQL server (default database)
print(f"Connecting to PostgreSQL at {host}:{port}...")
try:
    # Connect to template1 database to create our database
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database="template1"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
    exists = cursor.fetchone()
    
    if exists:
        print(f"✅ Database '{dbname}' already exists")
    else:
        # Create database
        print(f"Creating database '{dbname}'...")
        cursor.execute(f"CREATE DATABASE {dbname}")
        print(f"✅ Database '{dbname}' created successfully")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
