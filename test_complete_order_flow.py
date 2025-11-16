#!/usr/bin/env python3
"""
Test Complete Order Creation Flow
1. Register & Login
2. Add items to cart
3. Create order WITHOUT shipping address
4. Success!
"""
import requests
import uuid

BASE_URL = "http://localhost:8000/api/v1"

# Create unique test user
TEST_EMAIL = f"orderflow_{uuid.uuid4().hex[:8]}@test.com"
TEST_USERNAME = f"orderflow{uuid.uuid4().hex[:8]}"
TEST_PASSWORD = "TestPass123!"

print("🛒 Testing COMPLETE Order Flow WITHOUT Shipping Address...\n")

# Step 1: Register & Login
print("1️⃣ Registering and logging in...")
requests.post(f"{BASE_URL}/auth/register", json={
    "email": TEST_EMAIL,
    "username": TEST_USERNAME,
    "password": TEST_PASSWORD,
    "first_name": "Order",
    "last_name": "Flow"
})

response = requests.post(f"{BASE_URL}/auth/token", data={
    "username": TEST_EMAIL,
    "password": TEST_PASSWORD
})

token = response.json()["access_token"]
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
print(f"✅ Logged in\n")

# Step 2: Get first available product
print("2️⃣ Finding a product to add to cart...")
response = requests.get(f"{BASE_URL}/products/?page=1&limit=1")
if response.status_code == 200:
    products = response.json()
    if products and len(products) > 0:
        product = products[0]
        product_id = product['id']
        product_price = product['price']
        print(f"✅ Found product: {product['name']} (${product_price})\n")
    else:
        print("❌ No products found. Please add products to the database first.")
        exit(1)
else:
    print(f"❌ Failed to get products: {response.text}")
    exit(1)

# Step 3: Add product to cart
print("3️⃣ Adding product to cart...")
response = requests.post(
    f"{BASE_URL}/cart/items",
    headers=headers,
    json={
        "product_id": product_id,
        "quantity": 2
    }
)

if response.status_code in [200, 201]:
    cart_item = response.json()
    print(f"✅ Added to cart: {cart_item['quantity']}x ${cart_item['price_at_time']}\n")
else:
    print(f"❌ Failed to add to cart: {response.text}")
    exit(1)

# Step 4: Verify cart has items
print("4️⃣ Checking cart...")
response = requests.get(f"{BASE_URL}/cart", headers=headers)
if response.status_code == 200:
    cart = response.json()
    print(f"✅ Cart has {len(cart['items'])} items")
    print(f"   Total: ${cart['total_price']:.2f}\n")
else:
    print(f"⚠️  Cart check failed: {response.text}\n")

# Step 5: Create order WITHOUT shipping address
print("5️⃣ Creating order WITHOUT shipping address...")
response = requests.post(
    f"{BASE_URL}/orders/",
    headers=headers,
    json={
        "notes": "Test order - no shipping address yet"
    }
)

print(f"Status: {response.status_code}")

if response.status_code in [200, 201]:
    order = response.json()
    print(f"\n✅ SUCCESS! Order created WITHOUT shipping address!")
    print(f"   Order ID: {order['id']}")
    print(f"   Order Number: {order['order_number']}")
    print(f"   Status: {order['status']}")
    print(f"   Shipping Address: {order.get('shipping_address_id', 'None/null')}")
    print(f"   Subtotal: ${order['subtotal']:.2f}")
    print(f"   Tax: ${order['tax_amount']:.2f}")
    print(f"   Shipping: ${order['shipping_cost']:.2f}")
    print(f"   Total: ${order['total_amount']:.2f}")
    print(f"   Items: {len(order.get('items', []))}")
    
    print("\n" + "="*70)
    print("🎉 SUCCESS! Backend fix is working!")
    print("="*70)
    print("\n📝 Your frontend workflow:")
    print("1. ✅ User adds items to cart")
    print("2. ✅ User clicks 'Checkout' → Creates order (no address needed)")
    print("3. → User is taken to checkout page")
    print("4. → User enters shipping info on checkout page")
    print("5. → Update order with shipping address")
    print("6. → Process payment with Stripe")
    print("7. → Order confirmed!")
    
    # Show how to update order with address later
    print("\n💡 To add shipping address later:")
    print(f"   PUT /api/v1/orders/{order['id']}")
    print("   Body: { \"shipping_address_id\": \"address_id_here\" }")
    
elif response.status_code == 400:
    print(f"❌ Order creation failed: {response.text}")
    print("\n🔍 Possible reasons:")
    print("1. Cart is empty (should have items now)")
    print("2. Other validation error")
    print("\nLet's check the error detail...")
    
else:
    print(f"❌ Unexpected error: {response.status_code}")
    print(f"Response: {response.text}")

# Step 6: Test with explicit null too
print("\n\n6️⃣ Testing with shipping_address_id = null explicitly...")
# First add another item to cart
requests.post(
    f"{BASE_URL}/cart/items",
    headers=headers,
    json={"product_id": product_id, "quantity": 1}
)

response = requests.post(
    f"{BASE_URL}/orders/",
    headers=headers,
    json={
        "shipping_address_id": None,
        "billing_address_id": None,
        "notes": "Test order with explicit nulls"
    }
)

if response.status_code in [200, 201]:
    print(f"✅ Also works with explicit null values!")
else:
    print(f"⚠️  With explicit null: {response.status_code}")
    print(f"   {response.text}")
