#!/usr/bin/env python3
"""
Take screenshot of the Agent Forge website and analyze it for dark mode
"""

import sys
import os
import asyncio
import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Please install playwright: pip install playwright && playwright install")
    sys.exit(1)

async def take_website_screenshot():
    """Take a screenshot of the website and analyze it"""
    
    # Website URL (hosted on Google Cloud Storage)
    website_url = "https://storage.googleapis.com/tokenhunter-457310-agent-forge-website/index.html"
    
    print(f"🔥 Taking screenshot of: {website_url}")
    print("=" * 80)
    
    # Create screenshots directory if it doesn't exist
    screenshots_dir = Path("results/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    # Create timestamp for filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = screenshots_dir / f"agent_forge_website_{timestamp}.png"
    
    try:
        async with async_playwright() as p:
            print("🌐 Launching browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set viewport size for consistent screenshots
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            print("🌐 Navigating to website...")
            # Hard refresh to bypass cache
            await page.goto(website_url + "?cache_bust=" + str(int(asyncio.get_running_loop().time())), wait_until="networkidle")
            
            # Get page title
            page_title = await page.title()
            print(f"✅ Successfully loaded: {page_title}")
            
            # Wait for page to fully load and any animations to settle
            await asyncio.sleep(3)
            
            # Take screenshot
            print("📸 Taking screenshot...")
            await page.screenshot(path=screenshot_path, full_page=True)
            
            await browser.close()
            
            print(f"✅ Screenshot saved: {screenshot_path}")
            
            # Return information about the screenshot
            return {
                'success': True,
                'screenshot_path': str(screenshot_path),
                'website_url': website_url,
                'timestamp': timestamp,
                'page_title': page_title
            }
            
    except Exception as e:
        print(f"🚨 Error taking screenshot: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Main function"""
    result = await take_website_screenshot()
    
    if result and result['success']:
        print("\n" + "=" * 80)
        print("📊 SCREENSHOT ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"📄 Page Title: {result['page_title']}")
        print(f"🔗 Website URL: {result['website_url']}")
        print(f"📁 Screenshot Path: {result['screenshot_path']}")
        print(f"🕒 Timestamp: {result['timestamp']}")
        print("\n🎯 You can now analyze this screenshot to verify the dark mode implementation!")
        print(f"   Screenshot location: {result['screenshot_path']}")
        return result
    else:
        print("\n❌ Screenshot capture failed")
        return None

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)