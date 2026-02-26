"""
Fix product thumbnail URLs - replace webpage URLs with actual image URLs
and fix broken Unsplash links

Usage: python scripts/fix_product_images.py
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.product import Product


# Product-specific Unsplash image URLs (high quality, reliable)
PRODUCT_IMAGES = {
    # Fruits
    "Apple": "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&h=400&fit=crop&auto=format",
    "Banana": "https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=400&h=400&fit=crop&auto=format",
    "Orange": "https://images.unsplash.com/photo-1580052614034-c55d20bfee3b?w=400&h=400&fit=crop&auto=format",
    "Grape": "https://images.unsplash.com/photo-1599819177950-30f6505535e0?w=400&h=400&fit=crop&auto=format",
    "Strawberry": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400&h=400&fit=crop&auto=format",
    "Blueberry": "https://images.unsplash.com/photo-1498557850523-fd3d118b962e?w=400&h=400&fit=crop&auto=format",
    "Mango": "https://images.unsplash.com/photo-1553279791-38f4b3f6094f?w=400&h=400&fit=crop&auto=format",
    "Watermelon": "https://images.unsplash.com/photo-1589984662646-e7b2e4962f18?w=400&h=400&fit=crop&auto=format",
    "Pineapple": "https://images.unsplash.com/photo-1550258987-190a2d41a8ba?w=400&h=400&fit=crop&auto=format",
    "Avocado": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=400&h=400&fit=crop&auto=format",
    # Vegetables
    "Carrot": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=400&h=400&fit=crop&auto=format",
    "Broccoli": "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?w=400&h=400&fit=crop&auto=format",
    "Tomato": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400&h=400&fit=crop&auto=format",  # Fixed - old one was 404
    "Lettuce": "https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?w=400&h=400&fit=crop&auto=format",
    "Spinach": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400&h=400&fit=crop&auto=format",
    "Potato": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&h=400&fit=crop&auto=format",
    "Onion": "https://images.unsplash.com/photo-1587049352846-4a222e784098?w=400&h=400&fit=crop&auto=format",
    "Pepper": "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?w=400&h=400&fit=crop&auto=format",
    # Dairy
    "Milk": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=400&fit=crop&auto=format",
    "Cheese": "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=400&h=400&fit=crop&auto=format",
    "Yogurt": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400&h=400&fit=crop&auto=format",
    "Butter": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=400&h=400&fit=crop&auto=format",
    "Eggs": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400&h=400&fit=crop&auto=format",
    "Cream": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&h=400&fit=crop&auto=format",
    # Meat & Seafood
    "Chicken": "https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=400&h=400&fit=crop&auto=format",
    "Beef": "https://images.unsplash.com/photo-1603048297172-c92544798d5a?w=400&h=400&fit=crop&auto=format",
    "Pork": "https://images.unsplash.com/photo-1602470520998-f4a52199a3d6?w=400&h=400&fit=crop&auto=format",
    "Salmon": "https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6?w=400&h=400&fit=crop&auto=format",
    "Shrimp": "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=400&h=400&fit=crop&auto=format",
    "Turkey": "https://images.unsplash.com/photo-1626645738196-c2a7c87a8f58?w=400&h=400&fit=crop&auto=format",
    "Tuna": "https://images.unsplash.com/photo-1580526331485-9662cd36b4f9?w=400&h=400&fit=crop&auto=format",
    "Cod": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=400&h=400&fit=crop&auto=format",
    # Bakery
    "Bread": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=400&fit=crop&auto=format",
    "Bagel": "https://images.unsplash.com/photo-1551106652-a5bcf4b29f60?w=400&h=400&fit=crop&auto=format",  # Fixed - old one was 404
    "Croissant": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=400&h=400&fit=crop&auto=format",
    "Muffin": "https://images.unsplash.com/photo-1607958996333-41aef7caefaa?w=400&h=400&fit=crop&auto=format",
    "Cookie": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400&h=400&fit=crop&auto=format",
    "Donut": "https://images.unsplash.com/photo-1551024601-bec78aea704b?w=400&h=400&fit=crop&auto=format",
    # Beverages
    "Juice": "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&h=400&fit=crop&auto=format",
    "Coffee": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&h=400&fit=crop&auto=format",
    "Tea": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?w=400&h=400&fit=crop&auto=format",
    "Soda": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&h=400&fit=crop&auto=format",
    "Water": "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=400&h=400&fit=crop&auto=format",
    # Pantry
    "Pasta": "https://images.unsplash.com/photo-1551462147-37abc7f4ddb8?w=400&h=400&fit=crop&auto=format",
    "Rice": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&h=400&fit=crop&auto=format",
    "Cereal": "https://images.unsplash.com/photo-1596797882870-8c33deeac224?w=400&h=400&fit=crop&auto=format",
    "Oil": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400&h=400&fit=crop&auto=format",
    "Sauce": "https://images.unsplash.com/photo-1472476443507-c7a5948772fc?w=400&h=400&fit=crop&auto=format",
}


def get_product_image_url(product_name: str) -> str:
    """Get correct image URL for a product based on its name"""
    import re
    
    product_lower = product_name.lower()
    
    # Sort keys by length (longest first) to prioritize more specific matches
    sorted_keys = sorted(PRODUCT_IMAGES.keys(), key=len, reverse=True)
    
    # Try exact match first
    for key in sorted_keys:
        if key.lower() == product_lower:
            return PRODUCT_IMAGES[key]
    
    # Try word boundary match (e.g., "Cod" matches "Wild Cod" but not "Broccoli")
    for key in sorted_keys:
        # Match as whole word using word boundaries
        pattern = r'\b' + re.escape(key.lower()) + r'\b'
        if re.search(pattern, product_lower):
            return PRODUCT_IMAGES[key]
    
    # Try substring match as fallback (prioritize longer matches)
    for key in sorted_keys:
        if key.lower() in product_lower:
            return PRODUCT_IMAGES[key]
    
    # If no match, return a generic grocery image
    return "https://images.unsplash.com/photo-1534080564583-6be75777b70a?w=400&h=400&fit=crop&auto=format"


def fix_product_images(db: Session, force_all: bool = False):
    """Fix product thumbnail URLs
    
    Args:
        db: Database session
        force_all: If True, reassign ALL images based on product names (ignores current URLs)
    """
    
    print("\n🔍 Analyzing product thumbnails...")
    if force_all:
        print("⚠️  FORCE MODE: Will reassign ALL product images based on names")
    
    # Get all products
    products = db.query(Product).all()
    total_products = len(products)
    
    print(f"📊 Found {total_products} products to check")
    
    issues_found = 0
    fixed_count = 0
    
    for product in products:
        needs_fix = False
        reason = ""
        
        if force_all:
            # Force reassign all images
            needs_fix = True
            reason = "Force reassignment based on product name"
        else:
            # Check if thumbnail is None or empty
            if not product.thumbnail or product.thumbnail.strip() == "":
                needs_fix = True
                reason = "Empty/None thumbnail"
            
            # Check for webpage URLs (unsplash.com/photos/)
            elif "unsplash.com/photos/" in product.thumbnail:
                needs_fix = True
                reason = "Webpage URL instead of image URL"
            
            # Check for missing query parameters
            elif product.thumbnail.startswith("https://images.unsplash.com/photo-") and "?" not in product.thumbnail:
                needs_fix = True
                reason = "Missing URL parameters"
            
            # Check for known 404 URLs
            elif "photo-1546470427-1d9fcc4a1a2a" in product.thumbnail or \
                 "photo-1551106652-a5bcf4b1a60" in product.thumbnail:
                needs_fix = True
                reason = "Known 404 image"
        
        if needs_fix:
            issues_found += 1
            old_url = product.thumbnail
            new_url = get_product_image_url(product.name)
            
            if issues_found <= 10 or force_all:  # Show first 10 or all in force mode
                print(f"\n{'🔄' if force_all else '❌'} #{issues_found}: {product.name}")
                print(f"   Reason: {reason}")
                if old_url and old_url != new_url:
                    print(f"   Old: {old_url[:80]}...")
                print(f"   New: {new_url[:80]}...")
            
            product.thumbnail = new_url
            fixed_count += 1
    
    if fixed_count > 0:
        print(f"\n{'='*60}")
        print(f"⚠️  Found {issues_found} products {'to reassign' if force_all else 'with image issues'}")
        print(f"✅ Ready to {'reassign' if force_all else 'fix'} {fixed_count} products")
        print(f"{'='*60}")
        
        confirmation = input(f"\n⚠️  Update {fixed_count} product images? Type 'YES' to confirm: ")
        
        if confirmation != 'YES':
            print("\n❌ Aborted by user")
            db.rollback()
            return
        
        # Commit changes
        db.commit()
        print(f"\n✅ Successfully updated {fixed_count} product images!")
    else:
        print(f"\n✅ All {total_products} products have valid image URLs!")
    
    # Show summary
    print(f"\n📊 Summary:")
    print(f"   Total products: {total_products}")
    print(f"   Issues found: {issues_found}")
    print(f"   Fixed: {fixed_count}")


def main():
    """Main function"""
    print("=" * 60)
    print("🖼️  FIX PRODUCT THUMBNAIL URLS")
    print("=" * 60)
    
    # Check for force mode argument
    force_all = len(sys.argv) > 1 and sys.argv[1] == '--force'
    
    db = SessionLocal()
    
    try:
        fix_product_images(db, force_all=force_all)
        print("\n" + "=" * 60)
        print("🎉 IMAGE FIX COMPLETED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error fixing images: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
