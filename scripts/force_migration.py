#!/usr/bin/env python3
"""
Force migration script for production server
Run this manually on the server to apply database migrations
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the parent directory to sys.path
root_path = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(root_path))

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            cwd=root_path
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        print(f"Output: {e.stdout}")
        return False

def main():
    print("🚀 Starting forced database migration...")
    
    # Set environment variables
    os.environ['DATABASE_URL'] = 'postgresql://kl63:Kevinlin1234!@localhost:5432/fastapi_api'
    
    # Check current migration status
    print("\n📊 Checking current migration status...")
    run_command("alembic current", "Check current migration")
    
    # Show available migrations
    print("\n📋 Available migrations:")
    run_command("alembic history", "List migration history")
    
    # Upgrade to latest migration
    print("\n⬆️ Applying all migrations...")
    if run_command("alembic upgrade head", "Apply migrations"):
        print("\n✅ All migrations applied successfully!")
        
        # Verify migration status
        print("\n🔍 Verifying migration status...")
        run_command("alembic current", "Verify current migration")
        
        print("\n🎉 Database migration completed!")
        print("You can now restart the FastAPI application:")
        print("pm2 restart fastapi-app")
    else:
        print("\n❌ Migration failed. Check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
