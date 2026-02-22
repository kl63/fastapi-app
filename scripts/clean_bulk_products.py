"""
Clean up bulk-seeded products (removes products with # in the name)
Usage: python scripts/clean_bulk_products.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.product import Product


def clean_bulk_products(db: Session):
    """Delete products with # in the name (bulk-seeded products)"""
    
    print("\n🔍 Finding bulk-seeded products...")
    
    # Find all products with # in the name
    bulk_products = db.query(Product).filter(Product.name.like('%#%')).all()
    
    count = len(bulk_products)
    
    if count == 0:
        print("✅ No bulk-seeded products found to clean.")
        return
    
    print(f"⚠️  Found {count} bulk-seeded products with '#' in the name")
    print(f"\nExample products to delete:")
    for i, product in enumerate(bulk_products[:5]):
        print(f"  - {product.name}")
    
    if count > 5:
        print(f"  ... and {count - 5} more")
    
    confirmation = input(f"\n⚠️  Delete {count} products? Type 'YES' to confirm: ")
    
    if confirmation != 'YES':
        print("\n❌ Aborted by user")
        return
    
    # Delete products
    print(f"\n🗑️  Deleting {count} products...")
    
    for product in bulk_products:
        db.delete(product)
    
    db.commit()
    
    print(f"\n✅ Successfully deleted {count} bulk-seeded products!")
    
    # Count remaining products
    remaining = db.query(Product).count()
    print(f"📊 Remaining products in database: {remaining}")


def main():
    """Main cleanup function"""
    print("=" * 60)
    print("🧹 CLEAN UP BULK-SEEDED PRODUCTS")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        clean_bulk_products(db)
        print("\n" + "=" * 60)
        print("🎉 CLEANUP COMPLETED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error cleaning database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
