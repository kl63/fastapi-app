#!/usr/bin/env python3
"""
Test Stripe Payment Flow with Dummy Card
This script demonstrates the complete payment flow using Stripe test cards
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "lin.kevin.1923@gmail.com"
TEST_USER_PASSWORD = "your_password_here"  # Replace with actual password

# Stripe test card - always succeeds
TEST_CARD = {
    "number": "4242424242424242",
    "exp_month": 12,
    "exp_year": 2034,
    "cvc": "123"
}

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_json(data, title=""):
    """Pretty print JSON data"""
    if title:
        print(f"\n{title}:")
    print(json.dumps(data, indent=2))

def login():
    """Login and get JWT token"""
    print_header("Step 1: Login to Get Token")
    
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return None
    
    data = response.json()
    token = data["access_token"]
    print(f"✅ Login successful!")
    print(f"Token: {token[:50]}...")
    return token

def get_or_create_address(token):
    """Get or create a test address"""
    print_header("Step 2: Get/Create Shipping Address")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to get existing addresses
    response = requests.get(f"{BASE_URL}/addresses", headers=headers)
    
    if response.status_code == 200:
        addresses = response.json()
        if addresses:
            address = addresses[0]
            print(f"✅ Using existing address: {address['id']}")
            print_json(address, "Address Details")
            return address["id"]
    
    # Create new address
    print("Creating new address...")
    response = requests.post(
        f"{BASE_URL}/addresses",
        headers=headers,
        json={
            "type": "both",
            "first_name": "John",
            "last_name": "Doe",
            "street": "123 Test Street",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94102",
            "country": "USA",
            "phone": "555-0123",
            "is_default": True
        }
    )
    
    if response.status_code in [200, 201]:
        address = response.json()
        print(f"✅ Address created: {address['id']}")
        print_json(address, "Address Details")
        return address["id"]
    else:
        print(f"❌ Failed to create address: {response.text}")
        return None

def create_test_order(token, address_id):
    """Create a test order"""
    print_header("Step 3: Create Test Order")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    order_data = {
        "shipping_address_id": address_id,
        "billing_address_id": address_id,
        "notes": "Test order for Stripe payment integration"
    }
    
    response = requests.post(
        f"{BASE_URL}/orders",
        headers=headers,
        json=order_data
    )
    
    if response.status_code in [200, 201]:
        order = response.json()
        print(f"✅ Order created successfully!")
        print(f"Order ID: {order['id']}")
        print(f"Order Number: {order['order_number']}")
        print(f"Status: {order['status']}")
        print(f"Total Amount: ${order['total_amount']:.2f}")
        print_json(order, "Order Details")
        return order
    else:
        print(f"❌ Failed to create order: {response.text}")
        return None

def create_payment_intent(token, order_id):
    """Create Stripe PaymentIntent"""
    print_header("Step 4: Create Stripe Payment Intent")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/orders/{order_id}/create-payment-intent",
        headers=headers
    )
    
    if response.status_code == 200:
        payment_data = response.json()
        print(f"✅ Payment Intent created successfully!")
        print(f"Payment Intent ID: {payment_data['payment_intent_id']}")
        print(f"Amount: ${payment_data['amount']:.2f}")
        print(f"Currency: {payment_data['currency'].upper()}")
        print(f"Client Secret: {payment_data['client_secret'][:50]}...")
        print_json(payment_data, "Payment Intent Details")
        return payment_data
    else:
        print(f"❌ Failed to create payment intent: {response.text}")
        return None

def simulate_frontend_payment(client_secret, payment_intent_id):
    """Simulate what the frontend would do with Stripe.js"""
    print_header("Step 5: Frontend Payment Simulation")
    
    print("In a real frontend (Next.js), you would:")
    print("1. Use the client_secret with Stripe Elements")
    print("2. Collect card details from user")
    print("3. Call stripe.confirmCardPayment()")
    print("\nFor testing, use these test cards:")
    print("  • 4242 4242 4242 4242 (Success)")
    print("  • 4000 0000 0000 9995 (Decline - Insufficient funds)")
    print("  • 4000 0025 0000 3155 (Requires 3D Secure)")
    
    print("\n🔧 Using Stripe API directly to complete payment...")
    
    import stripe
    from app.core.config import settings
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        # Confirm the payment with test card
        payment_intent = stripe.PaymentIntent.confirm(
            payment_intent_id,
            payment_method_data={
                "type": "card",
                "card": {
                    "number": TEST_CARD["number"],
                    "exp_month": TEST_CARD["exp_month"],
                    "exp_year": TEST_CARD["exp_year"],
                    "cvc": TEST_CARD["cvc"],
                }
            }
        )
        
        print(f"✅ Payment completed!")
        print(f"Status: {payment_intent.status}")
        print(f"Amount: ${payment_intent.amount / 100:.2f}")
        return payment_intent.status == "succeeded"
        
    except Exception as e:
        print(f"❌ Payment failed: {str(e)}")
        return False

def verify_order_status(token, order_id):
    """Verify the order status was updated"""
    print_header("Step 6: Verify Order Status")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/orders/{order_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        order = response.json()
        print(f"✅ Order Status: {order['status']}")
        print(f"Order Number: {order['order_number']}")
        print(f"Total: ${order['total_amount']:.2f}")
        
        if order['status'] == 'confirmed':
            print("\n🎉 SUCCESS! Payment processed and order confirmed!")
        else:
            print(f"\n⚠️  Order is still {order['status']}")
            print("Note: Webhook may take a few seconds to update status")
        
        return order
    else:
        print(f"❌ Failed to get order: {response.text}")
        return None

def main():
    """Run the complete payment flow test"""
    print("\n" + "🔥"*30)
    print("  STRIPE PAYMENT INTEGRATION TEST")
    print("  Using Test Card: 4242 4242 4242 4242")
    print("🔥"*30)
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n❌ Test failed at login step")
        return
    
    # Step 2: Get/Create Address
    address_id = get_or_create_address(token)
    if not address_id:
        print("\n❌ Test failed at address step")
        return
    
    # Step 3: Create Order
    order = create_test_order(token, address_id)
    if not order:
        print("\n❌ Test failed at order creation step")
        return
    
    order_id = order["id"]
    
    # Step 4: Create Payment Intent
    payment_data = create_payment_intent(token, order_id)
    if not payment_data:
        print("\n❌ Test failed at payment intent step")
        return
    
    # Step 5: Simulate Payment (what frontend does)
    payment_success = simulate_frontend_payment(
        payment_data["client_secret"],
        payment_data["payment_intent_id"]
    )
    
    if not payment_success:
        print("\n❌ Test failed at payment step")
        return
    
    # Wait a moment for webhook
    import time
    print("\n⏳ Waiting 2 seconds for webhook to process...")
    time.sleep(2)
    
    # Step 6: Verify Order Status
    final_order = verify_order_status(token, order_id)
    
    # Final Summary
    print_header("TEST SUMMARY")
    print(f"✅ Order Created: {order_id}")
    print(f"✅ Payment Intent: {payment_data['payment_intent_id']}")
    print(f"✅ Payment Status: {'SUCCEEDED' if payment_success else 'FAILED'}")
    print(f"✅ Final Order Status: {final_order['status'] if final_order else 'UNKNOWN'}")
    
    print("\n" + "🎊"*30)
    print("  STRIPE INTEGRATION TEST COMPLETE!")
    print("🎊"*30 + "\n")

if __name__ == "__main__":
    main()
