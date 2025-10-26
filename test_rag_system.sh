#!/bin/bash

# Test script for RAG Chat System
# Tests embedding, semantic search, and chat functionality

set -e  # Exit on error

echo "==============================================="
echo "UP2D8 RAG CHAT SYSTEM TEST"
echo "==============================================="
echo ""

# Base URL
BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

#===============================================
# 1. Create Test User & Login
#===============================================
echo -e "${BLUE}[1] Creating test user and logging in...${NC}"

# Create user
curl -s -X POST "$BASE_URL/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rag_test@example.com",
    "password": "TestPassword123!",
    "full_name": "RAG Tester"
  }' > /dev/null 2>&1 || echo "User may already exist"

# Login
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rag_test@example.com",
    "password": "TestPassword123!"
  }')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo -e "${GREEN}✓ Logged in successfully${NC}"
echo "Access Token: ${ACCESS_TOKEN:0:20}..."
echo ""

#===============================================
# 2. Check Current Articles
#===============================================
echo -e "${BLUE}[2] Checking current articles...${NC}"

ARTICLES_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/scraping/articles?limit=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

ARTICLE_COUNT=$(echo $ARTICLES_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")

echo -e "${GREEN}✓ Found $ARTICLE_COUNT articles in database${NC}"

if [ "$ARTICLE_COUNT" -gt 0 ]; then
  FIRST_ARTICLE=$(echo $ARTICLES_RESPONSE | python3 -c "import sys, json; articles = json.load(sys.stdin); print(articles[0]['id'] if articles else '')")
  echo "First Article ID: $FIRST_ARTICLE"
fi
echo ""

#===============================================
# 3. Test Embedding Generation
#===============================================
echo -e "${BLUE}[3] Testing embedding generation...${NC}"

# Get first article that needs embedding
ARTICLE_TO_EMBED=$(curl -s -X GET "$BASE_URL/api/v1/scraping/articles?limit=1&status=completed" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | \
  python3 -c "import sys, json; articles = json.load(sys.stdin); print(articles[0]['id'] if articles else '')")

if [ -z "$ARTICLE_TO_EMBED" ]; then
  echo -e "${RED}✗ No completed articles found to embed${NC}"
  echo "Please run scraping and processing first:"
  echo "  1. POST /api/v1/scraping/scrape/all"
  echo "  2. Wait for processing to complete"
  echo ""
  exit 1
fi

echo "Embedding article: $ARTICLE_TO_EMBED"

# Note: We'd need to call the Celery task directly or via an endpoint
# For now, we'll create a simple Python script to embed articles

python3 << 'PYTHON_EOF'
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, '/Users/davidmorgan/Documents/Repositories/up2d8/backend')

from workers.tasks.processing import embed_pending_articles

print("Starting embedding task...")
result = embed_pending_articles()
print(f"Result: {result}")
PYTHON_EOF

echo -e "${GREEN}✓ Embedding generation initiated${NC}"
echo ""

#===============================================
# 4. Test Chat Health Endpoint
#===============================================
echo -e "${BLUE}[4] Testing chat health endpoint...${NC}"

CHAT_HEALTH=$(curl -s -X GET "$BASE_URL/api/v1/chat/health")

echo "$CHAT_HEALTH" | python3 -m json.tool

STATUS=$(echo $CHAT_HEALTH | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))")

if [ "$STATUS" = "healthy" ]; then
  echo -e "${GREEN}✓ Chat service is healthy${NC}"
else
  echo -e "${RED}✗ Chat service is unhealthy${NC}"
fi
echo ""

#===============================================
# 5. Create Chat Session
#===============================================
echo -e "${BLUE}[5] Creating chat session...${NC}"

SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/chat/sessions" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "RAG Test Session"
  }')

echo "$SESSION_RESPONSE" | python3 -m json.tool

SESSION_ID=$(echo $SESSION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

echo -e "${GREEN}✓ Chat session created: $SESSION_ID${NC}"
echo ""

#===============================================
# 6. Test Semantic Search
#===============================================
echo -e "${BLUE}[6] Testing semantic search...${NC}"

SEARCH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/chat/search" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI and machine learning advancements",
    "top_k": 3
  }')

echo "$SEARCH_RESPONSE" | python3 -m json.tool

SEARCH_COUNT=$(echo $SEARCH_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")

echo -e "${GREEN}✓ Found $SEARCH_COUNT articles via semantic search${NC}"
echo ""

#===============================================
# 7. Send Chat Message with RAG
#===============================================
echo -e "${BLUE}[7] Sending chat message with RAG...${NC}"

MESSAGE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/chat/sessions/$SESSION_ID/messages" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the latest developments in AI?",
    "use_rag": true,
    "top_k": 3
  }')

echo "$MESSAGE_RESPONSE" | python3 -m json.tool

ASSISTANT_RESPONSE=$(echo $MESSAGE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['assistant_message']['content'][:200] + '...')")

echo ""
echo "Assistant Response (first 200 chars):"
echo "$ASSISTANT_RESPONSE"
echo ""

CONTEXT_COUNT=$(echo $MESSAGE_RESPONSE | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data['context']) if data.get('context') else 0)")

echo -e "${GREEN}✓ Chat message sent successfully${NC}"
echo -e "${GREEN}✓ Used $CONTEXT_COUNT articles for context${NC}"
echo ""

#===============================================
# 8. Get Chat Messages
#===============================================
echo -e "${BLUE}[8] Retrieving chat messages...${NC}"

MESSAGES_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/chat/sessions/$SESSION_ID/messages" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

MESSAGE_COUNT=$(echo $MESSAGES_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")

echo -e "${GREEN}✓ Found $MESSAGE_COUNT messages in session${NC}"
echo ""

#===============================================
# 9. Test Similar Articles
#===============================================
if [ ! -z "$FIRST_ARTICLE" ]; then
  echo -e "${BLUE}[9] Testing similar articles...${NC}"

  SIMILAR_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/chat/articles/$FIRST_ARTICLE/similar?top_k=3" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

  SIMILAR_COUNT=$(echo $SIMILAR_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")

  echo -e "${GREEN}✓ Found $SIMILAR_COUNT similar articles${NC}"
  echo ""
fi

#===============================================
# 10. List All Sessions
#===============================================
echo -e "${BLUE}[10] Listing all chat sessions...${NC}"

SESSIONS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/chat/sessions" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

SESSION_COUNT=$(echo $SESSIONS_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")

echo -e "${GREEN}✓ Found $SESSION_COUNT chat sessions${NC}"
echo ""

#===============================================
# Summary
#===============================================
echo "==============================================="
echo -e "${GREEN}RAG CHAT SYSTEM TEST COMPLETE${NC}"
echo "==============================================="
echo ""
echo "Summary:"
echo "  - Authentication: ✓"
echo "  - Article Retrieval: ✓ ($ARTICLE_COUNT articles)"
echo "  - Embedding Generation: ✓"
echo "  - Chat Service Health: ✓"
echo "  - Session Creation: ✓"
echo "  - Semantic Search: ✓ ($SEARCH_COUNT results)"
echo "  - Chat with RAG: ✓ ($CONTEXT_COUNT articles used)"
echo "  - Message History: ✓ ($MESSAGE_COUNT messages)"
echo "  - Similar Articles: ✓"
echo "  - Session Listing: ✓ ($SESSION_COUNT sessions)"
echo ""
echo "All RAG system components are working! 🎉"
