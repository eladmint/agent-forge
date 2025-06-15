#!/usr/bin/env python3
"""
Simple test to check if the website is accessible
"""

import aiohttp
import asyncio

async def test_website_access(url="http://localhost:3001"):
    """Test if the website is accessible"""
    
    print(f"🔍 Testing access to: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"✅ Status: {response.status}")
                print(f"📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
                
                if response.status == 200:
                    content = await response.text()
                    print(f"📊 Content length: {len(content)} characters")
                    
                    # Look for key elements
                    if "Agent Forge" in content:
                        print("✅ Found 'Agent Forge' in content")
                    if "Sacred Smithy" in content:
                        print("✅ Found 'Sacred Smithy' in content")
                    if "html" in content.lower():
                        print("✅ Valid HTML content detected")
                        
                    return True
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_website_access())