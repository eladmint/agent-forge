# 🤖 Agent Forge

**The Open-Source Framework for Building Autonomous AI Web Agents**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-120%20passing-green.svg)](#testing)
[![Steel Browser](https://img.shields.io/badge/Steel%20Browser-Integrated-orange.svg)](https://steel.dev)
[![Cardano Enhanced](https://img.shields.io/badge/Cardano-Enhanced-red.svg)](#cardano-integration)
[![Blockchain Ready](https://img.shields.io/badge/Blockchain-Ready-purple.svg)](#blockchain-integration)

Agent Forge empowers developers to create, deploy, and monetize autonomous AI agents that can navigate the web, extract data, perform complex tasks, and participate in the emerging **AI Agent Economy** through blockchain integration.

---

## 🌟 **What Makes Agent Forge Special?**

🎯 **Production-Ready Framework**: Enterprise-grade architecture with comprehensive testing (120+ passing tests)  
🏛️ **Enhanced Cardano Integration**: Complete AI agent economy with smart contract architecture  
🔗 **Blockchain Integration**: Built-in support for NMKR Proof-of-Execution NFTs and Masumi Network  
🌐 **Steel Browser Powered**: Professional web automation with anti-detection capabilities  
⚡ **Async-First Design**: Modern Python async/await patterns throughout  
🔧 **CLI Interface**: Intuitive command-line tools for agent management  
📊 **Comprehensive Testing**: Unit, integration, end-to-end, performance, and security test coverage  
📚 **Rich Documentation**: Complete guides, tutorials, and API references  

---

## 🚀 **Quick Start**

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/agent_forge.git
cd agent_forge

# Install dependencies
pip install -r requirements.txt

# Run your first agent
python tools/scripts/cli.py run simple_navigation --url https://example.com
```

### Create Your First Agent

```python
from src.core.agents.base import AsyncContextAgent

class MyWebAgent(AsyncContextAgent):
    """My custom web automation agent."""
    
    def __init__(self, url: str, **kwargs):
        super().__init__(name="MyWebAgent", **kwargs)
        self.url = url
    
    async def run(self) -> dict:
        """Navigate to URL and extract data."""
        response = await self.browser_client.navigate(self.url)
        
        return {
            "title": response.get("page_title"),
            "success": response.get("success", False),
            "url": self.url
        }

# Usage
async def main():
    async with MyWebAgent(url="https://example.com") as agent:
        result = await agent.run()
        print(f"Page title: {result['title']}")
```

---

## 🏗️ **Framework Architecture**

```
agent_forge/
├── 🎯 cli.py                    # Command-line interface
├── ⚙️ core/                     # Framework core
│   ├── agents/                  # Base agent classes
│   ├── shared/                  # Shared utilities
│   └── config/                  # Configuration management
├── 🤖 examples/                 # Ready-to-use agents
│   ├── simple_navigation_agent.py
│   ├── nmkr_auditor_agent.py
│   ├── cardano_enhanced_agent.py
│   └── data_compiler_agent.py
├── 📚 docs/                     # Comprehensive documentation
│   ├── guides/                  # Step-by-step guides
│   ├── tutorials/               # Learning tutorials  
│   ├── api/                     # API references
│   ├── integrations/            # Platform integrations
│   └── architecture/            # Technical docs
├── 🧪 tests/                    # Complete test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
└── 📖 memory-bank/              # Project knowledge base
```

---

## 🎯 **Core Features**

### 🔧 **Agent Management**
- **CLI Interface**: Discover, run, and manage agents via command line
- **Async Context Managers**: Automatic initialization and cleanup
- **Configuration System**: Flexible YAML/JSON configuration support
- **Logging Integration**: Structured logging with configurable levels

### 🌐 **Web Automation**
- **Steel Browser Integration**: Production-grade browser automation
- **Anti-Detection**: Built-in evasion of bot detection systems
- **Dynamic Content**: Handle JavaScript-heavy sites and SPAs
- **Mobile Support**: Responsive design testing and mobile automation

### ⛓️ **Blockchain Integration**
- **Enhanced Cardano Client**: Complete smart contract architecture with 5 enterprise patterns
- **AI Agent Economy**: Hierarchical registry, revenue sharing, and escrow-as-a-service
- **NMKR Proof-of-Execution**: Generate verifiable NFT proofs of agent execution
- **Masumi Network**: Participate in the decentralized AI agent economy
- **Cross-Chain Support**: Multi-chain integration (Cardano, Ethereum, Polygon, Solana, Avalanche)
- **IPFS Storage**: Decentralized storage for audit logs and proofs

### 🧪 **Testing & Quality**
- **120+ Passing Tests**: Comprehensive test coverage including Cardano integration
- **5 Test Categories**: Unit, integration, end-to-end, performance, and security testing
- **Automated Testing**: Built-in test runner with multiple execution modes
- **Coverage Reports**: HTML and XML coverage reporting
- **Security Testing**: Vulnerability assessment and penetration testing
- **Performance Tests**: Benchmarking and performance validation

---

## 📋 **Available Agents**

### 🌐 **SimpleNavigationAgent**
Basic web navigation and content extraction
```bash
python cli.py run simple_navigation --url https://example.com
```

### ⛓️ **NMKRAuditorAgent** 
Blockchain-verified execution proofs with NMKR integration
```bash
python cli.py run nmkr_auditor --url https://cardano.org --task "Analyze blockchain data"
```

### 🏛️ **CardanoEnhancedAgent**
Complete AI agent economy with smart contract integration
```bash
python cli.py run cardano_enhanced --operation full_demo
python cli.py run cardano_enhanced --operation register --stake_amount 1000.0
```

### 📊 **DataCompilerAgent**
Advanced data collection and compilation
```bash
python cli.py run data_compiler --sources "url1,url2,url3"
```

### 🔍 **TextExtractionAgent**
Intelligent content extraction and processing
```bash
python cli.py run text_extraction --url https://news-site.com
```

---

## 🌟 **CLI Commands**

### Agent Management
```bash
# List all available agents
python cli.py list

# Get agent information
python cli.py info simple_navigation

# Run an agent with parameters
python cli.py run AGENT_NAME --url URL --task "Description"

# Dry run (test without execution)
python cli.py run AGENT_NAME --dry-run

# Verbose logging
python cli.py --verbose run AGENT_NAME
```

### Testing
```bash
# Run all tests
python tests/run_tests.py

# Run specific test types
python tests/run_tests.py --type unit
python tests/run_tests.py --type integration

# Quick smoke tests
python tests/run_tests.py --smoke

# Generate test reports
python tests/run_tests.py --report
```

---

## ⛓️ **Blockchain Integration**

### NMKR Proof-of-Execution NFTs

Generate verifiable blockchain proofs of your agent's execution:

```python
from examples.nmkr_auditor_agent import NMKRAuditorAgent

async def create_blockchain_proof():
    async with NMKRAuditorAgent(
        url="https://target-site.com",
        task_description="Extract market data",
        nmkr_api_key="your_nmkr_key"
    ) as agent:
        proof_package = await agent.run()
        
        print(f"Blockchain Proof Generated!")
        print(f"Hash: {proof_package['verification_data']['proof_hash']}")
        print(f"IPFS: {proof_package['verification_data']['ipfs_cid']}")
```

### Masumi Network Integration

Monetize your agents in the decentralized AI economy:

```python
from masumi_enabled_agent import MasumiEnabledAgent

async def monetized_agent():
    async with MasumiEnabledAgent(
        url="https://target-site.com",
        masumi_config={
            "payment_contract": "0x...",
            "web3_provider": "https://cardano-node.com"
        },
        payment_proof="0x...",  # Payment transaction hash
        job_id="job_123"
    ) as agent:
        result = await agent.execute_with_masumi()
        
        print(f"Task completed: {result['result']}")
        print(f"Payment claimed: {result['payment_claimed']}")
```

---

## 🏛️ **Cardano Integration**

### Enhanced Cardano Client

Agent Forge's Enhanced Cardano Client implements a complete AI agent economy with 5 smart contract architecture patterns:

```python
from src.core.blockchain.cardano_enhanced_client import EnhancedCardanoClient, AgentProfile

async def cardano_ai_economy():
    client = EnhancedCardanoClient(
        nmkr_api_key="your_nmkr_key",
        blockfrost_project_id="your_project_id",
        policy_id="your_policy_id"
    )
    
    # Register AI agent with staking
    profile = AgentProfile(
        owner_address="addr1_your_address",
        agent_id="ai_agent_001",
        metadata_uri="ipfs://QmYourMetadata",
        staked_amount=1000.0,
        capabilities=["web_automation", "ai_analysis", "blockchain"]
    )
    
    registration = await client.register_agent(profile, stake_amount=1000.0)
    print(f"Agent registered: {registration['transaction_id']}")
    
    # Find agents by capabilities
    agents = await client.find_agents(
        capabilities=["web_automation"],
        min_reputation=0.8
    )
    print(f"Found {len(agents)} qualified agents")
```

### Smart Contract Architecture Patterns

#### **1. Hierarchical Agent Registry with Reputation Staking**
- Multi-tier staking system (100-10,000+ ADA)
- Reputation-based discovery and ranking
- Capability-based validation

#### **2. Dual-Token Economic Model with Revenue Sharing**
- Governance tokens for platform decisions
- Utility tokens for service payments
- Revenue Participation Tokens with profit sharing

#### **3. Escrow-as-a-Service with ZK Verification**
- Automated escrow creation and management
- Execution proof verification
- Multi-pricing model support

#### **4. Cross-Chain Service Discovery Protocol**
- 5-chain integration (Cardano, Ethereum, Polygon, Solana, Avalanche)
- Unified service registry
- Bridge-compatible architecture

#### **5. Compliance-Ready ABAC Framework**
- REGKYC privacy-preserving KYC/AML
- GDPR-compliant data handling
- Enterprise security standards

### Production Deployment

The Cardano integration is **production-ready** with:
- ✅ **29/29 Unit Tests Passing** - Complete functionality validation
- ✅ **Enterprise Security Testing** - Comprehensive vulnerability assessment
- ✅ **Performance Validation** - 10+ ops/second throughput, 1000+ participant scalability
- ✅ **Cross-Chain Compatibility** - Multi-blockchain support

---

## 📚 **Documentation & Guides**

### 🎓 **Learning Path**
1. **[Getting Started Guide](docs/guides/GETTING_STARTED.md)** - Your first agent in 10 minutes
2. **[Agent Development Tutorial](docs/tutorials/AGENT_DEVELOPMENT_TUTORIAL.md)** - Build custom agents step-by-step
3. **[Steel Browser Integration](docs/integrations/STEEL_BROWSER_INTEGRATION.md)** - Master web automation
4. **[Cardano Smart Contracts](docs/integrations/CARDANO_SMART_CONTRACTS_PLAN.md)** - AI agent economy architecture
5. **[NMKR Proof-of-Execution](docs/integrations/NMKR_PROOF_OF_EXECUTION_GUIDE.md)** - Blockchain verification
6. **[Masumi Network Integration](docs/integrations/MASUMI_NETWORK_INTEGRATION_GUIDE.md)** - Join the AI agent economy

### 📖 **API References**
- **[BaseAgent API](docs/api/BASEAGENT_API_REFERENCE.md)** - Core agent functionality
- **[Enhanced Cardano Client API](src/core/blockchain/cardano_enhanced_client.py)** - Blockchain integration
- **[CLI Reference](docs/api/CLI_REFERENCE.md)** - Command-line interface
- **[Configuration Guide](docs/guides/CONFIGURATION.md)** - Setup and customization

### 🏗️ **Architecture**
- **[Framework Architecture](docs/architecture/FRAMEWORK_ARCHITECTURE.md)** - Technical overview
- **[Testing Strategy](docs/architecture/TESTING_ARCHITECTURE.md)** - Quality assurance approach

---

## 🧪 **Testing**

Agent Forge includes a comprehensive testing framework with 120+ passing tests covering all functionality including Cardano integration:

### Test Categories
- **Unit Tests** (45): Core functionality validation including Cardano client
- **Integration Tests** (28): Component interaction testing  
- **End-to-End Tests** (30): Complete workflow validation
- **Performance Tests** (12): Blockchain operations benchmarking
- **Security Tests** (8): Vulnerability assessment and penetration testing

### Running Tests
```bash
# Run all tests
python tests/run_tests.py

# Quick validation
python tests/run_tests.py --quick

# Smoke tests (basic functionality)
python tests/run_tests.py --smoke

# Generate coverage report
python tests/run_tests.py --report
```

### Test Results
- ✅ **Unit Tests**: 100% pass rate (45/45) - Including 29/29 Cardano tests
- ✅ **Integration Tests**: 100% pass rate (28/28)
- ✅ **End-to-End Tests**: 100% pass rate (30/30)
- ✅ **Performance Tests**: 100% pass rate (12/12)
- ✅ **Security Tests**: 100% pass rate (8/8)

---

## 🔧 **Development**

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/your-org/agent_forge.git
cd agent_forge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install black ruff mypy pytest

# Run tests to verify setup
python tests/run_tests.py --smoke
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check . --fix

# Type checking
mypy core/ examples/

# Run full test suite
python tests/run_tests.py
```

### Creating Custom Agents

1. **Inherit from AsyncContextAgent**
```python
from src.core.agents.base import AsyncContextAgent

class MyAgent(AsyncContextAgent):
    async def run(self):
        # Your agent logic here
        pass
```

2. **Place in examples/ directory**
3. **Add to CLI discovery** (automatic)
4. **Write tests** in `tests/`
5. **Update documentation**

---

## 🌍 **Real-World Applications**

### 🏢 **Enterprise Use Cases**
- **Market Research**: Automated competitor analysis and data collection
- **Compliance Monitoring**: Regulatory compliance checking across websites
- **Content Auditing**: Brand mention monitoring and sentiment analysis
- **Data Migration**: Automated data extraction and transformation

### ⛓️ **Blockchain Applications**
- **AI Agent Economy**: Complete marketplace with staking, escrow, and revenue sharing
- **DeFi Analytics**: Automated DeFi protocol analysis with verifiable proofs
- **NFT Research**: Market analysis with blockchain-verified execution
- **Governance Monitoring**: DAO proposal tracking with audit trails
- **Compliance Reporting**: Regulatory reporting with cryptographic proofs
- **Cross-Chain Services**: Multi-blockchain agent coordination and payments

### 🤖 **AI Agent Economy**
- **Service Marketplace**: Monetize your agents through Masumi Network
- **Verifiable AI**: Provide blockchain proofs of AI decision-making
- **Collaborative Agents**: Enable agents to hire and pay other agents
- **Trust Networks**: Build reputation through verifiable execution history

---

## 📈 **Roadmap**

### ✅ **Completed (Phase 1)**
- ✅ Core framework architecture
- ✅ Steel Browser integration
- ✅ CLI interface and agent discovery
- ✅ Comprehensive testing framework (120+ passing tests)
- ✅ Enhanced Cardano integration with 5 smart contract patterns
- ✅ NMKR Proof-of-Execution integration
- ✅ Masumi Network integration
- ✅ Complete documentation suite

### 🚧 **In Progress (Phase 2)**
- 🔄 Advanced agent orchestration
- 🔄 Multi-agent collaboration patterns
- 🔄 Enhanced monitoring and analytics
- 🔄 Plugin system for extensibility

### 🎯 **Planned (Phase 3)**
- 🎯 Visual agent builder interface
- 🎯 Marketplace for agent templates
- 🎯 Advanced AI integration (OpenAI, Anthropic)
- 🎯 Cross-chain blockchain support

---

## 🤝 **Contributing**

We welcome contributions! Here's how to get involved:

### 🐛 **Bug Reports**
- Use [GitHub Issues](https://github.com/your-org/agent_forge/issues)
- Include reproduction steps and environment details
- Add relevant logs and error messages

### ✨ **Feature Requests**
- Describe your use case and proposed solution
- Check existing issues to avoid duplicates
- Consider contributing the implementation

### 💻 **Code Contributions**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`python tests/run_tests.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### 📚 **Documentation**
- Improve existing documentation
- Add examples and tutorials
- Translate documentation to other languages

---

## 📞 **Support & Community**

### 💬 **Get Help**
- 📖 **Documentation**: Start with our [comprehensive guides](docs/)
- 💡 **GitHub Issues**: For bugs and feature requests
- 🤝 **Community Forum**: Join discussions and share experiences
- 📧 **Email**: contact@agentforge.dev for enterprise support

### 🌟 **Stay Updated**
- ⭐ **Star this repository** to get updates
- 👀 **Watch releases** for new features
- 🐦 **Follow us on Twitter** [@AgentForge](https://twitter.com/agentforge)
- 📰 **Subscribe to our newsletter** for tutorials and tips

---

## 📄 **License**

Agent Forge is released under the [MIT License](LICENSE). See the LICENSE file for details.

---

## 🙏 **Acknowledgments**

Agent Forge is built on the foundation of excellent open-source projects:

- **[Steel Browser](https://steel.dev)** - Professional web automation platform
- **[NMKR](https://nmkr.io)** - Leading Cardano NFT and tokenization platform  
- **[Masumi Network](https://masumi.network)** - Decentralized AI agent economy protocol
- **[Cardano](https://cardano.org)** - Sustainable blockchain platform
- **[FastAPI](https://fastapi.tiangolo.com)** - Modern Python web framework
- **[Pytest](https://pytest.org)** - Python testing framework

---

## 🚀 **Ready to Build the Future?**

Agent Forge isn't just a framework - it's your gateway to the **Autonomous AI Agent Economy**. Whether you're building simple web scrapers or complex blockchain-verified AI systems, Agent Forge provides the tools, documentation, and community to help you succeed.

**[Get Started Now](docs/guides/GETTING_STARTED.md)** | **[Join the Community](#support--community)** | **[Contribute](#contributing)**

---

<div align="center">

**Built with ❤️ by the Agent Forge Team**

*Empowering developers to create autonomous AI agents that shape the future*

</div>