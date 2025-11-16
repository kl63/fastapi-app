from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class CartItemBase(BaseModel):
    """Base cart item schema"""
    product_id: str
    quantity: int


class CartItemCreate(CartItemBase):
    """Schema for adding item to cart"""
    pass


class CartItemUpdate(BaseModel):
    """Schema for updating cart item"""
    quantity: int


class CartItemInDBBase(CartItemBase):
    """Base cart item schema for DB"""
    id: str
    user_id: str
    price_at_time: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartItem(CartItemInDBBase):
    """Cart item response schema"""
    total_price: Optional[float] = None
    # Exclude product relationship to avoid serialization issues
    
    class Config:
        from_attributes = True


class CartItemInDB(CartItemInDBBase):
    """Cart item schema for DB operations"""
    pass


class Cart(BaseModel):
    """Shopping cart schema"""
    items: List[CartItem] = []
    total_items: int = 0
    subtotal: float = 0.0
    discount_amount: float = 0.0
    discount_code: Optional[str] = None
    total: float = 0.0

    class Config:
        from_attributes = True


class DiscountCode(BaseModel):
    """Schema for applying discount code"""
    code: str
