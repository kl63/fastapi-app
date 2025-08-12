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
from app.schemas.payment import (
    PaymentIntentCreate, PaymentIntentResponse, OrderPaymentCreate, OrderPaymentResponse
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


# Stripe Payment Integration Endpoints

@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
def create_payment_intent(
    *,
    db: Session = Depends(get_db),
    payment_data: PaymentIntentCreate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Create a Stripe payment intent for order payment
    """
    try:
        # Add user information to metadata
        metadata = payment_data.metadata or {}
        metadata.update({
            "user_id": current_user.id,
            "user_email": current_user.email
        })
        
        payment_intent = StripeService.create_payment_intent(
            amount=payment_data.amount,
            currency=payment_data.currency,
            customer_id=payment_data.customer_id,
            payment_method_id=payment_data.payment_method_id,
            metadata=metadata
        )
        
        return PaymentIntentResponse(
            id=payment_intent["id"],
            client_secret=payment_intent["client_secret"],
            status=payment_intent["status"],
            amount=payment_intent["amount"],
            currency=payment_intent["currency"],
            metadata=payment_intent.get("metadata")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create payment intent: {str(e)}"
        )


@router.post("/create-order-with-payment", response_model=OrderPaymentResponse)
def create_order_with_payment(
    *,
    db: Session = Depends(get_db),
    order_payment_data: OrderPaymentCreate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Create an order and associated payment intent
    """
    try:
        # First create the order (without payment processing)
        order_create = OrderCreate(
            shipping_address_id=order_payment_data.shipping_address_id,
            billing_address_id=order_payment_data.billing_address_id,
            notes=order_payment_data.notes
        )
        
        order = create_order(db, user_id=current_user.id, order_in=order_create)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create order. Please check your cart and address."
            )
        
        # Create payment intent for the order
        metadata = {
            "order_id": order.id,
            "user_id": current_user.id,
            "user_email": current_user.email
        }
        
        payment_intent = StripeService.create_payment_intent(
            amount=float(order.total_amount),
            currency="usd",
            payment_method_id=order_payment_data.payment_method_id,
            metadata=metadata
        )
        
        # TODO: Store payment_intent_id in order or payment table
        # This would require updating the order model to include payment_intent_id
        
        return OrderPaymentResponse(
            order_id=order.id,
            payment_intent_id=payment_intent["id"],
            client_secret=payment_intent["client_secret"],
            amount=float(order.total_amount),
            status=payment_intent["status"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create order with payment: {str(e)}"
        )


@router.post("/confirm-payment/{order_id}")
def confirm_order_payment(
    *,
    db: Session = Depends(get_db),
    order_id: str,
    payment_intent_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Confirm payment for an order
    """
    try:
        # Verify order belongs to user
        order = get_order(db, order_id=order_id, user_id=current_user.id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Retrieve payment intent status
        payment_intent = StripeService.retrieve_payment_intent(payment_intent_id)
        
        if payment_intent["status"] == "succeeded":
            # Update order status to confirmed
            update_order_status(
                db, 
                order_id=order_id, 
                status=OrderStatus.CONFIRMED,
                notes="Payment confirmed via Stripe"
            )
            
            return {
                "message": "Payment confirmed successfully",
                "order_id": order_id,
                "payment_status": payment_intent["status"]
            }
        else:
            return {
                "message": "Payment not yet completed",
                "order_id": order_id,
                "payment_status": payment_intent["status"]
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to confirm payment: {str(e)}"
        )


@router.post("/refund/{order_id}")
def refund_order(
    *,
    db: Session = Depends(get_db),
    order_id: str,
    payment_intent_id: str,
    refund_amount: Optional[float] = None,
    current_user: DBUser = Depends(get_current_active_admin),
) -> Any:
    """
    Process refund for an order (admin only)
    """
    try:
        # Verify order exists
        order = get_order(db, order_id=order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Create refund in Stripe
        refund = StripeService.create_refund(
            payment_intent_id=payment_intent_id,
            amount=refund_amount
        )
        
        if refund["status"] == "succeeded":
            # Update order status
            update_order_status(
                db,
                order_id=order_id,
                status=OrderStatus.REFUNDED,
                notes=f"Refund processed: {refund['id']}"
            )
            
            return {
                "message": "Refund processed successfully",
                "refund_id": refund["id"],
                "amount": refund["amount"] / 100,  # Convert from cents
                "status": refund["status"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Refund failed with status: {refund['status']}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process refund: {str(e)}"
        )
