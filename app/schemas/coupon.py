from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime
from enum import Enum


class DiscountType(str, Enum):
    """Discount type enum"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


class CouponBase(BaseModel):
    """Base coupon schema"""
    code: str
    name: str
    description: Optional[str] = None
    discount_type: DiscountType
    discount_value: float
    minimum_order_amount: Optional[float] = None
    maximum_discount_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    usage_limit_per_user: Optional[int] = None
    valid_from: datetime
    valid_until: datetime
    is_active: bool = True

    @validator('discount_value')
    def validate_discount_value(cls, v, values):
        if v <= 0:
            raise ValueError('Discount value must be positive')
        
        discount_type = values.get('discount_type')
        if discount_type == DiscountType.PERCENTAGE and v > 100:
            raise ValueError('Percentage discount cannot exceed 100%')
        
        return v


class CouponCreate(CouponBase):
    """Schema for creating coupon"""
    pass


class CouponUpdate(BaseModel):
    """Schema for updating coupon"""
    name: Optional[str] = None
    description: Optional[str] = None
    discount_type: Optional[DiscountType] = None
    discount_value: Optional[float] = None
    minimum_order_amount: Optional[float] = None
    maximum_discount_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    usage_limit_per_user: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None

    @validator('discount_value')
    def validate_discount_value(cls, v, values):
        if v is not None and v <= 0:
            raise ValueError('Discount value must be positive')
        
        discount_type = values.get('discount_type')
        if v is not None and discount_type == DiscountType.PERCENTAGE and v > 100:
            raise ValueError('Percentage discount cannot exceed 100%')
        
        return v


class CouponInDBBase(CouponBase):
    """Base coupon schema for DB"""
    id: str
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Coupon(CouponInDBBase):
    """Coupon response schema"""
    pass


class CouponInDB(CouponInDBBase):
    """Coupon schema for DB operations"""
    pass


class CouponValidation(BaseModel):
    """Schema for validating coupon code"""
    code: str
    cart_total: float
