"""
Steel Browser Client for Agent Forge Framework

This module provides a client interface to interact with the Steel Browser
service for web automation and scraping tasks.
"""

import asyncio
import logging
import aiohttp
from typing import Dict, Any, Optional


class SteelBrowserClient:
    """
    Client for interacting with the Steel Browser service.
    
    This client provides methods to navigate to URLs, extract content,
    and perform browser automation tasks through the Steel Browser API.
    """
    
    def __init__(self, api_url: str, timeout: int = 30):
        """
        Initialize the Steel Browser client.
        
        Args:
            api_url: The URL of the Steel Browser service
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.logger = logging.getLogger(f"{__name__}.SteelBrowserClient")
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
            
    async def navigate(self, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL and extract basic page information.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            Dictionary containing page information including title
        """
        await self._ensure_session()
        
        try:
            self.logger.info(f"Navigating to URL: {url}")
            
            # Prepare request payload
            payload = {
                "url": url,
                "extract_title": True,
                "extract_text": False,
                "wait_for": "load"
            }
            
            # Make request to Steel Browser service
            async with self.session.post(
                f"{self.api_url}/navigate",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Successfully navigated to {url}")
                    return result
                else:
                    error_text = await response.text()
                    self.logger.error(f"Navigation failed with status {response.status}: {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "page_title": None
                    }
                    
        except asyncio.TimeoutError:
            self.logger.error(f"Navigation to {url} timed out")
            return {
                "success": False,
                "error": "Request timed out",
                "page_title": None
            }
        except Exception as e:
            self.logger.error(f"Navigation to {url} failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "page_title": None
            }
            
    async def extract_content(self, url: str, selectors: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Navigate to a URL and extract specific content using CSS selectors.
        
        Args:
            url: The URL to navigate to
            selectors: Optional dictionary of CSS selectors to extract content
            
        Returns:
            Dictionary containing extracted content
        """
        await self._ensure_session()
        
        try:
            self.logger.info(f"Extracting content from URL: {url}")
            
            payload = {
                "url": url,
                "extract_title": True,
                "extract_text": True,
                "selectors": selectors or {},
                "wait_for": "load"
            }
            
            async with self.session.post(
                f"{self.api_url}/extract",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    self.logger.info(f"Successfully extracted content from {url}")
                    return result
                else:
                    error_text = await response.text()
                    self.logger.error(f"Content extraction failed with status {response.status}: {error_text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    
        except Exception as e:
            self.logger.error(f"Content extraction from {url} failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
            
    async def get_page_title(self, url: str) -> Optional[str]:
        """
        Get the page title for a specific URL.
        
        Args:
            url: The URL to get the title for
            
        Returns:
            The page title if successful, None otherwise
        """
        result = await self.navigate(url)
        return result.get('page_title') if result.get('success') else None
        
    async def health_check(self) -> bool:
        """
        Check if the Steel Browser service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        await self._ensure_session()
        
        try:
            async with self.session.get(f"{self.api_url}/health") as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
            
    def __str__(self) -> str:
        """String representation of the client."""
        return f"SteelBrowserClient(api_url='{self.api_url}')"
        
    def __repr__(self) -> str:
        """Detailed string representation of the client."""
        return f"SteelBrowserClient(api_url='{self.api_url}', timeout={self.timeout})"