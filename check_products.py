#!/usr/bin/env python3
"""
Check products in database and their status
"""
from app.db.session import SessionLocal
from app.models.product import Product

db = SessionLocal()

print("\n🔍 Checking Products in Database...\n")

products = db.query(Product).all()

if not products:
    print("❌ NO PRODUCTS FOUND IN DATABASE!")
    print("\nYou need to add products to your database first.")
    print("\nExample SQL:")
    print("""
    INSERT INTO product (id, name, sku, price, is_active, in_stock, category_id)
    VALUES 
      ('1', 'Test Product 1', 'TEST001', 9.99, true, true, null),
      ('2', 'Test Product 2', 'TEST002', 19.99, true, true, null);
    """)
else:
    print(f"Found {len(products)} products:\n")
    
    for product in products:
        status_icon = "✅" if (product.is_active and product.in_stock) else "❌"
        print(f"{status_icon} Product ID: {product.id}")
        print(f"   Name: {product.name}")
        print(f"   SKU: {product.sku}")
        print(f"   Price: ${product.price}")
        print(f"   Active: {product.is_active}")
        print(f"   In Stock: {product.in_stock}")
        print(f"   Can Add to Cart: {'YES ✅' if (product.is_active and product.in_stock) else 'NO ❌'}")
        print()
    
    # Show which products can be added to cart
    available = [p for p in products if p.is_active and p.in_stock]
    if available:
        print(f"\n✅ {len(available)} products CAN be added to cart:")
        for p in available:
            print(f"   - Product ID: '{p.id}' ({p.name})")
    else:
        print("\n❌ NO products can be added to cart!")
        print("All products are either inactive or out of stock.")
        print("\nFix: Update products to set is_active=true and in_stock=true")

db.close()
