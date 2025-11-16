#!/usr/bin/env python3
"""
Test Order Creation WITHOUT Shipping Address
Verifies that shipping_address_id is now optional
"""
import requests
import uuid
import json

BASE_URL = "http://localhost:8000/api/v1"

# Create unique test user
TEST_EMAIL = f"ordertest_{uuid.uuid4().hex[:8]}@test.com"
TEST_USERNAME = f"ordertest{uuid.uuid4().hex[:8]}"
TEST_PASSWORD = "TestPass123!"

print("🛒 Testing Order Creation WITHOUT Shipping Address...\n")

# Step 1: Register & Login
print("1️⃣ Registering and logging in...")
requests.post(f"{BASE_URL}/auth/register", json={
    "email": TEST_EMAIL,
    "username": TEST_USERNAME,
    "password": TEST_PASSWORD,
    "first_name": "Order",
    "last_name": "Test"
})

response = requests.post(f"{BASE_URL}/auth/token", data={
    "username": TEST_EMAIL,
    "password": TEST_PASSWORD
})

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Logged in\n")

# Step 2: Add item to cart (optional - just for context)
print("2️⃣ Creating order WITHOUT shipping address...")

# Test creating order without shipping_address_id
order_data = {
    "notes": "Test order - no shipping address yet"
    # shipping_address_id intentionally omitted!
}

response = requests.post(
    f"{BASE_URL}/orders",
    headers=headers,
    json=order_data
)

print(f"Status: {response.status_code}")

if response.status_code in [200, 201]:
    order = response.json()
    print(f"✅ Order created successfully WITHOUT shipping address!")
    print(f"   Order ID: {order['id']}")
    print(f"   Order Number: {order['order_number']}")
    print(f"   Status: {order['status']}")
    print(f"   Shipping Address: {order.get('shipping_address_id', 'None')}")
    print(f"   Total: ${order['total_amount']:.2f}")
    
    print("\n" + "="*70)
    print("🎉 SUCCESS! Order schema fix is working!")
    print("="*70)
    print("\n📝 Your frontend can now:")
    print("1. Create order without shipping address")
    print("2. Collect shipping info on checkout page")
    print("3. Update order with shipping address later")
    
else:
    print(f"❌ Order creation failed: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Show what the API expects
    print("\n📋 Let's check the API docs...")
    response = requests.get("http://localhost:8000/openapi.json")
    openapi = response.json()
    
    # Find OrderCreate schema
    if "components" in openapi and "schemas" in openapi["components"]:
        order_create = openapi["components"]["schemas"].get("OrderCreate", {})
        print("\nOrderCreate schema:")
        print(json.dumps(order_create, indent=2))

# Step 3: Test with shipping_address_id = null explicitly
print("\n\n3️⃣ Testing with shipping_address_id = null explicitly...")

order_data_with_null = {
    "shipping_address_id": None,
    "notes": "Test order - shipping address explicitly null"
}

response = requests.post(
    f"{BASE_URL}/orders",
    headers=headers,
    json=order_data_with_null
)

if response.status_code in [200, 201]:
    print(f"✅ Also works with explicit null!")
else:
    print(f"⚠️  With explicit null: {response.status_code}")
    print(f"Response: {response.text}")
