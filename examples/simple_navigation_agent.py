"""
Simple Navigation Agent

An example agent that demonstrates basic web navigation using the Agent Forge framework.
This agent uses the steel browser client to navigate to a URL and extract the page title.
"""

import asyncio
from typing import Optional
from core.agents.base import AsyncContextAgent


class SimpleNavigationAgent(AsyncContextAgent):
    """
    A simple agent that navigates to a URL and extracts the page title.
    
    This agent demonstrates:
    - BaseAgent inheritance and async patterns
    - Integration with framework utilities (steel browser)
    - Basic web navigation and data extraction
    - Proper error handling and logging
    """
    
    def __init__(self, name: Optional[str] = None, config: Optional[dict] = None, url: Optional[str] = None):
        """
        Initialize the SimpleNavigationAgent.
        
        Args:
            name: Optional agent name (defaults to class name)
            config: Optional configuration dictionary
            url: Target URL to navigate to
        """
        super().__init__(name, config)
        provided_url = url or self.config.get('url')
        
        if not provided_url:
            raise ValueError("URL must be provided either as parameter or in config")
        
        # Ensure URL is a string
        if not isinstance(provided_url, str):
            raise ValueError("URL must be a string")
            
        self.url: str = provided_url
            
        self.logger.info(f"SimpleNavigationAgent initialized with URL: {self.url}")
    
    async def run(self) -> Optional[str]:
        """
        Navigate to the URL using the Steel Browser client and extract the page title.
        
        Returns:
            Optional[str]: The page title if successful, None otherwise
        """
        self.logger.info(f"Navigating to {self.url} using functional Steel Browser...")
        if not self.browser_client:
            self.logger.error("Browser client not initialized. Aborting.")
            return None

        try:
            # Ensure URL is properly formatted
            if not self.url.startswith(('http://', 'https://')):
                self.url = f"https://{self.url}"
            
            response = await self.browser_client.navigate(self.url)

            if response and response.get('page_title'):
                title = response.get('page_title')
                self.logger.info(f"Successfully retrieved page title.")
                print(f"📄 Page Title: {title}")
                return title
            else:
                self.logger.error(f"Failed to retrieve content from {self.url}. Response: {response}")
                return None
        except Exception as e:
            self.logger.error(f"Error during navigation: {e}")
            print(f"❌ Navigation failed: {e}")
            return None
    
    async def _cleanup(self):
        """
        Clean up agent resources.
        
        This method should be called when the agent is no longer needed.
        It performs cleanup operations such as closing connections,
        releasing resources, or saving state.
        """
        self.logger.info("Cleaning up SimpleNavigationAgent...")
        
        # Close browser client if needed
        if self.browser_client and hasattr(self.browser_client, 'close'):
            try:
                await self.browser_client.close()
                self.logger.info("Browser client closed successfully")
            except Exception as e:
                self.logger.warning(f"Error closing browser client: {e}")


# Example usage and testing
async def main():
    """Example usage of SimpleNavigationAgent."""
    agent = SimpleNavigationAgent(url="https://news.ycombinator.com")
    
    try:
        # Initialize agent
        success = await agent.initialize()
        if not success:
            print("❌ Agent initialization failed")
            return
        
        # Run agent
        result = await agent.run()
        print(f"✅ Agent result: {result}")
        
    finally:
        # Cleanup
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())