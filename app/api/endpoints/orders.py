from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user, get_current_active_admin
from app.crud.order import (
    get_order, get_user_orders, create_order, 
    update_order_status, cancel_order, get_all_orders
)
from app.models.user import User as DBUser
from app.schemas.order import (
    Order, OrderCreate, OrderStatusUpdate, OrderStatus
)
from app.services.stripe_service import StripeService

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


# ========================================
# PAYMENT ENDPOINTS (Stripe Integration)
# ========================================

class CreatePaymentIntentRequest(BaseModel):
    """Request schema for creating payment intent"""
    order_id: str


class PaymentIntentResponse(BaseModel):
    """Response schema for payment intent"""
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str


@router.post("/{order_id}/create-payment-intent", response_model=PaymentIntentResponse)
def create_payment_intent_for_order(
    *,
    db: Session = Depends(get_db),
    order_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Create a Stripe PaymentIntent for an order
    
    This endpoint:
    1. Verifies the order belongs to the user
    2. Creates a PaymentIntent with Stripe
    3. Returns client_secret for frontend to complete payment
    
    Frontend should use the client_secret with Stripe Elements
    """
    # Get order and verify ownership
    order = get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify order belongs to user
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order"
        )
    
    # Check if order is already paid
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order is already {order.status}. Cannot create payment intent."
        )
    
    try:
        # Create payment intent with Stripe
        payment_intent = StripeService.create_payment_intent(
            amount=float(order.total_amount),
            currency="usd",
            metadata={
                "order_id": order.id,
                "order_number": order.order_number,
                "user_id": current_user.id,
            },
            customer_email=current_user.email,
        )
        
        return PaymentIntentResponse(
            client_secret=payment_intent["client_secret"],
            payment_intent_id=payment_intent["id"],
            amount=float(order.total_amount),
            currency=payment_intent["currency"],
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create payment intent: {str(e)}"
        )


class ConfirmPaymentRequest(BaseModel):
    """Request schema for confirming payment"""
    payment_intent_id: str


@router.post("/{order_id}/confirm-payment")
def confirm_order_payment(
    *,
    db: Session = Depends(get_db),
    order_id: str,
    payment_data: ConfirmPaymentRequest,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Confirm payment for an order
    
    This endpoint:
    1. Verifies the PaymentIntent with Stripe
    2. Updates order status if payment succeeded
    3. Returns payment status
    """
    # Get order and verify ownership
    order = get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify order belongs to user
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this order"
        )
    
    try:
        # Retrieve payment intent from Stripe
        payment_intent = StripeService.retrieve_payment_intent(payment_data.payment_intent_id)
        
        # Check if payment succeeded
        if payment_intent["status"] == "succeeded":
            # Update order status
            update_order_status(
                db,
                order_id=order_id,
                new_status=OrderStatus.CONFIRMED,
                notes=f"Payment confirmed. PaymentIntent: {payment_data.payment_intent_id}"
            )
            
            return {
                "success": True,
                "message": "Payment confirmed successfully",
                "order_id": order_id,
                "payment_status": payment_intent["status"],
            }
        else:
            return {
                "success": False,
                "message": f"Payment not completed. Status: {payment_intent['status']}",
                "order_id": order_id,
                "payment_status": payment_intent["status"],
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to confirm payment: {str(e)}"
        )


@router.post("/{order_id}/refund")
def refund_order_payment(
    *,
    db: Session = Depends(get_db),
    order_id: str,
    payment_intent_id: str,
    amount: Optional[float] = None,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Process refund for an order (Admin only)
    
    Args:
        order_id: Order ID
        payment_intent_id: Stripe PaymentIntent ID
        amount: Optional partial refund amount
    """
    # Get order
    order = get_order(db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    try:
        # Create refund in Stripe
        refund = StripeService.create_refund(
            payment_intent_id=payment_intent_id,
            amount=amount,
            reason="requested_by_customer"
        )
        
        # Update order status
        update_order_status(
            db,
            order_id=order_id,
            new_status=OrderStatus.REFUNDED,
            notes=f"Refund processed. Refund ID: {refund['id']}"
        )
        
        return {
            "success": True,
            "message": "Refund processed successfully",
            "refund_id": refund["id"],
            "amount": refund["amount"],
            "status": refund["status"],
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process refund: {str(e)}"
        )
