#!/usr/bin/env python3
"""
Test script for FreshCart E-Commerce API
This script tests all the major endpoints to ensure they're working correctly.
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("🔐 Testing Authentication Endpoints...")
    
    # Use timestamp to create unique email
    import time
    unique_email = f"test{int(time.time())}@example.com"
    
    # Test registration
    register_data = {
        "email": unique_email,
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{API_URL}/auth/register", json=register_data)
    print(f"Register: {response.status_code}")
    if response.status_code != 200:
        print(f"Register Error: {response.text}")
        # Try with existing user for login test
        unique_email = "test@example.com"
    
    # Test login
    login_data = {
        "email": unique_email,
        "password": "testpassword123"
    }
    
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    print(f"Login: {response.status_code}")
    if response.status_code != 200:
        print(f"Login Error: {response.text}")
        return None
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_user_endpoints(headers):
    """Test user endpoints"""
    print("👤 Testing User Endpoints...")
    
    # Get user profile
    response = requests.get(f"{API_URL}/users/profile", headers=headers)
    print(f"Get Profile: {response.status_code}")
    
    # Update profile
    update_data = {
        "first_name": "Updated",
        "phone": "+1234567890"
    }
    response = requests.put(f"{API_URL}/users/profile", json=update_data, headers=headers)
    print(f"Update Profile: {response.status_code}")

def test_category_endpoints(headers):
    """Test category endpoints"""
    print("📂 Testing Category Endpoints...")
    
    # Get categories
    response = requests.get(f"{API_URL}/categories")
    print(f"Get Categories: {response.status_code}")
    
    # Create category (requires admin)
    category_data = {
        "name": "Test Category",
        "slug": "test-category",
        "description": "A test category"
    }
    response = requests.post(f"{API_URL}/categories", json=category_data, headers=headers)
    print(f"Create Category: {response.status_code}")

def test_product_endpoints(headers):
    """Test product endpoints"""
    print("🛍️ Testing Product Endpoints...")
    
    # Get products
    response = requests.get(f"{API_URL}/products")
    print(f"Get Products: {response.status_code}")
    
    # Get featured products
    response = requests.get(f"{API_URL}/products/featured")
    print(f"Get Featured Products: {response.status_code}")
    
    # Search products
    response = requests.get(f"{API_URL}/products/search?q=test")
    print(f"Search Products: {response.status_code}")

def test_cart_endpoints(headers):
    """Test cart endpoints"""
    print("🛒 Testing Cart Endpoints...")
    
    # Get cart
    response = requests.get(f"{API_URL}/cart", headers=headers)
    print(f"Get Cart: {response.status_code}")
    
    # Add item to cart (requires valid product ID)
    cart_item_data = {
        "product_id": "test-product-id",
        "quantity": 2
    }
    response = requests.post(f"{API_URL}/cart/items", json=cart_item_data, headers=headers)
    print(f"Add to Cart: {response.status_code}")

def test_wishlist_endpoints(headers):
    """Test wishlist endpoints"""
    print("❤️ Testing Wishlist Endpoints...")
    
    # Get wishlist
    response = requests.get(f"{API_URL}/wishlist", headers=headers)
    print(f"Get Wishlist: {response.status_code}")
    
    # Add item to wishlist
    wishlist_item_data = {
        "product_id": "test-product-id"
    }
    response = requests.post(f"{API_URL}/wishlist/items", json=wishlist_item_data, headers=headers)
    print(f"Add to Wishlist: {response.status_code}")

def test_address_endpoints(headers):
    """Test address endpoints"""
    print("🏠 Testing Address Endpoints...")
    
    # Get addresses
    response = requests.get(f"{API_URL}/addresses", headers=headers)
    print(f"Get Addresses: {response.status_code}")
    
    # Create address
    address_data = {
        "type": "shipping",
        "first_name": "Test",
        "last_name": "User",
        "address_line_1": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "postal_code": "12345",
        "country": "US"
    }
    response = requests.post(f"{API_URL}/addresses", json=address_data, headers=headers)
    print(f"Create Address: {response.status_code}")

def test_order_endpoints(headers):
    """Test order endpoints"""
    print("📦 Testing Order Endpoints...")
    
    # Get orders
    response = requests.get(f"{API_URL}/orders", headers=headers)
    print(f"Get Orders: {response.status_code}")

def test_review_endpoints(headers):
    """Test review endpoints"""
    print("⭐ Testing Review Endpoints...")
    
    # Get user reviews
    response = requests.get(f"{API_URL}/reviews/user", headers=headers)
    print(f"Get User Reviews: {response.status_code}")

def test_notification_endpoints(headers):
    """Test notification endpoints"""
    print("🔔 Testing Notification Endpoints...")
    
    # Get notifications
    response = requests.get(f"{API_URL}/notifications", headers=headers)
    print(f"Get Notifications: {response.status_code}")

def test_coupon_endpoints(headers):
    """Test coupon endpoints"""
    print("🎫 Testing Coupon Endpoints...")
    
    # Validate coupon
    coupon_data = {
        "code": "TEST10",
        "cart_total": 50.0
    }
    response = requests.post(f"{API_URL}/coupons/validate", json=coupon_data, headers=headers)
    print(f"Validate Coupon: {response.status_code}")

def main():
    """Main test function"""
    print("🚀 Starting FreshCart API Tests...\n")
    
    # Test authentication first
    headers = test_auth_endpoints()
    
    if not headers:
        print("❌ Authentication failed. Cannot proceed with other tests.")
        return
    
    print("✅ Authentication successful!\n")
    
    # Test all other endpoints
    test_user_endpoints(headers)
    print()
    
    test_category_endpoints(headers)
    print()
    
    test_product_endpoints(headers)
    print()
    
    test_cart_endpoints(headers)
    print()
    
    test_wishlist_endpoints(headers)
    print()
    
    test_address_endpoints(headers)
    print()
    
    test_order_endpoints(headers)
    print()
    
    test_review_endpoints(headers)
    print()
    
    test_notification_endpoints(headers)
    print()
    
    test_coupon_endpoints(headers)
    print()
    
    print("🎉 API Tests Completed!")
    print(f"📖 View API Documentation: {BASE_URL}/docs")
    print(f"🔍 View OpenAPI Schema: {BASE_URL}/openapi.json")

if __name__ == "__main__":
    main()
