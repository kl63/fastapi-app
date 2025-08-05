from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class CartItem(Base):
    """
    Cart item model for shopping cart functionality
    """
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    product_id = Column(String, ForeignKey("product.id"), nullable=False)
    
    # Item details
    quantity = Column(Integer, nullable=False, default=1)
    price_at_time = Column(Float, nullable=False)  # Price when added to cart
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")
    
    @property
    def total_price(self):
        """Calculate total price for this cart item"""
        return self.quantity * self.price_at_time
    
    def __repr__(self):
        return f"<CartItem {self.product.name} x{self.quantity}>"
