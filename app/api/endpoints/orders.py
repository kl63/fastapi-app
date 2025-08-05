from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_active_admin
from app.crud.order import (
    get_order, get_user_orders, create_order, 
    update_order_status, cancel_order, get_all_orders
)
from app.models.user import User as DBUser
from app.schemas.order import (
    Order, OrderCreate, OrderStatusUpdate, OrderStatus
)

router = APIRouter()


@router.get("/", response_model=List[Order])
def get_orders(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[OrderStatus] = None,
) -> Any:
    """
    Get user's orders with optional status filter
    """
    orders = get_user_orders(
        db, user_id=current_user.id, skip=skip, limit=limit, status=status
    )
    return orders


@router.post("/", response_model=Order)
def create_order_endpoint(
    *,
    db: Session = Depends(get_db),
    order_in: OrderCreate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Create new order from cart
    """
    order = create_order(db, user_id=current_user.id, order_in=order_in)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create order. Please check your cart and address."
        )
    return order


@router.get("/{order_id}", response_model=Order)
def get_order_endpoint(
    *,
    db: Session = Depends(get_db),
    order_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get specific order by ID
    """
    order = get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user owns the order
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return order


@router.put("/{order_id}/cancel")
def cancel_order_endpoint(
    *,
    db: Session = Depends(get_db),
    order_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Cancel order
    """
    order = get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user owns the order
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = cancel_order(db, order_id=order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel order at this stage"
        )
    
    return {"message": "Order cancelled successfully"}


# Admin endpoints
@router.get("/admin/all", response_model=List[Order])
def get_all_orders_admin(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_active_admin),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[OrderStatus] = None,
) -> Any:
    """
    Get all orders (admin only)
    """
    orders = get_all_orders(db, skip=skip, limit=limit, status=status)
    return orders


@router.put("/{order_id}/status")
def update_order_status_endpoint(
    *,
    db: Session = Depends(get_db),
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Update order status (admin only)
    """
    order = update_order_status(
        db, order_id=order_id, 
        new_status=status_update.status,
        notes=status_update.notes
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return {"message": "Order status updated successfully"}
