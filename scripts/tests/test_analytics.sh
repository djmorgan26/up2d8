#!/bin/bash

# Test Analytics System

echo "=== Testing UP2D8 Analytics System ==="
echo ""

# Login to get access token
echo "1. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"SecurePass123!\"}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -m json.tool | grep access_token | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Login failed"
  echo $LOGIN_RESPONSE | python3 -m json.tool
  exit 1
fi

echo "✅ Logged in successfully"
echo ""

# Test top companies endpoint
echo "2. Testing GET /analytics/companies/top"
curl -s "http://localhost:8000/api/v1/analytics/companies/top?limit=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

# Test top industries endpoint
echo "3. Testing GET /analytics/industries/top"
curl -s "http://localhost:8000/api/v1/analytics/industries/top?limit=10" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

# Test source performance endpoint
echo "4. Testing GET /analytics/sources/performance"
curl -s "http://localhost:8000/api/v1/analytics/sources/performance" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

# Test daily stats endpoint
echo "5. Testing GET /analytics/daily/stats"
curl -s "http://localhost:8000/api/v1/analytics/daily/stats?days=7" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

# Test summary endpoint
echo "6. Testing GET /analytics/summary"
curl -s "http://localhost:8000/api/v1/analytics/summary" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

echo "=== Analytics Testing Complete ==="
