# 🤖 Agent Forge Core Agents

**Purpose:** This directory contains the core agent framework components and specialized agents for autonomous web automation. These agents perform specific, modular tasks in web scraping, data extraction, and browser automation workflows.

**📖 FRAMEWORK REFERENCE:** For the complete Agent Forge framework documentation, see:
- **[📋 Framework Architecture](../../docs/architecture/FRAMEWORK_ARCHITECTURE.md)**
- **[🎓 Agent Development Tutorial](../../docs/tutorials/AGENT_DEVELOPMENT_TUTORIAL.md)**

---

## 🏗️ Agent Forge Architecture

The agents in this directory implement the core Agent Forge framework patterns. They demonstrate modern async/await patterns, Steel Browser integration, and autonomous web automation capabilities.

**Key Agent Categories:**
- **BaseAgent Framework:** Core `AsyncContextAgent` implementation providing standard lifecycle management
- **Web Automation:** Agents using Steel Browser for production-grade web navigation and content extraction
- **Data Processing:** Agents for structured data compilation, validation, and enhancement
- **Blockchain Integration:** Advanced agents with NMKR Proof-of-Execution and Cardano NFT capabilities

## 📁 Directory Organization

This directory contains the core Agent Forge framework components. For working examples, see the `/examples/` directory.

### 🎯 Core Framework Components
- **`base.py`**: Core `AsyncContextAgent` base class and framework patterns
- **`models.py`**: Pydantic data models for structured agent data
- **`__init__.py`**: Package initialization and exports

### 🤖 Working Examples
For complete, working agent implementations, see:
- **[Examples Directory](../../examples/)** - Production-ready agents including:
  - `SimpleNavigationAgent` - Basic web navigation
  - `NMKRAuditorAgent` - Blockchain verification (642 lines, complete)
  - `DataCompilerAgent` - Data processing and validation
  - `PageScraperAgent` - Advanced web scraping

---

## 📚 Framework Documentation

- **[Framework Architecture](../../docs/architecture/FRAMEWORK_ARCHITECTURE.md)** - Complete technical overview
- **[Agent Development Tutorial](../../docs/tutorials/AGENT_DEVELOPMENT_TUTORIAL.md)** - Step-by-step learning guide
- **[Getting Started](../../docs/guides/GETTING_STARTED.md)** - Quick setup and first agent
- **[API Reference](../../docs/api/)** - Detailed API documentation