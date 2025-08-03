import pytest
from fastapi import status

from app.core.config import settings


def test_login_success(client, normal_user):
    """Test successful login with correct credentials"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "normaluser", "password": "userpassword"},
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    token = response.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"


def test_login_incorrect_password(client, normal_user):
    """Test login with incorrect password"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "normaluser", "password": "wrongpassword"},
    )
    
    # Check response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "nonexistentuser", "password": "password"},
    )
    
    # Check response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_user(client):
    """Test user registration"""
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newuserpassword",
        "full_name": "New Test User"
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=user_data,
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["full_name"] == user_data["full_name"]
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_existing_email(client, normal_user):
    """Test registration with existing email"""
    user_data = {
        "email": "user@example.com",  # Same as normal_user
        "username": "differentusername",
        "password": "password123",
        "full_name": "Different User"
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=user_data,
    )
    
    # Check response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
