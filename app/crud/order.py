from typing import Any, Dict, Optional, Union, List
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.order import Order, OrderItem, OrderStatusHistory
from app.models.cart import CartItem
from app.models.address import Address
from app.schemas.order import OrderCreate, OrderStatus
from app.crud.cart import get_user_cart_items, clear_user_cart


def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ORD-{timestamp}"


def get_order(db: Session, order_id: str) -> Optional[Order]:
    """Get order by ID"""
    return db.query(Order).filter(Order.id == order_id).first()


def get_user_orders(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[OrderStatus] = None
) -> List[Order]:
    """Get user's orders with optional status filter"""
    query = db.query(Order).filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def get_all_orders(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[OrderStatus] = None
) -> List[Order]:
    """Get all orders (admin only)"""
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def create_order(db: Session, user_id: str, order_in: OrderCreate) -> Optional[Order]:
    """Create new order from user's cart"""
    try:
        # Get user's cart items
        cart_items = get_user_cart_items(db, user_id)
        if not cart_items:
            return None
        
        # Validate addresses (optional - can be added later at checkout)
        shipping_address = None
        if order_in.shipping_address_id:
            shipping_address = db.query(Address).filter(
                Address.id == order_in.shipping_address_id,
                Address.user_id == user_id
            ).first()
            if not shipping_address:
                return None  # If ID provided but invalid, return error
        
        billing_address = None
        if order_in.billing_address_id:
            billing_address = db.query(Address).filter(
                Address.id == order_in.billing_address_id,
                Address.user_id == user_id
            ).first()
            if not billing_address:
                return None
        
        # Calculate totals
        subtotal = sum(item.total_price for item in cart_items)
        tax_amount = subtotal * 0.08  # 8% tax (configurable)
        shipping_cost = 5.99 if subtotal < 50 else 0  # Free shipping over $50
        discount_amount = 0.0  # TODO: Apply discount codes
        total_amount = subtotal + tax_amount + shipping_cost - discount_amount
        
        # Create order
        order_id = str(uuid.uuid4())
        order_number = generate_order_number()
        
        db_order = Order(
            id=order_id,
            user_id=user_id,
            order_number=order_number,
            status=OrderStatus.PENDING,
            delivery_address_id=order_in.shipping_address_id,  # Use delivery_address_id (actual column)
            billing_address_id=order_in.billing_address_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            delivery_fee=shipping_cost,  # Use delivery_fee (actual column)
            discount_amount=discount_amount,
            total_amount=total_amount,
            notes=order_in.notes,
        )
        db.add(db_order)
        db.flush()  # Get the order ID
        
        # Create order items from cart items
        for cart_item in cart_items:
            order_item_id = str(uuid.uuid4())
            # Get product details for snapshot
            product = cart_item.product
            
            db_order_item = OrderItem(
                id=order_item_id,
                order_id=order_id,
                product_id=cart_item.product_id,
                product_name=product.name if product else "Unknown Product",
                product_sku=product.sku if product else "N/A",
                quantity=cart_item.quantity,
                unit_price=cart_item.price_at_time,
                total_price=cart_item.price_at_time * cart_item.quantity,
                product_image=product.image_url if product and hasattr(product, 'image_url') else None,
                product_weight=product.weight if product and hasattr(product, 'weight') else None,
                product_unit=product.unit if product and hasattr(product, 'unit') else None,
            )
            db.add(db_order_item)
        
        # Create initial status history
        status_history_id = str(uuid.uuid4())
        db_status_history = OrderStatusHistory(
            id=status_history_id,
            order_id=order_id,
            status=OrderStatus.PENDING,
            notes="Order created",
        )
        db.add(db_status_history)
        
        # Clear user's cart
        clear_user_cart(db, user_id)
        
        db.commit()
        db.refresh(db_order)
        return db_order
        
    except Exception as e:
        db.rollback()
        return None


def update_order_status(
    db: Session, 
    order_id: str, 
    new_status: OrderStatus,
    notes: Optional[str] = None
) -> Optional[Order]:
    """Update order status"""
    try:
        order = get_order(db, order_id)
        if not order:
            return None
        
        # Update order status
        old_status = order.status
        order.status = new_status
        db.add(order)
        
        # Add status history
        status_history_id = str(uuid.uuid4())
        db_status_history = OrderStatusHistory(
            id=status_history_id,
            order_id=order_id,
            status=new_status,
            notes=notes or f"Status changed from {old_status} to {new_status}",
        )
        db.add(db_status_history)
        
        db.commit()
        db.refresh(order)
        return order
        
    except Exception:
        db.rollback()
        return None


def cancel_order(db: Session, order_id: str) -> bool:
    """Cancel order if possible"""
    try:
        order = get_order(db, order_id)
        if not order:
            return False
        
        # Check if order can be cancelled
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            return False
        
        # Update status to cancelled
        update_order_status(db, order_id, OrderStatus.CANCELLED, "Order cancelled by user")
        return True
        
    except Exception:
        db.rollback()
        return False
