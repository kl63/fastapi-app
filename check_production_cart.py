#!/usr/bin/env python3
"""Check production cart for user"""
import sys
sys.path.insert(0, '/var/www/fastapi-app')

from app.db.session import SessionLocal
from app.models.cart import CartItem
from app.models.user import User

db = SessionLocal()

# Find user by email
user = db.query(User).filter(User.email == "lin.kevin.1923@gmail.com").first()

if user:
    print(f"✅ Found user: {user.email} (ID: {user.id})")
    
    # Check cart items
    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    
    print(f"\n🛒 Cart has {len(cart_items)} items:\n")
    
    for item in cart_items:
        print(f"   - Product ID: {item.product_id}")
        print(f"     Quantity: {item.quantity}")
        print(f"     Price at time: ${item.price_at_time}")
        print()
else:
    print("❌ User not found")

db.close()
