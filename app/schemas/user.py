from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime, date


class UserBase(BaseModel):
    """Base user schema with common attributes"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_active: bool = True
    is_admin: bool = False
    is_verified: bool = False


class UserRegister(BaseModel):
    """Schema for user registration (from API docs)"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserCreate(UserBase):
    """Schema for user creation (internal)"""
    username: str
    password: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'Username must be alphanumeric'
        return v


class UserProfileUpdate(BaseModel):
    """Schema for user profile updates (from API docs)"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None


class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str


class ForgotPassword(BaseModel):
    """Schema for forgot password request"""
    email: EmailStr


class ResetPassword(BaseModel):
    """Schema for password reset"""
    token: str
    new_password: str


class UserUpdate(UserBase):
    """Schema for user updates (internal)"""
    username: Optional[str] = None
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """Base schema for users in DB"""
    id: str
    username: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """Schema for user responses (without password)"""
    pass


class UserProfile(User):
    """Schema for user profile responses"""
    pass


class UserInDB(UserInDBBase):
    """Schema for user in DB (with hashed_password)"""
    hashed_password: str
