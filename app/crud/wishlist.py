from typing import List, Optional
import uuid
from sqlalchemy.orm import Session

from app.models.wishlist import WishlistItem
from app.models.product import Product
from app.schemas.wishlist import WishlistItemCreate


def get_user_wishlist(db: Session, user_id: str) -> List[WishlistItem]:
    """Get all wishlist items for a user"""
    return db.query(WishlistItem).filter(WishlistItem.user_id == user_id).all()


def get_wishlist_item(db: Session, user_id: str, product_id: str) -> Optional[WishlistItem]:
    """Get specific wishlist item for user"""
    return db.query(WishlistItem).filter(
        WishlistItem.user_id == user_id,
        WishlistItem.product_id == product_id
    ).first()


def add_item_to_wishlist(db: Session, user_id: str, item_in: WishlistItemCreate) -> Optional[WishlistItem]:
    """Add item to wishlist"""
    # Check if product exists and is active
    product = db.query(Product).filter(Product.id == item_in.product_id).first()
    if not product or not product.is_active:
        return None
    
    # Check if item already exists in wishlist
    existing_item = get_wishlist_item(db, user_id, item_in.product_id)
    if existing_item:
        return None  # Item already in wishlist
    
    # Create new wishlist item
    wishlist_item_id = str(uuid.uuid4())
    db_wishlist_item = WishlistItem(
        id=wishlist_item_id,
        user_id=user_id,
        product_id=item_in.product_id
    )
    db.add(db_wishlist_item)
    db.commit()
    db.refresh(db_wishlist_item)
    return db_wishlist_item


def remove_item_from_wishlist(db: Session, user_id: str, product_id: str) -> bool:
    """Remove item from wishlist"""
    try:
        wishlist_item = get_wishlist_item(db, user_id, product_id)
        if not wishlist_item:
            return False
        
        db.delete(wishlist_item)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def clear_user_wishlist(db: Session, user_id: str) -> bool:
    """Clear all items from user's wishlist"""
    try:
        db.query(WishlistItem).filter(WishlistItem.user_id == user_id).delete()
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
