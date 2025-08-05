from sqlalchemy import Boolean, Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class Address(Base):
    """
    Address model for user shipping and billing addresses
    """
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    
    # Address type
    type = Column(String, nullable=False)  # "home", "work", "other"
    
    # Address details
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    street = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip_code = Column(String, nullable=False)
    country = Column(String, nullable=False, default="US")
    phone = Column(String, nullable=True)
    
    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="addresses")
    delivery_orders = relationship("Order", foreign_keys="Order.delivery_address_id", back_populates="delivery_address")
    billing_orders = relationship("Order", foreign_keys="Order.billing_address_id", back_populates="billing_address")
    
    @property
    def full_name(self):
        """Get full name for address"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def formatted_address(self):
        """Get formatted address string"""
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}, {self.country}"
