import requests
import json

# Create admin user
url = "http://localhost:8000/api/v1/auth/register"
payload = {
    "email": "lin.kevin.1923@gmail.com",
    "first_name": "Kevin",
    "last_name": "Lin (ADMIN)",
    "phone": "string",
    "date_of_birth": "2025-12-23",
    "is_active": True,
    "is_admin": True,
    "is_verified": True,
    "username": "string",
    "password": "@Kevinlin1234"
}

print("Creating admin user...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

response = requests.post(url, json=payload)
print(f"\nStatus Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
