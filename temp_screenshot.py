#!/usr/bin/env python3
"""
Temporary script to take a screenshot of the website
"""

import asyncio
from playwright.async_api import async_playwright
import sys

async def screenshot_website(url: str, output_file: str):
    """Take a screenshot of a website"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Set viewport size
        await page.set_viewport_size({"width": 1280, "height": 800})
        
        try:
            # Navigate to the URL
            await page.goto(url, wait_until="networkidle")
            
            # Wait a bit for any animations
            await asyncio.sleep(2)
            
            # Take screenshot
            await page.screenshot(path=output_file, full_page=True)
            print(f"Screenshot saved to {output_file}")
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    url = "https://storage.googleapis.com/tokenhunter-457310-agent-forge-website/index.html"
    output = "website_dark_mode_check.png"
    
    asyncio.run(screenshot_website(url, output))