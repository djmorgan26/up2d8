#!/bin/bash

echo "==========================================  "
echo "Testing TechCrunch AI Scrape"
echo "=========================================="
echo ""

echo "Step 1: Login and get token"
echo "-----------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"scraper@test.com\",\"password\":\"TestPassword123!\"}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Login failed. Creating new account..."
    curl -s -X POST "http://localhost:8000/api/v1/auth/signup" \
      -H "Content-Type: application/json" \
      -d "{\"email\":\"tester@test.com\",\"password\":\"TestPassword123!\",\"full_name\":\"Tester\"}" | python3 -m json.tool

    echo ""
    echo "Re-attempting login..."
    LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
      -H "Content-Type: application/json" \
      -d "{\"email\":\"tester@test.com\",\"password\":\"TestPassword123!\"}")
    ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
fi

echo "✅ Authenticated"
echo ""

echo "Step 2: Trigger TechCrunch AI scrape"
echo "-----------------------------------"
curl -s -X POST "http://localhost:8000/api/v1/scraping/scrape/techcrunch_ai" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

echo "Waiting 15 seconds for scrape to complete..."
sleep 15
echo ""

echo "Step 3: Check articles"
echo "-----------------------------------"
curl -s "http://localhost:8000/api/v1/scraping/articles?limit=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

echo "Step 4: Get article statistics"
echo "-----------------------------------"
curl -s "http://localhost:8000/api/v1/scraping/articles/stats" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

echo "=========================================="
echo "Test Complete!"
echo "=========================================="
