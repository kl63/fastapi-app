"""
Fix NULL values in user table for is_verified, created_at, updated_at
"""
from sqlalchemy import create_engine, text
from datetime import datetime
from app.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Update users with NULL values
with engine.connect() as conn:
    # Fix is_verified
    result = conn.execute(text("""
        UPDATE "user" 
        SET is_verified = false 
        WHERE is_verified IS NULL
    """))
    print(f"✅ Updated {result.rowcount} users with NULL is_verified")
    
    # Fix created_at
    result = conn.execute(text("""
        UPDATE "user" 
        SET created_at = :now 
        WHERE created_at IS NULL
    """), {"now": datetime.utcnow()})
    print(f"✅ Updated {result.rowcount} users with NULL created_at")
    
    # Fix updated_at
    result = conn.execute(text("""
        UPDATE "user" 
        SET updated_at = :now 
        WHERE updated_at IS NULL
    """), {"now": datetime.utcnow()})
    print(f"✅ Updated {result.rowcount} users with NULL updated_at")
    
    conn.commit()
    
print("\n✅ All NULL values fixed!")
