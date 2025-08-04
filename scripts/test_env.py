#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Print basic diagnostic information
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Try to load from .env file
env_file = Path('.env')
if env_file.exists():
    print(f".env file found at {env_file.absolute()}")
    load_dotenv(dotenv_path=env_file)
    print("Loaded environment from .env file")
else:
    print(f"No .env file found at {env_file.absolute()}")

# Print relevant environment variables
print(f"DATABASE_URL: '{os.environ.get('DATABASE_URL')}'")
print(f"SECRET_KEY: '{os.environ.get('SECRET_KEY')}'")

# Test importing database modules
try:
    print("\nTrying to import database modules...")
    
    # Try both relative and absolute imports
    try:
        sys.path.insert(0, os.getcwd())
        from app.db.session import engine
        print(f"Successfully imported database session (engine URL: {engine.url})")
    except ImportError as e:
        print(f"Relative import failed: {e}")
        
        # Try using python-dotenv explicitly with current file
        print("\nTrying explicit dotenv loading...")
        project_dir = Path(__file__).parent.parent
        load_dotenv(project_dir / '.env')
        print(f"DATABASE_URL after explicit load: '{os.environ.get('DATABASE_URL')}'")
        
except Exception as e:
    print(f"Error importing database modules: {e}")

print("\nEnvironment test complete")
