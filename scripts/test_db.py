import os
import sys
import psycopg2

# Get the database URL from arguments
db_url = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('DATABASE_URL')
print(f"Testing connection to: {db_url}")

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print("Connection successful!")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Connection error: {str(e)}")
    # Don't fail - we'll let the app handle this
