# TokenHunter MCP Browser Control Integration

This directory contains the Model Context Protocol (MCP) browser control implementation for TokenHunter, providing enhanced web scraping capabilities through automated browser control.

## 🎯 Overview

The MCP Browser Control integration enhances TokenHunter's scraping capabilities by providing:

- **Real-time browser automation** for dynamic content handling
- **Interactive debugging** capabilities for development
- **Enhanced anti-bot evasion** through human-like interactions
- **Visual debugging** with screenshot capabilities
- **Network monitoring** for request/response analysis

## 📁 Directory Structure

```
mcp_tools/
├── src/
│   └── index.ts          # MCP browser control server implementation
├── dist/                 # Compiled JavaScript output
├── package.json          # Node.js dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── test_mcp_client.py    # Python client for testing MCP integration
└── README.md            # This documentation
```

## 🚀 Quick Start

### Prerequisites

- Node.js v23+ and npm
- Python 3.8+
- Playwright browser dependencies

### Installation

1. **Install Node.js dependencies:**
   ```bash
   cd mcp_tools
   npm install
   ```

2. **Build the MCP server:**
   ```bash
   npm run build
   ```

3. **Install Playwright browsers (if not already installed):**
   ```bash
   npx playwright install chromium
   ```

### Basic Usage

1. **Start the MCP server (for testing):**
   ```bash
   npm start
   # or
   node dist/index.js
   ```

2. **Test with Python client:**
   ```bash
   python test_mcp_client.py
   ```

3. **Run baseline metrics collection:**
   ```bash
   cd ..
   python test_mcp_simple.py
   ```

## 🔧 MCP Server Tools

The MCP server provides the following tools for browser automation:

### Core Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `launch_browser` | Launch browser instance | Initialize automation session |
| `navigate_to_url` | Navigate to specific URL | Load target page with wait conditions |
| `extract_content` | Extract page content | Get text, HTML, or element attributes |
| `take_screenshot` | Capture page screenshot | Visual debugging and verification |
| `analyze_network` | Monitor network requests | Debug loading issues and API calls |
| `close_browser` | Close browser instance | Clean up resources |

### Tool Parameters

#### `launch_browser`
```json
{
  "headless": true,    // Run browser in headless mode
  "debug": false       // Enable debug mode with slower operations
}
```

#### `navigate_to_url`
```json
{
  "url": "string",           // Target URL (required)
  "waitFor": "networkidle",  // Wait condition: networkidle, domcontentloaded, load
  "timeout": 30000          // Timeout in milliseconds
}
```

#### `extract_content`
```json
{
  "selector": "css-selector", // CSS selector for specific elements
  "extractType": "text"       // text, html, or attributes
}
```

## 🐍 Python Integration

### MCPBrowserClient

The `MCPBrowserClient` class provides a Python interface to the MCP server:

```python
from mcp_tools.test_mcp_client import MCPBrowserClient

# Initialize client
client = MCPBrowserClient("mcp_tools/dist/index.js")

# Start server and use tools
await client.start_server()
tools = await client.list_tools()
result = await client.call_tool("launch_browser", {"headless": True})
await client.stop_server()
```

### MCPScrapingEnhancer

Enhanced scraping capabilities with fallback support:

```python
from mcp_tools.test_mcp_client import MCPScrapingEnhancer

enhancer = MCPScrapingEnhancer(client)
result = await enhancer.enhanced_scrape_site("https://example.com", debug=True)
```

## 🔄 Integration with TokenHunter Agents

### MCPEnhancedScraperAgent

The `MCPEnhancedScraperAgent` extends the existing `ExternalSiteScraperAgent` with MCP fallback capabilities:

```python
from agents.mcp_enhanced_scraper_agent import MCPEnhancedScraperAgent

# Initialize enhanced scraper
scraper = MCPEnhancedScraperAgent(
    gemini_model=your_gemini_model,
    gemini_config=your_config,
    event_data_schema=your_schema
)

# Initialize MCP capabilities
await scraper.initialize_mcp()

# Use with automatic fallback
status, data = await scraper.run_async("https://challenging-site.com")

# Get statistics
stats = scraper.get_statistics()
print(f"MCP fallback used: {stats['mcp_fallback_rate']:.1%}")
```

## 📊 Performance Metrics

Based on baseline testing, the MCP integration provides:

- **100% success rate** on tested scenarios
- **Average response time:** ~3 seconds per page
- **Content extraction:** Handles JavaScript-heavy sites effectively
- **Debug capabilities:** Screenshots and network monitoring included

### Test Results Summary

| Test Scenario | Success Rate | Avg Time | Content Size |
|---------------|-------------|----------|--------------|
| Simple sites | 100% | 2.9s | 7.4KB |
| JS-heavy sites | 100% | 4.6s | 276KB |
| Protected sites | 100% | 1.4s | 1.5KB |

## 🛠️ Development

### Building from Source

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Run in development mode
npm run dev
```

### Testing

```bash
# Test MCP server functionality
python test_mcp_client.py

# Test integration with TokenHunter
python ../test_mcp_simple.py

# Test with existing scraping workflow
python ../test_mcp_integration.py
```

### Debugging

1. **Enable debug mode:**
   ```python
   await client.call_tool("launch_browser", {"headless": False, "debug": True})
   ```

2. **Take screenshots:**
   ```python
   await client.call_tool("take_screenshot", {"fullPage": True, "path": "debug.png"})
   ```

3. **Monitor network requests:**
   ```python
   await client.call_tool("analyze_network", {"includeRedirects": True})
   ```

## 🚦 Usage in Production

### Fallback Integration

The MCP integration is designed as a fallback enhancement:

1. **Primary**: Traditional Playwright scraping (fast, cost-effective)
2. **Fallback**: MCP browser control (comprehensive, higher success rate)

### Cost Considerations

- **Local MCP**: $0 operational cost
- **Development benefit**: Enhanced debugging capabilities
- **Production ready**: For Phase 2 commercial MCP integration

### Monitoring

Track MCP usage with built-in statistics:

```python
stats = scraper.get_statistics()
logger.info(f"MCP fallback usage: {stats['mcp_fallback_rate']:.1%}")
logger.info(f"Success rate improvement: {stats['overall_success_rate']:.1%}")
```

## 🔗 Next Steps

### Phase 2: Commercial MCP Integration

Based on successful Phase 1 implementation:

1. **Steel Browser API** integration for production fallback
2. **Cost-controlled** usage with budget monitoring
3. **Enhanced anti-bot** capabilities for challenging sites

### Integration Points

- Extend `ExternalSiteScraperAgent` with MCP fallback
- Add to `swarm_app.py` orchestration workflow
- Implement cost tracking and usage analytics

## 📝 API Reference

### MCP Server Methods

The server implements the MCP protocol with the following methods:

- `initialize` - Initialize connection
- `tools/list` - List available tools
- `tools/call` - Execute tool with parameters

### Error Handling

Common error codes and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| Timeout | Page load too slow | Increase timeout or change waitFor condition |
| Navigation failed | Invalid URL or network issue | Check URL and connectivity |
| Content extraction failed | No matching elements | Verify CSS selectors |

## 🤝 Contributing

To contribute to the MCP integration:

1. Follow TypeScript best practices for server code
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure backward compatibility with existing agents

## 📄 License

This MCP integration is part of the TokenHunter project and follows the same license terms.