from typing import Any, Dict, Optional, Union, List
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.coupon import Coupon
from app.schemas.coupon import CouponCreate, CouponUpdate


def get_coupon(db: Session, coupon_id: str) -> Optional[Coupon]:
    """Get coupon by ID"""
    return db.query(Coupon).filter(Coupon.id == coupon_id).first()


def get_coupon_by_code(db: Session, code: str) -> Optional[Coupon]:
    """Get coupon by code"""
    return db.query(Coupon).filter(Coupon.code == code).first()


def get_coupons(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[Coupon]:
    """Get multiple coupons with optional active filter"""
    query = db.query(Coupon)
    
    if is_active is not None:
        query = query.filter(Coupon.is_active == is_active)
    
    return query.order_by(Coupon.created_at.desc()).offset(skip).limit(limit).all()


def create_coupon(db: Session, coupon_in: CouponCreate) -> Optional[Coupon]:
    """Create new coupon"""
    # Check if code already exists
    existing_coupon = get_coupon_by_code(db, coupon_in.code)
    if existing_coupon:
        return None
    
    coupon_id = str(uuid.uuid4())
    db_coupon = Coupon(
        id=coupon_id,
        code=coupon_in.code,
        name=coupon_in.name,
        description=coupon_in.description,
        discount_type=coupon_in.discount_type,
        discount_value=coupon_in.discount_value,
        minimum_order_amount=coupon_in.minimum_order_amount,
        maximum_discount_amount=coupon_in.maximum_discount_amount,
        usage_limit=coupon_in.usage_limit,
        usage_limit_per_user=coupon_in.usage_limit_per_user,
        valid_from=coupon_in.valid_from,
        valid_until=coupon_in.valid_until,
        is_active=coupon_in.is_active,
        usage_count=0,
    )
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


def update_coupon(
    db: Session, 
    db_coupon: Coupon, 
    coupon_in: Union[CouponUpdate, Dict[str, Any]]
) -> Coupon:
    """Update coupon"""
    if isinstance(coupon_in, dict):
        update_data = coupon_in
    else:
        update_data = coupon_in.dict(exclude_unset=True)
    
    # Update coupon attributes
    for field in update_data:
        if hasattr(db_coupon, field):
            setattr(db_coupon, field, update_data[field])
            
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon


def delete_coupon(db: Session, coupon_id: str) -> bool:
    """Delete coupon"""
    try:
        coupon = get_coupon(db, coupon_id=coupon_id)
        if not coupon:
            return False
        
        db.delete(coupon)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def validate_coupon_code(
    db: Session, 
    code: str, 
    user_id: str, 
    cart_total: float
) -> Dict[str, Any]:
    """Validate coupon code and return discount information"""
    coupon = get_coupon_by_code(db, code)
    if not coupon:
        return {"valid": False, "message": "Invalid coupon code"}
    
    # Use the coupon's validation method
    is_valid, message = coupon.is_valid(user_id=user_id, cart_total=cart_total)
    
    if not is_valid:
        return {"valid": False, "message": message}
    
    # Calculate discount
    discount_amount = coupon.calculate_discount(cart_total)
    
    return {
        "valid": True,
        "message": "Coupon is valid",
        "discount_amount": discount_amount,
        "coupon": {
            "id": coupon.id,
            "code": coupon.code,
            "name": coupon.name,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value
        }
    }
