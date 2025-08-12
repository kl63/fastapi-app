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
    price: float


class OrderItemCreate(OrderItemBase):
    """Schema for creating order item"""
    pass


class OrderItemInDBBase(OrderItemBase):
    """Base order item schema for DB"""
    id: str
    order_id: str

    class Config:
        from_attributes = True


class OrderItem(OrderItemInDBBase):
    """Order item response schema"""
    total_price: Optional[float] = None
    product: Optional[Dict[str, Any]] = None


class OrderBase(BaseModel):
    """Base order schema"""
    shipping_address_id: str
    billing_address_id: Optional[str] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Schema for creating order"""
    payment_method_id: Optional[str] = None
    save_payment_method: bool = False


class OrderInDBBase(OrderBase):
    """Base order schema for DB"""
    id: str
    user_id: str
    order_number: str
    status: OrderStatus
    subtotal: float
    tax_amount: float
    shipping_cost: float
    discount_amount: float
    total_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Order(OrderInDBBase):
    """Order response schema"""
    items: List[OrderItem] = []
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    status_history: Optional[List[Dict[str, Any]]] = []
    payment_intent_id: Optional[str] = None
    payment_status: Optional[str] = None


class OrderInDB(OrderInDBBase):
    """Order schema for DB operations"""
    pass


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: OrderStatus
    notes: Optional[str] = None
