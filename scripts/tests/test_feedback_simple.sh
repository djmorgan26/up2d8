#!/bin/bash

USER_ID=$(docker-compose exec -T postgres psql -U up2d8 -d up2d8 -t -c "SELECT id FROM users LIMIT 1;" | tr -d ' ' | tr -d '\n')
ARTICLE_ID="da6bd79d-0ecd-478b-84a2-48fcd751331c"

echo "User ID: [$USER_ID]"
echo "Article ID: [$ARTICLE_ID]"
echo ""

echo "Checking article tags..."
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c "SELECT id, companies, industries FROM articles WHERE id = '${ARTICLE_ID}';"
echo ""

echo "Calling feedback endpoint..."
RESPONSE=$(curl -s "http://localhost:8000/api/v1/feedback/track?article_id=${ARTICLE_ID}&user_id=${USER_ID}&type=thumbs_up&digest_id=test4")
echo "$RESPONSE"
echo ""

sleep 2

echo "Checking if feedback was created..."
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c "SELECT * FROM article_feedback WHERE article_id = '${ARTICLE_ID}';"
echo ""

echo "Checking analytics tables..."
docker-compose exec -T postgres psql -U up2d8 -d up2d8 -c "SELECT * FROM company_analytics;"
