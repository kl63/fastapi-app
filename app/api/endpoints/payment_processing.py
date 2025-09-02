from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.payment_processing import PaymentProcessRequest, PaymentProcessResponse
from app.models.user import User as DBUser
from app.models.payment import PaymentMethod, Payment
from app.services.stripe_service import StripeService
from app.crud.payment import get_payment_method, create_payment
from app.api.deps import get_db, get_current_user
from app.schemas.payment import PaymentCreate, PaymentStatus

router = APIRouter()


@router.post("/process", response_model=PaymentProcessResponse)
def process_payment(
    *,
    db: Session = Depends(get_db),
    payment_request: PaymentProcessRequest,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Process a payment using a saved payment method
    """
    try:
        # Get the payment method
        payment_method = get_payment_method(db, payment_request.payment_method_id)
        
        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment method not found"
            )
            
        if payment_method.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to use this payment method"
            )
        
        # Prepare metadata
        metadata = payment_request.metadata or {}
        metadata.update({
            "user_id": str(current_user.id),
            "payment_method_id": payment_request.payment_method_id,
            "description": payment_request.description or "Payment"
        })
        
        # Get customer ID from payment method payment_metadata
        customer_id = None
        
        # Debug print the payment method
        print(f"Payment method: {payment_method.__dict__}")
        
        # Check for payment_metadata
        if hasattr(payment_method, "payment_metadata") and payment_method.payment_metadata:
            print(f"Payment metadata found: {payment_method.payment_metadata}")
            customer_id = payment_method.payment_metadata.get("stripe_customer_id")
            
        # If no customer ID in payment_metadata, try to get it from Stripe directly
        if not customer_id and payment_method.external_id:
            try:
                # Retrieve the payment method from Stripe to get its customer
                stripe_payment_method = StripeService.retrieve_payment_method(payment_method.external_id)
                if stripe_payment_method and "customer" in stripe_payment_method:
                    customer_id = stripe_payment_method["customer"]
                    print(f"Found customer ID from Stripe: {customer_id}")
            except Exception as e:
                print(f"Error retrieving payment method from Stripe: {e}")
                
        print(f"Using customer ID: {customer_id}")
        
        # Create payment intent with Stripe
        payment_intent = StripeService.create_payment_intent(
            amount=float(payment_request.amount),
            currency="usd",
            customer_id=customer_id,  # Pass customer ID if available
            payment_method_id=payment_method.external_id,  # Use the Stripe ID
            metadata=metadata,
            # Handle off-session payments for saved cards
            return_url="https://fastapi.kevinlinportfolio.com/payment-success"
        )
        
        # Create payment record in our database
        payment_create = PaymentCreate(
            amount=payment_request.amount,
            payment_method_id=payment_request.payment_method_id,
            status=PaymentStatus.PROCESSING,
            transaction_id=payment_intent["id"],
            provider="stripe",
            metadata=metadata
        )
        
        payment = create_payment(db, payment_create=payment_create, user_id=current_user.id)
        
        # Return the payment response
        return PaymentProcessResponse(
            payment_id=payment.id,
            status=payment.status,
            amount=payment.amount,
            transaction_id=payment.transaction_id,
            payment_method_id=payment.payment_method_id,
            created_at=payment.created_at.isoformat()
        )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not process payment: {str(e)}"
        )
