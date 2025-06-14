# 🛠️ Agent Forge MCP Tools Reference

**Complete reference for all Agent Forge tools available in Claude Desktop and MCP clients**

This comprehensive reference documents every tool available through Agent Forge's MCP integration. Use this guide to understand tool capabilities, parameters, return values, and usage examples.

## 📋 Table of Contents

- [Core Tools](#core-tools) (6 essential tools)
- [Auto-Discovered Agent Tools](#auto-discovered-agent-tools) (8+ specialized agents)
- [Diagnostic Tools](#diagnostic-tools) (3 system tools)
- [Usage Patterns](#usage-patterns)
- [Error Handling](#error-handling)

## 🔧 Core Tools

These 6 core tools are always available and provide essential Agent Forge functionality:

### **navigate_website**

**Purpose**: Web automation with Steel Browser integration for dynamic page interaction.

#### Parameters
```python
url: str           # Target website URL (required)
instructions: str  # Natural language navigation instructions (required)
```

#### Returns
```python
{
    "success": bool,
    "data": {
        "page_title": str,
        "extracted_content": str,
        "screenshots": List[str],  # Base64 encoded images
        "navigation_log": List[str]
    },
    "execution_time": float,
    "agent_used": "SimpleNavigationAgent"
}
```

#### Example Usage
```
# In Claude Desktop:
"Use navigate_website to go to TechCrunch and extract the top 3 headlines from the homepage"

# Parameters automatically parsed:
url: "https://techcrunch.com"
instructions: "extract the top 3 headlines from the homepage"
```

#### Advanced Example
```
"Navigate to Amazon, search for 'iPhone 15', and extract the prices and ratings of the first 5 results"
```

---

### **generate_blockchain_proof**

**Purpose**: Generate NMKR NFT proof for task verification and audit trails.

#### Parameters
```python
task_description: str  # Description of task to prove (required)
url: str              # URL analyzed (optional)
metadata: dict        # Additional proof metadata (optional)
```

#### Returns
```python
{
    "success": bool,
    "data": {
        "nft_metadata": {
            "name": str,
            "description": str,
            "image": str,          # IPFS CID
            "attributes": List[dict]
        },
        "proof_hash": str,         # SHA-256 verification hash
        "ipfs_cid": str,          # Decentralized storage CID
        "mint_payload": dict,      # NMKR API payload
        "verification_url": str    # Blockchain verification link
    },
    "execution_time": float,
    "agent_used": "NMKRAuditorAgent"
}
```

#### Example Usage
```
# In Claude Desktop:
"Generate a blockchain proof for my comprehensive analysis of Apple's homepage accessibility and performance"

# Parameters automatically parsed:
task_description: "comprehensive analysis of Apple's homepage accessibility and performance"
url: "https://apple.com" (inferred from context)
```

#### Advanced Example
```
"Create an NFT proof for this 5-site competitive analysis, including all the data I gathered and my conclusions"
```

---

### **compile_data_from_sources**

**Purpose**: Multi-source data aggregation and intelligent compilation.

#### Parameters
```python
sources: List[str]    # List of data sources/URLs (required)
instructions: str     # Compilation instructions (required)
format: str          # Output format preference (optional)
```

#### Returns
```python
{
    "success": bool,
    "data": {
        "compiled_data": dict,     # Structured compiled results
        "source_summaries": List[dict],  # Per-source analysis
        "data_quality_score": float,     # 0.0-1.0 quality rating
        "compilation_notes": str,        # AI analysis notes
        "total_sources_processed": int
    },
    "execution_time": float,
    "agent_used": "DataCompilerAgent"
}
```

#### Example Usage
```
# In Claude Desktop:
"Use compile_data_from_sources to gather pricing information from these 3 competitor websites and create a comparison table"

# With sources list:
sources: ["https://competitor1.com/pricing", "https://competitor2.com/pricing", "https://competitor3.com/pricing"]
instructions: "gather pricing information and create a comparison table"
```

#### Advanced Example
```
"Compile data from 5 tech news sites about the latest AI developments, focusing on business applications and market trends"
```

---

### **extract_text_content**

**Purpose**: Intelligent content extraction with cleaning and formatting.

#### Parameters
```python
url: str             # Source URL (required)
content_type: str    # Type of content to extract (optional)
format: str          # Output format (optional: "markdown", "plain", "structured")
```

#### Returns
```python
{
    "success": bool,
    "data": {
        "extracted_content": str,     # Main content
        "title": str,                 # Page/article title
        "author": str,                # Content author (if available)
        "publish_date": str,          # Publication date (if available)
        "word_count": int,            # Content word count
        "reading_time": int,          # Estimated reading time (minutes)
        "content_quality": float,     # 0.0-1.0 quality score
        "extraction_method": str      # Method used for extraction
    },
    "execution_time": float,
    "agent_used": "EnhancedTextExtractionAgent"
}
```

#### Example Usage
```
# In Claude Desktop:
"Use extract_text_content to get the full article text from this research paper URL and format it as clean markdown"

# Parameters:
url: "https://arxiv.org/abs/2024.12345"
content_type: "research paper"
format: "markdown"
```

#### Advanced Example
```
"Extract the main content from this blog post and summarize the key points in bullet format"
```

---

### **validate_website_data**

**Purpose**: Comprehensive website validation and accessibility checking.

#### Parameters
```python
url: str                # Website to validate (required)
validation_type: str    # Type of validation (optional: "accessibility", "seo", "performance", "all")
standards: List[str]    # Validation standards to check (optional)
```

#### Returns
```python
{
    "success": bool,
    "data": {
        "validation_results": {
            "accessibility": {
                "score": float,           # 0.0-1.0
                "issues": List[dict],     # Detailed issues
                "compliant": bool
            },
            "seo": {
                "score": float,
                "recommendations": List[str],
                "critical_issues": List[str]
            },
            "performance": {
                "load_time": float,
                "optimization_score": float,
                "recommendations": List[str]
            }
        },
        "overall_score": float,           # Combined score
        "priority_fixes": List[str],      # Most important issues
        "validation_timestamp": str
    },
    "execution_time": float,
    "agent_used": "EnhancedValidationAgent"
}
```

#### Example Usage
```
# In Claude Desktop:
"Use validate_website_data to check our company website for accessibility issues and provide improvement recommendations"

# Parameters:
url: "https://ourcompany.com"
validation_type: "accessibility"
```

#### Advanced Example
```
"Run a complete validation of this e-commerce site including SEO, accessibility, and performance metrics"
```

---

### **get_agent_info**

**Purpose**: Agent capabilities overview and system status information.

#### Parameters
```python
# No parameters required
```

#### Returns
```python
{
    "success": bool,
    "data": {
        "agent_forge_version": str,
        "available_agents": List[dict],   # All available agents with descriptions
        "core_tools": List[dict],         # Core MCP tools
        "auto_discovered_tools": List[dict],  # Auto-discovered agent tools
        "system_status": {
            "steel_browser_available": bool,
            "nmkr_integration_ready": bool,
            "mcp_server_version": str
        },
        "capabilities_summary": str,
        "setup_status": dict
    },
    "execution_time": float
}
```

#### Example Usage
```
# In Claude Desktop:
"Use get_agent_info to show me all available Agent Forge capabilities and their current status"
```

## 🤖 Auto-Discovered Agent Tools

These tools are automatically generated from Agent Forge agents using the auto-discovery system:

### **data_compiler**

**Purpose**: Advanced data compilation and analysis with AI enhancement.

#### Capabilities
- Multi-source data aggregation
- Intelligent data normalization
- Quality scoring and validation
- Structured output generation

#### Example Usage
```
"Use the data_compiler agent to analyze these 5 market research reports and identify common trends"
```

---

### **external_site_scraper**

**Purpose**: Comprehensive website scraping with anti-detection.

#### Capabilities
- Large-scale content extraction
- Dynamic content handling
- Rate limiting and politeness
- Robust error recovery

#### Example Usage
```
"Use external_site_scraper to gather all product information from this e-commerce category page"
```

---

### **simple_navigation**

**Purpose**: Basic web navigation and quick data extraction.

#### Capabilities
- Fast page analysis
- Clean content extraction
- Basic interaction handling
- Optimized for speed

#### Example Usage
```
"Use simple_navigation to quickly check the homepage of these 10 companies and extract their main value propositions"
```

---

### **crew_ai**

**Purpose**: Multi-agent coordination and complex task orchestration.

#### Capabilities
- Agent team coordination
- Complex workflow management
- Task delegation and synthesis
- Collaborative problem solving

#### Example Usage
```
"Use crew_ai to coordinate a comprehensive competitor analysis involving multiple data sources and validation steps"
```

---

### **masumi_navigation**

**Purpose**: Blockchain-enabled navigation with Web3 integration.

#### Capabilities
- Web3 site navigation
- Blockchain data extraction
- DeFi protocol analysis  
- Crypto asset information gathering

#### Example Usage
```
"Use masumi_navigation to analyze this DeFi protocol's documentation and extract key tokenomics information"
```

---

### **nmkrauditor**

**Purpose**: NMKR blockchain auditing and Cardano NFT analysis.

#### Capabilities
- NFT metadata validation
- Cardano blockchain analysis
- NMKR project auditing
- Proof-of-execution generation

#### Example Usage
```
"Use nmkrauditor to validate this NFT collection's metadata and generate a comprehensive audit report"
```

---

### **page_scraper**

**Purpose**: Targeted page content extraction with formatting preservation.

#### Capabilities
- Clean content extraction
- Format preservation
- Selective content targeting
- Quality optimization

#### Example Usage
```
"Use page_scraper to extract the main article content from this news page while preserving the formatting"
```

---

### **enhanced_validation**

**Purpose**: Advanced data validation with multi-layer quality checking.

#### Capabilities
- Multi-criteria validation
- Quality scoring algorithms
- Completeness assessment
- Reliability verification

#### Example Usage
```
"Use enhanced_validation to assess the quality and reliability of the data I collected from these sources"
```

## 🔍 Diagnostic Tools

Available in `mcp_server_enhanced.py` for system monitoring and debugging:

### **get_agent_forge_status**

**Purpose**: System health and agent availability diagnostics.

#### Returns
```python
{
    "success": bool,
    "data": {
        "total_agents_discovered": int,
        "agents_list": List[str],
        "system_health": {
            "memory_usage": str,
            "cpu_usage": str,
            "disk_space": str
        },
        "configuration_status": dict,
        "last_discovery_time": str
    }
}
```

---

### **execute_agent_by_name**

**Purpose**: Direct agent execution by name for testing.

#### Parameters
```python
agent_name: str       # Name of agent to execute
url: str             # Target URL
instructions: str    # Task instructions
```

---

### **test_agent_forge_installation**

**Purpose**: Comprehensive installation and dependency validation.

#### Returns
```python
{
    "success": bool,
    "data": {
        "installation_status": "complete" | "partial" | "failed",
        "missing_dependencies": List[str],
        "configuration_issues": List[str],
        "recommendations": List[str]
    }
}
```

## 📝 Usage Patterns

### **Sequential Tool Usage**
```
1. "Use get_agent_info to show available capabilities"
2. "Use navigate_website to analyze the homepage" 
3. "Use validate_website_data to check for issues"
4. "Use generate_blockchain_proof to verify this analysis"
```

### **Comparative Analysis**
```
"Use compile_data_from_sources to gather data from these 5 competitor sites, then use enhanced_validation to assess data quality, and finally use generate_blockchain_proof to create a verifiable record of this competitive intelligence"
```

### **Content Workflow**
```
"Use extract_text_content to get the article text, then use the enhanced_validation agent to assess credibility, and use data_compiler to create a structured summary"
```

### **Website Audit Workflow**
```
"Use navigate_website to explore the site navigation, then validate_website_data for technical issues, then external_site_scraper to gather all content, and finally generate_blockchain_proof for the complete audit trail"
```

## ⚠️ Error Handling

### **Common Error Types**

#### **Tool Execution Errors**
```python
{
    "success": false,
    "error": {
        "type": "ToolExecutionError",
        "message": "Agent failed to process URL",
        "details": {
            "agent_name": "SimpleNavigationAgent",
            "error_code": "NAVIGATION_FAILED",
            "retry_suggested": true
        }
    }
}
```

#### **Parameter Validation Errors**
```python
{
    "success": false,
    "error": {
        "type": "ParameterValidationError", 
        "message": "Invalid URL format",
        "details": {
            "parameter": "url",
            "provided_value": "not-a-url",
            "expected_format": "Valid HTTP/HTTPS URL"
        }
    }
}
```

#### **Resource Limit Errors**
```python
{
    "success": false,
    "error": {
        "type": "ResourceLimitError",
        "message": "Rate limit exceeded for Steel Browser",
        "details": {
            "service": "Steel Browser",
            "retry_after": 60,
            "suggestion": "Wait before retrying"
        }
    }
}
```

### **Error Recovery Patterns**

1. **Automatic Retry**: Most tools will retry failed operations once
2. **Graceful Degradation**: Tools fall back to simpler methods when advanced methods fail
3. **Detailed Error Logging**: All errors include actionable troubleshooting information
4. **Resource Cleanup**: Failed operations properly clean up resources

## 🎯 Best Practices

### **Tool Selection**
- Use `navigate_website` for dynamic page interaction
- Use `extract_text_content` for static content extraction
- Use `compile_data_from_sources` for multi-source analysis
- Use `generate_blockchain_proof` for verification and audit trails

### **Parameter Optimization**
- Provide clear, specific instructions for better results
- Include context about the type of content or data expected
- Specify output format preferences when available

### **Performance Tips**
- Use `simple_navigation` for quick analysis tasks
- Use `external_site_scraper` for comprehensive data gathering
- Combine tools in logical sequences for complex workflows
- Use diagnostic tools to troubleshoot issues

### **Error Prevention**
- Validate URLs before using navigation tools
- Provide clear task descriptions for blockchain proof generation
- Test individual agents before complex multi-tool workflows
- Monitor system status with diagnostic tools

## 📚 Additional Resources

### **Related Documentation**
- **[MCP Integration Guide](../integrations/MCP_INTEGRATION_GUIDE.md)** - Complete technical setup
- **[MCP Quick Start](../guides/MCP_QUICK_START.md)** - 5-minute setup guide
- **[Claude Desktop Setup](../CLAUDE_DESKTOP_SETUP.md)** - Detailed configuration
- **[Framework Architecture](../architecture/FRAMEWORK_ARCHITECTURE.md)** - Core concepts

### **Example Workflows**
- **[Getting Started Guide](../guides/GETTING_STARTED.md)** - Basic framework usage
- **[Agent Development Tutorial](../tutorials/AGENT_DEVELOPMENT_TUTORIAL.md)** - Building custom agents
- **[Best Practices](../BEST_PRACTICES.md)** - Production patterns

### **Troubleshooting**
- **[Troubleshooting Guide](../TROUBLESHOOTING.md)** - Common issues and solutions
- **[MCP Integration Guide - Troubleshooting](../integrations/MCP_INTEGRATION_GUIDE.md#troubleshooting)** - MCP-specific issues

---

**Ready to start using these tools?** Follow the [MCP Quick Start Guide](../guides/MCP_QUICK_START.md) to get Agent Forge running in Claude Desktop in 5 minutes!