#!/usr/bin/env python3
"""
Test payment intent endpoint
"""
import requests
import uuid
from app.db.session import SessionLocal
from app.models.user import User
from app.models.cart import CartItem
from app.models.product import Product
from app.core.security import get_password_hash
from app.crud.order import create_order
from app.schemas.order import OrderCreate

BASE_URL = "http://localhost:8000/api/v1"

print("\n" + "="*70)
print("💳 Testing Payment Intent Endpoint")
print("="*70 + "\n")

db = SessionLocal()

try:
    # Create test user
    print("1️⃣  Creating test user...")
    user_id = str(uuid.uuid4())
    test_user = User(
        id=user_id,
        email=f"payment_{uuid.uuid4().hex[:8]}@test.com",
        username=f"payment{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("TestPass123!"),
        first_name="Payment",
        last_name="Test",
        is_active=True,
        is_admin=False
    )
    db.add(test_user)
    db.commit()
    print(f"   ✅ User created\n")
    
    # Add cart item
    print("2️⃣  Adding item to cart...")
    product = db.query(Product).first()
    cart_item = CartItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        product_id=product.id,
        quantity=1,
        price_at_time=product.price
    )
    db.add(cart_item)
    db.commit()
    print(f"   ✅ Cart item added\n")
    
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
    
    # Create order
    print("4️⃣  Creating order...")
    order_in = OrderCreate()
    order = create_order(db, user_id=user_id, order_in=order_in)
    print(f"   ✅ Order created: {order.id}")
    print(f"   Total: ${order.total_amount}\n")
    
    # Test payment intent endpoint
    print("5️⃣  Creating payment intent...")
    print(f"   POST /orders/{order.id}/create-payment-intent\n")
    
    response = requests.post(
        f"{BASE_URL}/orders/{order.id}/create-payment-intent",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    print(f"   Response Status: {response.status_code}\n")
    
    if response.status_code == 200:
        payment_data = response.json()
        
        print("   " + "🎉"*23)
        print("   " + " "*8 + "SUCCESS!")
        print("   " + "🎉"*23 + "\n")
        
        print("   💳 Payment Intent Created:")
        print(f"      Client Secret: {payment_data['client_secret'][:20]}...")
        print(f"      Payment Intent ID: {payment_data['payment_intent_id']}")
        print(f"      Amount: ${payment_data['amount']}")
        print(f"      Currency: {payment_data['currency']}")
        
        print("\n" + "="*70)
        print("✅ PAYMENT INTENT ENDPOINT WORKING!")
        print("="*70)
        
        print("\n🎊 Your frontend will now work!")
        print("   Refresh the checkout page and you'll see the Stripe form! 🚀\n")
        
    else:
        print(f"   ❌ FAILED: {response.status_code}")
        print(f"   Response: {response.text}\n")
        
finally:
    db.close()
