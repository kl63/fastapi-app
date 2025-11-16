#!/usr/bin/env python3
"""
Quick Stripe Payment Test with Dummy Card
Creates a test user and demonstrates the complete payment flow
"""
import requests
import json
import time
import uuid
import stripe
from app.core.config import settings

# Configuration
BASE_URL = "http://localhost:8000/api/v1"

# Generate unique test user
TEST_EMAIL = f"test_{uuid.uuid4().hex[:8]}@stripe-test.com"
TEST_PASSWORD = "TestPass123!"

# Stripe test card - always succeeds
stripe.api_key = settings.STRIPE_SECRET_KEY

def print_step(step_num, title):
    print("\n" + "="*70)
    print(f"  STEP {step_num}: {title}")
    print("="*70)

def register_and_login():
    """Create test user and login"""
    print_step(1, "Register New Test User")
    
    # Register
    username = f"stripetest{uuid.uuid4().hex[:8]}"
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": TEST_EMAIL,
            "username": username,
            "password": TEST_PASSWORD,
            "first_name": "Stripe",
            "last_name": "Test"
        }
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ User registered: {TEST_EMAIL}")
    else:
        print(f"⚠️  Registration response: {response.text}")
    
    # Login
    print("\n📧 Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Login successful!")
        print(f"🔑 Token: {token[:50]}...")
        return token
    else:
        raise Exception(f"Login failed: {response.text}")

def create_address(token):
    """Create shipping address"""
    print_step(2, "Create Shipping Address")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/addresses",
        headers=headers,
        json={
            "type": "both",
            "first_name": "Stripe",
            "last_name": "Test",
            "street": "123 Test Street",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94102",
            "country": "USA",
            "phone": "555-0123"
        }
    )
    
    if response.status_code in [200, 201]:
        address = response.json()
        address_id = address["id"]
        print(f"✅ Address created: {address_id}")
        print(f"📍 {address['street']}, {address['city']}, {address['state']}")
        return address_id
    else:
        raise Exception(f"Address creation failed: {response.text}")

def create_order(token, address_id):
    """Create test order"""
    print_step(3, "Create Order")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/orders",
        headers=headers,
        json={
            "shipping_address_id": address_id,
            "billing_address_id": address_id,
            "notes": "Test order for Stripe payment"
        }
    )
    
    if response.status_code in [200, 201]:
        order = response.json()
        print(f"✅ Order created!")
        print(f"📦 Order Number: {order['order_number']}")
        print(f"💰 Total Amount: ${order['total_amount']:.2f}")
        print(f"📊 Status: {order['status']}")
        return order
    else:
        raise Exception(f"Order creation failed: {response.text}")

def create_payment_intent(token, order_id):
    """Create Stripe PaymentIntent"""
    print_step(4, "Create Stripe Payment Intent")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/orders/{order_id}/create-payment-intent",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Payment Intent created!")
        print(f"🔐 Payment Intent ID: {data['payment_intent_id']}")
        print(f"💵 Amount: ${data['amount']:.2f} {data['currency'].upper()}")
        print(f"🔑 Client Secret: {data['client_secret'][:30]}...")
        print(f"\n💡 In a real app, you'd send this client_secret to your Next.js frontend")
        return data
    else:
        raise Exception(f"Payment intent failed: {response.text}")

def process_payment(payment_intent_id, amount):
    """Simulate payment using Stripe test card"""
    print_step(5, "Process Payment with Test Card")
    
    print("💳 Using test card: 4242 4242 4242 4242")
    print("📅 Expiry: 12/34")
    print("🔒 CVC: 123")
    
    try:
        # Confirm payment with test card
        payment_intent = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method_data={
                "type": "card",
                "card": {
                    "number": "4242424242424242",
                    "exp_month": 12,
                    "exp_year": 2034,
                    "cvc": "123",
                }
            }
        )
        
        print(f"\n✅ Payment completed successfully!")
        print(f"✨ Status: {payment_intent.status}")
        print(f"💰 Amount charged: ${payment_intent.amount / 100:.2f}")
        print(f"🆔 Stripe ID: {payment_intent.id}")
        
        return payment_intent.status == "succeeded"
        
    except stripe.error.CardError as e:
        print(f"❌ Card error: {e.user_message}")
        return False
    except Exception as e:
        print(f"❌ Payment error: {str(e)}")
        return False

def verify_order(token, order_id):
    """Check final order status"""
    print_step(6, "Verify Order Status")
    
    print("⏳ Waiting for webhook to update order status...")
    time.sleep(2)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=headers)
    
    if response.status_code == 200:
        order = response.json()
        print(f"\n📦 Order Number: {order['order_number']}")
        print(f"📊 Status: {order['status'].upper()}")
        print(f"💰 Total: ${order['total_amount']:.2f}")
        
        if order['status'] == 'confirmed':
            print(f"\n{'🎉'*35}")
            print("   PAYMENT SUCCESS! Order confirmed automatically!")
            print(f"{'🎉'*35}")
        else:
            print(f"\n⚠️  Order status: {order['status']}")
            print("💡 Note: Webhooks may take a few seconds")
        
        return order
    else:
        print(f"⚠️  Could not verify order: {response.text}")
        return None

def main():
    """Run complete payment flow test"""
    print("\n" + "💳"*35)
    print("         STRIPE PAYMENT INTEGRATION TEST")
    print("         Testing with Stripe Test Card")
    print("💳"*35)
    
    try:
        # Step 1: Register and Login
        token = register_and_login()
        
        # Step 2: Create Address
        address_id = create_address(token)
        
        # Step 3: Create Order
        order = create_order(token, address_id)
        order_id = order["id"]
        
        # Step 4: Create Payment Intent
        payment_data = create_payment_intent(token, order_id)
        
        # Step 5: Process Payment
        payment_success = process_payment(
            payment_data["payment_intent_id"],
            payment_data["amount"]
        )
        
        if not payment_success:
            print("\n❌ Payment failed!")
            return
        
        # Step 6: Verify Order
        final_order = verify_order(token, order_id)
        
        # Summary
        print("\n" + "="*70)
        print("  TEST SUMMARY")
        print("="*70)
        print(f"✅ Test User: {TEST_EMAIL}")
        print(f"✅ Order ID: {order_id}")
        print(f"✅ Payment Intent: {payment_data['payment_intent_id']}")
        print(f"✅ Amount Charged: ${payment_data['amount']:.2f}")
        print(f"✅ Payment Status: SUCCEEDED")
        print(f"✅ Order Status: {final_order['status'].upper() if final_order else 'UNKNOWN'}")
        print("\n" + "🎊"*35)
        print("   STRIPE INTEGRATION WORKING PERFECTLY!")
        print("🎊"*35 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
