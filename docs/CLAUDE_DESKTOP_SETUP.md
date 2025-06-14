# 🎉 Agent Forge - Claude Desktop Setup

**Get Agent Forge agents working in Claude Desktop in 5 minutes!**

Agent Forge's 11+ agents including enterprise intelligence capabilities can now be used directly in Claude Desktop through natural language - no coding required. Simply set up the MCP integration and start using powerful web automation, blockchain capabilities, brand monitoring, and due diligence automation through conversation.

## ⚡ Quick Setup (5 minutes)

### 1. Install Agent Forge MCP Server

```bash
# Navigate to Agent Forge directory
cd /path/to/agent_forge

# Install MCP dependencies
pip install -r mcp_requirements.txt
```

### 2. Test the MCP Server

```bash
# Test server functionality
python mcp_server_enhanced.py
```

### 3. Configure Claude Desktop

#### For macOS:
Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

#### For Windows:
Edit: `%APPDATA%/Claude/claude_desktop_config.json`

#### For Linux:
Edit: `~/.config/Claude/claude_desktop_config.json`

### 4. Add Agent Forge Configuration

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

**Important:** Replace `/full/path/to/agent_forge` with your actual Agent Forge directory path.

### 5. Restart Claude Desktop

Close and reopen Claude Desktop to load the new configuration.

## 🚀 Available Agent Forge Tools

Once configured, you can use these tools in Claude Desktop through natural language:

### **Core Tools**
- **navigate_website** - Web automation with Steel Browser integration
- **generate_blockchain_proof** - NMKR NFT proof generation for task verification
- **compile_data_from_sources** - Multi-source data aggregation
- **extract_text_content** - Intelligent content extraction
- **validate_website_data** - Website validation and accessibility checking
- **get_agent_info** - Agent capabilities overview

### **Enterprise Intelligence Tools** (NEW)
- **visual_intelligence** - Brand monitoring and competitive intelligence through image analysis
- **research_compiler** - M&A due diligence and market research automation

### **Auto-Discovered Agents** (10+ agents)
- **data_compiler** - Advanced data compilation and analysis
- **external_site_scraper** - Comprehensive website scraping
- **simple_navigation** - Basic web navigation and extraction
- **crew_ai** - Multi-agent coordination
- **masumi_navigation** - Blockchain-enabled navigation
- **nmkrauditor** - NMKR blockchain auditing
- **page_scraper** - Targeted page content extraction
- **enhanced_validation** - Advanced data validation

## 💬 Example Usage

### Web Research
```
Claude, use navigate_website to check the latest news on TechCrunch and extract the main headlines
```

### Blockchain Verification
```
Claude, use generate_blockchain_proof to create a verification NFT for analyzing the Apple website homepage
```

### Data Compilation
```
Please use compile_data_from_sources to gather information from these 3 competitor websites and create a comparison
```

### Content Analysis
```
Use extract_text_content to get the full article content from this research paper URL
```

### Enterprise Intelligence (NEW)
```
Claude, use visual_intelligence to analyze these conference photos and identify all competitor logos and their sponsorship tiers
```

```
Please use research_compiler to compile a due diligence report for TechCorp acquisition from these data sources
```

### Brand Monitoring
```
Use visual_intelligence to monitor our competitor's presence at this tech conference and analyze their brand positioning
```

### Market Research
```
Claude, use research_compiler to create a competitive analysis report comparing our pricing strategy with these 5 competitors
```

### Website Validation
```
Run validate_website_data on our company website to check for accessibility issues
```

## 🔧 Troubleshooting

### Common Issues

#### "MCP server not found"
- Check file paths in configuration are correct
- Ensure Python and dependencies are installed
- Verify Agent Forge directory structure

#### "Permission denied"
- Check Python executable permissions
- Verify file permissions on MCP server script

#### "Import errors"
- Ensure all dependencies from `mcp_requirements.txt` are installed
- Check PYTHONPATH is set correctly in configuration
- Verify Agent Forge is properly installed

#### "Agent execution fails"
- Check Claude Desktop logs for detailed errors
- Test agents individually: `python cli.py run simple_navigation --url https://example.com`
- Verify Steel Browser integration is working

## 🔍 Advanced Configuration

### With Virtual Environment
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

### With Environment Variables
```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "python",
      "args": ["/full/path/to/agent_forge/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/agent_forge",
        "NMKR_API_KEY": "your-nmkr-api-key",
        "STEEL_BROWSER_API_KEY": "your-steel-browser-key",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Debug Mode
```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "python",
      "args": ["/full/path/to/agent_forge/mcp_server_enhanced.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/agent_forge",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## 🎯 Next Steps

1. **Try the example commands** above to test your setup
2. **Explore the [MCP Tools Reference](api/MCP_TOOLS_REFERENCE.md)** for complete tool documentation
3. **Read the [MCP Integration Guide](integrations/MCP_INTEGRATION_GUIDE.md)** for advanced usage
4. **Set up blockchain integration** with [NMKR Proof-of-Execution Guide](integrations/NMKR_PROOF_OF_EXECUTION_GUIDE.md)
5. **Join the Agent Forge community** for tips and best practices

## 📚 Additional Resources

- **[Complete MCP Integration Guide](integrations/MCP_INTEGRATION_GUIDE.md)** - Detailed technical setup
- **[MCP Tools Reference](api/MCP_TOOLS_REFERENCE.md)** - Complete tool documentation
- **[Framework Documentation](README.md)** - Full Agent Forge documentation
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions

---

**Need Help?** Check our [Troubleshooting Guide](TROUBLESHOOTING.md) or refer to the complete [MCP Integration Guide](integrations/MCP_INTEGRATION_GUIDE.md) for detailed technical documentation.