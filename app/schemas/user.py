from typing import Optional
from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_admin: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation"""
    email: EmailStr
    username: str
    password: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'Username must be alphanumeric'
        return v


class UserUpdate(UserBase):
    """Schema for user updates"""
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """Base schema for users in DB"""
    id: str

    class Config:
        orm_mode = True


class User(UserInDBBase):
    """Schema for user responses (without password)"""
    pass


class UserInDB(UserInDBBase):
    """Schema for user in DB (with hashed_password)"""
    hashed_password: str
