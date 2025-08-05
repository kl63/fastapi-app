from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema"""
    name: str
    slug: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    sku: str
    category_id: str
    brand: Optional[str] = None
    unit: Optional[str] = None
    weight: Optional[str] = None
    dimensions: Optional[str] = None
    images: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    is_organic: bool = False
    is_featured: bool = False
    is_on_sale: bool = False
    is_active: bool = True
    in_stock: bool = True
    stock_quantity: int = 0
    low_stock_threshold: int = 10
    nutrition_facts: Optional[Dict[str, Any]] = None
    ingredients: Optional[str] = None
    allergens: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProductCreate(ProductBase):
    """Schema for product creation"""
    pass


class ProductUpdate(BaseModel):
    """Schema for product updates"""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    sku: Optional[str] = None
    category_id: Optional[str] = None
    brand: Optional[str] = None
    unit: Optional[str] = None
    weight: Optional[str] = None
    dimensions: Optional[str] = None
    images: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    is_organic: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_on_sale: Optional[bool] = None
    is_active: Optional[bool] = None
    in_stock: Optional[bool] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None
    nutrition_facts: Optional[Dict[str, Any]] = None
    ingredients: Optional[str] = None
    allergens: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class ProductStockUpdate(BaseModel):
    """Schema for stock updates"""
    stock_quantity: int
    in_stock: bool


class ProductInDBBase(ProductBase):
    """Base product schema for DB"""
    id: str
    cost_price: Optional[float] = None
    view_count: int = 0
    purchase_count: int = 0
    rating_average: float = 0.0
    rating_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Product(ProductInDBBase):
    """Product response schema"""
    is_low_stock: Optional[bool] = None
    discount_percentage: Optional[float] = None
    category: Optional[Dict[str, Any]] = None


class ProductSummary(BaseModel):
    """Product summary schema for lists"""
    id: str
    name: str
    slug: str
    price: float
    original_price: Optional[float] = None
    thumbnail: Optional[str] = None
    is_organic: bool = False
    is_on_sale: bool = False
    in_stock: bool = True
    rating_average: float = 0.0
    rating_count: int = 0
    discount_percentage: Optional[float] = None

    class Config:
        from_attributes = True


class ProductInDB(ProductInDBBase):
    """Product schema for DB operations"""
    pass
