#!/bin/bash
echo "Testing production address creation..."
curl -X POST 'https://fastapi.kevinlinportfolio.com/api/v1/addresses/' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjQwMjQ0MzIsInN1YiI6IjZkMjRiZDRhLWQ2MTMtNGIyNC04ZGMwLWZmYTkyM2M0NjdjOSJ9.Xq7edD4olV711yGyTrIvSW6oMEwri0vrAU_pdDYBrl4' \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "shipping",
    "first_name": "John",
    "last_name": "Doe",
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "country": "US",
    "phone": "555-1234",
    "is_default": true
  }' | python3 -m json.tool
