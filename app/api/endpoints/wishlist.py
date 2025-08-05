from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.wishlist import (
    get_user_wishlist, add_item_to_wishlist, 
    remove_item_from_wishlist, clear_user_wishlist
)
from app.models.user import User as DBUser
from app.schemas.wishlist import WishlistItem, WishlistItemCreate

router = APIRouter()


@router.get("/", response_model=List[WishlistItem])
def get_wishlist(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get user's wishlist
    """
    wishlist = get_user_wishlist(db, user_id=current_user.id)
    return wishlist


@router.post("/items", response_model=WishlistItem)
def add_item_to_wishlist_endpoint(
    *,
    db: Session = Depends(get_db),
    item_in: WishlistItemCreate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Add item to wishlist
    """
    wishlist_item = add_item_to_wishlist(
        db, user_id=current_user.id, item_in=item_in
    )
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not add item to wishlist or item already exists"
        )
    return wishlist_item


@router.delete("/items/{product_id}")
def remove_item_from_wishlist_endpoint(
    *,
    db: Session = Depends(get_db),
    product_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Remove item from wishlist
    """
    success = remove_item_from_wishlist(
        db, user_id=current_user.id, product_id=product_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )
    return {"message": "Item removed from wishlist"}


@router.delete("/")
def clear_wishlist(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Clear all items from wishlist
    """
    success = clear_user_wishlist(db, user_id=current_user.id)
    return {"message": "Wishlist cleared successfully"}
