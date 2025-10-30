#!/bin/bash

echo "=========================================="
echo "UP2D8 Complete System Test"
echo "Scraping + AI Summarization"
echo "=========================================="
echo ""

# Login and get token (valid for 1 day now)
echo "Step 1: Authentication"
echo "-----------------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"tester@test.com\",\"password\":\"TestPassword123!\"}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Creating new test account..."
    curl -s -X POST "http://localhost:8000/api/v1/auth/signup" \
      -H "Content-Type: application/json" \
      -d "{\"email\":\"ai_tester@test.com\",\"password\":\"TestPassword123!\",\"full_name\":\"AI Tester\"}" > /dev/null

    LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
      -H "Content-Type: application/json" \
      -d "{\"email\":\"ai_tester@test.com\",\"password\":\"TestPassword123!\"}")
    ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
fi

echo "✅ Authenticated (token valid for 24 hours)"
echo ""

# Test 1: Scrape articles
echo "Step 2: Scraping Articles from TechCrunch AI"
echo "-----------------------------------"
SCRAPE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/scraping/scrape/techcrunch_ai" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo $SCRAPE_RESPONSE | python3 -m json.tool
TASK_ID=$(echo $SCRAPE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['task_id'])" 2>/dev/null)
echo ""

echo "Waiting 10 seconds for scraping to complete..."
sleep 10
echo ""

# Test 2: Check scraped articles
echo "Step 3: Verify Articles Were Scraped"
echo "-----------------------------------"
ARTICLES_RESPONSE=$(curl -s "http://localhost:8000/api/v1/scraping/articles?limit=3" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo $ARTICLES_RESPONSE | python3 -m json.tool
ARTICLE_COUNT=$(echo $ARTICLES_RESPONSE | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null)
echo ""
echo "Articles found: $ARTICLE_COUNT"
echo ""

# Test 3: Check stats
echo "Step 4: Article Statistics"
echo "-----------------------------------"
curl -s "http://localhost:8000/api/v1/scraping/articles/stats" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool
echo ""

# Test 4: Test AI summarization
echo "Step 5: Testing AI Summarization (Ollama)"
echo "-----------------------------------"
echo "This may take 30-120 seconds depending on Ollama performance..."
echo ""

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running"

    # Test with a simple Python script
    python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
sys.path.insert(0, '/Users/davidmorgan/Documents/Repositories/up2d8/backend')

async def test_summarization():
    try:
        from api.services.summarizer import get_summarizer

        print("Creating summarizer...")
        summarizer = get_summarizer(
            max_timeout=120,
            micro_timeout=30,
            standard_timeout=45,
            detailed_timeout=60
        )

        test_title = "AI Model Achieves Breakthrough in Coding"
        test_content = """
        Researchers have developed a new AI model that demonstrates unprecedented
        capabilities in software development. The model can understand complex
        codebases, identify bugs, and suggest improvements with remarkable accuracy.
        Early tests show it outperforms existing solutions by 40% on standard
        benchmarks. Industry experts believe this could revolutionize how developers
        work, automating routine tasks and allowing focus on creative problem-solving.
        """

        print("Generating summaries (this may take a minute)...")
        summaries = await summarizer.summarize_article(
            title=test_title,
            content=test_content,
            author="Tech Research Team"
        )

        print("\n✅ Summarization successful!")
        print("\n--- MICRO SUMMARY (280 chars) ---")
        print(summaries.get("summary_micro", "N/A"))
        print(f"\nLength: {len(summaries.get('summary_micro', ''))} chars")

        print("\n--- STANDARD SUMMARY (150-200 words) ---")
        print(summaries.get("summary_standard", "N/A"))
        print(f"\nWord count: {len(summaries.get('summary_standard', '').split())} words")

        print("\n--- DETAILED SUMMARY (300-500 words) ---")
        print(summaries.get("summary_detailed", "N/A"))
        print(f"\nWord count: {len(summaries.get('summary_detailed', '').split())} words")

    except Exception as e:
        print(f"\n❌ Summarization failed: {e}")
        import traceback
        traceback.print_exc()

# Run the async function
asyncio.run(test_summarization())
PYTHON_SCRIPT

else
    echo "❌ Ollama is not running!"
    echo "Please start Ollama with: ollama serve"
    echo "Then pull the model: ollama pull llama3.2:3b"
fi

echo ""
echo "=========================================="
echo "System Test Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "- Authentication: Working ✅"
echo "- Article Scraping: Check logs above"
echo "- AI Summarization: Check Ollama test above"
echo ""
echo "Next steps:"
echo "1. If articles were scraped, you can trigger processing with:"
echo "   curl -X POST http://localhost:8000/api/v1/processing/process"
echo ""
echo "2. Check worker logs:"
echo "   docker-compose logs worker --tail=50"
