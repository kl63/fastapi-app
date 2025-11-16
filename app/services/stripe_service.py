"""
Stripe Payment Service
Handles all Stripe API interactions securely on the backend.
NEVER expose secret keys to the frontend!
"""
import stripe
from typing import Dict, Any, Optional
from app.core.config import settings

# Initialize Stripe with secret key (backend only!)
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service class for Stripe payment operations"""
    
    @staticmethod
    def create_payment_intent(
        amount: float,
        currency: str = "usd",
        metadata: Optional[Dict[str, Any]] = None,
        customer_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a PaymentIntent for processing payment
        
        Args:
            amount: Amount in dollars (will be converted to cents)
            currency: Currency code (default: usd)
            metadata: Optional metadata (order_id, user_id, etc.)
            customer_email: Optional customer email
            
        Returns:
            PaymentIntent object with client_secret for frontend
        """
        try:
            # Convert amount to cents (Stripe uses smallest currency unit)
            amount_cents = int(amount * 100)
            
            # Create payment intent parameters
            params = {
                "amount": amount_cents,
                "currency": currency,
                "automatic_payment_methods": {
                    "enabled": True,
                },
            }
            
            # Add optional parameters
            if metadata:
                params["metadata"] = metadata
            if customer_email:
                params["receipt_email"] = customer_email
                
            # Create the payment intent
            payment_intent = stripe.PaymentIntent.create(**params)
            
            return {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "status": payment_intent.status,
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve a PaymentIntent to check its status
        
        Args:
            payment_intent_id: The PaymentIntent ID
            
        Returns:
            PaymentIntent details
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "metadata": payment_intent.metadata,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def cancel_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Cancel a PaymentIntent
        
        Args:
            payment_intent_id: The PaymentIntent ID
            
        Returns:
            Canceled PaymentIntent details
        """
        try:
            payment_intent = stripe.PaymentIntent.cancel(payment_intent_id)
            return {
                "id": payment_intent.id,
                "status": payment_intent.status,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def create_refund(
        payment_intent_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a refund for a payment
        
        Args:
            payment_intent_id: The PaymentIntent ID
            amount: Optional partial refund amount in dollars
            reason: Optional reason for refund
            
        Returns:
            Refund details
        """
        try:
            params = {"payment_intent": payment_intent_id}
            
            if amount:
                params["amount"] = int(amount * 100)  # Convert to cents
            if reason:
                params["reason"] = reason
                
            refund = stripe.Refund.create(**params)
            
            return {
                "id": refund.id,
                "amount": refund.amount / 100,  # Convert back to dollars
                "status": refund.status,
                "payment_intent": refund.payment_intent,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Verify and construct webhook event from Stripe
        
        Args:
            payload: Raw request body
            sig_header: Stripe-Signature header
            
        Returns:
            Verified webhook event
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise Exception("Invalid signature")
    
    @staticmethod
    def get_publishable_key() -> str:
        """
        Get Stripe publishable key (safe to expose to frontend)
        
        Returns:
            Publishable key
        """
        return settings.STRIPE_PUBLISHABLE_KEY
