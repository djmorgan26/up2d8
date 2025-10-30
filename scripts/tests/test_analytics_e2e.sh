#!/bin/bash

# End-to-End Analytics Testing Script

set -e  # Exit on error

echo "========================================"
echo "UP2D8 Analytics E2E Test"
echo "========================================"
echo ""

# Step 1: Login
echo "1. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}')

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -m json.tool | grep -A 1 '"access_token"' | tail -1 | cut -d'"' -f2)
USER_ID=$(echo "$LOGIN_RESPONSE" | python3 -m json.tool | grep -A 1 '"id"' | grep -v "digest_id" | tail -1 | cut -d'"' -f2)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Login failed"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Logged in (User ID: $USER_ID)"
echo ""

# Step 2: Scrape articles from Anthropic GitHub (has company tags)
echo "2. Scraping articles from Anthropic GitHub..."
SCRAPE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/scraping/scrape/anthropic_github \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$SCRAPE_RESPONSE" | python3 -m json.tool
echo ""

# Wait for scraping to complete
sleep 3

# Step 3: Check if articles have company/industry tags
echo "3. Verifying articles have company/industry tags..."
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c \
  "SELECT id, title, companies, industries FROM articles WHERE source_id = 'anthropic_github' LIMIT 3;"
echo ""

# Step 4: Get one article ID for testing
ARTICLE_ID=$(docker-compose exec -T postgres psql -U up2d8 -d up2d8 -t -c \
  "SELECT id FROM articles WHERE source_id = 'anthropic_github' LIMIT 1;" | tr -d ' ')

if [ -z "$ARTICLE_ID" ]; then
  echo "❌ No articles found from Anthropic GitHub"
  exit 1
fi

echo "✅ Using article ID: $ARTICLE_ID"
echo ""

# Step 5: Simulate giving feedback (thumbs up)
echo "4. Simulating user feedback (thumbs up)..."
FEEDBACK_URL="http://localhost:8000/api/v1/feedback/track?article_id=${ARTICLE_ID}&user_id=${USER_ID}&type=thumbs_up&digest_id=test"

curl -s "$FEEDBACK_URL" > /dev/null
echo "✅ Feedback recorded"
echo ""

# Wait for analytics to be updated
sleep 2

# Step 6: Check analytics tables
echo "5. Verifying analytics data..."
echo ""

echo "--- Company Analytics ---"
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c \
  "SELECT company_name, total_positive_feedback, popularity_score FROM company_analytics ORDER BY popularity_score DESC LIMIT 5;"
echo ""

echo "--- Industry Analytics ---"
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c \
  "SELECT industry_name, total_positive_feedback, popularity_score FROM industry_analytics ORDER BY popularity_score DESC LIMIT 5;"
echo ""

echo "--- Source Analytics ---"
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c \
  "SELECT s.name, sa.total_positive_feedback, sa.engagement_rate FROM source_analytics sa JOIN sources s ON sa.source_id = s.id WHERE s.id = 'anthropic_github';"
echo ""

echo "--- Article Analytics ---"
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c \
  "SELECT article_id, positive_feedback_count FROM article_analytics WHERE article_id = '${ARTICLE_ID}';"
echo ""

# Step 7: Test analytics API endpoints
echo "6. Testing analytics API endpoints..."
echo ""

echo "--- GET /analytics/companies/top ---"
curl -s "http://localhost:8000/api/v1/analytics/companies/top?limit=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

echo "--- GET /analytics/industries/top ---"
curl -s "http://localhost:8000/api/v1/analytics/industries/top?limit=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

echo "--- GET /analytics/summary ---"
curl -s "http://localhost:8000/api/v1/analytics/summary" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

echo "========================================"
echo "✅ Analytics E2E Test Complete!"
echo "========================================"
