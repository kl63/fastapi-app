from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str
    slug: str
    description: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    parent_id: Optional[str] = None
    is_active: bool = True
    is_featured: bool = False
    sort_order: int = 0
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for category creation"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for category updates"""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    parent_id: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class CategoryInDBBase(CategoryBase):
    """Base category schema for DB"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Category(CategoryInDBBase):
    """Category response schema"""
    children: Optional[List['Category']] = None
    product_count: Optional[int] = None


class CategoryInDB(CategoryInDBBase):
    """Category schema for DB operations"""
    pass


# Update forward references
Category.model_rebuild()
