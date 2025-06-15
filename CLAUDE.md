# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Commands

### Development Commands
```bash
# Testing
pytest                          # Run all tests
pytest tests/unit              # Run unit tests only
pytest -m integration          # Run integration tests only
pytest -m e2e                  # Run end-to-end tests only
pytest -k "test_name"          # Run specific test by name pattern
python test_runner.py          # Run MCP integration tests
python tests/cardano_test_runner.py  # Run Cardano integration tests

# Code Quality
black .                        # Format code with Black
ruff check . --fix            # Lint and auto-fix code issues
mypy src/core/ examples/          # Type checking for core modules

# Agent Management
python tools/scripts/cli.py list             # List all available agents
python tools/scripts/cli.py info <agent>     # Get detailed agent information
python tools/scripts/cli.py run <agent> [options]  # Run specific agent
python tools/scripts/cli.py run <agent> --dry-run  # Test without execution
python tools/scripts/cli.py --verbose run <agent>  # Run with verbose logging

# MCP Server
python src/mcp/mcp_server.py          # Start MCP server for Claude Desktop integration
```

### Next.js Website (in `website/` directory)
```bash
cd website
npm run dev                   # Start development server
npm run build                # Create production build
npm run lint                 # Run ESLint checks
```

## High-Level Architecture

### Framework Design Philosophy
Agent Forge follows an **async-first architecture** with a strong emphasis on:
- **Context Management**: All agents inherit from `AsyncContextAgent` which provides automatic resource cleanup via async context managers
- **Self-Contained Dependencies**: Core utilities in `core/shared/` provide all necessary functionality without external service dependencies
- **Enhanced Cardano Integration**: Complete AI agent economy with 5 smart contract patterns (registry, escrow, revenue sharing, cross-chain, compliance)
- **Blockchain Integration**: Native support for NMKR Proof-of-Execution NFTs and Masumi Network AI agent economy
- **MCP Integration**: FastMCP wrapper enables agents to work seamlessly in Claude Desktop and other MCP clients

### Key Architectural Patterns

#### 1. AsyncContextAgent Pattern
The foundation of all agents - provides lifecycle management, error handling, and resource cleanup:
```python
class MyAgent(AsyncContextAgent):
    async def run(self) -> dict:
        # Agent logic here
        pass

# Usage with automatic cleanup
async with MyAgent() as agent:
    result = await agent.run()
```

#### 2. Agent Discovery System
The CLI automatically discovers agents by:
- Scanning `examples/` directory for Python files
- Looking for classes inheriting from `AsyncContextAgent`
- Extracting metadata from class docstrings and attributes
- No manual registration required - just drop agent files in `examples/`

#### 3. Blockchain Integration Architecture
Three-layer blockchain integration:
- **Enhanced Cardano Layer**: Complete AI agent economy with smart contract patterns (EnhancedCardanoClient)
- **NMKR Layer**: Generates CIP-25 compliant NFTs as proof-of-execution with metadata stored on IPFS
- **Masumi Layer**: Enables agent monetization through MIP-003 compliant API for AI agent economy participation

#### 4. MCP Server Architecture
The MCP integration (`mcp_server.py`) wraps Agent Forge agents as MCP tools:
- Auto-discovers all agents in `examples/` directory
- Exposes each agent as an MCP tool with proper parameter schemas
- Handles async execution and result formatting for MCP clients
- Enables natural language agent invocation in Claude Desktop

#### 5. Testing Strategy
Multi-layer testing approach ensures production reliability:
- **Unit Tests**: Test individual components in isolation (including 29 Cardano client tests)
- **Integration Tests**: Verify component interactions
- **E2E Tests**: Validate complete agent workflows including AI economy
- **Performance Tests**: Benchmark blockchain operations (10+ ops/sec, 1000+ participants)
- **Security Tests**: Validate staking attacks, escrow vulnerabilities, input sanitization
- **MCP Tests**: Ensure proper MCP server functionality

### Service Organization

```
agent_forge/
├── src/                     # Main source code
│   ├── core/               # Framework core (DO NOT modify without understanding impact)
│   │   ├── agents/         # Base agent classes and interfaces
│   │   ├── blockchain/     # Enhanced Cardano, NMKR and Masumi integrations
│   │   └── shared/         # Self-contained utilities (AI, auth, database, web)
│   ├── mcp/                # MCP integration servers
│   └── agent_forge/        # Additional framework components
│
├── examples/               # Production-ready agent implementations
│   └── *.py               # Each file contains one agent class
│
├── tools/                  # Development tools and utilities
│   ├── scripts/            # CLI tools and utilities
│   └── demos/              # Demo implementations
│
└── tests/                  # Comprehensive test suite
```

### Critical Implementation Notes

1. **Async Context Managers**: Always use agents within async context managers to ensure proper cleanup
2. **Agent Discovery**: Place new agents in `examples/` directory - they're automatically discovered
3. **Cardano Integration**: Use `CardanoEnhancedAgent` for complete AI economy features
4. **Blockchain Proofs**: Use `NMKRAuditorAgent` as reference for NMKR integration patterns
5. **MCP Integration**: Test agents via `tools/scripts/cli.py` before exposing through MCP server
6. **Error Handling**: Framework provides comprehensive error handling - don't suppress exceptions
7. **Configuration**: Use agent `__init__` parameters for configuration, not environment variables
8. **Testing**: Add tests for new agents in appropriate test categories (unit/integration/e2e/performance/security)

### Framework Extension Points

1. **Custom Agents**: Inherit from `AsyncContextAgent` and implement `run()` method
2. **New Utilities**: Add to `src/core/shared/` following existing patterns
3. **Cardano Extensions**: Extend `EnhancedCardanoClient` for additional smart contract patterns
4. **Blockchain Extensions**: Extend `src/core/blockchain/` for new chain integrations
5. **MCP Tools**: Agents are automatically exposed as MCP tools when placed in `examples/`

### Performance Considerations

- **Async Everything**: Use async/await throughout for non-blocking operations
- **Resource Management**: Context managers ensure proper cleanup even on errors
- **Connection Pooling**: HTTP clients use connection pooling by default
- **Batch Operations**: Framework supports batch processing for efficiency
- **Caching**: Built-in caching for AI embeddings and repeated operations

## 📚 **Agent Forge Memory Bank**

Agent Forge maintains its own dedicated memory bank in `memory-bank/` for framework-specific development context and knowledge preservation.

### **Key Memory Bank Files:**
- **[memory-bank/00-AGENT_FORGE_KNOWLEDGE_SYSTEM.md](memory-bank/00-AGENT_FORGE_KNOWLEDGE_SYSTEM.md)** - Master navigation for framework knowledge
- **[memory-bank/01-README-DevProcess.md](memory-bank/01-README-DevProcess.md)** - Framework development workflow and CLI commands  
- **[memory-bank/02-activeContext.md](memory-bank/02-activeContext.md)** - Current development status and priorities
- **[memory-bank/04-projectbrief.md](memory-bank/04-projectbrief.md)** - Framework vision and multi-chain capabilities

### **Memory Bank Organization:**
- **[memory-bank/adrs/](memory-bank/adrs/)** - Architectural Decision Records for framework design
- **[memory-bank/current-focus/](memory-bank/current-focus/)** - Active development priorities and session context
- **[memory-bank/archive/](memory-bank/archive/)** - Historical documentation and completed phases

### **Framework Development Workflow:**
1. **Start Session:** Read `memory-bank/02-activeContext.md` for current framework status
2. **Understand Architecture:** Review `memory-bank/01-README-DevProcess.md` for development patterns
3. **Check Priorities:** Review `memory-bank/current-focus/` for immediate tasks
4. **Document Progress:** Update relevant memory bank files with achievements
5. **Record Decisions:** Create ADRs in `memory-bank/adrs/` for architectural choices

**Memory Bank Purpose:** Preserve context, decisions, and learnings across Agent Forge development sessions, enabling consistent progress on the world's first production-ready multi-chain AI agent framework.