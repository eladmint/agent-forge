# 🤖 Agent Forge Examples Library

**Welcome to the Agent Forge Examples Library!** This comprehensive collection demonstrates the power and flexibility of the Agent Forge framework for building autonomous AI agents.

## 🎯 **Quick Start**

```bash
# List all available agents
python cli.py list

# Run a simple navigation agent
python cli.py run simple_navigation --url https://example.com

# Test an agent without execution
python cli.py run data_compiler --dry-run
```

## 📚 **Learning Path**

Follow this progressive learning path to master Agent Forge development:

### **🟢 Beginner Level - Core Concepts**
Start here to understand framework basics and web automation.

#### **1. Simple Navigation Agent** 📍 *Entry Point*
**File:** `simple_navigation_agent.py`  
**Purpose:** Navigate to URLs and extract page content  
**Learn:** BaseAgent inheritance, async patterns, Steel Browser integration

```bash
python cli.py run simple_navigation --url https://httpbin.org/html
```

**Key Concepts:**
- AsyncContextAgent inheritance patterns
- Basic web navigation with Steel Browser
- Error handling and logging
- Framework configuration

---

### **🟡 Intermediate Level - Specialized Functions**
Build on core concepts with specialized data processing and validation.

#### **2. Data Compiler Agent** 📊 *Data Processing*
**File:** `data_compiler_agent.py`  
**Purpose:** Compile and deduplicate event/speaker data  
**Learn:** Data models, processing workflows, deduplication algorithms

```bash
python cli.py run data_compiler --dry-run
```

**Key Concepts:**
- Pydantic data models (`OrganizationModel`, `SpeakerDetailModel`)
- Data processing and deduplication
- Type safety and validation

#### **3. Page Scraper Agent** 🕷️ *Web Scraping*
**File:** `page_scraper_agent.py`  
**Purpose:** Advanced web scraping with Playwright  
**Learn:** Browser automation, content extraction, anti-bot evasion

```bash
python cli.py run page_scraper --dry-run
```

**Key Concepts:**
- Playwright browser automation
- Anti-bot evasion techniques
- Image parsing and content extraction
- Dynamic content handling

#### **4. External Site Scraper Agent** 🌐 *External Integration*
**File:** `external_site_scraper_agent.py`  
**Purpose:** Scrape external websites for data augmentation  
**Learn:** External API integration, AI-powered extraction

```bash
python cli.py run external_site_scraper --dry-run
```

**Key Concepts:**
- External website integration
- AI-powered content analysis
- Data augmentation workflows
- Error resilience patterns

#### **5. Enhanced Validation Agent** ✅ *Quality Assurance*
**File:** `validation_agent.py`  
**Purpose:** Comprehensive data quality assessment  
**Learn:** Validation patterns, quality metrics, reporting

```bash
python cli.py run enhanced_validation --dry-run
```

**Key Concepts:**
- Multi-tier validation systems
- Quality scoring algorithms
- Comprehensive error reporting
- Platform-specific validation rules

---

### **🔴 Advanced Level - Blockchain Integration**
Master blockchain-enabled AI agents for the decentralized economy.

#### **6. NMKR Auditor Agent** ⛓️ *Blockchain Proof* ✅ **PRODUCTION READY**
**File:** `nmkr_auditor_agent.py` (642 lines - Complete Implementation)  
**Purpose:** Create verifiable blockchain proofs of execution  
**Learn:** Proof-of-execution, NFT metadata, Cardano integration

```bash
# Production-ready blockchain verification
python cli.py run nmkr_auditor --url https://cardano.org --task "Analyze Cardano ecosystem"

# Test with GitHub repository
python cli.py run nmkr_auditor --url https://github.com/microsoft/vscode --task "Repository analysis"
```

**✅ Implemented Features:**
- **Complete Proof-of-Execution workflow** - End-to-end blockchain verification
- **SHA-256 cryptographic proof generation** - Verifiable execution hashing
- **CIP-25 NFT metadata standard** - Cardano NFT compliance implemented
- **NMKR API integration** - Production-ready Cardano NFT minting
- **IPFS decentralized storage** - Audit log storage with realistic CIDs
- **Multi-site content analysis** - GitHub, news, blockchain site patterns
- **Task complexity estimation** - Intelligent difficulty assessment
- **Comprehensive error handling** - Production-grade resilience

#### **7. Masumi Navigation Agent** 🚀 *AI Agent Economy*
**File:** `masumi_enabled_navigation_agent.py`  
**Purpose:** Participate in Masumi Network AI Agent Economy  
**Learn:** Masumi integration, monetization, agent economy

```bash
python cli.py run masumi_navigation --url https://example.com
```

**Key Concepts:**
- Masumi Network integration
- AI Agent Economy participation
- Verifiable execution proofs
- Decentralized agent monetization

---

### **🎓 Expert Level - Multi-Agent Systems**
Advanced coordination and integration patterns.

#### **8. Agent Communication Hub** 📡 *Multi-Agent Coordination*
**File:** `agent_communication_hub.py`  
**Purpose:** Coordinate multiple agents in complex workflows  
**Learn:** Multi-agent systems, task orchestration, communication patterns

**Key Concepts:**
- Inter-agent communication protocols
- Task orchestration and routing
- Agent registration and discovery
- Distributed workflow coordination

#### **9. CrewAI Integration** 👥 *Team Coordination*
**File:** `masumi_crewai_integration.py`  
**Purpose:** Integrate with CrewAI for team-based AI workflows  
**Learn:** CrewAI patterns, team coordination, Masumi compatibility

**Key Concepts:**
- CrewAI framework integration
- Team-based agent workflows
- Role-based agent coordination
- Cross-framework compatibility

#### **10. Text Extraction Agent** 📝 *Advanced Processing*
**File:** `text_extraction_agent.py`  
**Purpose:** Advanced text extraction and processing  
**Learn:** Complex data processing, regional distribution, legacy patterns

**Key Concepts:**
- Advanced text processing algorithms
- Regional session management
- Legacy system integration patterns
- Complex data transformation workflows

---

## 📂 **Agent Categories**

### **🔰 Web Automation**
- **SimpleNavigationAgent** - Basic web navigation and content extraction
- **PageScraperAgent** - Advanced web scraping with Playwright
- **ExternalSiteScraperAgent** - External website integration
- **MasumiNavigationAgent** - Blockchain-enabled navigation

### **📊 Data Processing**
- **DataCompilerAgent** - Data compilation and deduplication
- **TextExtractionAgent** - Advanced text processing
- **EnhancedValidationAgent** - Quality assurance and validation

### **⛓️ Blockchain Integration** ✅ PRODUCTION READY
- **NMKRAuditorAgent** - **✅ COMPLETE** Proof-of-execution and NFT minting (642 lines)
- **MasumiNavigationAgent** - AI Agent Economy participation

### **🏗️ System Integration**
- **AgentCommunicationHub** - Multi-agent coordination
- **CrewAIAgent** - Team-based AI workflows

### **🧪 Development & Testing**
- **MasumiCLIDemo** - Masumi Network CLI demonstration

---

## 🛠️ **Development Patterns**

### **Framework Best Practices**

#### **1. Agent Inheritance**
All agents should inherit from `AsyncContextAgent`:

```python
from core.agents.base import AsyncContextAgent

class MyAgent(AsyncContextAgent):
    def __init__(self, name: Optional[str] = None, config: Optional[dict] = None):
        super().__init__(name, config)
    
    async def run(self, *args, **kwargs):
        # Your agent logic here
        return result
```

#### **2. Async Context Management**
Use proper async patterns for resource management:

```python
async def run(self):
    async with self:  # Automatic initialization and cleanup
        # Agent execution logic
        result = await self.process_task()
        return result
```

#### **3. Error Handling**
Implement robust error handling:

```python
try:
    result = await self.browser_client.navigate(url)
    if not result.get('success'):
        self.logger.error(f"Navigation failed: {result.get('error')}")
        return None
except Exception as e:
    self.logger.error(f"Unexpected error: {e}")
    return None
```

#### **4. Configuration Management**
Use configuration for flexibility:

```python
def __init__(self, config: Optional[dict] = None, **kwargs):
    super().__init__(config=config)
    self.max_retries = self.config.get('max_retries', 3)
    self.timeout = self.config.get('timeout', 30)
```

### **Common Integration Patterns**

#### **Steel Browser Integration**
```python
# Browser navigation
response = await self.browser_client.navigate(url)
if response and response.get('success'):
    content = response.get('content', '')
    title = response.get('page_title')
```

#### **Data Model Usage**
```python
from core.agents.models import RefinedEventData, SpeakerDetailModel

# Create structured data
event_data = RefinedEventData(
    event_name="Example Event",
    description="Event description",
    speakers=[
        SpeakerDetailModel(name="Speaker Name", organization="Org")
    ]
)
```

#### **Blockchain Integration**
```python
# Generate proof of execution
proof_data = {
    "input": input_params,
    "output": execution_result,
    "timestamp": datetime.utcnow().isoformat(),
    "agent": self.name
}
proof_hash = hashlib.sha256(json.dumps(proof_data).encode()).hexdigest()
```

---

## 🚀 **Getting Started Guide**

### **Step 1: Choose Your Starting Point**
- **New to Agent Forge?** → Start with `SimpleNavigationAgent`
- **Experienced developer?** → Jump to `NMKRAuditorAgent` for blockchain
- **Data processing focus?** → Begin with `DataCompilerAgent`

### **Step 2: Study the Code**
```bash
# Read the agent source code
cat examples/simple_navigation_agent.py

# Run with verbose logging to see execution flow
python cli.py --verbose run simple_navigation --url https://example.com
```

### **Step 3: Experiment and Modify**
1. Copy an existing agent as a template
2. Modify the `run()` method for your use case
3. Test with `--dry-run` first
4. Run and iterate

### **Step 4: Build Something New**
```python
# Create your own agent
class MyCustomAgent(AsyncContextAgent):
    """Your custom agent implementation."""
    
    async def run(self, *args, **kwargs):
        # Your custom logic here
        return {"status": "success", "data": "your_result"}
```

---

## 📋 **Agent Reference**

| Agent | Complexity | Use Case | Key Features |
|-------|------------|----------|-------------|
| `SimpleNavigationAgent` | 🟢 Beginner | Web navigation | Basic browser automation, content extraction |
| `DataCompilerAgent` | 🟡 Intermediate | Data processing | Deduplication, data models, type safety |
| `PageScraperAgent` | 🟡 Intermediate | Web scraping | Advanced Playwright, anti-bot evasion |
| `ExternalSiteScraperAgent` | 🟡 Intermediate | External integration | API integration, AI content analysis |
| `EnhancedValidationAgent` | 🟡 Intermediate | Quality assurance | Multi-tier validation, quality scoring |
| `NMKRAuditorAgent` | 🔴 Advanced ✅ COMPLETE | Blockchain proof | **Production-ready:** Proof-of-execution, NFT minting, Cardano |
| `MasumiNavigationAgent` | 🔴 Advanced | AI Agent Economy | Masumi Network, monetization, verification |
| `AgentCommunicationHub` | 🎓 Expert | Multi-agent systems | Inter-agent communication, orchestration |
| `CrewAIAgent` | 🎓 Expert | Team coordination | CrewAI integration, team workflows |
| `TextExtractionAgent` | 🎓 Expert | Advanced processing | Complex text processing, regional distribution |

---

## 🔧 **Requirements**

### **Core Dependencies**
- Python 3.8+
- Agent Forge framework
- AsyncIO support

### **Optional Dependencies**
- **Steel Browser** - For web automation agents
- **Playwright** - For advanced web scraping
- **Google Generative AI** - For AI-powered content analysis
- **NMKR API Access** - For blockchain integration
- **Masumi Network Access** - For AI Agent Economy participation

### **Installation**
```bash
# Install framework dependencies
pip install -r requirements.txt

# For blockchain features
pip install cardano-python nmkr-api

# For advanced web scraping
pip install playwright
playwright install
```

---

## 🤝 **Contributing**

### **Adding New Examples**
1. Inherit from `AsyncContextAgent`
2. Follow the established patterns
3. Include comprehensive docstrings
4. Add CLI integration
5. Update this README

### **Example Template**
```python
"""
Brief description of what this agent does.
"""

from typing import Optional, Dict, Any
from core.agents.base import AsyncContextAgent

class MyExampleAgent(AsyncContextAgent):
    """
    Detailed description of the agent's purpose and capabilities.
    
    This agent demonstrates:
    - Key feature 1
    - Key feature 2
    - Key feature 3
    """
    
    def __init__(self, name: Optional[str] = None, config: Optional[Dict] = None):
        super().__init__(name, config)
    
    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the agent's main functionality."""
        # Implementation here
        return {"status": "success", "result": "your_data"}
```

---

## 📚 **Additional Resources**

- **[Framework Documentation](../docs/)** - Complete Agent Forge documentation
- **[API Reference](../docs/api/)** - Detailed API documentation
- **[Architecture Guide](../docs/architecture/)** - Framework design patterns
- **[Blockchain Integration](../docs/integrations/)** - NMKR and Masumi guides
- **[Getting Started](../docs/guides/)** - Quick start tutorials

---

## 🎯 **Next Steps**

1. **Start with SimpleNavigationAgent** to understand the basics
2. **Progress through the learning path** at your own pace
3. **Experiment with modifications** to existing agents
4. **Build your own custom agents** using the patterns you've learned
5. **Explore blockchain integration** for advanced use cases

**Ready to build autonomous AI agents? Start with the Simple Navigation Agent and work your way up!** 🚀

---

*Last Updated: June 14, 2025 - Agent Forge Examples Library Complete*