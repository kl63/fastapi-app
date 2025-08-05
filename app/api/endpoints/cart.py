from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.cart import (
    get_user_cart, add_item_to_cart, update_cart_item, 
    remove_cart_item, clear_user_cart, apply_discount_to_cart,
    remove_discount_from_cart
)
from app.models.user import User as DBUser
from app.schemas.cart import (
    Cart, CartItem, CartItemCreate, CartItemUpdate, DiscountCode
)

router = APIRouter()


@router.get("/", response_model=Cart)
def get_cart(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get user's shopping cart
    """
    cart = get_user_cart(db, user_id=current_user.id)
    return cart


@router.post("/items", response_model=CartItem)
def add_item_to_cart_endpoint(
    *,
    db: Session = Depends(get_db),
    item_in: CartItemCreate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Add item to cart
    """
    cart_item = add_item_to_cart(
        db, user_id=current_user.id, item_in=item_in
    )
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not add item to cart"
        )
    return cart_item


@router.put("/items/{item_id}", response_model=CartItem)
def update_cart_item_endpoint(
    *,
    db: Session = Depends(get_db),
    item_id: str,
    item_in: CartItemUpdate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Update cart item quantity
    """
    cart_item = update_cart_item(
        db, item_id=item_id, user_id=current_user.id, item_in=item_in
    )
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    return cart_item


@router.delete("/items/{item_id}")
def remove_cart_item_endpoint(
    *,
    db: Session = Depends(get_db),
    item_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Remove item from cart
    """
    success = remove_cart_item(
        db, item_id=item_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    return {"message": "Item removed from cart"}


@router.delete("/")
def clear_cart(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Clear all items from cart
    """
    success = clear_user_cart(db, user_id=current_user.id)
    return {"message": "Cart cleared successfully"}


@router.post("/discount")
def apply_discount_code(
    *,
    db: Session = Depends(get_db),
    discount_code: DiscountCode,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Apply discount code to cart
    """
    result = apply_discount_to_cart(
        db, user_id=current_user.id, code=discount_code.code
    )
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    return {"message": result["message"], "discount_amount": result["discount_amount"]}


@router.delete("/discount")
def remove_discount_code(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Remove discount code from cart
    """
    success = remove_discount_from_cart(db, user_id=current_user.id)
    return {"message": "Discount code removed"}
