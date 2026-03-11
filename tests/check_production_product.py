#!/usr/bin/env python3
"""Check production product"""
import sys
sys.path.insert(0, '/var/www/fastapi-app')

from app.db.session import SessionLocal
from app.models.product import Product

db = SessionLocal()

product_id = "b1acdd8d-ab77-4a40-90b8-6aab6f5b6137"
product = db.query(Product).filter(Product.id == product_id).first()

if product:
    print(f"✅ Found product: {product.name}")
    print(f"   ID: {product.id}")
    print(f"   Price: ${product.price}")
    print(f"   Is Active: {product.is_active}")
    print(f"   In Stock: {product.in_stock}")
    print(f"   Stock Quantity: {product.stock_quantity}")
else:
    print(f"❌ Product {product_id} NOT FOUND!")
    print("\nAvailable products:")
    products = db.query(Product).limit(5).all()
    for p in products:
        print(f"   - {p.name} ({p.id})")

db.close()
