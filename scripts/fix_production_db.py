#!/usr/bin/env python3
"""
Comprehensive production database fix script
This will create a new migration with all the missing columns and tables
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the parent directory to sys.path
root_path = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(root_path))

def run_command(command, description, check=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            capture_output=True, 
            text=True,
            cwd=root_path
        )
        print(f"✅ {description} completed")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr and check:
            print(f"Stderr: {result.stderr}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        print(f"Output: {e.stdout}")
        return False

def main():
    print("🚀 Starting comprehensive production database fix...")
    
    # Set environment variables
    os.environ['DATABASE_URL'] = 'postgresql://kl63:Kevinlin1234!@localhost:5432/fastapi_api'
    
    print("\n📊 Current status:")
    run_command("alembic current", "Check current migration", check=False)
    run_command("alembic heads", "Check migration heads", check=False)
    run_command("ls -la alembic/versions/", "List migration files", check=False)
    
    print("\n🔧 Creating new migration for missing schema...")
    # Create a new migration that will add all missing columns and tables
    if run_command("alembic revision --autogenerate -m 'Add missing e-commerce schema'", "Generate new migration"):
        print("\n⬆️ Applying the new migration...")
        if run_command("alembic upgrade head", "Apply new migration"):
            print("\n✅ Database schema updated successfully!")
            
            # Verify the fix
            print("\n🔍 Verifying database schema...")
            run_command("alembic current", "Check final migration status", check=False)
            
            print("\n🎉 Production database fix completed!")
            print("Restart the application: pm2 restart fastapi-app")
            return 0
        else:
            print("\n❌ Failed to apply migration")
            return 1
    else:
        print("\n❌ Failed to generate migration")
        return 1

if __name__ == "__main__":
    exit(main())
