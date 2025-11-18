#!/usr/bin/env python3
"""Fix production database schema - make address columns nullable"""
import sys
sys.path.insert(0, '/var/www/fastapi-app')

from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

print("🔧 Fixing production database schema...")
print("Making billing_address_id and delivery_address_id nullable\n")

with engine.connect() as conn:
    # Make billing_address_id nullable
    print("1️⃣  Altering billing_address_id...")
    conn.execute(text("""
        ALTER TABLE "order" 
        ALTER COLUMN billing_address_id DROP NOT NULL;
    """))
    print("   ✅ billing_address_id is now nullable\n")
    
    # Make delivery_address_id nullable  
    print("2️⃣  Altering delivery_address_id...")
    conn.execute(text("""
        ALTER TABLE "order" 
        ALTER COLUMN delivery_address_id DROP NOT NULL;
    """))
    print("   ✅ delivery_address_id is now nullable\n")
    
    conn.commit()

print("✅ Schema fix complete!")
print("Orders can now be created without billing address!")
