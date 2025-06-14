# 🔗 Integrations

This directory contains comprehensive integration guides for external services and technologies used with the Agent Forge framework.

## 📚 **Available Integration Guides**

### **🎉 [MCP Integration Guide](MCP_INTEGRATION_GUIDE.md)** ✅ COMPLETE
**Model Context Protocol integration for Claude Desktop and MCP clients:**

- **✅ FastMCP Server Implementation** - Complete MCP server with 6 core tools + auto-discovery
- **✅ Claude Desktop Integration** - Production-ready 5-minute setup with troubleshooting
- **✅ Auto-Discovery System** - Automatically exposes 8+ Agent Forge agents as MCP tools  
- **✅ Natural Language Interface** - Use agents through conversation in Claude Desktop
- **✅ Advanced Configuration** - Virtual environments, custom env vars, debugging modes
- **✅ Development Guide** - Custom tool creation and MCP server extension
- **📋 Quick Start**: See [MCP Quick Start Guide](../guides/MCP_QUICK_START.md) for 5-minute setup

**Perfect for:** Claude Desktop users, conversational AI interfaces, rapid agent deployment

### **🌐 [Steel Browser Integration](STEEL_BROWSER_INTEGRATION.md)**
Complete web automation integration guide:

- **Overview** - Production-ready browser automation service
- **Integration Architecture** - How Steel Browser integrates with BaseAgent
- **Setup and Configuration** - Automatic and manual configuration options
- **Usage Patterns** - From basic navigation to advanced interactions
- **Advanced Features** - Screenshots, JavaScript execution, form automation
- **Error Handling** - Comprehensive error management and retry mechanisms
- **Best Practices** - Resource management, performance optimization, debugging

### **🔐 [NMKR Proof-of-Execution Guide](NMKR_PROOF_OF_EXECUTION_GUIDE.md)** ✅ IMPLEMENTED
Cardano blockchain integration for verifiable agents:

- **✅ NMKRAuditorAgent** - Complete 642-line implementation ready for production
- **✅ NMKR Studio API Integration** - Full API payload construction and minting support
- **✅ CIP-25 Metadata Standard** - Cardano NFT metadata compliance implemented
- **✅ Proof-of-Execution Workflow** - End-to-end blockchain verification system
- **✅ IPFS Integration** - Decentralized storage simulation with realistic CIDs
- **✅ Comprehensive Testing** - Multi-site analysis and validation framework
- **📋 Usage**: `python cli.py run nmkr_auditor --url URL --task "description"`

**Perfect for:** System integration, external service connectivity, blockchain development

---

## 🎯 **Integration Categories**

### **🎉 MCP & Conversational AI** ✅ PRODUCTION READY
- [MCP Integration Guide](MCP_INTEGRATION_GUIDE.md) - **Complete Claude Desktop integration**
- **✅ FastMCP server** with 6 core tools + 8 auto-discovered agents  
- **✅ Natural language interface** for non-technical users
- **✅ 5-minute setup** with comprehensive troubleshooting guides

### **🌐 Web Automation**
- [Steel Browser Integration](STEEL_BROWSER_INTEGRATION.md) - Production browser automation
- HTTP client patterns and request management
- Anti-detection and robust scraping techniques

### **⛓️ Blockchain & NFTs** ✅ IMPLEMENTED
- [NMKR Proof-of-Execution Guide](NMKR_PROOF_OF_EXECUTION_GUIDE.md) - **Complete Cardano NFT minting**
- **✅ Cryptographic proof generation** - SHA-256 verification implemented
- **✅ Decentralized storage integration** - IPFS CID simulation ready
- **✅ Production-ready agent** - [NMKRAuditorAgent](../../examples/nmkr_auditor_agent.py) available

### **🔮 Future Integrations**
The framework is designed to support additional integrations:
- Database systems (PostgreSQL, MongoDB, etc.)
- AI/ML services (OpenAI, Anthropic, etc.)
- Cloud platforms (AWS, GCP, Azure)
- Messaging systems (Telegram, Discord, Slack)

---

## 🛠️ **Integration Development**

### **Adding New Integrations**
1. **Core Utilities** - Add to `core/shared/` directory structure
2. **BaseAgent Integration** - Extend initialization and cleanup patterns
3. **Configuration** - Add configuration management patterns
4. **Documentation** - Create comprehensive integration guide
5. **Examples** - Provide working example agents

### **Integration Patterns**
- **Async/Await** - All integrations use modern async patterns
- **Error Handling** - Comprehensive error management and recovery
- **Configuration** - Flexible configuration and credential management
- **Resource Management** - Proper initialization and cleanup

---

## 📋 **Usage Guide**

### **For Web Automation**
1. Review [Steel Browser Integration](STEEL_BROWSER_INTEGRATION.md)
2. Start with basic navigation patterns
3. Progress to advanced interactions and error handling

### **For Blockchain Integration** ✅ READY TO USE
1. **Import and configure**: `from examples.nmkr_auditor_agent import NMKRAuditorAgent`
2. **Set API credentials**: Configure NMKR API key and project UID
3. **Execute with proofs**: `await agent.run(url, task_description)` - generates complete blockchain verification
4. **Deploy to production**: Full audit trails and NFT minting ready

### **For Custom Integrations**
1. Review existing integration patterns
2. Follow framework architecture guidelines
3. Implement proper async and error handling

---

**Return to:** [📚 Main Documentation](../README.md)