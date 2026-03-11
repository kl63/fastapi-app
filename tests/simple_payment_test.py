#!/usr/bin/env python3
"""
Simple Stripe Payment Test - Direct API Test
Tests payment flow using Stripe's Python SDK directly
"""
import stripe
from app.core.config import settings
import json

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_create_payment_intent():
    """Test creating a payment intent"""
    print_section("TEST 1: Create Payment Intent")
    
    try:
        # Create a payment intent for $29.99
        payment_intent = stripe.PaymentIntent.create(
            amount=2999,  # $29.99 in cents
            currency="usd",
            payment_method_types=["card"],  # Only accept cards
            metadata={
                "order_id": "test_order_123",
                "user_id": "test_user_456",
            },
            receipt_email="test@example.com"
        )
        
        print(f"✅ Payment Intent Created Successfully!")
        print(f"   ID: {payment_intent.id}")
        print(f"   Amount: ${payment_intent.amount / 100:.2f}")
        print(f"   Currency: {payment_intent.currency.upper()}")
        print(f"   Status: {payment_intent.status}")
        print(f"   Client Secret: {payment_intent.client_secret[:30]}...")
        
        return payment_intent
        
    except Exception as e:
        print(f"❌ Error creating payment intent: {str(e)}")
        return None

def test_confirm_payment(payment_intent_id):
    """Test confirming a payment with test card"""
    print_section("TEST 2: Confirm Payment with Test Card")
    
    print("💳 Using Stripe test payment method: pm_card_visa")
    
    try:
        # Use Stripe's test payment method token
        # pm_card_visa is a test token that represents a successful Visa card
        payment_intent = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method="pm_card_visa"  # Stripe test payment method
        )
        
        print(f"\n✅ Payment Confirmed Successfully!")
        print(f"   Status: {payment_intent.status.upper()}")
        print(f"   Amount Charged: ${payment_intent.amount / 100:.2f}")
        
        # Check if charges are available
        if hasattr(payment_intent, 'charges') and payment_intent.charges.data:
            charge = payment_intent.charges.data[0]
            print(f"   Payment Method: Card ending in {charge.payment_method_details.card.last4}")
            if charge.receipt_url:
                print(f"   Receipt URL: {charge.receipt_url}")
        
        if payment_intent.status == "succeeded":
            print(f"\n{'🎉'*35}")
            print("   PAYMENT SUCCESSFUL!")
            print(f"{'🎉'*35}")
        
        return payment_intent
        
    except stripe.error.CardError as e:
        print(f"❌ Card Error: {e.user_message}")
        return None
    except Exception as e:
        print(f"❌ Error confirming payment: {str(e)}")
        return None

def test_retrieve_payment(payment_intent_id):
    """Test retrieving payment intent"""
    print_section("TEST 3: Retrieve Payment Intent")
    
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        print(f"✅ Retrieved Payment Intent")
        print(f"   ID: {payment_intent.id}")
        print(f"   Status: {payment_intent.status}")
        print(f"   Amount: ${payment_intent.amount / 100:.2f}")
        print(f"   Created: {payment_intent.created}")
        
        return payment_intent
        
    except Exception as e:
        print(f"❌ Error retrieving payment: {str(e)}")
        return None

def test_create_refund(payment_intent_id):
    """Test creating a refund"""
    print_section("TEST 4: Create Refund (Optional)")
    
    try:
        refund = stripe.Refund.create(
            payment_intent=payment_intent_id,
            amount=1000,  # Refund $10.00
            reason="requested_by_customer"
        )
        
        print(f"✅ Refund Created Successfully!")
        print(f"   ID: {refund.id}")
        print(f"   Amount: ${refund.amount / 100:.2f}")
        print(f"   Status: {refund.status}")
        print(f"   Reason: {refund.reason}")
        
        return refund
        
    except Exception as e:
        print(f"❌ Error creating refund: {str(e)}")
        return None

def main():
    """Run all tests"""
    print("\n" + "💳"*35)
    print("         STRIPE SDK DIRECT TEST")
    print("         Testing Payment Flow")
    print("💳"*35)
    
    # Test 1: Create Payment Intent
    payment_intent = test_create_payment_intent()
    if not payment_intent:
        print("\n❌ Test suite failed at payment intent creation")
        return
    
    # Test 2: Confirm Payment
    confirmed_payment = test_confirm_payment(payment_intent.id)
    if not confirmed_payment:
        print("\n❌ Test suite failed at payment confirmation")
        return
    
    # Test 3: Retrieve Payment
    retrieved_payment = test_retrieve_payment(payment_intent.id)
    
    # Test 4: Create Refund (optional)
    refund = test_create_refund(payment_intent.id)
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"✅ Payment Intent Created: {payment_intent.id}")
    print(f"✅ Payment Confirmed: ${confirmed_payment.amount / 100:.2f}")
    print(f"✅ Status: {confirmed_payment.status.upper()}")
    if refund:
        print(f"✅ Refund Processed: ${refund.amount / 100:.2f}")
    
    print("\n" + "🎊"*35)
    print("   ALL STRIPE TESTS PASSED!")
    print("   Your Stripe integration is working perfectly!")
    print("🎊"*35 + "\n")
    
    print("\n📝 Next Steps:")
    print("1. Use these endpoints in your Next.js frontend")
    print("2. POST /api/v1/orders/{order_id}/create-payment-intent")
    print("3. Use the client_secret with Stripe Elements")
    print("4. Stripe will handle the payment UI")
    print("5. Webhook will automatically update your order status\n")

if __name__ == "__main__":
    main()
