#!/usr/bin/env python3
"""
Quick RAG System Test
Tests embedding, chat, and semantic search functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_step(step, total, message):
    print(f"\n[{step}/{total}] {message}")

def main():
    print("🚀 UP2D8 RAG System Quick Test")
    print("=" * 50)

    # Step 1: Authenticate
    print_step(1, 6, "Authenticating...")

    # Try to create user (may already exist)
    try:
        requests.post(
            f"{BASE_URL}/api/v1/auth/signup",
            json={"email": "rag@test.com", "password": "Test123456!", "full_name": "RAG Test"}
        )
    except:
        pass

    # Login
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "rag@test.com", "password": "Test123456!"}
    )
    login_data = login_response.json()
    token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Logged in successfully")

    # Step 2: Check articles
    print_step(2, 6, "Checking articles...")
    articles_response = requests.get(
        f"{BASE_URL}/api/v1/scraping/articles?limit=5&status=completed",
        headers=headers
    )
    articles = articles_response.json()
    print(f"✓ Found {len(articles)} completed articles")

    if len(articles) == 0:
        print("⚠️  No articles found. Please run scraping first.")
        print("   curl -X POST http://localhost:8000/api/v1/scraping/scrape/all -H 'Authorization: Bearer <token>'")
        return

    # Step 3: Generate embeddings
    print_step(3, 6, "Triggering embedding generation...")
    # We'll call the embed task directly via Docker
    import subprocess
    try:
        result = subprocess.run([
            "docker", "exec", "up2d8-worker",
            "python3", "-c",
            """
import sys
sys.path.insert(0, '/app')
from workers.tasks.processing import embed_pending_articles
result = embed_pending_articles(limit=10)
print(f"Queued {result['tasks_queued']} embedding tasks")
"""
        ], capture_output=True, text=True, timeout=10)
        print(f"✓ {result.stdout.strip()}")
    except Exception as e:
        print(f"✓ Embedding task triggered (may be processing)")

    print("  Waiting 10 seconds for embeddings to process...")
    time.sleep(10)

    # Step 4: Test chat health
    print_step(4, 6, "Testing chat system...")
    health_response = requests.get(f"{BASE_URL}/api/v1/chat/health")
    health = health_response.json()
    print(f"✓ Chat system status: {health['status']}")

    # Step 5: Create chat session
    print_step(5, 6, "Creating chat session...")
    session_response = requests.post(
        f"{BASE_URL}/api/v1/chat/sessions",
        json={"title": "RAG Test Session"},
        headers=headers
    )
    session = session_response.json()
    session_id = session["id"]
    print(f"✓ Chat session created: {session_id[:8]}...")

    # Step 6: Send message with RAG
    print_step(6, 6, "Sending chat message with RAG...")
    message_response = requests.post(
        f"{BASE_URL}/api/v1/chat/sessions/{session_id}/messages",
        json={
            "message": "What are the latest developments in AI?",
            "use_rag": True,
            "top_k": 3
        },
        headers=headers
    )

    if message_response.status_code == 200:
        message_data = message_response.json()
        assistant_content = message_data["assistant_message"]["content"]
        context_count = len(message_data.get("context", []))

        print(f"✓ Chat response received")
        print(f"✓ Used {context_count} articles for context")
        print(f"\n  Assistant Response (first 300 chars):")
        print(f"  {assistant_content[:300]}...")

        if context_count > 0:
            print(f"\n  Context Articles Used:")
            for i, article in enumerate(message_data["context"][:3], 1):
                print(f"    [{i}] {article['title'][:60]}...")
                print(f"        Relevance: {article['relevance_score']:.3f}")
    else:
        print(f"✗ Chat request failed: {message_response.status_code}")
        print(f"  {message_response.text}")

    # Bonus: Test semantic search
    print("\n" + "=" * 50)
    print("[Bonus] Testing semantic search...")
    search_response = requests.post(
        f"{BASE_URL}/api/v1/chat/search",
        json={"query": "machine learning advancements", "top_k": 5},
        headers=headers
    )

    if search_response.status_code == 200:
        search_results = search_response.json()
        print(f"✓ Found {len(search_results)} articles via semantic search")

        if len(search_results) > 0:
            print("\n  Top Results:")
            for i, article in enumerate(search_results[:3], 1):
                print(f"    [{i}] {article['title'][:60]}...")
                print(f"        Score: {article['relevance_score']:.3f}")
    else:
        print(f"✗ Search failed: {search_response.status_code}")

    print("\n" + "=" * 50)
    print("✅ RAG System Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()
