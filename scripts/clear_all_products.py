"""
Clear ALL products from database
Usage: python scripts/clear_all_products.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.product import Product


def clear_all_products(db: Session):
    """Delete all products from database"""
    
    print("\n🔍 Counting products...")
    
    count = db.query(Product).count()
    
    if count == 0:
        print("✅ No products found in database.")
        return
    
    print(f"⚠️  Found {count} products in database")
    
    confirmation = input(f"\n⚠️  DELETE ALL {count} PRODUCTS? Type 'YES' to confirm: ")
    
    if confirmation != 'YES':
        print("\n❌ Aborted by user")
        return
    
    # Delete all products
    print(f"\n🗑️  Deleting all {count} products...")
    
    db.query(Product).delete()
    db.commit()
    
    print(f"\n✅ Successfully deleted all products!")
    print(f"📊 Products remaining: {db.query(Product).count()}")


def main():
    """Main cleanup function"""
    print("=" * 60)
    print("🧹 CLEAR ALL PRODUCTS FROM DATABASE")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        clear_all_products(db)
        print("\n" + "=" * 60)
        print("🎉 DATABASE CLEARED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error clearing database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
