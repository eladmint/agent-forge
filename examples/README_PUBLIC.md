# 🚀 Agent Forge Community Examples

**Open source examples demonstrating core Agent Forge capabilities**

## 🟢 **Community Tier Agents**

These agents are part of the Agent Forge open source community tier, providing complete functionality to learn and build with the framework.

### 📍 **Simple Navigation Agent**
**Perfect entry point for learning Agent Forge basics**
```bash
python cli.py run simple_navigation --url https://example.com
```
**Features:**
- Basic web navigation and page interaction
- Error handling and resilience patterns
- Foundation for building more complex agents
- Complete BaseAgent implementation example

### 📝 **Text Extraction Agent**
**Fundamental text processing and extraction**
```bash
python cli.py run text_extraction --url https://example.com
```
**Features:**
- Advanced text extraction and processing
- Content cleaning and normalization
- Multi-format text handling
- Production-ready extraction patterns

### 🕷️ **Page Scraper Agent**
**Production-ready web scraping foundation**
```bash
python cli.py run page_scraper --dry-run
```
**Features:**
- Playwright browser automation
- Anti-bot detection evasion
- Robust content extraction
- Error handling and retry logic

### ✅ **Validation Agent**
**Data quality and validation patterns**
```bash
python cli.py run validation --dry-run
```
**Features:**
- Comprehensive data validation
- Quality metrics and scoring
- Error reporting and logging
- Production validation patterns

### 📚 **Documentation Manager Agent**
**Automated documentation management**
```bash
python cli.py run documentation_manager --dry-run
```
**Features:**
- Documentation generation and updates
- Content organization and structuring
- Version control integration
- Automated documentation workflows

## 🎯 **Learning Path**

**Recommended progression for new users:**

1. **Start Here:** `simple_navigation` - Learn basic Agent Forge patterns
2. **Build Skills:** `text_extraction` - Master content processing
3. **Advanced Automation:** `page_scraper` - Complex web automation
4. **Quality Assurance:** `validation` - Production-ready validation
5. **Documentation:** `documentation_manager` - Automated workflows

## 🚀 **Getting Started**

### **Prerequisites**
```bash
# Install Agent Forge
pip install agent-forge

# Set up environment
cp .env.example .env
# Edit .env with your configuration
```

### **Quick Start**
```bash
# List available agents
python cli.py list

# Run your first agent
python cli.py run simple_navigation --url https://example.com

# Test without execution
python cli.py run page_scraper --dry-run

# Get help
python cli.py --help
```

## 🔧 **Framework Features Demonstrated**

### **Core Capabilities**
- **BaseAgent Foundation**: Async patterns and error handling
- **Browser Integration**: Steel Browser automation
- **Configuration Management**: Environment and settings
- **CLI Interface**: Command-line agent management
- **Testing Framework**: Validation and quality assurance

### **Production Patterns**
- **Error Handling**: Comprehensive error management
- **Logging**: Structured logging and debugging
- **Configuration**: Environment-based configuration
- **Testing**: Unit and integration testing
- **Documentation**: Automated documentation generation

## 📈 **Next Steps**

### **Upgrade to Professional Tier**
Access advanced agents and premium features:
- Advanced web automation workflows
- Multi-agent coordination systems
- Enhanced data processing pipelines
- Premium support and documentation

### **Enterprise Solutions**
Enterprise-grade intelligence and automation:
- Brand monitoring and competitive intelligence
- M&A due diligence and market research
- Risk assessment and compliance automation
- Custom agent development and integration

### **Learn More**
- **[Framework Documentation](../docs/README.md)** - Complete guides and references
- **[MCP Integration](../docs/CLAUDE_DESKTOP_SETUP.md)** - Use agents in Claude Desktop
- **[Getting Started Guide](../docs/guides/GETTING_STARTED.md)** - Detailed setup instructions

## 🤝 **Community & Support**

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community Q&A and examples
- **Contributing**: Guidelines for community contributions
- **Documentation**: Comprehensive guides and tutorials

---

**Agent Forge Community Edition** - Production-ready AI web automation framework  
**License**: Apache 2.0 Open Source  
**Learn More**: [Agent Forge Documentation](../docs/README.md)