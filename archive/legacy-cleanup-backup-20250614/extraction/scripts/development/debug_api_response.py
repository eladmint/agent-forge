#!/usr/bin/env python3
"""
Debug API Response Script
========================

This script helps debug why API responses are empty and checks 
the actual response structure.

"""

import json
import time

import requests


def debug_api_response():
    """Debug what's happening with API responses"""
    api_url = "https://chatbot-api-service-v2-oo6mrfxexq-uc.a.run.app"

    print("🐛 Debugging API Response")
    print("=========================")

    query_data = {
        "message": "Show me EthCC events",
        "user_id": "debug_user_123",
        "chat_id": "debug_chat_123",
    }

    print(f"📤 Sending request: {json.dumps(query_data, indent=2)}")

    try:
        response = requests.post(f"{api_url}/v2/chat", json=query_data, timeout=30)

        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print(f"📥 Response JSON: {json.dumps(result, indent=2)}")

            # Check for specific fields
            if "response" in result:
                response_text = result["response"]
                print(f"📝 Response text length: {len(response_text)}")
                if response_text:
                    print(f"📝 Response preview: '{response_text[:200]}...'")
                else:
                    print("⚠️ Response text is empty!")

            if "debug" in result:
                print(f"🔍 Debug info: {json.dumps(result['debug'], indent=2)}")

        else:
            print(f"❌ Error response: {response.text}")

    except Exception as e:
        print(f"❌ Request failed: {e}")


def test_different_queries():
    """Test different types of queries to see what works"""
    api_url = "https://chatbot-api-service-v2-oo6mrfxexq-uc.a.run.app"

    print("\n🧪 Testing Different Query Types")
    print("=================================")

    test_queries = [
        "Hello",
        "What is TokenHunter?",
        "Show me events",
        "EthCC",
        "Ethereum events in Brussels",
        "List speakers at conferences",
        "What events are happening in July?",
    ]

    for i, query in enumerate(test_queries):
        print(f"\n🔍 Query {i+1}: '{query}'")

        query_data = {
            "message": query,
            "user_id": f"test_user_{i}",
            "chat_id": f"test_chat_{i}",
        }

        try:
            response = requests.post(f"{api_url}/v2/chat", json=query_data, timeout=20)

            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")

                print(f"   ✅ Status: {response.status_code}")
                print(f"   📏 Length: {len(response_text)} chars")

                if response_text:
                    # Show first 100 chars
                    preview = response_text[:100].replace("\n", " ")
                    print(f"   📝 Preview: '{preview}...'")
                else:
                    print("   ⚠️ Empty response")

                # Check for any error indicators
                if "error" in result:
                    print(f"   ❌ Error: {result['error']}")
                if "debug" in result:
                    debug_info = result["debug"]
                    if isinstance(debug_info, dict):
                        print(f"   🔍 Debug keys: {list(debug_info.keys())}")

            else:
                print(f"   ❌ Failed: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        time.sleep(1)  # Rate limiting


def check_database_connection():
    """Check if we can query the database directly"""
    api_url = "https://chatbot-api-service-v2-oo6mrfxexq-uc.a.run.app"

    print("\n🗄️ Checking Database Connection")
    print("===============================")

    # Try admin endpoints for system status
    try:
        admin_response = requests.get(f"{api_url}/admin/status", timeout=10)
        print(f"📊 Admin status: {admin_response.status_code}")

        if admin_response.status_code == 200:
            admin_data = admin_response.json()
            print(f"📊 Admin data keys: {list(admin_data.keys())}")

    except Exception as e:
        print(f"❌ Admin status failed: {e}")


def main():
    debug_api_response()
    test_different_queries()
    check_database_connection()


if __name__ == "__main__":
    main()
