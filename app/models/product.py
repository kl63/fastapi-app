from sqlalchemy import Boolean, Column, String, Integer, Float, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class Product(Base):
    """
    Product model for e-commerce items
    """
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    short_description = Column(Text, nullable=True)
    
    # Pricing
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)  # For sale items
    cost_price = Column(Float, nullable=True)  # For profit calculation
    
    # Product details
    sku = Column(String, unique=True, nullable=False, index=True)
    category_id = Column(String, ForeignKey("category.id"), nullable=False)
    brand = Column(String, nullable=True)
    unit = Column(String, nullable=True)  # "per piece", "per kg", etc.
    weight = Column(String, nullable=True)
    dimensions = Column(String, nullable=True)
    
    # Images and media
    images = Column(JSON, nullable=True)  # Array of image URLs
    thumbnail = Column(String, nullable=True)  # Main product image
    
    # Product attributes
    is_organic = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_on_sale = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Inventory
    in_stock = Column(Boolean, default=True)
    stock_quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    
    # Nutrition and additional info
    nutrition_facts = Column(JSON, nullable=True)  # Nutrition information
    ingredients = Column(Text, nullable=True)
    allergens = Column(JSON, nullable=True)  # Array of allergens
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # SEO
    meta_title = Column(String, nullable=True)
    meta_description = Column(Text, nullable=True)
    
    # Statistics
    view_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    rating_average = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    wishlist_items = relationship("WishlistItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock"""
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if on sale"""
        if self.original_price and self.price < self.original_price:
            return round(((self.original_price - self.price) / self.original_price) * 100, 2)
        return 0
    
    def __repr__(self):
        return f"<Product {self.name}>"
