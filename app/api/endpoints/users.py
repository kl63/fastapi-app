from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_admin, get_db
from app.crud.user import get_user_by_id, get_users, update_user, update_user_password
from app.models.user import User as DBUser
from app.schemas.user import User, UserUpdate, UserProfile, UserProfileUpdate, PasswordChange
from app.core.security import verify_password

router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Retrieve users. Admin only.
    """
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.get("/profile", response_model=UserProfile)
def read_user_profile(
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get current user profile.
    """
    return current_user


@router.put("/profile", response_model=UserProfile)
def update_user_profile(
    *,
    db: Session = Depends(get_db),
    user_in: UserProfileUpdate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Update current user profile.
    """
    # Convert UserProfileUpdate to UserUpdate for internal use
    user_update = UserUpdate(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        phone=user_in.phone,
        date_of_birth=user_in.date_of_birth,
        email=current_user.email,  # Keep existing email
        username=current_user.username,  # Keep existing username
    )
    user = update_user(db, db_user=current_user, user_in=user_update)
    return user


@router.put("/password")
def change_password(
    *,
    db: Session = Depends(get_db),
    password_change: PasswordChange,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Change user password.
    """
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    success = update_user_password(db, user=current_user, new_password=password_change.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update password"
        )
    
    return {"message": "Password updated successfully"}


@router.get("/me", response_model=User)
def read_user_me(
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get current user (legacy endpoint).
    """
    return current_user


@router.patch("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Update current user (legacy endpoint).
    """
    user = update_user(db, db_user=current_user, user_in=user_in)
    return user


@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get a specific user by id.
    """
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Only admins can access other user profiles
    if user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return user


@router.patch("/{user_id}", response_model=User)
def update_user_by_id(
    *,
    db: Session = Depends(get_db),
    user_id: str,
    user_in: UserUpdate,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Update a user. Admin only.
    """
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = update_user(db, db_user=user, user_in=user_in)
    return user
