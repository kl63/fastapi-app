from typing import Optional, Dict, Any
from pydantic import BaseModel, validator
from datetime import datetime


class ReviewBase(BaseModel):
    """Base review schema"""
    product_id: str
    rating: int
    title: Optional[str] = None
    comment: Optional[str] = None

    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v


class ReviewCreate(ReviewBase):
    """Schema for creating review"""
    pass


class ReviewUpdate(BaseModel):
    """Schema for updating review"""
    rating: Optional[int] = None
    title: Optional[str] = None
    comment: Optional[str] = None

    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v


class ReviewInDBBase(ReviewBase):
    """Base review schema for DB"""
    id: str
    user_id: str
    is_verified: bool
    helpful_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Review(ReviewInDBBase):
    """Review response schema"""
    user: Optional[Dict[str, Any]] = None
    product: Optional[Dict[str, Any]] = None


class ReviewInDB(ReviewInDBBase):
    """Review schema for DB operations"""
    pass
