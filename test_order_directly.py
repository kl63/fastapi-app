#!/usr/bin/env python3
"""
Test Order Creation by directly adding cart items to database
"""
import uuid
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.cart import CartItem
from app.models.product import Product
from app.core.security import get_password_hash

# Create test user and cart items directly in database
db = SessionLocal()

print("🛒 Testing Order Creation with Manual Cart Setup...\n")

try:
    # Step 1: Create test user
    print("1️⃣ Creating test user in database...")
    user_id = str(uuid.uuid4())
    test_user = User(
        id=user_id,
        email=f"dbtest_{uuid.uuid4().hex[:8]}@test.com",
        username=f"dbtest{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("TestPass123!"),
        first_name="DB",
        last_name="Test",
        is_active=True,
        is_admin=False
    )
    db.add(test_user)
    db.commit()
    print(f"✅ User created: {test_user.email}\n")
    
    # Step 2: Get a product
    print("2️⃣ Finding product...")
    product = db.query(Product).first()
    if not product:
        print("❌ No products in database. Please add products first.")
        exit(1)
    print(f"✅ Found product: {product.name} (${product.price})\n")
    
    # Step 3: Add cart items manually
    print("3️⃣ Adding items to user's cart in database...")
    cart_item = CartItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        product_id=product.id,
        quantity=2,
        price_at_time=product.price
    )
    db.add(cart_item)
    db.commit()
    print(f"✅ Cart item added: 2x {product.name}\n")
    
    # Step 4: Login to get token
    print("4️⃣ Getting auth token...")
    import requests
    
    response = requests.post(
        "http://localhost:8000/api/v1/auth/token",
        data={
            "username": test_user.email,
            "password": "TestPass123!"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        exit(1)
    
    token = response.json()["access_token"]
    print(f"✅ Got token\n")
    
    # Step 5: Create order WITHOUT shipping address
    print("5️⃣ Creating order WITHOUT shipping address...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/orders/",
        headers=headers,
        json={
            "notes": "Test order - no shipping address"
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        order = response.json()
        print(f"\n✅✅✅ SUCCESS! Order created WITHOUT shipping address! ✅✅✅")
        print(f"\n   Order ID: {order['id']}")
        print(f"   Order Number: {order['order_number']}")
        print(f"   Status: {order['status']}")
        print(f"   Shipping Address ID: {order.get('shipping_address_id', 'null')}")
        print(f"   Subtotal: ${order['subtotal']:.2f}")
        print(f"   Tax: ${order['tax_amount']:.2f}")
        print(f"   Shipping: ${order['shipping_cost']:.2f}")
        print(f"   Total: ${order['total_amount']:.2f}")
        
        print("\n" + "🎉"*35)
        print("   BACKEND FIX WORKING PERFECTLY!")
        print("🎉"*35)
        
        print("\n📝 Frontend Integration:")
        print("1. ✅ User adds items to cart via /cart/items")
        print("2. ✅ User clicks 'Checkout'")
        print("3. ✅ POST /orders/ with no shipping_address_id")
        print("4. ✅ Redirect to /checkout/:orderId page")
        print("5. → User fills shipping form")
        print("6. → PUT /orders/:orderId to add shipping address")
        print("7. → Process payment")
        print("8. → Success!")
        
    else:
        print(f"\n❌ Order creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        
finally:
    db.close()
