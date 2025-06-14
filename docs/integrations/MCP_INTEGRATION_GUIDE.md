# 🔗 Agent Forge MCP Integration Guide

**Complete technical guide for integrating Agent Forge with Model Context Protocol (MCP) clients**

Agent Forge provides **native MCP integration** enabling your autonomous agents to work seamlessly in **Claude Desktop**, Cursor, and other MCP clients through natural language conversation. This guide covers everything from basic setup to advanced customization.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Setup](#quick-setup) 
- [Technical Architecture](#technical-architecture)
- [Available Tools](#available-tools)
- [Advanced Configuration](#advanced-configuration)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

### What is MCP Integration?

Model Context Protocol (MCP) is Anthropic's open standard for connecting AI assistants to external tools and data sources. Agent Forge's MCP integration allows you to:

- **Use Agent Forge agents through natural conversation** in Claude Desktop
- **Access web automation capabilities** through simple requests
- **Generate blockchain proofs** via conversational commands
- **Leverage 8+ specialized agents** without coding
- **Scale agent capabilities** across multiple MCP clients

### Key Benefits

- **🚀 Zero Learning Curve**: Natural language interface for non-technical users
- **⚡ Instant Access**: 5-minute setup to full functionality
- **🔧 Production Ready**: Battle-tested agents with robust error handling
- **🌐 Cross-Platform**: Works in Claude Desktop, Cursor, and other MCP clients
- **🤖 Auto-Discovery**: Automatically exposes all available agents as MCP tools

## ⚡ Quick Setup

### Prerequisites

- Python 3.9+ installed
- Agent Forge framework installed
- Claude Desktop or other MCP client

### 1. Install MCP Dependencies

```bash
# Navigate to Agent Forge directory
cd /path/to/agent_forge

# Install MCP requirements
pip install -r mcp_requirements.txt
```

### 2. Test MCP Server

```bash
# Test the MCP server functionality
python mcp_server_enhanced.py
```

You should see output indicating successful agent discovery and tool registration.

### 3. Configure Claude Desktop

**For detailed Claude Desktop setup, see:** [Claude Desktop Setup Guide](../CLAUDE_DESKTOP_SETUP.md)

Add this configuration to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "python",
      "args": ["/full/path/to/agent_forge/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/agent_forge"
      }
    }
  }
}
```

### 4. Restart and Test

1. Restart Claude Desktop
2. Test with: `"Claude, use get_agent_info to show me available Agent Forge tools"`

## 🏗️ Technical Architecture

### MCP Server Components

Agent Forge's MCP integration consists of three main components:

#### 1. **Core MCP Server** (`mcp_server.py`)
```python
# 6 core tools providing essential Agent Forge functionality
tools = [
    "navigate_website",      # Web automation with Steel Browser
    "generate_blockchain_proof",  # NMKR NFT generation
    "compile_data_from_sources",  # Multi-source data aggregation
    "extract_text_content",  # Content extraction
    "validate_website_data", # Website validation
    "get_agent_info"        # Agent capabilities overview
]
```

#### 2. **Auto-Discovery System** (`mcp_auto_discovery.py`)
```python
# Automatically discovers and registers Agent Forge agents
class AgentDiscovery:
    def discover_agents() -> List[Type[AsyncContextAgent]]
    
class MCPToolGenerator:
    def generate_tools_from_agents(agents: List[Type[AsyncContextAgent]])
```

#### 3. **Enhanced MCP Server** (`mcp_server_enhanced.py`)
```python
# Combines core tools + auto-discovered agents + diagnostics
enhanced_tools = core_tools + auto_discovered_tools + [
    "get_agent_forge_status",     # System diagnostics
    "execute_agent_by_name",      # Direct agent execution
    "test_agent_forge_installation"  # Installation validation
]
```

### Data Flow Architecture

```
Claude Desktop Request
          ↓
    MCP Protocol Layer
          ↓
    Agent Forge MCP Server
          ↓
    Tool Routing & Validation
          ↓
    Agent Execution Engine
          ↓
    Steel Browser / NMKR / Masumi
          ↓
    Structured Response
          ↓
    MCP Protocol Response
          ↓
    Claude Desktop Display
```

### Security Model

- **Environment Isolation**: Each agent runs in isolated execution context
- **Input Validation**: All MCP inputs validated before agent execution
- **Error Containment**: Agent failures don't crash MCP server
- **Resource Management**: Automatic cleanup of agent resources
- **Credential Security**: API keys managed through environment variables

## 🛠️ Available Tools

### Core Tools (Always Available)

#### **navigate_website**
**Purpose**: Web automation with Steel Browser integration
```python
# Usage in Claude Desktop
"Navigate to TechCrunch and extract the main headlines"

# Parameters
url: str           # Target website URL
instructions: str  # Natural language navigation instructions
```

#### **generate_blockchain_proof**
**Purpose**: Generate NMKR NFT proof for task verification
```python
# Usage in Claude Desktop  
"Generate a blockchain proof for analyzing the Apple homepage"

# Parameters
task_description: str  # Description of task to prove
url: str              # URL analyzed (optional)
```

#### **compile_data_from_sources**
**Purpose**: Multi-source data aggregation and analysis
```python
# Usage in Claude Desktop
"Compile data from these 3 competitor websites and create a comparison"

# Parameters
sources: List[str]    # List of data sources/URLs
instructions: str     # Compilation instructions
```

#### **extract_text_content**
**Purpose**: Intelligent content extraction from web pages
```python
# Usage in Claude Desktop
"Extract the full article content from this research paper URL"

# Parameters
url: str             # Source URL
content_type: str    # Type of content to extract (optional)
```

#### **validate_website_data**
**Purpose**: Website validation and accessibility checking
```python
# Usage in Claude Desktop
"Validate our company website for accessibility issues"

# Parameters
url: str                # Website to validate
validation_type: str    # Type of validation (optional)
```

#### **get_agent_info**
**Purpose**: Agent capabilities overview and status
```python
# Usage in Claude Desktop
"Show me all available Agent Forge tools and their capabilities"

# No parameters required
```

### Auto-Discovered Agent Tools

Agent Forge automatically discovers and exposes these agents as MCP tools:

#### **data_compiler**
- **Purpose**: Advanced data compilation and analysis
- **Specialization**: Multi-source data aggregation with AI enhancement

#### **external_site_scraper**  
- **Purpose**: Comprehensive website scraping
- **Specialization**: Large-scale content extraction

#### **simple_navigation**
- **Purpose**: Basic web navigation and extraction
- **Specialization**: Quick page analysis and data retrieval

#### **crew_ai**
- **Purpose**: Multi-agent coordination
- **Specialization**: Complex task orchestration

#### **masumi_navigation**
- **Purpose**: Blockchain-enabled navigation
- **Specialization**: Web3 and blockchain site analysis

#### **nmkrauditor**
- **Purpose**: NMKR blockchain auditing
- **Specialization**: Cardano NFT verification and auditing

#### **page_scraper**
- **Purpose**: Targeted page content extraction
- **Specialization**: Clean content extraction with formatting

#### **enhanced_validation**
- **Purpose**: Advanced data validation
- **Specialization**: Multi-layer validation with quality scoring

### Diagnostic Tools (Enhanced Server Only)

#### **get_agent_forge_status**
- **Purpose**: System health and agent availability diagnostics
- **Returns**: Agent count, system status, configuration validation

#### **execute_agent_by_name**
- **Purpose**: Direct agent execution by name
- **Parameters**: `agent_name: str, url: str, instructions: str`

#### **test_agent_forge_installation**
- **Purpose**: Comprehensive installation and dependency validation
- **Returns**: Installation status, missing dependencies, configuration issues

## ⚙️ Advanced Configuration

### Custom Environment Variables

```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "python",
      "args": ["/full/path/to/agent_forge/mcp_server_enhanced.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/agent_forge",
        "NMKR_API_KEY": "your-nmkr-api-key",
        "STEEL_BROWSER_API_KEY": "your-steel-browser-key",
        "LOG_LEVEL": "INFO",
        "MCP_DEBUG": "true"
      }
    }
  }
}
```

### Virtual Environment Configuration

```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "/full/path/to/agent_forge/venv/bin/python",
      "args": ["/full/path/to/agent_forge/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/agent_forge"
      }
    }
  }
}
```

### Multiple Server Configuration

```json
{
  "mcpServers": {
    "agent-forge-core": {
      "command": "python",
      "args": ["/path/to/agent_forge/mcp_server.py"]
    },
    "agent-forge-enhanced": {
      "command": "python", 
      "args": ["/path/to/agent_forge/mcp_server_enhanced.py"]
    }
  }
}
```

### Logging and Debugging

Enable detailed logging for troubleshooting:

```bash
# Set environment variables for debugging
export LOG_LEVEL=DEBUG
export MCP_DEBUG=true

# Run server with verbose output
python mcp_server_enhanced.py --verbose
```

## 👨‍💻 Development Guide

### Creating Custom MCP Tools

You can extend the MCP server with custom tools:

```python
# In mcp_server.py or custom file
from fastmcp import FastMCP

app = FastMCP("Agent Forge")

@app.tool()
def custom_agent_tool(url: str, task: str) -> str:
    """Custom agent implementation"""
    # Your custom agent logic here
    return "Custom agent result"
```

### Adding New Agent Discovery

Extend the auto-discovery system:

```python
# In mcp_auto_discovery.py
class CustomAgentDiscovery(AgentDiscovery):
    def discover_custom_agents(self) -> List[Type[AsyncContextAgent]]:
        # Custom agent discovery logic
        return discovered_agents
```

### Testing Custom Integrations

```python
# Test script for custom tools
import asyncio
from mcp_server_enhanced import app

async def test_custom_tool():
    result = await app.call_tool("custom_agent_tool", {
        "url": "https://example.com",
        "task": "Test task"
    })
    print(f"Result: {result}")

asyncio.run(test_custom_tool())
```

### Performance Optimization

#### Async Execution
All agents run asynchronously for optimal performance:

```python
# Concurrent agent execution example
async def run_multiple_agents():
    tasks = [
        agent1.run(url1, task1),
        agent2.run(url2, task2),
        agent3.run(url3, task3)
    ]
    results = await asyncio.gather(*tasks)
    return results
```

#### Resource Management
Proper cleanup prevents resource leaks:

```python
@app.tool()
async def managed_agent_tool(url: str) -> str:
    agent = None
    try:
        agent = SomeAgent()
        result = await agent.run(url)
        return result
    finally:
        if agent:
            await agent.cleanup()
```

#### Caching Strategies
Cache frequently used results:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_agent_result(url: str, instructions: str) -> str:
    # Cached computation
    return result
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### "MCP server not found"
**Cause**: Incorrect file paths in configuration
**Solution**: 
```bash
# Verify paths exist
ls -la /full/path/to/agent_forge/mcp_server.py

# Test Python can import
python -c "import sys; sys.path.append('/path/to/agent_forge'); from mcp_server import app"
```

#### "Import errors during startup"
**Cause**: Missing dependencies or PYTHONPATH issues
**Solution**:
```bash
# Install all requirements
pip install -r mcp_requirements.txt

# Verify Agent Forge can be imported
python -c "from core.agents.base_agent import AsyncContextAgent"
```

#### "Agent execution fails"
**Cause**: Missing API keys or configuration
**Solution**:
```bash
# Check environment variables
echo $NMKR_API_KEY
echo $STEEL_BROWSER_API_KEY

# Test individual agents
python cli.py run simple_navigation --url https://example.com
```

#### "Performance issues"
**Cause**: Resource contention or memory leaks
**Solution**:
```python
# Monitor resource usage
import psutil
print(f"Memory usage: {psutil.virtual_memory().percent}%")

# Enable garbage collection
import gc
gc.collect()
```

### Diagnostic Commands

#### Test MCP Server Health
```bash
# Basic functionality test
python mcp_server_enhanced.py --test

# Full diagnostic
python -c "
from mcp_auto_discovery import AgentDiscovery
discovery = AgentDiscovery()
agents = discovery.discover_agents()
print(f'Found {len(agents)} agents')
"
```

#### Validate Agent Discovery
```bash
python -c "
from mcp_auto_discovery import AgentDiscovery, MCPToolGenerator
discovery = AgentDiscovery()
agents = discovery.discover_agents()
generator = MCPToolGenerator()
tools = generator.generate_tools_from_agents(agents)
print(f'Generated {len(tools)} MCP tools')
"
```

#### Check Claude Desktop Logs
- **macOS**: `~/Library/Logs/Claude/claude_desktop.log`
- **Windows**: `%LOCALAPPDATA%\Claude\logs\claude_desktop.log`
- **Linux**: `~/.local/share/Claude/logs/claude_desktop.log`

### Advanced Debugging

#### Enable MCP Protocol Logging
```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "python",
      "args": ["/path/to/agent_forge/mcp_server_enhanced.py"],
      "env": {
        "MCP_LOG_LEVEL": "DEBUG",
        "MCP_TRACE": "true"
      }
    }
  }
}
```

#### Custom Error Handling
```python
# In your MCP server
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.tool()
async def debug_agent_tool(url: str) -> str:
    try:
        logger.info(f"Processing URL: {url}")
        # Agent execution
        result = await some_agent.run(url)
        logger.info(f"Success: {result[:100]}...")
        return result
    except Exception as e:
        logger.error(f"Agent failed: {str(e)}", exc_info=True)
        raise
```

## 📚 Additional Resources

### Documentation Links
- **[Claude Desktop Setup](../CLAUDE_DESKTOP_SETUP.md)** - Quick 5-minute setup guide
- **[MCP Tools Reference](../api/MCP_TOOLS_REFERENCE.md)** - Complete tool documentation
- **[Framework Architecture](../architecture/FRAMEWORK_ARCHITECTURE.md)** - Core concepts and patterns
- **[NMKR Integration](NMKR_PROOF_OF_EXECUTION_GUIDE.md)** - Blockchain proof generation
- **[Steel Browser Integration](STEEL_BROWSER_INTEGRATION.md)** - Web automation setup

### Community and Support
- **Framework Memory Bank**: `/memory-bank/` - Development context and history
- **Example Implementations**: `/examples/` - Working agent code samples
- **Core Framework**: `/core/` - Source code and utilities
- **GitHub Issues**: Report bugs and request features

### Next Steps
1. **Try the Quick Setup** above to get running in 5 minutes
2. **Explore available tools** with `get_agent_info` in Claude Desktop  
3. **Test core functionality** with example commands
4. **Review advanced configuration** for production use
5. **Develop custom tools** using the development guide

---

**Ready to get started?** Follow the [Quick Setup](#quick-setup) section above, or jump directly to the [Claude Desktop Setup Guide](../CLAUDE_DESKTOP_SETUP.md) for step-by-step instructions.