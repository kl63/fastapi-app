from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_admin, get_db
from app.crud.user import get_user_by_id, get_users, update_user
from app.models.user import User as DBUser
from app.schemas.user import User, UserUpdate

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


@router.get("/me", response_model=User)
def read_user_me(
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get current user profile.
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
    Update current user profile.
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
