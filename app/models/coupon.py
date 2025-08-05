from sqlalchemy import Boolean, Column, String, Integer, Float, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class Coupon(Base):
    """
    Coupon model for discount codes and promotions
    """
    id = Column(String, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    
    # Coupon details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False)  # "percentage", "fixed_amount", "free_shipping"
    value = Column(Float, nullable=False)  # Percentage or fixed amount
    
    # Usage limits
    usage_limit = Column(Integer, nullable=True)  # Total usage limit
    user_usage_limit = Column(Integer, default=1)  # Per user usage limit
    current_usage = Column(Integer, default=0)
    
    # Conditions
    minimum_order_amount = Column(Float, nullable=True)
    maximum_discount_amount = Column(Float, nullable=True)
    applicable_categories = Column(JSON, nullable=True)  # Array of category IDs
    applicable_products = Column(JSON, nullable=True)  # Array of product IDs
    
    # Validity
    valid_from = Column(DateTime, nullable=False)
    valid_until = Column(DateTime, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Public or private coupon
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_valid(self, user_id=None, cart_total=0.0):
        """Check if coupon is valid for use"""
        now = datetime.utcnow()
        
        # Check if active
        if not self.is_active:
            return False, "Coupon is not active"
        
        # Check date validity
        if now < self.valid_from:
            return False, "Coupon is not yet valid"
        
        if now > self.valid_until:
            return False, "Coupon has expired"
        
        # Check usage limit
        if self.usage_limit and self.current_usage >= self.usage_limit:
            return False, "Coupon usage limit reached"
        
        # Check minimum order amount
        if self.minimum_order_amount and cart_total < self.minimum_order_amount:
            return False, f"Minimum order amount of ${self.minimum_order_amount} required"
        
        return True, "Coupon is valid"
    
    def calculate_discount(self, cart_total):
        """Calculate discount amount for given cart total"""
        if self.type == "percentage":
            discount = (cart_total * self.value) / 100
            if self.maximum_discount_amount:
                discount = min(discount, self.maximum_discount_amount)
            return discount
        elif self.type == "fixed_amount":
            return min(self.value, cart_total)
        elif self.type == "free_shipping":
            return 0  # Shipping discount handled separately
        
        return 0
    
    def __repr__(self):
        return f"<Coupon {self.code} - {self.type} {self.value}>"
