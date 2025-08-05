from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class WishlistItemBase(BaseModel):
    """Base wishlist item schema"""
    product_id: str


class WishlistItemCreate(WishlistItemBase):
    """Schema for adding item to wishlist"""
    pass


class WishlistItemInDBBase(WishlistItemBase):
    """Base wishlist item schema for DB"""
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class WishlistItem(WishlistItemInDBBase):
    """Wishlist item response schema"""
    product: Optional[Dict[str, Any]] = None


class WishlistItemInDB(WishlistItemInDBBase):
    """Wishlist item schema for DB operations"""
    pass
