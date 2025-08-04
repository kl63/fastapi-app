import os
import sys
print(f"Python version: {sys.version}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
print(f"Current directory: {os.getcwd()}")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")

try:
    from app.db.base import Base
    from app.db.session import engine
    print("Successfully imported database modules")
    print(f"Engine URL: {engine.url}")
    Base.metadata.create_all(bind=engine)
    print("Successfully created database tables")
except Exception as e:
    print(f"Error creating database tables: {str(e)}")
