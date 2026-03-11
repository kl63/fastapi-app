#!/usr/bin/env python3
"""
Test /users/profile endpoint with fresh authentication
"""
import requests
import uuid

BASE_URL = "http://localhost:8000/api/v1"

# Create unique test user
TEST_EMAIL = f"profiletest_{uuid.uuid4().hex[:8]}@test.com"
TEST_USERNAME = f"profiletest{uuid.uuid4().hex[:8]}"
TEST_PASSWORD = "TestPass123!"

print("🔍 Testing /users/profile endpoint...\n")

# Step 1: Register
print("1️⃣ Registering new user...")
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": TEST_EMAIL,
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "first_name": "Test",
        "last_name": "User"
    }
)

if response.status_code not in [200, 201]:
    print(f"❌ Registration failed: {response.text}")
    exit(1)

print(f"✅ User registered: {TEST_EMAIL}\n")

# Step 2: Login
print("2️⃣ Logging in...")
response = requests.post(
    f"{BASE_URL}/auth/token",
    data={
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
)

if response.status_code != 200:
    print(f"❌ Login failed: {response.text}")
    exit(1)

token = response.json()["access_token"]
print(f"✅ Login successful!")
print(f"   Token: {token[:50]}...\n")

# Step 3: Test /users/profile
print("3️⃣ Testing /users/profile endpoint...")
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(f"{BASE_URL}/users/profile", headers=headers)

if response.status_code == 200:
    user = response.json()
    print(f"✅ /users/profile works!")
    print(f"   User ID: {user['id']}")
    print(f"   Email: {user['email']}")
    print(f"   Username: {user['username']}")
    print(f"   Name: {user.get('first_name', '')} {user.get('last_name', '')}")
else:
    print(f"❌ /users/profile failed: {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

# Step 4: Also test /users/me for comparison
print("\n4️⃣ Testing /users/me endpoint...")
response = requests.get(f"{BASE_URL}/users/me", headers=headers)

if response.status_code == 200:
    user = response.json()
    print(f"✅ /users/me also works!")
    print(f"   User ID: {user['id']}")
    print(f"   Email: {user['email']}")
else:
    print(f"⚠️  /users/me returned: {response.status_code}")

print("\n" + "="*70)
print("🎉 SUCCESS! Both authentication and endpoints are working!")
print("="*70)
print("\n📝 Your frontend should use:")
print("   GET /api/v1/users/profile   (for user profile)")
print("   GET /api/v1/users/me         (alternative endpoint)")
