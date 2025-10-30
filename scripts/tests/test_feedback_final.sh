#!/bin/bash

USER_ID="8d86607d-b0da-4c46-b735-0ea237a3e87a"
ARTICLE_ID="da6bd79d-0ecd-478b-84a2-48fcd751331c"

echo "=== Testing Analytics Tracking ==="
echo ""

echo "1. Calling feedback endpoint (no digest_id)..."
curl -s "http://localhost:8000/api/v1/feedback/track?article_id=${ARTICLE_ID}&user_id=${USER_ID}&type=thumbs_up"
echo ""
echo ""

sleep 3

echo "2. Checking company_analytics..."
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c "SELECT * FROM company_analytics;"
echo ""

echo "3. Checking industry_analytics..."
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c "SELECT * FROM industry_analytics;"
echo ""

echo "4. Checking article_analytics..."
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c "SELECT * FROM article_analytics WHERE article_id = '${ARTICLE_ID}';"
echo ""

echo "=== Test Complete ==="
