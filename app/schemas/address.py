from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class AddressBase(BaseModel):
    """Base address schema"""
    type: str  # "home", "work", "other"
    first_name: str
    last_name: str
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"
    phone: Optional[str] = None
    is_default: bool = False


class AddressCreate(AddressBase):
    """Schema for address creation"""
    pass


class AddressUpdate(BaseModel):
    """Schema for address updates"""
    type: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    is_default: Optional[bool] = None


class AddressInDBBase(AddressBase):
    """Base address schema for DB"""
    id: str
    user_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Address(AddressInDBBase):
    """Address response schema"""
    full_name: Optional[str] = None
    formatted_address: Optional[str] = None


class AddressInDB(AddressInDBBase):
    """Address schema for DB operations"""
    pass
