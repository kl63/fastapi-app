"""
Fix alembic_version table after deleting payment migrations
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Update alembic_version to point to the last valid migration
with engine.connect() as conn:
    # Check current version
    result = conn.execute(text("SELECT version_num FROM alembic_version"))
    current = result.fetchone()
    print(f"Current version: {current[0] if current else 'None'}")
    
    # Update to the last valid migration before the deleted ones
    conn.execute(text("UPDATE alembic_version SET version_num = '6235c6122bf8'"))
    conn.commit()
    
    # Verify update
    result = conn.execute(text("SELECT version_num FROM alembic_version"))
    new_version = result.fetchone()
    print(f"Updated to version: {new_version[0]}")
    
print("\n✅ Alembic version table fixed!")
print("Now run: alembic upgrade head")
