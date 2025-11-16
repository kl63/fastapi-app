"""
Stripe Webhook Handler
Receives and processes payment events from Stripe
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.order import update_order_status, get_order
from app.schemas.order import OrderStatus
from app.services.stripe_service import StripeService

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> Any:
    """
    Handle Stripe webhook events
    
    This endpoint receives notifications from Stripe about payment events:
    - payment_intent.succeeded: Payment completed successfully
    - payment_intent.payment_failed: Payment failed
    - payment_intent.canceled: Payment canceled
    - charge.refunded: Refund processed
    
    IMPORTANT: Configure this webhook URL in your Stripe Dashboard:
    https://dashboard.stripe.com/webhooks
    """
    try:
        # Get raw payload and signature
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature header"
            )
        
        # Verify webhook signature and construct event
        event = StripeService.construct_webhook_event(payload, sig_header)
        
        # Handle different event types
        event_type = event["type"]
        event_data = event["data"]["object"]
        
        if event_type == "payment_intent.succeeded":
            await handle_payment_succeeded(db, event_data)
            
        elif event_type == "payment_intent.payment_failed":
            await handle_payment_failed(db, event_data)
            
        elif event_type == "payment_intent.canceled":
            await handle_payment_canceled(db, event_data)
            
        elif event_type == "charge.refunded":
            await handle_refund(db, event_data)
            
        else:
            print(f"Unhandled event type: {event_type}")
        
        return {"status": "success", "event_type": event_type}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}"
        )


async def handle_payment_succeeded(db: Session, payment_intent: dict) -> None:
    """
    Handle successful payment event
    Automatically confirms the order when payment succeeds
    """
    try:
        metadata = payment_intent.get("metadata", {})
        order_id = metadata.get("order_id")
        
        if order_id:
            # Update order status to confirmed
            update_order_status(
                db,
                order_id=order_id,
                new_status=OrderStatus.CONFIRMED,
                notes=f"✅ Payment succeeded (webhook). PaymentIntent: {payment_intent['id']}"
            )
            print(f"✅ Order {order_id} confirmed after successful payment")
            
    except Exception as e:
        print(f"❌ Error handling payment success: {str(e)}")


async def handle_payment_failed(db: Session, payment_intent: dict) -> None:
    """
    Handle failed payment event
    """
    try:
        metadata = payment_intent.get("metadata", {})
        order_id = metadata.get("order_id")
        
        if order_id:
            # Update order with failure note
            order = get_order(db, order_id=order_id)
            if order and order.status == OrderStatus.PENDING:
                update_order_status(
                    db,
                    order_id=order_id,
                    new_status=OrderStatus.CANCELLED,
                    notes=f"❌ Payment failed (webhook). PaymentIntent: {payment_intent['id']}"
                )
                print(f"❌ Order {order_id} canceled due to payment failure")
            
    except Exception as e:
        print(f"❌ Error handling payment failure: {str(e)}")


async def handle_payment_canceled(db: Session, payment_intent: dict) -> None:
    """
    Handle canceled payment event
    """
    try:
        metadata = payment_intent.get("metadata", {})
        order_id = metadata.get("order_id")
        
        if order_id:
            # Update order status to cancelled
            order = get_order(db, order_id=order_id)
            if order and order.status == OrderStatus.PENDING:
                update_order_status(
                    db,
                    order_id=order_id,
                    new_status=OrderStatus.CANCELLED,
                    notes=f"⚠️ Payment canceled (webhook). PaymentIntent: {payment_intent['id']}"
                )
                print(f"⚠️ Order {order_id} canceled due to payment cancellation")
            
    except Exception as e:
        print(f"❌ Error handling payment cancellation: {str(e)}")


async def handle_refund(db: Session, charge: dict) -> None:
    """
    Handle refund event
    """
    try:
        # Get payment intent from charge
        payment_intent_id = charge.get("payment_intent")
        
        if payment_intent_id:
            # You might want to store payment_intent_id in your order
            # For now, just log the event
            print(f"💰 Refund processed for PaymentIntent: {payment_intent_id}")
            
    except Exception as e:
        print(f"❌ Error handling refund: {str(e)}")
