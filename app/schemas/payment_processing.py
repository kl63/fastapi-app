from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class PaymentProcessRequest(BaseModel):
    """Schema for processing a payment"""
    amount: Decimal = Field(..., description="Amount to charge in dollars")
    payment_method_id: str = Field(..., description="ID of the payment method to use")
    description: Optional[str] = Field(None, description="Description of the payment")
    metadata: Optional[dict] = Field(None, description="Additional metadata for the payment")


class PaymentProcessResponse(BaseModel):
    """Response schema for processed payment"""
    payment_id: str
    status: str
    amount: Decimal
    transaction_id: str
    payment_method_id: str
    created_at: str
