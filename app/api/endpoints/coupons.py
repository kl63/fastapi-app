from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_active_admin
from app.crud.coupon import (
    get_coupon, get_coupons, create_coupon, update_coupon, 
    delete_coupon, validate_coupon_code
)
from app.models.user import User as DBUser
from app.schemas.coupon import Coupon, CouponCreate, CouponUpdate, CouponValidation

router = APIRouter()


@router.post("/validate")
def validate_coupon(
    *,
    db: Session = Depends(get_db),
    coupon_validation: CouponValidation,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Validate coupon code
    """
    result = validate_coupon_code(
        db, 
        code=coupon_validation.code, 
        user_id=current_user.id,
        cart_total=coupon_validation.cart_total
    )
    return result


# Admin endpoints
@router.get("/", response_model=List[Coupon])
def get_coupons_admin(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = None,
) -> Any:
    """
    Get all coupons (admin only)
    """
    coupons = get_coupons(db, skip=skip, limit=limit, is_active=is_active)
    return coupons


@router.post("/", response_model=Coupon)
def create_coupon_admin(
    *,
    db: Session = Depends(get_db),
    coupon_in: CouponCreate,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Create new coupon (admin only)
    """
    coupon = create_coupon(db, coupon_in=coupon_in)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create coupon. Code may already exist."
        )
    return coupon


@router.get("/{coupon_id}", response_model=Coupon)
def get_coupon_admin(
    *,
    db: Session = Depends(get_db),
    coupon_id: str,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Get coupon by ID (admin only)
    """
    coupon = get_coupon(db, coupon_id=coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    return coupon


@router.put("/{coupon_id}", response_model=Coupon)
def update_coupon_admin(
    *,
    db: Session = Depends(get_db),
    coupon_id: str,
    coupon_in: CouponUpdate,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Update coupon (admin only)
    """
    coupon = get_coupon(db, coupon_id=coupon_id)
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    coupon = update_coupon(db, db_coupon=coupon, coupon_in=coupon_in)
    return coupon


@router.delete("/{coupon_id}")
def delete_coupon_admin(
    *,
    db: Session = Depends(get_db),
    coupon_id: str,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Delete coupon (admin only)
    """
    success = delete_coupon(db, coupon_id=coupon_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    return {"message": "Coupon deleted successfully"}
