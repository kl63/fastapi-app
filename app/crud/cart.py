from typing import Any, Dict, Optional, Union, List
import uuid
from sqlalchemy.orm import Session

from app.models.cart import CartItem
from app.models.product import Product
from app.models.coupon import Coupon
from app.schemas.cart import CartItemCreate, CartItemUpdate, Cart


def get_user_cart_items(db: Session, user_id: str) -> List[CartItem]:
    """Get all cart items for a user"""
    return db.query(CartItem).filter(CartItem.user_id == user_id).all()


def get_user_cart(db: Session, user_id: str) -> Cart:
    """Get user's complete cart with calculations"""
    cart_items = get_user_cart_items(db, user_id)
    
    # Calculate totals
    total_items = sum(item.quantity for item in cart_items)
    subtotal = sum(item.total_price for item in cart_items)
    
    # TODO: Apply any active discount codes
    discount_amount = 0.0
    discount_code = None
    
    total = subtotal - discount_amount
    
    return Cart(
        items=cart_items,
        total_items=total_items,
        subtotal=subtotal,
        discount_amount=discount_amount,
        discount_code=discount_code,
        total=total
    )


def get_cart_item(db: Session, item_id: str, user_id: str) -> Optional[CartItem]:
    """Get specific cart item for user"""
    return db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == user_id
    ).first()


def get_cart_item_by_product(db: Session, user_id: str, product_id: str) -> Optional[CartItem]:
    """Get cart item by product for user"""
    return db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == product_id
    ).first()


def add_item_to_cart(db: Session, user_id: str, item_in: CartItemCreate) -> Optional[CartItem]:
    """Add item to cart or update quantity if exists"""
    # Get product to check availability and price
    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product or not product.is_active or not product.in_stock:
        return None
    
    # Check if item already exists in cart
    existing_item = get_cart_item_by_product(db, user_id, item_in.product_id)
    
    if existing_item:
        # Update quantity
        existing_item.quantity += item_in.quantity
        db.add(existing_item)
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Create new cart item
        cart_item_id = str(uuid.uuid4())
        db_cart_item = CartItem(
            id=cart_item_id,
            user_id=user_id,
            product_id=item_in.product_id,
            quantity=item_in.quantity,
            price_at_time=product.price
        )
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item


def update_cart_item(
    db: Session, 
    item_id: str, 
    user_id: str, 
    item_in: CartItemUpdate
) -> Optional[CartItem]:
    """Update cart item quantity"""
    cart_item = get_cart_item(db, item_id, user_id)
    if not cart_item:
        return None
    
    if item_in.quantity <= 0:
        # Remove item if quantity is 0 or negative
        db.delete(cart_item)
        db.commit()
        return None
    
    cart_item.quantity = item_in.quantity
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_cart_item(db: Session, item_id: str, user_id: str) -> bool:
    """Remove item from cart"""
    try:
        cart_item = get_cart_item(db, item_id, user_id)
        if not cart_item:
            return False
        
        db.delete(cart_item)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def clear_user_cart(db: Session, user_id: str) -> bool:
    """Clear all items from user's cart"""
    try:
        db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def apply_discount_to_cart(db: Session, user_id: str, code: str) -> Dict[str, Any]:
    """Apply discount code to cart"""
    # Get coupon
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    if not coupon:
        return {"success": False, "message": "Invalid discount code"}
    
    # Get cart total
    cart = get_user_cart(db, user_id)
    
    # Validate coupon
    is_valid, message = coupon.is_valid(user_id=user_id, cart_total=cart.subtotal)
    if not is_valid:
        return {"success": False, "message": message}
    
    # Calculate discount
    discount_amount = coupon.calculate_discount(cart.subtotal)
    
    # TODO: Store discount code application in session or database
    # For now, just return the discount amount
    
    return {
        "success": True, 
        "message": "Discount code applied successfully",
        "discount_amount": discount_amount
    }


def remove_discount_from_cart(db: Session, user_id: str) -> bool:
    """Remove discount code from cart"""
    # TODO: Remove stored discount code from session or database
    return True
