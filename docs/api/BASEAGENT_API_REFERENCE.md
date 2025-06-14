# 📖 BaseAgent API Reference

Complete API documentation for the BaseAgent class, the foundation of all Agent Forge agents.

## 📋 **Table of Contents**

- [Class Overview](#class-overview)
- [Constructor](#constructor)
- [Core Methods](#core-methods)
- [Properties](#properties)
- [Event Hooks](#event-hooks)
- [Error Handling](#error-handling)
- [Examples](#examples)

---

## 🎯 **Class Overview**

The `BaseAgent` class is the abstract base class that provides the foundation for all Agent Forge agents. It implements the core lifecycle, logging, configuration, and resource management patterns.

### **Class Definition**

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

class BaseAgent(ABC):
    """
    Abstract base class for all Agent Forge agents.
    
    Provides standard lifecycle management, configuration handling,
    logging capabilities, and resource management patterns.
    """
```

### **Key Features**

- **Lifecycle Management** - Standardized initialization, execution, and cleanup
- **Async Support** - Built-in async/await patterns for modern Python
- **Configuration** - Flexible configuration management system
- **Logging** - Comprehensive logging with agent-specific loggers
- **Resource Management** - Automatic browser client and resource setup
- **Status Monitoring** - Built-in status reporting and health checks
- **Error Handling** - Comprehensive error handling patterns

---

## 🏗️ **Constructor**

### **`__init__(self, name: Optional[str] = None, config: Optional[Dict[str, Any]] = None)`**

Initialize a new BaseAgent instance.

**Parameters:**
- `name` (Optional[str]) - Agent name for logging and identification
- `config` (Optional[Dict[str, Any]]) - Configuration dictionary

**Example:**
```python
# Basic initialization
agent = MyAgent()

# With name
agent = MyAgent(name="my_custom_agent")

# With configuration
config = {"timeout": 30, "debug": True}
agent = MyAgent(name="configured_agent", config=config)
```

**Configuration Properties Set:**
- `self.name` - Agent name (auto-generated if not provided)
- `self.config` - Configuration dictionary
- `self.logger` - Agent-specific logger
- `self._initialized` - Initialization state flag
- `self.browser_client` - Browser client (set during initialization)

---

## 🔧 **Core Methods**

### **Lifecycle Methods**

#### **`async initialize(self) -> bool`**

Initialize the agent and set up resources.

**Returns:** `bool` - True if initialization successful, False otherwise

**Behavior:**
- Sets up browser client with Steel Browser integration
- Calls `_initialize()` hook for agent-specific setup
- Marks agent as initialized
- Handles initialization errors gracefully

**Example:**
```python
class MyAgent(BaseAgent):
    async def run(self):
        if not self.is_ready():
            success = await self.initialize()
            if not success:
                return None
        # Agent logic here
```

**Override Pattern:**
```python
class CustomAgent(BaseAgent):
    async def _initialize(self) -> bool:
        """Agent-specific initialization logic."""
        # Custom setup code
        self.api_client = MyAPIClient()
        return True
```

---

#### **`async cleanup(self) -> None`**

Clean up agent resources.

**Behavior:**
- Calls `_cleanup()` hook for agent-specific cleanup
- Closes browser client if available
- Handles cleanup errors gracefully
- Resets initialization state

**Example:**
```python
# Automatic cleanup (recommended)
async with MyAgent() as agent:
    result = await agent.run()

# Manual cleanup
agent = MyAgent()
try:
    await agent.initialize()
    result = await agent.run()
finally:
    await agent.cleanup()
```

**Override Pattern:**
```python
class CustomAgent(BaseAgent):
    async def _cleanup(self) -> None:
        """Agent-specific cleanup logic."""
        if hasattr(self, 'api_client'):
            await self.api_client.close()
```

---

#### **`@abstractmethod async run(self, *args, **kwargs) -> Any`**

Execute the agent's main logic. **Must be implemented by subclasses.**

**Parameters:** Variable arguments and keyword arguments
**Returns:** Any - Agent execution results

**Example Implementation:**
```python
class MyAgent(BaseAgent):
    async def run(self, url: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """
        Navigate to URL and extract information.
        
        Args:
            url: Target URL to analyze
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with analysis results or None if failed
        """
        self.logger.info(f"Processing URL: {url}")
        
        try:
            response = await self.browser_client.navigate(url)
            return {
                "url": url,
                "title": response.get('page_title'),
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return None
```

---

### **Status and Monitoring Methods**

#### **`is_ready(self) -> bool`**

Check if the agent is ready for execution.

**Returns:** `bool` - True if agent is initialized and ready

**Example:**
```python
agent = MyAgent()
if not agent.is_ready():
    await agent.initialize()

# Now safe to run
result = await agent.run()
```

---

#### **`get_status(self) -> Dict[str, Any]`**

Get comprehensive agent status information.

**Returns:** `Dict[str, Any]` - Status dictionary with agent information

**Example:**
```python
agent = MyAgent()
status = agent.get_status()
print(f"Agent: {status['name']}")
print(f"Ready: {status['ready']}")
print(f"Browser Available: {status['browser_available']}")
```

**Status Dictionary Structure:**
```python
{
    "name": "agent_name",
    "ready": True,
    "initialized": True,
    "browser_available": True,
    "config_loaded": True,
    "logger_available": True,
    "class_name": "MyAgent"
}
```

---

### **Context Manager Support**

#### **`async __aenter__(self)`**

Async context manager entry - automatically initializes agent.

**Returns:** `self` - The agent instance

#### **`async __aexit__(self, exc_type, exc_val, exc_tb)`**

Async context manager exit - automatically cleans up resources.

**Example:**
```python
# Recommended usage pattern
async def process_urls(urls: List[str]):
    async with MyAgent() as agent:
        results = []
        for url in urls:
            result = await agent.run(url)
            results.append(result)
        return results
```

---

## 📊 **Properties**

### **Configuration Properties**

#### **`name: str`**
Agent name for identification and logging.

```python
agent = MyAgent(name="web_analyzer")
print(agent.name)  # "web_analyzer"
```

#### **`config: Dict[str, Any]`**
Agent configuration dictionary.

```python
agent = MyAgent(config={"timeout": 30, "debug": True})
timeout = agent.config.get("timeout", 10)
```

#### **`logger: logging.Logger`**
Agent-specific logger instance.

```python
agent = MyAgent()
agent.logger.info("Processing started")
agent.logger.error("An error occurred")
```

### **Resource Properties**

#### **`browser_client: SteelBrowserClient`**
Browser automation client (available after initialization).

```python
async with MyAgent() as agent:
    response = await agent.browser_client.navigate("https://example.com")
```

### **State Properties**

#### **`_initialized: bool`**
Internal flag tracking initialization state.

```python
agent = MyAgent()
print(agent._initialized)  # False

await agent.initialize()
print(agent._initialized)  # True
```

---

## 🔄 **Event Hooks**

BaseAgent provides several hooks that subclasses can override for custom behavior.

### **`async _initialize(self) -> bool`**

Called during initialization for agent-specific setup.

**Returns:** `bool` - True if successful, False otherwise

**Example:**
```python
class DatabaseAgent(BaseAgent):
    async def _initialize(self) -> bool:
        """Set up database connection."""
        try:
            self.db = await setup_database()
            return True
        except Exception as e:
            self.logger.error(f"Database setup failed: {e}")
            return False
```

### **`async _cleanup(self) -> None`**

Called during cleanup for agent-specific resource cleanup.

**Example:**
```python
class FileProcessingAgent(BaseAgent):
    async def _cleanup(self) -> None:
        """Clean up temporary files."""
        if hasattr(self, 'temp_files'):
            for file_path in self.temp_files:
                try:
                    os.remove(file_path)
                except OSError:
                    pass
```

### **`_configure_logging(self) -> None`**

Called during initialization to set up agent-specific logging.

**Example:**
```python
class VerboseAgent(BaseAgent):
    def _configure_logging(self) -> None:
        """Set up verbose logging."""
        super()._configure_logging()
        self.logger.setLevel(logging.DEBUG)
        
        # Add custom handler
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(handler)
```

---

## ⚠️ **Error Handling**

### **Exception Handling Patterns**

BaseAgent implements comprehensive error handling throughout the lifecycle.

#### **Initialization Errors**

```python
class RobustAgent(BaseAgent):
    async def _initialize(self) -> bool:
        """Initialize with proper error handling."""
        try:
            # Risky initialization code
            self.api_client = await setup_api_client()
            return True
        except ConnectionError as e:
            self.logger.error(f"API connection failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected initialization error: {e}")
            return False
```

#### **Runtime Errors**

```python
class SafeAgent(BaseAgent):
    async def run(self, url: str) -> Optional[Dict[str, Any]]:
        """Run with comprehensive error handling."""
        try:
            # Validate inputs
            if not url or not isinstance(url, str):
                raise ValueError("Invalid URL provided")
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self._process_url(url),
                timeout=30
            )
            
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"Processing timeout for {url}")
            return {"status": "timeout", "url": url}
            
        except ValueError as e:
            self.logger.error(f"Validation error: {e}")
            return {"status": "validation_error", "error": str(e)}
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {"status": "error", "error": str(e)}
```

#### **Cleanup Errors**

```python
class CleanupAgent(BaseAgent):
    async def _cleanup(self) -> None:
        """Cleanup with error handling."""
        # Close resources individually with error handling
        if hasattr(self, 'api_client'):
            try:
                await self.api_client.close()
            except Exception as e:
                self.logger.warning(f"API client cleanup failed: {e}")
        
        if hasattr(self, 'file_handles'):
            for handle in self.file_handles:
                try:
                    handle.close()
                except Exception as e:
                    self.logger.warning(f"File handle cleanup failed: {e}")
```

---

## 💡 **Examples**

### **Basic Agent Implementation**

```python
class SimpleWebAgent(BaseAgent):
    """Basic web page analyzer."""
    
    def __init__(self, name: Optional[str] = None, config: Optional[dict] = None):
        super().__init__(name, config)
    
    async def run(self, url: str) -> Optional[Dict[str, Any]]:
        """Analyze a web page."""
        self.logger.info(f"Analyzing: {url}")
        
        try:
            response = await self.browser_client.navigate(url)
            
            if response:
                return {
                    "url": url,
                    "title": response.get('page_title', 'Unknown'),
                    "content_length": len(response.get('content', '')),
                    "status": "success"
                }
            else:
                return {"url": url, "status": "failed"}
                
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return {"url": url, "status": "error", "error": str(e)}

# Usage
async def main():
    async with SimpleWebAgent() as agent:
        result = await agent.run("https://example.com")
        print(result)
```

### **Configurable Agent**

```python
class ConfigurableAgent(BaseAgent):
    """Agent with extensive configuration support."""
    
    def __init__(self, name: Optional[str] = None, config: Optional[dict] = None):
        super().__init__(name, config)
        
        # Configuration with defaults
        self.timeout = self.config.get('timeout', 30)
        self.retries = self.config.get('retries', 3)
        self.delay = self.config.get('delay', 1)
        
    async def run(self, url: str) -> Optional[Dict[str, Any]]:
        """Run with configuration-driven behavior."""
        for attempt in range(self.retries):
            try:
                self.logger.info(f"Attempt {attempt + 1}/{self.retries}")
                
                response = await asyncio.wait_for(
                    self.browser_client.navigate(url),
                    timeout=self.timeout
                )
                
                if response:
                    return {
                        "url": url,
                        "title": response.get('page_title'),
                        "attempts": attempt + 1,
                        "status": "success"
                    }
                    
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.retries - 1:
                    await asyncio.sleep(self.delay)
        
        return {"url": url, "status": "failed", "attempts": self.retries}

# Usage with configuration
config = {
    "timeout": 45,
    "retries": 5,
    "delay": 2
}

async def main():
    async with ConfigurableAgent(config=config) as agent:
        result = await agent.run("https://example.com")
        print(result)
```

### **Stateful Agent**

```python
class StatefulAgent(BaseAgent):
    """Agent that maintains state across operations."""
    
    def __init__(self, name: Optional[str] = None, config: Optional[dict] = None):
        super().__init__(name, config)
        self.processed_urls = set()
        self.results_cache = {}
    
    async def _initialize(self) -> bool:
        """Initialize with state loading."""
        success = await super()._initialize()
        if not success:
            return False
        
        # Load previous state if available
        await self._load_state()
        return True
    
    async def run(self, url: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """Run with caching and state management."""
        # Check cache unless force refresh
        if not force_refresh and url in self.results_cache:
            self.logger.info(f"Returning cached result for {url}")
            return self.results_cache[url]
        
        # Process URL
        self.logger.info(f"Processing new URL: {url}")
        
        try:
            response = await self.browser_client.navigate(url)
            
            if response:
                result = {
                    "url": url,
                    "title": response.get('page_title'),
                    "processed_at": datetime.now().isoformat(),
                    "status": "success"
                }
                
                # Update state
                self.processed_urls.add(url)
                self.results_cache[url] = result
                
                # Save state
                await self._save_state()
                
                return result
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return {"url": url, "status": "error", "error": str(e)}
    
    async def _load_state(self):
        """Load agent state."""
        # Implementation would load from file/database
        pass
    
    async def _save_state(self):
        """Save agent state."""
        # Implementation would save to file/database
        pass
    
    async def _cleanup(self) -> None:
        """Cleanup with state saving."""
        await self._save_state()
        await super()._cleanup()

# Usage
async def main():
    async with StatefulAgent() as agent:
        # First run - processes URL
        result1 = await agent.run("https://example.com")
        
        # Second run - returns cached result
        result2 = await agent.run("https://example.com")
        
        # Force refresh
        result3 = await agent.run("https://example.com", force_refresh=True)
```

---

## 📚 **Related Documentation**

- **[Getting Started Guide](GETTING_STARTED.md)** - Quick introduction to agent development
- **[Agent Development Tutorial](AGENT_DEVELOPMENT_TUTORIAL.md)** - Complete development guide
- **[Framework Architecture](FRAMEWORK_ARCHITECTURE.md)** - Framework design and patterns
- **[Steel Browser Integration](STEEL_BROWSER_INTEGRATION.md)** - Web automation guide
- **[Best Practices](BEST_PRACTICES.md)** - Professional development guidelines

---

**The BaseAgent class provides a comprehensive foundation for building autonomous AI agents. This API reference covers all available methods, properties, and patterns. Use this documentation alongside the examples and tutorials to build sophisticated, production-ready agents.**