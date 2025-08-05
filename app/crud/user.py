from typing import Any, Dict, Optional, Union
import uuid
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get multiple users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_in: UserCreate) -> User:
    """Create new user"""
    # Check if user already exists
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        return None
    
    # Create user with hashed password
    user_id = str(uuid.uuid4())
    db_user = User(
        id=user_id,
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        first_name=getattr(user_in, 'first_name', None),
        last_name=getattr(user_in, 'last_name', None),
        phone=getattr(user_in, 'phone', None),
        date_of_birth=getattr(user_in, 'date_of_birth', None),
        is_active=user_in.is_active,
        is_admin=user_in.is_admin,
        is_verified=getattr(user_in, 'is_verified', False),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: User, user_in: Union[UserUpdate, Dict[str, Any]]) -> User:
    """Update user"""
    if isinstance(user_in, dict):
        update_data = user_in
    else:
        update_data = user_in.dict(exclude_unset=True)
        
    # Hash password if it's being updated
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
        
    # Update user attributes
    for field in update_data:
        if hasattr(db_user, field):
            setattr(db_user, field, update_data[field])
            
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user: User, new_password: str) -> bool:
    """Update user password"""
    try:
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return True
    except Exception:
        db.rollback()
        return False


def authenticate_user(db: Session, username: str = None, email: str = None, password: str = None) -> Optional[User]:
    """Authenticate user by username/email and password"""
    user = None
    
    # If email is provided, use email authentication
    if email:
        user = get_user_by_email(db, email=email)
    # Otherwise, try username first, then email
    elif username:
        user = get_user_by_username(db, username=username)
        # If not found, try by email (in case username is actually an email)
        if not user:
            user = get_user_by_email(db, email=username)
        
    # If no user found or password doesn't match
    if not user or not verify_password(password, user.hashed_password):
        return None
        
    return user
