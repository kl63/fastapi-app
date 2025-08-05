#!/usr/bin/env python3
"""
Fix NULL values in user table for proper serialization
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to sys.path
root_path = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(root_path))

from app.db.session import SessionLocal
from app.models.user import User

def fix_null_values():
    print("🔧 Fixing NULL values in user table...")
    
    # Set environment variables
    os.environ['DATABASE_URL'] = 'postgresql://kl63:Kevinlin1234!@localhost:5432/fastapi_api'
    
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        print(f"Found {len(users)} users to check...")
        
        updated_count = 0
        current_time = datetime.utcnow()
        
        for user in users:
            needs_update = False
            
            # Fix is_verified if NULL
            if user.is_verified is None:
                user.is_verified = False
                needs_update = True
                print(f"  Fixed is_verified for user {user.email}")
            
            # Fix created_at if NULL
            if user.created_at is None:
                user.created_at = current_time
                needs_update = True
                print(f"  Fixed created_at for user {user.email}")
            
            # Fix updated_at if NULL
            if user.updated_at is None:
                user.updated_at = current_time
                needs_update = True
                print(f"  Fixed updated_at for user {user.email}")
            
            if needs_update:
                updated_count += 1
        
        if updated_count > 0:
            db.commit()
            print(f"\n✅ Updated {updated_count} users successfully!")
        else:
            print("\n✅ No users needed updating!")
            
        # Verify the fix
        print("\n🔍 Verifying fix...")
        users = db.query(User).all()
        for user in users:
            print(f"  User {user.email}:")
            print(f"    is_verified: {user.is_verified} (type: {type(user.is_verified)})")
            print(f"    created_at: {user.created_at} (type: {type(user.created_at)})")
            print(f"    updated_at: {user.updated_at} (type: {type(user.updated_at)})")
        
        print("\n🎉 All NULL values fixed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    fix_null_values()
