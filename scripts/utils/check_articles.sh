#!/bin/bash

LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"ai_tester@test.com\",\"password\":\"TestPassword123!\"}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Fetching first 3 articles..."
curl -s "http://localhost:8000/api/v1/scraping/articles?limit=3" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
