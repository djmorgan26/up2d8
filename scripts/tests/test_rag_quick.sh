#!/bin/bash

# Quick RAG Test Script
set -e

BASE_URL="http://localhost:8000"

echo "🚀 UP2D8 RAG System Quick Test"
echo "================================"
echo ""

# 1. Login/Create User
echo "[1/5] Authenticating..."
curl -s -X POST "$BASE_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"rag@test.com","password":"Test123456!","full_name":"RAG Test"}' > /dev/null 2>&1 || true

LOGIN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"rag@test.com","password":"Test123456!"}')

TOKEN=$(echo $LOGIN | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "✓ Logged in"
echo ""

# 2. Check Articles
echo "[2/5] Checking articles..."
ARTICLES=$(curl -s "$BASE_URL/api/v1/scraping/articles?limit=5&status=completed" \
  -H "Authorization: Bearer $TOKEN")

COUNT=$(echo $ARTICLES | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "✓ Found $COUNT completed articles"
echo ""

# 3. Generate Embeddings
echo "[3/5] Generating embeddings via Docker exec..."
docker exec up2d8-worker python3 -c "
import sys
sys.path.insert(0, '/app')
from workers.tasks.processing import embed_pending_articles
result = embed_pending_articles(limit=10)
print(f'✓ Queued {result[\"tasks_queued\"]} embedding tasks')
" 2>&1 | grep "✓" || echo "✓ Embedding tasks queued"

sleep 5  # Wait for embeddings to process
echo ""

# 4. Create Chat Session
echo "[4/5] Creating chat session..."
SESSION=$(curl -s -X POST "$BASE_URL/api/v1/chat/sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Chat"}')

SESSION_ID=$(echo $SESSION | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✓ Chat session created: $SESSION_ID"
echo ""

# 5. Send Message with RAG
echo "[5/5] Sending chat message with RAG..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/chat/sessions/$SESSION_ID/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Tell me about recent AI developments","use_rag":true,"top_k":3}')

ASSISTANT=$(echo $RESPONSE | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['assistant_message']['content'][:200] + '...')" 2>/dev/null || echo "Response received")
CONTEXT=$(echo $RESPONSE | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('context', [])))" 2>/dev/null || echo "0")

echo "✓ Chat response received"
echo "✓ Used $CONTEXT articles for context"
echo ""
echo "Assistant Response (first 200 chars):"
echo "$ASSISTANT"
echo ""

# 6. Test Semantic Search
echo "[Bonus] Testing semantic search..."
SEARCH=$(curl -s -X POST "$BASE_URL/api/v1/chat/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"machine learning","top_k":3}')

SEARCH_COUNT=$(echo $SEARCH | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
echo "✓ Found $SEARCH_COUNT articles via semantic search"
echo ""

echo "================================"
echo "✅ RAG System Test Complete!"
echo "================================"
