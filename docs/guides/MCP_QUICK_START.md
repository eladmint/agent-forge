# 🚀 Agent Forge MCP Quick Start

**Get Agent Forge working in Claude Desktop in 5 minutes!**

This guide gets you from zero to running Agent Forge agents in Claude Desktop through natural language conversation. Perfect for first-time users who want to see the magic of MCP integration.

## 🎯 What You'll Accomplish

By the end of this guide, you'll be able to:
- Use Agent Forge agents directly in Claude Desktop
- Navigate websites through conversation
- Generate blockchain proofs with simple requests
- Access 8+ specialized AI agents without coding

## ⚡ 5-Minute Setup

### Step 1: Install Agent Forge (2 minutes)

```bash
# Clone the repository
git clone https://github.com/your-org/agent-forge.git
cd agent-forge

# Install dependencies
pip install -r requirements.txt
pip install -r mcp_requirements.txt
```

### Step 2: Test the MCP Server (1 minute)

```bash
# Test that everything works
python mcp_server.py
```

You should see output like:
```
✅ Agent Forge MCP Server started successfully
✅ Found 8 agents: data_compiler, external_site_scraper, simple_navigation...
✅ Registered 6 core tools + 8 agent tools = 14 total tools
```

### Step 3: Configure Claude Desktop (2 minutes)

#### Find your config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`  
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

#### Add this configuration:

```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "python",
      "args": ["/REPLACE/WITH/YOUR/PATH/agent-forge/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/REPLACE/WITH/YOUR/PATH/agent-forge"
      }
    }
  }
}
```

**⚠️ Important**: Replace `/REPLACE/WITH/YOUR/PATH/agent-forge` with your actual path!

### Step 4: Restart Claude Desktop

Close and reopen Claude Desktop completely.

## 🎉 Test Your Setup

Try these commands in Claude Desktop:

### 1. **See Available Tools**
```
Claude, use get_agent_info to show me all available Agent Forge capabilities
```

### 2. **Navigate a Website**  
```
Use navigate_website to visit TechCrunch and tell me the top 3 headlines
```

### 3. **Generate Blockchain Proof**
```
Use generate_blockchain_proof to create verification for analyzing the Apple homepage
```

### 4. **Extract Content**
```
Use extract_text_content to get the main article from https://example-news-site.com/article
```

If these work, **congratulations! You're ready to use Agent Forge!** 🎊

## 🛠️ Available Tools at a Glance

| **Tool** | **What it does** | **Example Usage** |
|----------|------------------|-------------------|
| `navigate_website` | Web automation with browser | "Navigate to Amazon and find iPhone prices" |
| `generate_blockchain_proof` | Create NFT verification | "Generate proof for my website analysis" |  
| `compile_data_from_sources` | Multi-source data gathering | "Compile data from these 3 competitor sites" |
| `extract_text_content` | Clean content extraction | "Extract article text from this URL" |
| `validate_website_data` | Website quality checking | "Check our site for accessibility issues" |
| `get_agent_info` | Show available capabilities | "What Agent Forge tools are available?" |

**Plus 8 auto-discovered agents** for specialized tasks like blockchain auditing, multi-agent coordination, and advanced validation.

## 🎯 Real-World Examples

### **Market Research**
```
Claude, use the data_compiler agent to gather information from these 3 competitor websites: 
- https://competitor1.com
- https://competitor2.com  
- https://competitor3.com

Create a comparison table showing their pricing, features, and key messaging.
```

### **Content Analysis**
```
Use extract_text_content to get the full article from this research paper URL, then use the enhanced_validation agent to assess the quality and credibility of the claims made.
```

### **Website Audit**
```
Use validate_website_data to check our company website for accessibility issues and SEO problems, then use the external_site_scraper to see how our competitors handle the same issues.
```

### **Blockchain Verification**
```
I just completed a comprehensive analysis of 5 DeFi protocols. Use generate_blockchain_proof to create a verifiable NFT record of this analysis for my portfolio.
```

## 🆘 Quick Troubleshooting

### "Agent Forge tools not showing up"
1. Check your Claude Desktop config file path is correct
2. Verify you replaced the placeholder paths with your actual paths
3. Restart Claude Desktop completely
4. Test: `python mcp_server.py` should run without errors

### "Permission denied" errors
```bash
# Make sure the MCP server is executable
chmod +x mcp_server.py

# Check Python path
which python
```

### "Import errors"
```bash
# Reinstall dependencies
pip install -r mcp_requirements.txt

# Test imports
python -c "from core.agents.base_agent import AsyncContextAgent"
```

### "Agent execution fails"
```bash
# Test agents individually
python cli.py run simple_navigation --url https://example.com
```

## 🚀 Next Steps

### **Beginner Path**
1. ✅ **You're here!** Quick start complete
2. 📖 **[Read the Getting Started Guide](GETTING_STARTED.md)** - Learn framework basics
3. 🎓 **[Try Agent Development Tutorial](../tutorials/AGENT_DEVELOPMENT_TUTORIAL.md)** - Build your first agent

### **Advanced Path**  
1. 🔧 **[MCP Integration Guide](../integrations/MCP_INTEGRATION_GUIDE.md)** - Deep technical dive
2. 🏗️ **[Framework Architecture](../architecture/FRAMEWORK_ARCHITECTURE.md)** - Understand the system
3. 🛠️ **[MCP Tools Reference](../api/MCP_TOOLS_REFERENCE.md)** - Complete tool documentation

### **Production Path**
1. ⛓️ **[NMKR Blockchain Integration](../integrations/NMKR_PROOF_OF_EXECUTION_GUIDE.md)** - Add blockchain verification
2. 🌐 **[Steel Browser Setup](../integrations/STEEL_BROWSER_INTEGRATION.md)** - Advanced web automation
3. 📋 **[Best Practices](../BEST_PRACTICES.md)** - Production deployment patterns

## 💡 Pro Tips

### **Conversational Commands**
You don't need to remember exact tool names. These all work:
- "Navigate to that website and extract the main content"
- "Check this site for problems"  
- "Create a blockchain proof of this analysis"
- "What tools do you have available from Agent Forge?"

### **Combining Tools**
Agent Forge tools work great together:
```
Use navigate_website to check the homepage of Tesla.com, then use validate_website_data to audit it for accessibility issues, and finally use generate_blockchain_proof to create a verification record of this comprehensive analysis.
```

### **Batch Operations**
```
Use the external_site_scraper to gather data from these 10 URLs, then use compile_data_from_sources to analyze patterns across all of them.
```

## 🎊 Congratulations!

You now have Agent Forge running in Claude Desktop! You can:
- ✅ Control web browsers through conversation
- ✅ Generate blockchain proofs for verification  
- ✅ Access 8+ specialized AI agents
- ✅ Extract and analyze web content
- ✅ Validate websites for quality and accessibility

**Ready for more?** Check out the [complete MCP Integration Guide](../integrations/MCP_INTEGRATION_GUIDE.md) for advanced features and customization options.

---

**Need help?** See the [Troubleshooting Guide](../TROUBLESHOOTING.md) or review the [complete framework documentation](../README.md).