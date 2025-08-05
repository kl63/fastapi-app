from sqlalchemy import Boolean, Column, String, Float, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class PaymentMethod(Base):
    """
    Payment method model for user payment methods
    """
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    
    # Payment method details
    type = Column(String, nullable=False)  # "card", "paypal", "apple_pay", "google_pay"
    provider = Column(String, nullable=True)  # "visa", "mastercard", "amex", etc.
    
    # Card details (encrypted)
    last_four_digits = Column(String, nullable=True)
    expiry_month = Column(String, nullable=True)
    expiry_year = Column(String, nullable=True)
    cardholder_name = Column(String, nullable=True)
    
    # External payment method ID (from payment processor)
    external_id = Column(String, nullable=True)
    
    # Status
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="payment_methods")
    payments = relationship("Payment", back_populates="payment_method")
    
    def __repr__(self):
        return f"<PaymentMethod {self.type} ending in {self.last_four_digits}>"


class Payment(Base):
    """
    Payment model for order payments
    """
    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("order.id"), nullable=False)
    payment_method_id = Column(String, ForeignKey("paymentmethod.id"), nullable=True)
    
    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, nullable=False, default="pending")  # pending, processing, completed, failed, refunded
    
    # Payment processor details
    transaction_id = Column(String, nullable=True)  # External transaction ID
    processor = Column(String, nullable=True)  # "stripe", "paypal", etc.
    processor_response = Column(JSON, nullable=True)  # Raw response from processor
    
    # Failure details
    failure_reason = Column(String, nullable=True)
    failure_code = Column(String, nullable=True)
    
    # Refund details
    refunded_amount = Column(Float, default=0.0)
    refund_reason = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment {self.id} - ${self.amount} - {self.status}>"
