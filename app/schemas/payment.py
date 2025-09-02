"""
Payment schemas for Stripe integration
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class PaymentStatus(str, Enum):
    """Payment status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethodType(str, Enum):
    """Payment method type enum"""
    CARD = "card"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"


class PaymentCreate(BaseModel):
    """Schema for creating a payment"""
    order_id: Optional[str] = None
    amount: float
    currency: str = "USD"
    payment_method_id: Optional[str] = None
    provider: str = "stripe"  # Changed from processor for consistency
    status: Optional[PaymentStatus] = PaymentStatus.PENDING
    transaction_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PaymentIntentCreate(BaseModel):
    """Schema for creating a payment intent"""
    amount: float
    currency: str = "usd"
    payment_method_id: Optional[str] = None
    customer_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PaymentIntentConfirm(BaseModel):
    """Schema for confirming a payment intent"""
    payment_intent_id: str
    payment_method_id: str


class PaymentIntentResponse(BaseModel):
    """Response schema for payment intent"""
    id: str
    client_secret: str
    status: str
    amount: int
    currency: str
    metadata: Optional[Dict[str, Any]] = None


class StripeCustomerCreate(BaseModel):
    """Schema for creating a Stripe customer"""
    email: str
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class StripeCustomerResponse(BaseModel):
    """Response schema for Stripe customer"""
    id: str
    email: str
    name: Optional[str] = None
    created: int


class PaymentMethodCreate(BaseModel):
    """
    Schema for creating a payment method
    """
    type: str = Field(..., description="Type of payment method (card, paypal, etc.)")
    provider: str = Field("stripe", description="Payment provider (stripe, paypal, etc.)")
    
    # Card details
    last_four_digits: Optional[str] = None
    expiry_month: Optional[str] = None
    expiry_year: Optional[str] = None
    cardholder_name: Optional[str] = None
    
    # For API integration
    card_token: Optional[str] = None
    external_id: Optional[str] = None
    is_default: bool = False
    
    # Optional metadata
    payment_metadata: Optional[Dict[str, Any]] = None


class PaymentMethodResponse(BaseModel):
    """Response schema for payment method"""
    id: str
    type: str
    card: Optional[Dict[str, Any]] = None
    customer: Optional[str] = None


class RefundCreate(BaseModel):
    """Schema for creating a refund"""
    payment_intent_id: str
    amount: Optional[float] = None
    reason: Optional[str] = None


class RefundResponse(BaseModel):
    """Response schema for refund"""
    id: str
    amount: int
    currency: str
    status: str
    payment_intent: str


class WebhookEvent(BaseModel):
    """Schema for Stripe webhook events"""
    id: str
    type: str
    data: Dict[str, Any]
    created: int


class OrderPaymentCreate(BaseModel):
    """Schema for creating order with payment"""
    shipping_address_id: str
    billing_address_id: Optional[str] = None
    notes: Optional[str] = None
    payment_method_id: Optional[str] = None
    save_payment_method: bool = False


class OrderPaymentResponse(BaseModel):
    """Response schema for order payment"""
    order_id: str
    payment_intent_id: str
    client_secret: str
    amount: float
    status: str
