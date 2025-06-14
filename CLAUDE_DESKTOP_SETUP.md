# Agent Forge - Claude Desktop Integration Guide

This guide shows you how to integrate Agent Forge agents with Claude Desktop using the Model Context Protocol (MCP).

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
# Navigate to Agent Forge directory
cd /path/to/agent_forge

# Install MCP dependencies
pip install -r mcp_requirements.txt

# Or install individually
pip install fastmcp mcp aiohttp
```

### 2. Test the MCP Server

```bash
# Test the server locally
python mcp_server.py

# Or test with MCP inspector
mcp dev mcp_server.py
```

### 3. Configure Claude Desktop

#### For macOS:
Edit the configuration file at:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### For Windows:
Edit the configuration file at:
```
%APPDATA%/Claude/claude_desktop_config.json
```

#### For Linux:
Edit the configuration file at:
```
~/.config/Claude/claude_desktop_config.json
```

### 4. Add Agent Forge Configuration

Add this configuration to your `claude_desktop_config.json`:

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

**Important**: Replace `/full/path/to/agent_forge` with the actual path to your Agent Forge directory.

#### Example with virtual environment:
```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "/full/path/to/agent_forge/venv_unified/bin/python",
      "args": ["/full/path/to/agent_forge/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/agent_forge"
      }
    }
  }
}
```

### 5. Restart Claude Desktop

Close and reopen Claude Desktop to load the new MCP server configuration.

## Available Agent Forge Tools in Claude Desktop

Once configured, you can use these tools in Claude Desktop:

### 1. **navigate_website**
Navigate to websites and extract content
```
Hey Claude, use navigate_website to check the latest news on TechCrunch and extract the main headlines
```

### 2. **generate_blockchain_proof**
Generate NMKR Proof-of-Execution NFTs for tasks
```
Claude, use generate_blockchain_proof to create a verification NFT for analyzing the Apple website homepage
```

### 3. **compile_data_from_sources**
Collect and combine data from multiple websites
```
Please use compile_data_from_sources to gather information from these 3 competitor websites and create a comparison
```

### 4. **extract_text_content**
Intelligent text extraction from web pages
```
Use extract_text_content to get the full article content from this research paper URL
```

### 5. **validate_website_data**
Validate website structure and accessibility
```
Run validate_website_data on our company website to check for accessibility issues
```

### 6. **get_agent_info**
Get information about all available agents
```
Show me what Agent Forge agents are available and their capabilities
```

## Example Usage Scenarios

### Web Research and Analysis
```
"Claude, I need to research the top 5 AI companies. Use navigate_website to visit their websites, extract key information about their products and services, then compile a summary report."
```

### Competitive Intelligence
```
"Please use Agent Forge tools to monitor our top 3 competitors' pricing pages and create a comparison table."
```

### Content Analysis with Blockchain Verification
```
"Analyze this article for bias and misinformation, then use generate_blockchain_proof to create a verifiable record of your analysis."
```

### Website Quality Assurance
```
"Run a comprehensive audit of our website using validate_website_data and extract_text_content to check for content quality and accessibility issues."
```

## Troubleshooting

### Common Issues

#### 1. "MCP server not found"
- Check that the file paths in `claude_desktop_config.json` are correct
- Ensure Python and dependencies are installed
- Verify the Agent Forge directory structure

#### 2. "Permission denied"
- Make sure the Python executable has proper permissions
- Check file permissions on the MCP server script

#### 3. "Import errors"
- Verify that Agent Forge is properly installed
- Check that all dependencies from `mcp_requirements.txt` are installed
- Ensure PYTHONPATH is set correctly in the configuration

#### 4. "Agent execution fails"
- Check the Claude Desktop logs for detailed error messages
- Test agents individually using the CLI: `python cli.py run simple_navigation --url https://example.com`
- Verify Steel Browser integration is working

### Debug Mode

To enable debug logging, modify your configuration:

```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "python",
      "args": ["/full/path/to/agent_forge/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/agent_forge",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Testing Individual Components

```bash
# Test Agent Forge CLI
python cli.py list

# Test a specific agent
python cli.py run simple_navigation --url https://httpbin.org/html

# Test MCP server directly
python -c "
import asyncio
from mcp_server import navigate_website
result = asyncio.run(navigate_website('https://httpbin.org/html'))
print(result)
"
```

## Advanced Configuration

### Environment Variables

You can set environment variables for enhanced functionality:

```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "python",
      "args": ["/full/path/to/agent_forge/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/agent_forge",
        "NMKR_API_KEY": "your-nmkr-api-key",
        "MASUMI_NETWORK_KEY": "your-masumi-key",
        "STEEL_BROWSER_API_KEY": "your-steel-browser-key",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Custom Agent Configuration

To add custom configuration for specific agents:

```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "python",
      "args": ["/full/path/to/agent_forge/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/agent_forge",
        "AGENT_CONFIG": "/path/to/custom/agent_config.json"
      }
    }
  }
}
```

## Security Considerations

### Blockchain Operations
- Store sensitive API keys in environment variables, not in the configuration file
- Use secure key management for NMKR and Masumi Network credentials
- Monitor blockchain operations for unexpected transactions

### Web Automation
- Be mindful of rate limiting when accessing external websites
- Respect robots.txt and website terms of service
- Use appropriate delays between requests

### Data Privacy
- Be cautious when processing sensitive data through web agents
- Ensure compliance with data protection regulations
- Consider local processing for sensitive information

## Getting Help

- **Agent Forge Documentation**: See the `docs/` directory
- **MCP Protocol Documentation**: https://modelcontextprotocol.io/
- **Claude Desktop Support**: https://support.anthropic.com/
- **GitHub Issues**: Report bugs and request features

## Next Steps

1. Try the example commands above
2. Explore creating custom agents using Agent Forge
3. Set up blockchain integration for proof-of-execution
4. Configure monitoring and logging for production use
5. Join the Agent Forge community for tips and best practices