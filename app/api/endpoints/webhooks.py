"""
Stripe webhook endpoints for handling payment events
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
    """
    try:
        # Get the raw payload and signature
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature header"
            )
        
        # Construct and verify the webhook event
        event = StripeService.construct_webhook_event(payload, sig_header)
        
        # Handle different event types
        if event["type"] == "payment_intent.succeeded":
            await handle_payment_succeeded(db, event["data"]["object"])
            
        elif event["type"] == "payment_intent.payment_failed":
            await handle_payment_failed(db, event["data"]["object"])
            
        elif event["type"] == "payment_intent.canceled":
            await handle_payment_canceled(db, event["data"]["object"])
            
        elif event["type"] == "charge.dispute.created":
            await handle_chargeback_created(db, event["data"]["object"])
            
        else:
            print(f"Unhandled event type: {event['type']}")
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}"
        )


async def handle_payment_succeeded(db: Session, payment_intent: dict) -> None:
    """
    Handle successful payment
    """
    try:
        metadata = payment_intent.get("metadata", {})
        order_id = metadata.get("order_id")
        
        if order_id:
            # Update order status to confirmed
            update_order_status(
                db,
                order_id=order_id,
                status=OrderStatus.CONFIRMED,
                notes=f"Payment succeeded: {payment_intent['id']}"
            )
            print(f"Order {order_id} confirmed after successful payment")
            
    except Exception as e:
        print(f"Error handling payment success: {str(e)}")


async def handle_payment_failed(db: Session, payment_intent: dict) -> None:
    """
    Handle failed payment
    """
    try:
        metadata = payment_intent.get("metadata", {})
        order_id = metadata.get("order_id")
        
        if order_id:
            # Update order status to cancelled
            update_order_status(
                db,
                order_id=order_id,
                status=OrderStatus.CANCELLED,
                notes=f"Payment failed: {payment_intent['id']}"
            )
            print(f"Order {order_id} cancelled due to payment failure")
            
    except Exception as e:
        print(f"Error handling payment failure: {str(e)}")


async def handle_payment_canceled(db: Session, payment_intent: dict) -> None:
    """
    Handle canceled payment
    """
    try:
        metadata = payment_intent.get("metadata", {})
        order_id = metadata.get("order_id")
        
        if order_id:
            # Update order status to cancelled
            update_order_status(
                db,
                order_id=order_id,
                status=OrderStatus.CANCELLED,
                notes=f"Payment canceled: {payment_intent['id']}"
            )
            print(f"Order {order_id} cancelled due to payment cancellation")
            
    except Exception as e:
        print(f"Error handling payment cancellation: {str(e)}")


async def handle_chargeback_created(db: Session, charge: dict) -> None:
    """
    Handle chargeback/dispute creation
    """
    try:
        payment_intent_id = charge.get("payment_intent")
        
        if payment_intent_id:
            # You might want to implement logic to find the order by payment_intent_id
            # and update its status or create a notification for admin review
            print(f"Chargeback created for payment intent: {payment_intent_id}")
            
    except Exception as e:
        print(f"Error handling chargeback: {str(e)}")
