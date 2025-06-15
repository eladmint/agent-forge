"""
Frontend Debugger Agent - Agent Forge

A specialized agent for debugging frontend websites and web applications.
This agent can:
- Navigate to websites and take screenshots
- Analyze website errors and issues
- Check network responses and status codes
- Validate HTML, CSS, and JavaScript functionality
- Generate debugging reports with visual evidence

Perfect for:
- Website deployment validation
- Frontend issue investigation
- Performance analysis
- User experience testing
"""

import asyncio
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from agent_forge.core.base_agent import BaseAgent


class FrontendDebuggerAgent(BaseAgent):
    """
    Frontend Debugger Agent for comprehensive website analysis and debugging.
    
    Features:
    - Website screenshot capture
    - Error detection and analysis
    - Performance metrics collection
    - Network request monitoring
    - HTML/CSS validation
    - Accessibility checks
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Frontend Debugger Agent."""
        super().__init__(config)
        self.name = "Frontend Debugger Agent"
        self.version = "1.0.0"
        
    async def debug_website(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Main debugging method that performs comprehensive website analysis.
        
        Args:
            url: Website URL to debug
            **kwargs: Additional options like screenshot_path, check_performance, etc.
            
        Returns:
            Comprehensive debugging report with screenshots and analysis
        """
        print(f"🔍 Starting frontend debugging for: {url}")
        
        report = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "agent": f"{self.name} v{self.version}",
            "results": {}
        }
        
        try:
            # Navigate to the website
            print("📱 Navigating to website...")
            page_data = await self.browser_client.navigate(url)
            
            if not page_data or 'error' in page_data:
                report["results"]["navigation_error"] = page_data.get('error', 'Unknown navigation error')
                return report
                
            report["results"]["navigation"] = {
                "status": "success",
                "title": page_data.get('page_title', 'Unknown'),
                "url": page_data.get('current_url', url)
            }
            
            # Take screenshot
            print("📸 Capturing screenshot...")
            screenshot_result = await self._capture_screenshot(url, kwargs.get('screenshot_path'))
            report["results"]["screenshot"] = screenshot_result
            
            # Check for errors in page content
            print("🔍 Analyzing page content for errors...")
            error_analysis = await self._analyze_page_errors(page_data)
            report["results"]["error_analysis"] = error_analysis
            
            # Check network status
            print("🌐 Checking network responses...")
            network_status = await self._check_network_status(url)
            report["results"]["network_status"] = network_status
            
            # Performance metrics (if requested)
            if kwargs.get('check_performance', True):
                print("⚡ Collecting performance metrics...")
                performance = await self._collect_performance_metrics(page_data)
                report["results"]["performance"] = performance
                
            # HTML validation
            print("📝 Validating HTML structure...")
            html_validation = await self._validate_html_structure(page_data)
            report["results"]["html_validation"] = html_validation
            
            print("✅ Frontend debugging complete!")
            
        except Exception as e:
            print(f"❌ Error during frontend debugging: {str(e)}")
            report["results"]["error"] = str(e)
            
        return report
    
    async def _capture_screenshot(self, url: str, save_path: Optional[str] = None) -> Dict[str, Any]:
        """Capture a screenshot of the website."""
        try:
            # Use Steel Browser to take screenshot
            screenshot_data = await self.browser_client.screenshot(url)
            
            if save_path:
                # Save screenshot to specified path
                screenshot_path = Path(save_path)
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                
                if isinstance(screenshot_data, str):
                    # Base64 data
                    with open(screenshot_path, 'wb') as f:
                        f.write(base64.b64decode(screenshot_data))
                else:
                    # Binary data
                    with open(screenshot_path, 'wb') as f:
                        f.write(screenshot_data)
                        
                return {
                    "status": "success",
                    "path": str(screenshot_path),
                    "size": screenshot_path.stat().st_size if screenshot_path.exists() else 0
                }
            else:
                return {
                    "status": "success",
                    "data": screenshot_data,
                    "format": "base64" if isinstance(screenshot_data, str) else "binary"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _analyze_page_errors(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the page content for common errors."""
        errors = []
        warnings = []
        
        try:
            page_content = page_data.get('content', '')
            
            # Check for common error patterns
            error_patterns = [
                ('404', 'Page not found'),
                ('500', 'Internal server error'),
                ('NoSuchBucket', 'Storage bucket does not exist'),
                ('Access Denied', 'Access denied error'),
                ('Error', 'Generic error detected'),
                ('Exception', 'Exception occurred'),
                ('Failed to load', 'Resource loading failure')
            ]
            
            for pattern, description in error_patterns:
                if pattern.lower() in page_content.lower():
                    errors.append({
                        "type": "content_error",
                        "pattern": pattern,
                        "description": description
                    })
            
            # Check for missing resources
            if 'style' not in page_content.lower():
                warnings.append("No CSS styles detected")
                
            if 'script' not in page_content.lower():
                warnings.append("No JavaScript detected")
                
            return {
                "errors": errors,
                "warnings": warnings,
                "error_count": len(errors),
                "warning_count": len(warnings)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "errors": [],
                "warnings": []
            }
    
    async def _check_network_status(self, url: str) -> Dict[str, Any]:
        """Check network status and response codes."""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return {
                        "status_code": response.status,
                        "status_text": response.reason,
                        "headers": dict(response.headers),
                        "content_type": response.headers.get('content-type', 'unknown'),
                        "content_length": response.headers.get('content-length', 'unknown')
                    }
                    
        except Exception as e:
            return {
                "error": str(e),
                "status_code": None
            }
    
    async def _collect_performance_metrics(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect basic performance metrics."""
        try:
            # Basic performance indicators
            content = page_data.get('content', '')
            
            return {
                "page_size": len(content),
                "load_time": page_data.get('load_time', 'unknown'),
                "has_images": 'img' in content.lower(),
                "has_css": 'style' in content.lower() or '.css' in content.lower(),
                "has_js": 'script' in content.lower() or '.js' in content.lower(),
                "title_length": len(page_data.get('page_title', '')),
                "meta_description": 'meta' in content.lower() and 'description' in content.lower()
            }
            
        except Exception as e:
            return {
                "error": str(e)
            }
    
    async def _validate_html_structure(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate basic HTML structure."""
        try:
            content = page_data.get('content', '').lower()
            
            validation = {
                "has_doctype": content.startswith('<!doctype'),
                "has_html_tag": '<html' in content,
                "has_head_tag": '<head' in content,
                "has_body_tag": '<body' in content,
                "has_title": '<title' in content,
                "has_meta_charset": 'charset' in content,
                "has_viewport_meta": 'viewport' in content
            }
            
            validation["score"] = sum(validation.values()) / len(validation) * 100
            validation["is_valid"] = validation["score"] > 70
            
            return validation
            
        except Exception as e:
            return {
                "error": str(e),
                "is_valid": False,
                "score": 0
            }
    
    async def run(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Main run method for the Frontend Debugger Agent.
        
        Args:
            url: Website URL to debug
            **kwargs: Additional debugging options
            
        Returns:
            Complete debugging report
        """
        return await self.debug_website(url, **kwargs)


# Convenience function for quick debugging
async def debug_frontend(url: str, screenshot_path: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Quick frontend debugging function.
    
    Args:
        url: Website URL to debug
        screenshot_path: Optional path to save screenshot
        **kwargs: Additional debugging options
        
    Returns:
        Debugging report
    """
    agent = FrontendDebuggerAgent()
    await agent.initialize()
    
    kwargs['screenshot_path'] = screenshot_path
    result = await agent.run(url, **kwargs)
    
    await agent.cleanup()
    return result


if __name__ == "__main__":
    # Example usage
    async def main():
        url = "https://storage.googleapis.com/tokenhunter-457310-agent-forge-website/index.html"
        screenshot_path = "/tmp/debug_screenshot.png"
        
        print(f"🔍 Debugging website: {url}")
        result = await debug_frontend(url, screenshot_path)
        
        print("\n📊 Debugging Report:")
        print(json.dumps(result, indent=2, default=str))
        
    asyncio.run(main())