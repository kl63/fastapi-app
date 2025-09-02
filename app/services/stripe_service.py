"""
Stripe payment processing service
"""
import stripe
from typing import Dict, Any, Optional
from decimal import Decimal

from app.core.config import settings

# Initialize Stripe with secret key (only if available)
try:
    stripe.api_key = settings.STRIPE_SECRET_KEY
except Exception:
    # Handle case where settings are not available (e.g., during testing)
    stripe.api_key = None


class StripeService:
    """Service class for Stripe payment operations"""
    
    @staticmethod
    def create_payment_intent(
        amount: float,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        payment_method_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        return_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe Payment Intent
        
        Args:
            amount: Amount in dollars (will be converted to cents)
            currency: Currency code (default: usd)
            customer_id: Stripe customer ID
            payment_method_id: Stripe payment method ID
            metadata: Additional metadata to attach to the payment intent
            return_url: URL to redirect after payment completion
            
        Returns:
            Payment intent object
        """
        try:
            # Convert amount to cents (Stripe expects amounts in smallest currency unit)
            amount_cents = int(amount * 100)
            
            payment_intent_data = {
                "amount": amount_cents,
                "currency": currency,
            }
            
            # If we're using a saved payment method, don't enable automatic methods
            if payment_method_id:
                payment_intent_data["payment_method"] = payment_method_id
                payment_intent_data["confirm"] = True
                payment_intent_data["off_session"] = True  # Since we're using a saved method
                # Prevent the need for authentication
                payment_intent_data["confirmation_method"] = "automatic"
            else:
                # Only use automatic payment methods for new payment methods
                payment_intent_data["automatic_payment_methods"] = {
                    "enabled": True,
                    "allow_redirects": "never"
                }
            
            if customer_id:
                payment_intent_data["customer"] = customer_id
            
            if return_url:
                payment_intent_data["return_url"] = return_url
                
            if metadata:
                payment_intent_data["metadata"] = metadata
            
            payment_intent = stripe.PaymentIntent.create(**payment_intent_data)
            return payment_intent
            
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def confirm_payment_intent(payment_intent_id: str, payment_method_id: str) -> Dict[str, Any]:
        """
        Confirm a payment intent with a payment method
        
        Args:
            payment_intent_id: The payment intent ID
            payment_method_id: The payment method ID
            
        Returns:
            Confirmed payment intent object
        """
        try:
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method_id
            )
            return payment_intent
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def create_customer(email: str, name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a Stripe customer
        
        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata
            
        Returns:
            Customer object
        """
        try:
            customer_data = {"email": email}
            
            if name:
                customer_data["name"] = name
                
            if metadata:
                customer_data["metadata"] = metadata
            
            customer = stripe.Customer.create(**customer_data)
            return customer
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def create_payment_method(
        type: str = "card",
        card_token: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a payment method
        
        Args:
            type: Payment method type (default: card)
            card_token: Card token from frontend
            customer_id: Customer to attach the payment method to
            
        Returns:
            Payment method object
        """
        try:
            if type == "card" and card_token:
                # For tokens, we need to use the token parameter directly
                # instead of nesting it under card
                payment_method = stripe.PaymentMethod.create(
                    type="card",
                    card={
                        "token": card_token
                    }
                )
            else:
                # Standard payment method creation without token
                payment_method_data = {"type": type}
                payment_method = stripe.PaymentMethod.create(**payment_method_data)
            
            # Attach to customer if provided
            if customer_id and payment_method:
                payment_method.attach(customer=customer_id)
            
            return payment_method
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Retrieve a payment intent by ID
        
        Args:
            payment_intent_id: The payment intent ID
            
        Returns:
            Payment intent object
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return payment_intent
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def cancel_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """
        Cancel a payment intent
        
        Args:
            payment_intent_id: The payment intent ID
            
        Returns:
            Cancelled payment intent object
        """
        try:
            payment_intent = stripe.PaymentIntent.cancel(payment_intent_id)
            return payment_intent
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def create_refund(payment_intent_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """
        Create a refund for a payment intent
        
        Args:
            payment_intent_id: The payment intent ID
            amount: Amount to refund in dollars (optional, defaults to full amount)
            
        Returns:
            Refund object
        """
        try:
            refund_data = {"payment_intent": payment_intent_id}
            
            if amount:
                # Convert amount to cents
                refund_data["amount"] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_data)
            return refund
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def retrieve_payment_method(payment_method_id: str) -> Dict[str, Any]:
        """
        Retrieve a payment method by ID
        
        Args:
            payment_method_id: The payment method ID
            
        Returns:
            Payment method object
        """
        try:
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
            return payment_method
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Construct and verify a webhook event
        
        Args:
            payload: Raw request payload
            sig_header: Stripe signature header
            
        Returns:
            Webhook event object
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            raise Exception(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f"Invalid signature: {str(e)}")
