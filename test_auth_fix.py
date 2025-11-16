#!/usr/bin/env python3
"""
Test Authentication Fix
Verifies that JWT tokens are now working correctly
"""
import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api/v1"

# Create unique test user
TEST_EMAIL = f"authtest_{uuid.uuid4().hex[:8]}@test.com"
TEST_USERNAME = f"authtest{uuid.uuid4().hex[:8]}"
TEST_PASSWORD = "TestPass123!"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_register():
    """Test user registration"""
    print_section("TEST 1: Register New User")
    
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "first_name": "Auth",
            "last_name": "Test"
        }
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ User registered successfully")
        print(f"   Email: {TEST_EMAIL}")
        print(f"   Username: {TEST_USERNAME}")
        return True
    else:
        print(f"❌ Registration failed: {response.text}")
        return False

def test_login():
    """Test login and token generation"""
    print_section("TEST 2: Login and Get Token")
    
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print(f"✅ Login successful!")
        print(f"   Token: {token[:50]}...")
        print(f"   Type: {data['token_type']}")
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_authenticated_endpoint(token):
    """Test accessing protected endpoint with token"""
    print_section("TEST 3: Access Protected Endpoint")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test /users/me endpoint
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Authentication successful!")
        print(f"   User ID: {user['id']}")
        print(f"   Email: {user['email']}")
        print(f"   Username: {user['username']}")
        return True
    else:
        print(f"❌ Authentication failed: {response.text}")
        return False

def test_token_structure(token):
    """Decode and verify token structure"""
    print_section("TEST 4: Verify Token Structure")
    
    try:
        from jose import jwt
        from datetime import datetime
        from app.core.config import settings
        
        # Decode token to inspect (verification happens in the API)
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        print(f"✅ Token decoded successfully")
        print(f"   Subject (user_id): {decoded.get('sub')}")
        print(f"   Expiration: {decoded.get('exp')}")
        
        # Check if exp is a valid timestamp
        if isinstance(decoded.get('exp'), int):
            exp_datetime = datetime.fromtimestamp(decoded['exp'])
            print(f"   Expires at: {exp_datetime}")
            print(f"   ✅ Expiration is a valid Unix timestamp")
        else:
            print(f"   ❌ Expiration is not a Unix timestamp: {type(decoded.get('exp'))}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Token decoding failed: {str(e)}")
        return False

def main():
    """Run all authentication tests"""
    print("\n" + "🔐"*35)
    print("         AUTHENTICATION FIX VERIFICATION TEST")
    print("🔐"*35)
    
    # Test 1: Register
    if not test_register():
        print("\n❌ Test suite failed at registration")
        return
    
    # Test 2: Login
    token = test_login()
    if not token:
        print("\n❌ Test suite failed at login")
        return
    
    # Test 3: Authenticated request
    if not test_authenticated_endpoint(token):
        print("\n❌ Test suite failed at authentication")
        return
    
    # Test 4: Token structure
    if not test_token_structure(token):
        print("\n❌ Test suite failed at token validation")
        return
    
    # Summary
    print_section("TEST SUMMARY")
    print("✅ User Registration: PASSED")
    print("✅ User Login: PASSED")
    print("✅ Token Generation: PASSED")
    print("✅ Protected Endpoint Access: PASSED")
    print("✅ Token Structure: PASSED")
    
    print("\n" + "🎉"*35)
    print("   ALL AUTHENTICATION TESTS PASSED!")
    print("   Your authentication is now working correctly!")
    print("🎉"*35 + "\n")
    
    print("\n📝 Frontend can now:")
    print("1. Register users via POST /api/v1/auth/register")
    print("2. Login via POST /api/v1/auth/token")
    print("3. Access protected endpoints with Bearer token")
    print("4. Token will auto-expire after 8 days\n")

if __name__ == "__main__":
    main()
