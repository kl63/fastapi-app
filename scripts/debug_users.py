#!/usr/bin/env python3
"""
Debug script to test the get_users function
"""
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
root_path = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(root_path))

from app.db.session import SessionLocal
from app.crud.user import get_users
from app.models.user import User

def debug_users():
    print("🔍 Debugging users endpoint...")
    
    # Set environment variables
    os.environ['DATABASE_URL'] = 'postgresql://kl63:Kevinlin1234!@localhost:5432/fastapi_api'
    
    db = SessionLocal()
    
    try:
        print("\n1. Testing database connection...")
        # Test basic query
        user_count = db.query(User).count()
        print(f"   Total users in database: {user_count}")
        
        print("\n2. Testing get_users function...")
        users = get_users(db, skip=0, limit=100)
        print(f"   get_users returned: {len(users)} users")
        
        print("\n3. Checking user data...")
        for i, user in enumerate(users):
            print(f"   User {i+1}:")
            print(f"     ID: {user.id}")
            print(f"     Email: {user.email}")
            print(f"     Username: {user.username}")
            print(f"     Admin: {user.is_admin}")
            print(f"     Active: {user.is_active}")
            
            # Try to serialize to dict (this is what FastAPI does)
            try:
                user_dict = {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone,
                    "date_of_birth": user.date_of_birth,
                    "is_active": user.is_active,
                    "is_admin": user.is_admin,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                    "last_login": user.last_login,
                    "full_name": user.full_name
                }
                print(f"     Serialization: ✅ Success")
            except Exception as e:
                print(f"     Serialization: ❌ Error - {e}")
                
        print("\n✅ Debug completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during debug: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    debug_users()
