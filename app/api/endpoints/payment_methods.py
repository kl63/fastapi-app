"""
Payment methods endpoints for managing user payment methods
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud.payment import (
    create_payment_method, get_user_payment_methods,
    get_payment_method, delete_payment_method, set_default_payment_method
)
from app.models.user import User as DBUser
from app.schemas.payment import (
    PaymentMethodCreate, PaymentMethodResponse
)
from app.services.stripe_service import StripeService

router = APIRouter()


@router.post("/", response_model=PaymentMethodResponse)
def create_user_payment_method(
    *,
    db: Session = Depends(get_db),
    payment_method_in: PaymentMethodCreate,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Create a new payment method for the current user
    """
    try:
        # Get or create a Stripe customer for this user
        customer_id = None
        stripe_customer_id_key = "stripe_customer_id"
        
        # Check if user has a payment method with customer ID in payment_metadata
        user_payment_methods = get_user_payment_methods(db, current_user.id)
        for pm in user_payment_methods:
            if hasattr(pm, "payment_metadata") and pm.payment_metadata and \
               stripe_customer_id_key in pm.payment_metadata:
                customer_id = pm.payment_metadata[stripe_customer_id_key]
                break
        
        # If no customer ID exists, create a new Stripe customer
        if not customer_id:
            customer = StripeService.create_customer(
                email=current_user.email,
                name=current_user.full_name,
                metadata={"user_id": str(current_user.id)}
            )
            customer_id = customer["id"]
            
            # Store the customer ID in user metadata (if your model supports it)
            # This would require updating your user model to handle metadata
            # For now we'll just use the customer ID for this operation
        
        # Create the payment method in Stripe with customer attachment
        stripe_payment_method = StripeService.create_payment_method(
            type=payment_method_in.type,
            card_token=payment_method_in.card_token,
            customer_id=customer_id  # Attach to customer immediately
        )
        
        # Extract card details for our database
        card_details = stripe_payment_method.get("card", {})
        
        # Create an enhanced payment method object with all required fields
        db_payment_method = PaymentMethodCreate(
            type=payment_method_in.type,
            card_token=payment_method_in.card_token,
            is_default=payment_method_in.is_default,
            # Add additional fields needed by the database model
            provider="stripe",
            last_four_digits=card_details.get("last4"),
            expiry_month=card_details.get("exp_month"),
            expiry_year=card_details.get("exp_year"),
            external_id=stripe_payment_method["id"],
            # Store the customer ID for future reference
            payment_metadata={"stripe_customer_id": customer_id}
        )
        
        # Create payment method in our database
        payment_method = create_payment_method(
            db,
            user_id=current_user.id,
            payment_method_in=db_payment_method
        )
        
        return payment_method
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create payment method: {str(e)}"
        )


@router.get("/", response_model=List[PaymentMethodResponse])
def get_payment_methods(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get all payment methods for the current user
    """
    payment_methods = get_user_payment_methods(db, user_id=current_user.id)
    return payment_methods


@router.get("/{payment_method_id}", response_model=PaymentMethodResponse)
def get_payment_method_by_id(
    *,
    db: Session = Depends(get_db),
    payment_method_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Get a specific payment method
    """
    payment_method = get_payment_method(db, payment_method_id=payment_method_id)
    
    if not payment_method or payment_method.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
        
    return payment_method


@router.delete("/{payment_method_id}")
def delete_user_payment_method(
    *,
    db: Session = Depends(get_db),
    payment_method_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Delete (deactivate) a payment method
    """
    # First get the payment method to check if it exists and belongs to the user
    payment_method = get_payment_method(db, payment_method_id=payment_method_id)
    
    if not payment_method or payment_method.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    
    # Delete from Stripe if it has an external ID
    if payment_method.external_id:
        try:
            StripeService.detach_payment_method(payment_method.external_id)
        except Exception as e:
            # Log the error but continue with local deletion
            print(f"Error detaching payment method from Stripe: {str(e)}")
    
    # Delete from our database
    success = delete_payment_method(
        db, payment_method_id=payment_method_id, user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not delete payment method"
        )
        
    return {"message": "Payment method deleted successfully"}


@router.post("/{payment_method_id}/set-default", response_model=PaymentMethodResponse)
def set_default_method(
    *,
    db: Session = Depends(get_db),
    payment_method_id: str,
    current_user: DBUser = Depends(get_current_user),
) -> Any:
    """
    Set a payment method as default
    """
    payment_method = set_default_payment_method(
        db, payment_method_id=payment_method_id, user_id=current_user.id
    )
    
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found or could not be set as default"
        )
        
    return payment_method
