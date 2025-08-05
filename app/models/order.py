from sqlalchemy import Boolean, Column, String, Integer, Float, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class Order(Base):
    """
    Order model for e-commerce orders
    """
    id = Column(String, primary_key=True, index=True)
    order_number = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    
    # Order status
    status = Column(String, nullable=False, default="pending")  # pending, confirmed, preparing, out_for_delivery, delivered, cancelled
    
    # Addresses
    delivery_address_id = Column(String, ForeignKey("address.id"), nullable=False)
    billing_address_id = Column(String, ForeignKey("address.id"), nullable=False)
    
    # Pricing
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Delivery details
    delivery_date = Column(DateTime, nullable=True)
    delivery_time_slot = Column(String, nullable=True)  # "10:00-12:00"
    special_instructions = Column(Text, nullable=True)
    
    # Discount info
    discount_code = Column(String, nullable=True)
    discount_type = Column(String, nullable=True)  # "percentage", "fixed_amount"
    discount_value = Column(Float, nullable=True)
    
    # Order tracking
    tracking_number = Column(String, nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    actual_delivery = Column(DateTime, nullable=True)
    
    # Additional info
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    delivery_address = relationship("Address", foreign_keys=[delivery_address_id], back_populates="delivery_orders")
    billing_address = relationship("Address", foreign_keys=[billing_address_id], back_populates="billing_orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
    
    @property
    def item_count(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items)
    
    def __repr__(self):
        return f"<Order {self.order_number}>"


class OrderItem(Base):
    """
    Order item model for individual items in an order
    """
    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("order.id"), nullable=False)
    product_id = Column(String, ForeignKey("product.id"), nullable=False)
    
    # Item details at time of order
    product_name = Column(String, nullable=False)
    product_sku = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Product snapshot
    product_image = Column(String, nullable=True)
    product_weight = Column(String, nullable=True)
    product_unit = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem {self.product_name} x{self.quantity}>"


class OrderStatusHistory(Base):
    """
    Order status history for tracking order progress
    """
    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("order.id"), nullable=False)
    
    # Status change details
    status = Column(String, nullable=False)
    notes = Column(Text, nullable=True)
    changed_by = Column(String, nullable=True)  # User ID or system
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="status_history")
    
    def __repr__(self):
        return f"<OrderStatusHistory {self.order.order_number} - {self.status}>"
