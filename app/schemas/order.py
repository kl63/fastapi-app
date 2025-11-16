from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enum"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderItemBase(BaseModel):
    """Base order item schema"""
    product_id: str
    quantity: int
    unit_price: float  # Matches database column
    product_name: str
    product_sku: str


class OrderItemCreate(OrderItemBase):
    """Schema for creating order item"""
    pass


class OrderItemInDBBase(OrderItemBase):
    """Base order item schema for DB"""
    id: str
    order_id: str
    total_price: float
    product_image: Optional[str] = None
    product_weight: Optional[str] = None
    product_unit: Optional[str] = None

    class Config:
        from_attributes = True


class OrderItem(OrderItemInDBBase):
    """Order item response schema"""
    # Exclude relationships to avoid serialization issues
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base order schema"""
    shipping_address_id: Optional[str] = None
    billing_address_id: Optional[str] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Schema for creating order"""
    pass


class OrderInDBBase(OrderBase):
    """Base order schema for DB"""
    id: str
    user_id: str
    order_number: str
    status: OrderStatus
    subtotal: float
    tax_amount: float
    delivery_fee: float  # Matches database column
    discount_amount: float
    total_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Order(OrderInDBBase):
    """Order response schema"""
    items: List[OrderItem] = []
    # Exclude relationships to avoid serialization issues
    class Config:
        from_attributes = True


class OrderInDB(OrderInDBBase):
    """Order schema for DB operations"""
    pass


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: OrderStatus
    notes: Optional[str] = None
