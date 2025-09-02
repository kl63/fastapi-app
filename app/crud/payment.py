"""
CRUD operations for payment models
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.payment import Payment, PaymentMethod
from app.schemas.payment import PaymentCreate, PaymentMethodCreate


def create_payment(
    db: Session,
    *,
    payment_create: PaymentCreate,
    user_id: str
) -> Payment:
    """
    Create a new payment record
    """
    payment_id = str(uuid4())
    
    db_payment = Payment(
        id=payment_id,
        user_id=user_id,
        order_id=payment_create.order_id,
        payment_method_id=payment_create.payment_method_id,
        amount=payment_create.amount,
        currency=payment_create.currency,
        status=payment_create.status,
        provider=payment_create.provider,  # Using provider instead of processor for consistency
        transaction_id=payment_create.transaction_id,
        metadata=payment_create.metadata
    )
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    return db_payment


def update_payment_status(
    db: Session,
    *,
    payment_id: Optional[str] = None,
    transaction_id: Optional[str] = None,
    status: str,
    processor_response: Optional[Dict[str, Any]] = None,
    failure_reason: Optional[str] = None,
    failure_code: Optional[str] = None
) -> Optional[Payment]:
    """
    Update payment status by payment_id or transaction_id
    """
    if not payment_id and not transaction_id:
        return None
        
    if payment_id:
        db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    else:
        db_payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
        
    if not db_payment:
        return None
        
    # Update payment status
    db_payment.status = status
    
    # Update processor response if provided
    if processor_response:
        db_payment.processor_response = processor_response
        
    # Update failure details if provided
    if failure_reason:
        db_payment.failure_reason = failure_reason
        
    if failure_code:
        db_payment.failure_code = failure_code
        
    db.commit()
    db.refresh(db_payment)
    
    return db_payment


def process_refund(
    db: Session,
    *,
    payment_id: str,
    refund_amount: Optional[float] = None,
    refund_reason: Optional[str] = None
) -> Optional[Payment]:
    """
    Process refund for a payment
    """
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    
    if not db_payment:
        return None
        
    # If refund amount not provided, refund full amount
    if not refund_amount:
        refund_amount = db_payment.amount
        
    # Update payment record with refund details
    db_payment.refunded_amount = refund_amount
    db_payment.refund_reason = refund_reason
    db_payment.status = "refunded"
    
    db.commit()
    db.refresh(db_payment)
    
    return db_payment


def get_payment(
    db: Session,
    payment_id: str
) -> Optional[Payment]:
    """
    Get payment by ID
    """
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_payment_by_transaction_id(
    db: Session,
    transaction_id: str
) -> Optional[Payment]:
    """
    Get payment by transaction ID
    """
    return db.query(Payment).filter(Payment.transaction_id == transaction_id).first()


def get_payments_by_order_id(
    db: Session,
    order_id: str
) -> List[Payment]:
    """
    Get all payments for an order
    """
    return db.query(Payment).filter(Payment.order_id == order_id).all()


# Payment Methods CRUD

def create_payment_method(
    db: Session,
    *,
    user_id: str,
    payment_method_in: PaymentMethodCreate
) -> PaymentMethod:
    """
    Create a new payment method for a user
    """
    payment_method_id = str(uuid4())
    
    db_payment_method = PaymentMethod(
        id=payment_method_id,
        user_id=user_id,
        type=payment_method_in.type,
        provider=payment_method_in.provider,
        last_four_digits=payment_method_in.last_four_digits,
        expiry_month=payment_method_in.expiry_month,
        expiry_year=payment_method_in.expiry_year,
        cardholder_name=payment_method_in.cardholder_name,
        external_id=payment_method_in.external_id,
        is_default=payment_method_in.is_default,
        payment_metadata=payment_method_in.payment_metadata
    )
    
    # If this is the default payment method, unset any other default
    if payment_method_in.is_default:
        db.query(PaymentMethod).filter(
            PaymentMethod.user_id == user_id,
            PaymentMethod.is_default == True
        ).update({"is_default": False})
        
    db.add(db_payment_method)
    db.commit()
    db.refresh(db_payment_method)
    
    return db_payment_method


def get_user_payment_methods(
    db: Session,
    user_id: str
) -> List[PaymentMethod]:
    """
    Get all payment methods for a user
    """
    return db.query(PaymentMethod).filter(
        PaymentMethod.user_id == user_id,
        PaymentMethod.is_active == True
    ).all()


def get_payment_method(
    db: Session,
    payment_method_id: str
) -> Optional[PaymentMethod]:
    """
    Get payment method by ID
    """
    return db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id
    ).first()


def get_payment_method_by_external_id(
    db: Session,
    external_id: str
) -> Optional[PaymentMethod]:
    """
    Get payment method by external ID (e.g. Stripe payment method ID)
    """
    return db.query(PaymentMethod).filter(
        PaymentMethod.external_id == external_id
    ).first()


def delete_payment_method(
    db: Session,
    payment_method_id: str,
    user_id: str
) -> bool:
    """
    Delete (deactivate) a payment method
    """
    db_payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id,
        PaymentMethod.user_id == user_id
    ).first()
    
    if not db_payment_method:
        return False
        
    # Soft delete by setting is_active to False
    db_payment_method.is_active = False
    
    db.commit()
    
    return True


def set_default_payment_method(
    db: Session,
    payment_method_id: str,
    user_id: str
) -> Optional[PaymentMethod]:
    """
    Set a payment method as default for a user
    """
    # Unset any existing default
    db.query(PaymentMethod).filter(
        PaymentMethod.user_id == user_id,
        PaymentMethod.is_default == True
    ).update({"is_default": False})
    
    # Set the new default
    db_payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id,
        PaymentMethod.user_id == user_id,
        PaymentMethod.is_active == True
    ).first()
    
    if not db_payment_method:
        return None
        
    db_payment_method.is_default = True
    
    db.commit()
    db.refresh(db_payment_method)
    
    return db_payment_method
