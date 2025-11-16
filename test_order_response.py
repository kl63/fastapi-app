#!/usr/bin/env python3
"""
Test order creation and manually serialize the response to find the issue
"""
import uuid
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.cart import CartItem
from app.models.product import Product
from app.core.security import get_password_hash
from app.crud.order import create_order
from app.schemas.order import OrderCreate, Order as OrderSchema

db = SessionLocal()

print("🔍 Testing Order Response Serialization...\n")

try:
    # Create test user
    user_id = str(uuid.uuid4())
    test_user = User(
        id=user_id,
        email=f"resptest_{uuid.uuid4().hex[:8]}@test.com",
        username=f"resptest{uuid.uuid4().hex[:8]}",
        hashed_password=get_password_hash("TestPass123!"),
        first_name="Response",
        last_name="Test",
        is_active=True,
        is_admin=False
    )
    db.add(test_user)
    db.commit()
    print(f"✅ User created\n")
    
    # Get product
    product = db.query(Product).first()
    
    # Add cart item
    cart_item = CartItem(
        id=str(uuid.uuid4()),
        user_id=user_id,
        product_id=product.id,
        quantity=1,
        price_at_time=product.price
    )
    db.add(cart_item)
    db.commit()
    print(f"✅ Cart item added\n")
    
    # Create order
    order_in = OrderCreate()
    order = create_order(db, user_id=user_id, order_in=order_in)
    
    if order:
        print(f"✅ Order created in DB: {order.id}\n")
        
        # Try to serialize it
        print("🔍 Attempting to serialize order to Pydantic schema...")
        
        try:
            # Check each field individually
            print(f"  - id: {order.id}")
            print(f"  - order_number: {order.order_number}")
            print(f"  - user_id: {order.user_id}")
            print(f"  - status: {order.status}")
            print(f"  - delivery_address_id: {order.delivery_address_id}")
            print(f"  - billing_address_id: {order.billing_address_id}")
            print(f"  - subtotal: {order.subtotal}")
            print(f"  - tax_amount: {order.tax_amount}")
            print(f"  - delivery_fee: {order.delivery_fee}")
            print(f"  - discount_amount: {order.discount_amount}")
            print(f"  - total_amount: {order.total_amount}")
            print(f"  - created_at: {order.created_at}")
            print(f"  - updated_at: {order.updated_at}")
            print(f"  - items count: {len(order.items)}")
            
            # Check items
            print("\n🔍 Checking order items...")
            for item in order.items:
                print(f"  Item: {item.product_name}")
                print(f"    - id: {item.id}")
                print(f"    - product_id: {item.product_id}")
                print(f"    - quantity: {item.quantity}")
                print(f"    - unit_price: {item.unit_price}")
                print(f"    - total_price: {item.total_price}")
            
            # Now try Pydantic serialization
            print("\n🔍 Converting to Pydantic schema...")
            order_schema = OrderSchema.from_orm(order)
            print("✅ Pydantic conversion successful!")
            print(f"\nOrder schema dict:")
            print(order_schema.dict())
            
        except Exception as e:
            print(f"\n❌ Serialization error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Order creation failed")
        
finally:
    db.close()
