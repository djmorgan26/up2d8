#!/usr/bin/env python3
"""
Test Script for WebSocket Chat with LangGraph Agent

Tests the WebSocket endpoint with streaming responses.
"""
import asyncio
import json
import sys
import os
import websockets
import httpx

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


async def get_auth_token():
    """Get authentication token for testing"""
    print("\n[1] Authenticating user...")

    # Try to login
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "SecurePass123!"
                }
            )

            if response.status_code == 200:
                data = response.json()
                token = data["access_token"]
                user_id = data["user"]["id"]
                print(f"   ✅ Authenticated as: test@example.com (ID: {user_id})")
                return token, user_id
            else:
                print(f"   ❌ Login failed: {response.status_code}")
                print(f"   Create test user first:")
                print(f"   curl -X POST {BASE_URL}/api/v1/auth/signup \\")
                print(f"     -H 'Content-Type: application/json' \\")
                print(f"     -d '{{\"email\":\"test@example.com\",\"password\":\"SecurePass123!\",\"full_name\":\"Test User\"}}'")
                return None, None

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return None, None


async def test_websocket_chat():
    """Test the WebSocket chat endpoint"""
    print("=" * 80)
    print("TESTING WEBSOCKET CHAT WITH LANGGRAPH AGENT")
    print("=" * 80)

    # Get auth token
    token, user_id = await get_auth_token()
    if not token:
        return

    # Generate session ID
    session_id = f"test-session-{user_id}"

    print(f"\n[2] Connecting to WebSocket...")
    print(f"   URL: {WS_URL}/api/v1/chat/ws/{session_id}?token={token[:20]}...")

    try:
        async with websockets.connect(
            f"{WS_URL}/api/v1/chat/ws/{session_id}?token={token}",
            ping_interval=None
        ) as websocket:
            print("   ✅ Connected to WebSocket")

            # Wait for ready message
            ready_msg = await websocket.recv()
            ready_data = json.loads(ready_msg)
            print(f"   📡 Received: {ready_data['type']}")
            print(f"   Session ID: {ready_data['data']['session_id']}")

            # Test queries
            test_queries = [
                "Hello! What can you help me with?",
                "What are the latest articles I have?",
                "Tell me about AI trends",
            ]

            for i, query in enumerate(test_queries, 1):
                print(f"\n[{i+2}] Testing query: '{query}'")
                print("   📤 Sending message...")

                # Send message
                await websocket.send(json.dumps({
                    "message": query
                }))

                # Receive and process responses
                full_response = ""
                sources = []
                metadata = None

                print("   📥 Receiving response:")

                while True:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                        data = json.loads(response)

                        msg_type = data["type"]

                        if msg_type == "start":
                            print(f"      🟢 Start - Processing message")

                        elif msg_type == "chunk":
                            content = data["data"]["content"]
                            full_response += content
                            print(f"      📝 Chunk: {content}", end="", flush=True)

                        elif msg_type == "source":
                            source = data["data"]
                            sources.append(source)
                            print(f"\n      📚 Source: {source['title']} (Relevance: {source['relevance_score']:.0%})")

                        elif msg_type == "end":
                            metadata = data["data"]
                            print(f"\n      🏁 Complete!")
                            print(f"         Confidence: {metadata.get('confidence', 0):.2f}")
                            print(f"         Query Type: {metadata.get('query_type')}")
                            print(f"         Memory Layers: {metadata.get('memory_layers_used')}")
                            break

                        elif msg_type == "error":
                            print(f"\n      ❌ Error: {data['data']['message']}")
                            break

                    except asyncio.TimeoutError:
                        print(f"\n      ⏱️  Timeout waiting for response")
                        break

                print(f"\n   ✅ Response complete!")
                print(f"   📊 Stats:")
                print(f"      Response length: {len(full_response)} chars")
                print(f"      Sources: {len(sources)}")

                # Small delay between queries
                await asyncio.sleep(1)

            print("\n[Final] Closing connection...")
            await websocket.close()
            print("   ✅ Connection closed")

    except websockets.exceptions.WebSocketException as e:
        print(f"   ❌ WebSocket error: {str(e)}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ WEBSOCKET TESTING COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    # Check if websockets package is installed
    try:
        import websockets
    except ImportError:
        print("❌ websockets package not installed")
        print("   Install with: pip install websockets")
        sys.exit(1)

    asyncio.run(test_websocket_chat())
