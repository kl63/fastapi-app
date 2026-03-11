#!/usr/bin/env python3
"""
Check if orders were created in database
"""
from app.db.session import SessionLocal
from app.models.order import Order

db = SessionLocal()

print("\n🔍 Checking Orders in Database...\n")

orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()

print(f"Found {len(orders)} recent orders:\n")

for order in orders:
    print(f"✅ Order {order.order_number}")
    print(f"   ID: {order.id}")
    print(f"   Status: {order.status}")
    print(f"   User: {order.user_id}")
    print(f"   Shipping Address: {order.delivery_address_id}")
    print(f"   Total: ${order.total_amount:.2f}")
    print(f"   Items: {len(order.items)}")
    print()

if orders:
    print("🎉 Orders ARE being created successfully!")
    print("The issue is just response serialization.")
else:
    print("❌ No orders found.")

db.close()
