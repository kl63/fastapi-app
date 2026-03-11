#!/usr/bin/env python3
"""
Test cart endpoint with correct product ID
"""
import requests
import uuid
from app.db.session import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.core.security import get_password_hash

BASE_URL = "http://localhost:8000/api/v1"

print("\n" + "="*70)
print("🛒 Testing Cart Endpoint with Correct Product ID")
print("="*70 + "\n")

# Get database
db = SessionLocal()

try:
    # Create test user
    print("1️⃣  Creating test user...")
    user_id = str(uuid.uuid4())
    test_user = User(
        id=user_id,
        email=f"carttest_{uuid.uuid4().hex[:8]}@test.com",
        username=f"carttest{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("TestPass123!"),
        first_name="Cart",
        last_name="Test",
        is_active=True,
        is_admin=False
    )
    db.add(test_user)
    db.commit()
    print(f"   ✅ User created\n")
    
    # Get real product ID
    product = db.query(Product).first()
    product_id = product.id
    print(f"2️⃣  Using product from database:")
    print(f"   Product ID: {product_id}")
    print(f"   Name: {product.name}")
    print(f"   Price: ${product.price}\n")
    
    # Login
    print("3️⃣  Getting auth token...")
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={
            "username": test_user.email,
            "password": "TestPass123!"
        }
    )
    token = response.json()["access_token"]
    print(f"   ✅ Token received\n")
    
    # Add to cart with CORRECT product ID
    print("4️⃣  Adding item to cart...")
    print(f"   POST /api/v1/cart/items")
    print(f"   Body: {{")
    print(f"     product_id: '{product_id}',")
    print(f"     quantity: 2")
    print(f"   }}\n")
    
    response = requests.post(
        f"{BASE_URL}/cart/items",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "product_id": product_id,  # Using REAL UUID!
            "quantity": 2
        }
    )
    
    print(f"   Response Status: {response.status_code}\n")
    
    if response.status_code == 200:
        cart_item = response.json()
        
        print("   " + "🎉"*23)
        print("   " + " "*10 + "SUCCESS!")
        print("   " + "🎉"*23 + "\n")
        
        print("   📦 Cart Item:")
        print(f"      Item ID: {cart_item['id']}")
        print(f"      Product ID: {cart_item['product_id']}")
        print(f"      Quantity: {cart_item['quantity']}")
        print(f"      Price: ${cart_item['price_at_time']}")
        print(f"      Total: ${cart_item['total_price']}")
        
        print("\n" + "="*70)
        print("✅ CART ENDPOINT WORKING!")
        print("="*70)
        
        print("\n📝 Frontend Fix:")
        print("   Your frontend needs to use REAL product UUIDs:")
        print(f"   ❌ product_id: '2'  (doesn't exist)")
        print(f"   ✅ product_id: '{product_id}'")
        
        print("\n💡 Recommended Approach:")
        print("   1. Fetch products from /api/v1/products/")
        print("   2. Display products with real IDs")
        print("   3. Add to cart using product.id from API")
        
    else:
        print(f"   ❌ FAILED: {response.status_code}")
        print(f"   Response: {response.text}")
        
finally:
    db.close()
