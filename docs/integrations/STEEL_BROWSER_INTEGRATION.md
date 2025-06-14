# 🌐 Steel Browser Integration Guide

This guide covers the Steel Browser integration in Agent Forge, providing comprehensive information on web automation capabilities, setup, and usage patterns.

## 📋 **Table of Contents**

- [Overview](#overview)
- [Integration Architecture](#integration-architecture)
- [Setup and Configuration](#setup-and-configuration)
- [Usage Patterns](#usage-patterns)
- [Advanced Features](#advanced-features)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

---

## 🎯 **Overview**

[Steel Browser](https://github.com/steel-dev/steel-browser) is an open-source browser automation service that provides reliable web scraping and interaction capabilities. Agent Forge integrates with Steel Browser as an external service to offer robust web automation without the complexity of managing browser infrastructure.

### **Integration Approach**

Agent Forge uses Steel Browser as a **service dependency** through HTTP API calls, similar to how you might use any cloud service or API. This approach provides clean separation of concerns and follows standard service-oriented architecture patterns.

**What we built:**
- **HTTP Client Wrapper** - Custom client for Steel Browser API endpoints
- **AsyncIO Integration** - Full async/await support for modern Python applications  
- **Error Handling Layer** - Robust error handling and retry mechanisms
- **Configuration Management** - Flexible service endpoint and timeout configuration
- **Agent Integration** - Seamless integration into BaseAgent lifecycle

**What we use from Steel Browser:**
- **Open Source Service** - Steel Browser's browser automation service (Apache 2.0 licensed)
- **API Endpoints** - `/navigate`, `/extract`, `/health` endpoints for web automation
- **Browser Infrastructure** - Managed Chromium instances for reliable web interaction

### **Key Benefits**

- **Production Ready** - Reliable service designed for production workloads
- **No Browser Management** - No need to install or manage browser dependencies
- **Service Architecture** - Clean separation between framework and browser infrastructure
- **Scalable** - Handles multiple concurrent requests through service endpoints
- **Consistent** - Reliable behavior across different environments
- **Open Source Foundation** - Built on proven open source browser automation technology

### **Integration Features**

- **Automatic Service Connection** - Browser client connected automatically in BaseAgent
- **Async HTTP Client** - Full async/await integration using aiohttp
- **Comprehensive Error Handling** - HTTP errors, timeouts, and service unavailability handling
- **Flexible Configuration** - Service endpoint, timeout, and retry configuration
- **Production Logging** - Detailed logging for debugging and monitoring
- **Health Monitoring** - Service health checks and connection validation

---

## 🏗️ **Integration Architecture**

### **Service-Based Architecture**

```
Agent Forge Framework                    Steel Browser Service
┌─────────────────────────────┐         ┌──────────────────────────┐
│ BaseAgent                   │  HTTP   │ Steel Browser API        │
│ ├── SteelBrowserClient     │◄────────┤ ├── /navigate             │
│ │   ├── navigate()         │ Requests │ ├── /extract_content      │
│ │   ├── extract_content()  │         │ ├── /health              │
│ │   └── health_check()     │         │ └── Browser Management   │
│ └── Automatic Integration   │         │     ├── Chromium         │
└─────────────────────────────┘         │     ├── Session Mgmt     │
                                        │     └── Resource Cleanup │
                                        └──────────────────────────┘
```

### **Communication Flow**

```
1. Agent Initialization
   ├── BaseAgent.initialize()
   ├── Create SteelBrowserClient instance
   ├── Configure service endpoint
   └── Test service connectivity

2. Web Automation Request
   ├── Agent calls browser_client.navigate(url)
   ├── HTTP POST to Steel Browser /navigate endpoint
   ├── Steel Browser processes request with Chromium
   ├── JSON response with page data
   └── Agent processes response data

3. Error Handling & Retry
   ├── HTTP/Network errors caught by client
   ├── Automatic retry with exponential backoff
   ├── Service health checking
   └── Graceful degradation on failures
```

### **Component Overview**

**1. Service Configuration**
```python
# core/shared/config/browser_config.py
STEEL_BROWSER_API_URL = "https://production-orchestrator-867263134607.us-central1.run.app"
```

**2. HTTP Client Implementation**
```python
# core/shared/web/browsers/steel_browser_client.py
class SteelBrowserClient:
    """HTTP client for Steel Browser service API."""
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Send navigation request to Steel Browser service."""
        
    async def extract_content(self, url: str, selectors: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Request content extraction from Steel Browser service."""
        
    async def health_check(self) -> bool:
        """Check Steel Browser service availability."""
```

**3. BaseAgent Service Integration**
```python
# core/agents/base.py
class BaseAgent(ABC):
    async def initialize(self) -> bool:
        """Initialize with Steel Browser service connection."""
        self.browser_client = SteelBrowserClient(api_url=STEEL_BROWSER_API_URL)
        return await self.browser_client.health_check()
```

---

## ⚙️ **Setup and Configuration**

### **Automatic Setup**

Steel Browser integration is automatic when using BaseAgent:

```python
from core.agents.base import BaseAgent

class MyAgent(BaseAgent):
    async def run(self):
        # Browser client is automatically available
        response = await self.browser_client.navigate("https://example.com")
        return response
```

### **Manual Configuration**

For custom setups or advanced configuration:

```python
from core.shared.web.browsers import SteelBrowserClient
from core.shared.config.browser_config import STEEL_BROWSER_API_URL

class CustomAgent(BaseAgent):
    async def initialize(self) -> bool:
        # Custom browser client with options
        self.browser_client = SteelBrowserClient(
            api_url=STEEL_BROWSER_API_URL,
            timeout=30,
            retries=3,
            headers={'User-Agent': 'Custom Agent'}
        )
        return True
```

### **Configuration Options**

```python
browser_config = {
    "api_url": "https://production-orchestrator-867263134607.us-central1.run.app",
    "timeout": 30,           # Request timeout in seconds
    "retries": 3,            # Number of retry attempts
    "wait_for": "load",      # Wait condition: 'load', 'networkidle', 'domcontentloaded'
    "viewport": {            # Browser viewport settings
        "width": 1920,
        "height": 1080
    },
    "headers": {             # Custom HTTP headers
        "User-Agent": "Agent Forge Browser Client"
    }
}
```

---

## 🛠️ **Usage Patterns**

### **Basic Navigation**

```python
class NavigationAgent(BaseAgent):
    async def run(self, url: str) -> Optional[Dict[str, Any]]:
        """Navigate to URL and extract basic information."""
        
        # Basic navigation
        response = await self.browser_client.navigate(url)
        
        if response:
            return {
                "title": response.get('page_title'),
                "url": url,
                "content_length": len(response.get('content', '')),
                "status": "success"
            }
        
        return None
```

### **Advanced Navigation with Options**

```python
class AdvancedNavigationAgent(BaseAgent):
    async def run(self, url: str) -> Optional[Dict[str, Any]]:
        """Navigate with advanced options."""
        
        # Navigation with custom options
        response = await self.browser_client.navigate(
            url=url,
            wait_for="networkidle",    # Wait for network to be idle
            timeout=30,                # 30 second timeout
            extract_content=True,      # Extract page content
            take_screenshot=False      # Don't take screenshot
        )
        
        return response
```

### **Content Extraction**

```python
class ContentExtractionAgent(BaseAgent):
    async def run(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract specific content from page."""
        
        # Navigate to page
        await self.browser_client.navigate(url)
        
        # Extract specific elements
        title = await self.browser_client.extract_text("h1")
        description = await self.browser_client.extract_text("meta[name='description']")
        links = await self.browser_client.extract_links()
        
        return {
            "title": title,
            "description": description,
            "link_count": len(links),
            "links": links[:10]  # First 10 links
        }
```

### **Interactive Operations**

```python
class InteractiveAgent(BaseAgent):
    async def run(self, search_term: str) -> Optional[Dict[str, Any]]:
        """Perform interactive operations on a page."""
        
        # Navigate to search page
        await self.browser_client.navigate("https://example.com/search")
        
        # Fill search form
        await self.browser_client.type("input[name='q']", search_term)
        
        # Click search button
        await self.browser_client.click("button[type='submit']")
        
        # Wait for results
        await self.browser_client.wait_for_selector(".results")
        
        # Extract results
        results = await self.browser_client.extract_text(".results")
        
        return {"search_term": search_term, "results": results}
```

### **Multi-Page Navigation**

```python
class MultiPageAgent(BaseAgent):
    async def run(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Navigate to multiple URLs and collect data."""
        
        results = []
        
        for url in urls:
            try:
                self.logger.info(f"Processing: {url}")
                
                # Navigate to each URL
                response = await self.browser_client.navigate(url)
                
                if response:
                    results.append({
                        "url": url,
                        "title": response.get('page_title'),
                        "status": "success",
                        "content_length": len(response.get('content', ''))
                    })
                    
                # Small delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Failed to process {url}: {e}")
                results.append({
                    "url": url,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
```

---

## 🔧 **Advanced Features**

### **Screenshot Capture**

```python
class ScreenshotAgent(BaseAgent):
    async def run(self, url: str) -> Optional[Dict[str, Any]]:
        """Capture screenshots of web pages."""
        
        # Navigate to page
        await self.browser_client.navigate(url)
        
        # Capture full page screenshot
        screenshot = await self.browser_client.screenshot(
            full_page=True,
            format="png"
        )
        
        # Save screenshot
        screenshot_path = f"screenshot_{int(time.time())}.png"
        with open(screenshot_path, "wb") as f:
            f.write(screenshot)
        
        return {
            "url": url,
            "screenshot_path": screenshot_path,
            "screenshot_size": len(screenshot)
        }
```

### **Custom JavaScript Execution**

```python
class JavaScriptAgent(BaseAgent):
    async def run(self, url: str) -> Optional[Dict[str, Any]]:
        """Execute custom JavaScript on pages."""
        
        # Navigate to page
        await self.browser_client.navigate(url)
        
        # Execute custom JavaScript
        js_result = await self.browser_client.evaluate_javascript("""
            () => {
                return {
                    title: document.title,
                    url: window.location.href,
                    links: Array.from(document.links).length,
                    images: Array.from(document.images).length,
                    scripts: Array.from(document.scripts).length
                };
            }
        """)
        
        return js_result
```

### **Form Automation**

```python
class FormAgent(BaseAgent):
    async def run(self, form_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Automate form submission."""
        
        # Navigate to form page
        await self.browser_client.navigate("https://example.com/contact")
        
        # Fill form fields
        for field_name, value in form_data.items():
            await self.browser_client.type(f"input[name='{field_name}']", value)
        
        # Submit form
        await self.browser_client.click("input[type='submit']")
        
        # Wait for response
        await self.browser_client.wait_for_selector(".success-message")
        
        # Extract success message
        message = await self.browser_client.extract_text(".success-message")
        
        return {"status": "submitted", "message": message}
```

### **Performance Monitoring**

```python
class PerformanceAgent(BaseAgent):
    async def run(self, url: str) -> Optional[Dict[str, Any]]:
        """Monitor page performance metrics."""
        
        start_time = time.time()
        
        # Navigate and measure timing
        response = await self.browser_client.navigate(
            url=url,
            performance_metrics=True
        )
        
        load_time = time.time() - start_time
        
        return {
            "url": url,
            "load_time": load_time,
            "performance_metrics": response.get('performance', {}),
            "page_size": len(response.get('content', '')),
            "resource_count": response.get('resource_count', 0)
        }
```

---

## ⚠️ **Error Handling**

### **Comprehensive Error Handling**

```python
class RobustAgent(BaseAgent):
    async def run(self, url: str) -> Optional[Dict[str, Any]]:
        """Agent with comprehensive error handling."""
        
        try:
            # Validate URL
            if not self._validate_url(url):
                self.logger.error(f"Invalid URL: {url}")
                return {"status": "error", "error": "Invalid URL"}
            
            # Navigate with timeout
            response = await asyncio.wait_for(
                self.browser_client.navigate(url),
                timeout=30
            )
            
            if not response:
                self.logger.warning("No response received")
                return {"status": "error", "error": "No response"}
            
            return {
                "status": "success",
                "url": url,
                "title": response.get('page_title', 'Unknown'),
                "content_available": bool(response.get('content'))
            }
            
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout navigating to {url}")
            return {"status": "error", "error": "Navigation timeout"}
            
        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP client error: {e}")
            return {"status": "error", "error": f"Client error: {e}"}
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {"status": "error", "error": f"Unexpected error: {e}"}
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except Exception:
            return False
```

### **Retry Mechanisms**

```python
class RetryAgent(BaseAgent):
    async def run(self, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Agent with retry logic."""
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{max_retries} for {url}")
                
                response = await self.browser_client.navigate(url)
                
                if response:
                    return {
                        "status": "success",
                        "url": url,
                        "attempts": attempt + 1,
                        "data": response
                    }
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                else:
                    return {
                        "status": "error",
                        "url": url,
                        "attempts": max_retries,
                        "error": str(e)
                    }
        
        return None
```

---

## 🎯 **Best Practices**

### **1. Resource Management**

```python
class WellManagedAgent(BaseAgent):
    async def run(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Properly manage browser resources."""
        
        results = []
        
        try:
            # Process URLs with proper resource management
            for url in urls:
                # Rate limiting
                await asyncio.sleep(1)
                
                # Process with timeout
                result = await asyncio.wait_for(
                    self._process_url(url),
                    timeout=30
                )
                
                results.append(result)
                
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            
        finally:
            # Cleanup is handled by BaseAgent.cleanup()
            pass
        
        return results
    
    async def _process_url(self, url: str) -> Dict[str, Any]:
        """Process a single URL."""
        response = await self.browser_client.navigate(url)
        return {
            "url": url,
            "title": response.get('page_title') if response else None,
            "success": bool(response)
        }
```

### **2. Performance Optimization**

```python
class OptimizedAgent(BaseAgent):
    async def run(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Optimized concurrent processing."""
        
        # Process URLs concurrently with semaphore
        semaphore = asyncio.Semaphore(5)  # Limit concurrent requests
        
        async def process_url(url: str) -> Dict[str, Any]:
            async with semaphore:
                try:
                    response = await self.browser_client.navigate(url)
                    return {
                        "url": url,
                        "status": "success",
                        "title": response.get('page_title') if response else None
                    }
                except Exception as e:
                    return {
                        "url": url,
                        "status": "error",
                        "error": str(e)
                    }
        
        # Execute all tasks concurrently
        tasks = [process_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r for r in results if isinstance(r, dict)]
```

### **3. Debugging and Monitoring**

```python
class MonitoredAgent(BaseAgent):
    async def run(self, url: str) -> Optional[Dict[str, Any]]:
        """Agent with comprehensive monitoring."""
        
        start_time = time.time()
        
        # Log start
        self.logger.info(f"Starting navigation to: {url}")
        
        try:
            # Navigate with monitoring
            response = await self.browser_client.navigate(url)
            
            # Calculate metrics
            duration = time.time() - start_time
            
            # Log results
            if response:
                self.logger.info(f"Navigation successful in {duration:.2f}s")
                self.logger.debug(f"Page title: {response.get('page_title')}")
                self.logger.debug(f"Content length: {len(response.get('content', ''))}")
            else:
                self.logger.warning(f"Navigation failed after {duration:.2f}s")
            
            return {
                "url": url,
                "duration": duration,
                "success": bool(response),
                "response": response
            }
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Navigation error after {duration:.2f}s: {e}")
            return {
                "url": url,
                "duration": duration,
                "success": False,
                "error": str(e)
            }
```

---

## 🏛️ **Open Source Attribution & Relationship**

### **Steel Browser Project**

Agent Forge builds upon the excellent work of the [Steel Browser](https://github.com/steel-dev/steel-browser) open source project:

- **License**: Apache 2.0 (allows commercial use)
- **Original Project**: https://github.com/steel-dev/steel-browser
- **Integration Method**: Service consumption via HTTP API
- **Relationship**: External service dependency, not a fork or code modification

### **What Agent Forge Contributes**

**Our Custom Implementation:**
- **HTTP Client Wrapper** (`steel_browser_client.py`) - 198 lines of custom Python client code
- **AsyncIO Integration** - Modern async/await patterns for Python applications
- **Error Handling & Retry Logic** - Production-ready error handling and resilience
- **Agent Framework Integration** - Seamless integration with BaseAgent lifecycle
- **Configuration Management** - Flexible service endpoint and timeout configuration
- **MCP Integration** - Exposing browser automation through MCP tools for Claude Desktop

**Development Approach:**
- **Service-Oriented Architecture** - Clean separation between framework and browser service
- **Standard Integration Pattern** - Similar to integrating with any external API service
- **No Source Code Modification** - Zero changes to Steel Browser's codebase
- **Proper Attribution** - Clear acknowledgment of Steel Browser's contributions

### **Hackathon Compliance**

This integration represents legitimate **"building from scratch using open source tools"** because:

✅ **Service Consumption** - We use Steel Browser as an external service, like using PostgreSQL or Redis  
✅ **Custom Client Code** - All integration code is our original work  
✅ **No Code Forking** - We don't distribute or modify Steel Browser's source code  
✅ **Standard Practice** - This is how modern applications integrate with external services  
✅ **Apache 2.0 License** - Explicitly permits commercial use and service consumption  

### **Technical Independence**

**Our Implementation is Fully Independent:**
- Can switch to different browser automation services without changing agent code
- All business logic and AI integration is our original work
- Service endpoint configuration makes Steel Browser swappable
- Error handling and retry logic is our custom implementation
- MCP integration and Claude Desktop functionality is entirely our contribution

---

## 📚 **Related Documentation**

- **[Getting Started Guide](GETTING_STARTED.md)** - Basic framework setup
- **[Agent Development Tutorial](AGENT_DEVELOPMENT_TUTORIAL.md)** - Complete agent development guide
- **[BaseAgent API Reference](BASEAGENT_API_REFERENCE.md)** - Complete API documentation
- **[Best Practices](BEST_PRACTICES.md)** - Professional development guidelines
- **[Open Source Strategy](../internal_docs/strategy/OPEN_SOURCE_RELEASE_STRATEGY.md)** - Framework open source approach

---

## 🙏 **Acknowledgments**

**Special thanks to the [Steel Browser](https://github.com/steel-dev/steel-browser) team** for creating an excellent open source browser automation service. Their work provides the reliable browser infrastructure that powers Agent Forge's web automation capabilities.

Agent Forge's Steel Browser integration demonstrates how modern frameworks can build upon open source services while contributing original value through innovative integration patterns, async architecture, and AI-first development approaches.

---

**Steel Browser integration in Agent Forge provides a powerful, reliable foundation for web automation built on proven open source technology. The service-based integration is designed to be simple to use while providing access to advanced features when needed. Follow the patterns in this guide to build robust, production-ready web automation agents.**