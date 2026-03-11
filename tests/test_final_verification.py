#!/usr/bin/env python3
"""
Final Verification: Order Creation Without Shipping Address
"""
import requests
import uuid
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.cart import CartItem
from app.models.product import Product
from app.core.security import get_password_hash

BASE_URL = "http://localhost:8000/api/v1"

print("\n" + "="*70)
print("🎯 FINAL VERIFICATION: Order Creation Without Shipping Address")
print("="*70 + "\n")

# Setup database
db = SessionLocal()

try:
    # Step 1: Create test user in database
    print("1️⃣  Creating test user...")
    user_id = str(uuid.uuid4())
    test_user = User(
        id=user_id,
        email=f"final_{uuid.uuid4().hex[:8]}@test.com",
        username=f"final{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("TestPass123!"),
        first_name="Final",
        last_name="Test",
        is_active=True,
        is_admin=False
    )
    db.add(test_user)
    db.commit()
    print(f"   ✅ User: {test_user.email}\n")
    
    # Step 2: Add items to cart
    print("2️⃣  Adding items to cart...")
    product = db.query(Product).first()
    cart_item = CartItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        product_id=product.id,
        quantity=3,
        price_at_time=product.price
    )
    db.add(cart_item)
    db.commit()
    print(f"   ✅ Cart: 3x {product.name} @ ${product.price}\n")
    
    # Step 3: Login to get token
    print("3️⃣  Getting authentication token...")
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={
            "username": test_user.email,
            "password": "TestPass123!"
        }
    )
    token = response.json()["access_token"]
    print(f"   ✅ Token received\n")
    
    # Step 4: Create order WITHOUT shipping address
    print("4️⃣  Creating order WITHOUT shipping address...")
    print("   Request: POST /api/v1/orders/")
    print("   Body: { notes: 'Test order' }")
    print("   shipping_address_id: <NOT PROVIDED>\n")
    
    response = requests.post(
        f"{BASE_URL}/orders/",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "notes": "Final verification test"
        }
    )
    
    print(f"   Response Status: {response.status_code}\n")
    
    if response.status_code == 200:
        order = response.json()
        
        print("   " + "🎉"*23)
        print("   " + " "*10 + "SUCCESS!")
        print("   " + "🎉"*23 + "\n")
        
        print("   📦 Order Details:")
        print(f"      Order ID: {order['id']}")
        print(f"      Order Number: {order['order_number']}")
        print(f"      Status: {order['status']}")
        print(f"      Shipping Address: {'None/null' if not order.get('shipping_address_id') else order['shipping_address_id']}")
        print(f"      \n      💰 Pricing:")
        print(f"      Subtotal: ${order['subtotal']:.2f}")
        print(f"      Tax: ${order['tax_amount']:.2f}")
        print(f"      Delivery Fee: ${order['delivery_fee']:.2f}")
        print(f"      Total: ${order['total_amount']:.2f}")
        print(f"      \n      📋 Items: {len(order['items'])}")
        for item in order['items']:
            print(f"         - {item['product_name']} (SKU: {item['product_sku']})")
            print(f"           {item['quantity']}x ${item['unit_price']} = ${item['total_price']}")
        
        print("\n" + "="*70)
        print("✅ BACKEND FIX VERIFIED SUCCESSFUL!")
        print("="*70)
        
        print("\n📝 Frontend Integration Ready:")
        print("   1. User adds items to cart ✅")
        print("   2. User clicks 'Checkout'")
        print("   3. POST /orders/ (no shipping_address_id) ✅ WORKING!")
        print("   4. Redirect to /checkout/:orderId")
        print("   5. User fills shipping form")
        print("   6. PUT /orders/:orderId (add shipping address)")
        print("   7. Process payment with Stripe")
        print("   8. Order confirmed!")
        
        print("\n🚀 Your backend is ready for checkout implementation!\n")
        
    else:
        print(f"   ❌ FAILED: {response.status_code}")
        print(f"   Response: {response.text}\n")
        
finally:
    db.close()
