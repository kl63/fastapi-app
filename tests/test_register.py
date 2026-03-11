import requests
import json

# Test user registration
url = "http://localhost:8000/api/v1/auth/register"
payload = {
    "email": "testuser123@example.com",
    "username": "testuser123",
    "password": "Test123456!",
    "first_name": "Test",
    "last_name": "User"
}

print("Testing user registration...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

response = requests.post(url, json=payload)
print(f"\nStatus Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
