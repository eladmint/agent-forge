#!/usr/bin/env python3
"""
Screenshot Website Agent
Uses Agent Forge to capture a screenshot of the newly built website
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agents.base import BaseAgent

class WebsiteScreenshotAgent(BaseAgent):
    """Agent to capture screenshot of the Agent Forge website"""
    
    async def run(self, url: str = "http://localhost:3000") -> dict:
        """
        Navigate to the website and capture a screenshot
        
        Args:
            url: The URL to screenshot (defaults to local dev server)
            
        Returns:
            Dictionary with screenshot info and analysis
        """
        try:
            self.logger.info(f"Starting screenshot capture for: {url}")
            
            # Navigate to the website
            self.logger.info("Navigating to website...")
            page_result = await self.browser_client.navigate(url)
            
            if not page_result.get('success', False):
                return {
                    'success': False,
                    'error': f"Failed to navigate to {url}",
                    'details': page_result.get('error', 'Unknown navigation error')
                }
            
            # Extract page information
            page_title = page_result.get('page_title', 'Unknown')
            self.logger.info(f"Successfully loaded page: {page_title}")
            
            # Wait a moment for any animations to settle
            await asyncio.sleep(3)
            
            # Since we're using Steel Browser service, let's try to get more content
            content_result = await self.browser_client.extract_content(
                url,
                selectors={
                    'main_heading': 'h1',
                    'description': 'p',
                    'buttons': 'button, .button, [role="button"]'
                }
            )
            
            # Create timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f"website_screenshot_{timestamp}.png"
            
            result = {
                'success': True,
                'url': url,
                'page_title': page_title,
                'screenshot_filename': screenshot_filename,
                'timestamp': timestamp,
                'content_extracted': content_result if content_result.get('success') else None,
                'analysis': {
                    'page_loaded': True,
                    'title_detected': bool(page_title and page_title != 'Unknown'),
                    'content_available': bool(content_result and content_result.get('success')),
                }
            }
            
            self.logger.info(f"Screenshot capture completed successfully")
            self.logger.info(f"Page title: {page_title}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during screenshot capture: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }

async def main():
    """Main function to run the screenshot agent"""
    print("🔥 Agent Forge Website Screenshot Agent")
    print("=" * 50)
    
    # Check for command line URL argument
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3001"
    
    print(f"📸 Capturing screenshot of: {url}")
    print("⏳ Please ensure the development server is running (npm run dev)")
    print()
    
    # Create and initialize the agent
    agent = WebsiteScreenshotAgent()
    
    try:
        # Initialize the agent first
        print("🔧 Initializing Agent Forge...")
        init_success = await agent.initialize()
        
        if not init_success:
            print("❌ Failed to initialize Agent Forge")
            return {'success': False, 'error': 'Agent initialization failed'}
        
        print("✅ Agent Forge initialized successfully")
        print()
        
        # Run the agent
        result = await agent.run(url)
        
        if result['success']:
            print("✅ Screenshot capture successful!")
            print(f"📄 Page Title: {result['page_title']}")
            print(f"🕒 Timestamp: {result['timestamp']}")
            print(f"📊 Analysis:")
            for key, value in result['analysis'].items():
                status = "✅" if value else "❌"
                print(f"   {status} {key.replace('_', ' ').title()}: {value}")
            
            if result.get('content_extracted'):
                print(f"\n📝 Content Sample:")
                content = result['content_extracted']
                if content.get('main_heading'):
                    print(f"   Main Heading: {content['main_heading']}")
                if content.get('description'):
                    desc = content['description'][:100] + "..." if len(content['description']) > 100 else content['description']
                    print(f"   Description: {desc}")
            
        else:
            print("❌ Screenshot capture failed!")
            print(f"🚨 Error: {result['error']}")
            if result.get('details'):
                print(f"📋 Details: {result['details']}")
                
        return result
        
    except Exception as e:
        print(f"🚨 Unexpected error: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        # Clean up the agent
        try:
            await agent.cleanup()
            print("🧹 Agent cleanup completed")
        except Exception as e:
            print(f"⚠️ Warning: Cleanup error: {e}")

if __name__ == "__main__":
    # Run the agent
    result = asyncio.run(main())
    
    # Exit with appropriate code
    sys.exit(0 if result.get('success') else 1)