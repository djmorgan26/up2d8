#!/bin/bash

ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZDg2NjA3ZC1iMGRhLTRjNDYtYjczNS0wZWEyMzdhM2U4N2EiLCJleHAiOjE3NjEzMTM5NjIsImlhdCI6MTc2MTMxMzA2MiwidHlwZSI6ImFjY2VzcyJ9.w8HPGSwSFrPxjA4zQ9U-aSiha77nR0JyMSFe6PMBwzI"

echo "=========================================="
echo "UP2D8 Scraping System End-to-End Test"
echo "=========================================="
echo ""

echo "Test 1: Sync sources to database"
echo "-----------------------------------"
curl -s -X POST "http://localhost:8000/api/v1/scraping/sources/sync" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

sleep 3

echo "Test 2: List all sources"
echo "-----------------------------------"
curl -s "http://localhost:8000/api/v1/scraping/sources?limit=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool | head -50
echo ""

echo "Test 3: Check scraping health"
echo "-----------------------------------"
curl -s "http://localhost:8000/api/v1/scraping/health" | python3 -m json.tool
echo ""

echo "Test 4: Manually trigger scrape for one source"
echo "-----------------------------------"
curl -s -X POST "http://localhost:8000/api/v1/scraping/scrape/openai_blog" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

echo "Waiting 10 seconds for scraping to complete..."
sleep 10

echo ""
echo "Test 5: Check articles"
echo "-----------------------------------"
curl -s "http://localhost:8000/api/v1/scraping/articles?limit=5" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool | head -100
echo ""

echo "Test 6: Get article statistics"
echo "-----------------------------------"
curl -s "http://localhost:8000/api/v1/scraping/articles/stats" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

echo "=========================================="
echo "Tests Complete!"
echo "=========================================="
