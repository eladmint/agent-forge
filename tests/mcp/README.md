# 🧪 MCP Integration Test Suite

**Comprehensive testing for Agent Forge Model Context Protocol (MCP) integration**

This directory contains specialized test suites for validating Agent Forge's MCP integration, ensuring seamless operation in Claude Desktop, Cursor, and other MCP clients.

## 📁 Test Files

### **Core Integration Tests**
- **`test_mcp_integration.py`** - Fundamental MCP functionality validation
  - MCP dependencies verification
  - MCP server import and functionality  
  - Agent discovery system (8 agents)
  - Core tools registration (6 tools)
  - Claude Desktop configuration validation
  - End-to-end integration verification

### **Real-World Usage Tests**
- **`test_claude_desktop_scenarios.py`** - Practical Claude Desktop usage scenarios
  - 10 comprehensive conversational test scenarios
  - Natural language command pattern validation
  - Parameter extraction from conversational input
  - Multi-tool workflow testing
  - Error recovery scenario validation
  - Cross-platform configuration testing

### **Performance & Benchmark Tests**  
- **`test_mcp_performance_benchmarks.py`** - Production readiness validation
  - Server startup performance (< 2 seconds)
  - Agent discovery performance (< 5 seconds)
  - Tool execution benchmarks (< 5 seconds)
  - Memory usage monitoring (< 500MB)
  - Concurrent request handling (10 simultaneous)
  - Load testing scenarios (sustained performance)
  - Resource cleanup verification

## 🚀 Running Tests

### **Individual Test Suites**
```bash
# Core integration tests
python tests/mcp/test_mcp_integration.py

# Claude Desktop scenarios
python tests/mcp/test_claude_desktop_scenarios.py

# Performance benchmarks
python tests/mcp/test_mcp_performance_benchmarks.py
```

### **Comprehensive Test Suite**
```bash
# Run all MCP tests with comprehensive reporting
python test_runner.py
```

### **Using pytest**
```bash
# Run all MCP tests
pytest tests/mcp/ -v

# Run specific test file
pytest tests/mcp/test_mcp_integration.py -v

# Run with coverage
pytest tests/mcp/ --cov=. --cov-report=html
```

## 📊 Test Categories

| **Category** | **File** | **Tests** | **Purpose** |
|--------------|----------|-----------|-------------|
| **Basic Integration** | `test_mcp_integration.py` | 6 tests | Core MCP functionality |
| **Usage Scenarios** | `test_claude_desktop_scenarios.py` | 10 scenarios | Real-world patterns |
| **Performance** | `test_mcp_performance_benchmarks.py` | 7 benchmarks | Production readiness |

## 🎯 Test Scenarios

The test suite includes these real-world Claude Desktop scenarios:

### **Beginner Scenarios**
1. **Agent Info Query**: `"Claude, use get_agent_info to show me all available Agent Forge tools"`

### **Intermediate Scenarios**  
2. **Website Navigation**: `"Use navigate_website to visit TechCrunch and extract the top 3 headlines"`
3. **Data Compilation**: `"Compile pricing data from these 3 competitor websites"`
4. **Content Extraction**: `"Extract full article text from this research paper URL"`
5. **Website Validation**: `"Check our company website for accessibility issues"`

### **Advanced Scenarios**
6. **Blockchain Proof**: `"Generate a blockchain proof for my analysis of Apple's homepage"`
7. **Multi-Tool Workflow**: Sequential use of multiple tools for complex analysis
8. **Performance Testing**: Large-scale data processing scenarios
9. **Error Recovery**: Invalid URLs and parameter handling
10. **Natural Language**: Ambiguous requests requiring interpretation

## 📋 Prerequisites

### **Dependencies**
```bash
# Install MCP dependencies
pip install -r mcp_requirements.txt

# Verify installation
python -c "import fastmcp, mcp; print('MCP dependencies ready')"
```

### **Claude Desktop Configuration**
Ensure Claude Desktop is configured with Agent Forge MCP server:
```json
{
  "mcpServers": {
    "agent-forge": {
      "command": "python",
      "args": ["/path/to/agent_forge/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/agent_forge"
      }
    }
  }
}
```

## ✅ Success Criteria

### **Integration Tests**
- ✅ MCP server imports successfully
- ✅ Agent discovery finds all 8 agents
- ✅ Core tools (6) register properly
- ✅ Claude Desktop config validates

### **Scenario Tests**
- ✅ All 10 scenarios have proper structure
- ✅ Conversational patterns validated
- ✅ Parameter extraction works correctly
- ✅ Error scenarios handled gracefully

### **Performance Tests**
- ✅ Server startup < 2 seconds
- ✅ Agent discovery < 5 seconds  
- ✅ Tool execution < 5 seconds
- ✅ Memory usage < 500MB
- ✅ Concurrent requests succeed
- ✅ Load testing passes

## 🔧 Troubleshooting

### **Common Issues**

#### **Import Errors**
```bash
# Check Python path
export PYTHONPATH="/path/to/agent_forge:$PYTHONPATH"

# Verify dependencies
pip install fastmcp mcp aiohttp requests
```

#### **Agent Discovery Fails**
```bash
# Test discovery manually
python -c "
from mcp_auto_discovery import AgentDiscovery
discovery = AgentDiscovery()
agents = discovery.discover_agents()
print(f'Found {len(agents)} agents: {list(agents.keys())}')
"
```

#### **Performance Issues**
```bash
# Check system resources
python -c "
import psutil
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'CPU: {psutil.cpu_percent()}%')
"
```

### **Test Debugging**
```bash
# Run with verbose output
python tests/mcp/test_mcp_integration.py -v

# Run single test method
python -m pytest tests/mcp/test_mcp_integration.py::MCPIntegrationTestSuite::test_03_agent_discovery -v

# Enable debug logging
LOG_LEVEL=DEBUG python tests/mcp/test_mcp_integration.py
```

## 📈 Performance Benchmarks

Expected performance metrics for production readiness:

| **Metric** | **Threshold** | **Purpose** |
|------------|---------------|-------------|
| Server Startup | < 2 seconds | Fast initialization |
| Agent Discovery | < 5 seconds | Reasonable scan time |
| Tool Execution | < 5 seconds | Responsive interaction |
| Memory Usage | < 500MB | Resource efficiency |
| Concurrent Requests | 10 simultaneous | Multi-user support |

## 🎉 Production Readiness

When all tests pass:
- ✅ **Deploy to Claude Desktop** with confidence
- ✅ **Test with real users** using provided scenarios
- ✅ **Monitor performance** in production environment
- ✅ **Proceed with open source release** (MCP-First Launch)

## 📚 Related Documentation

- **[MCP Integration Guide](../../docs/integrations/MCP_INTEGRATION_GUIDE.md)** - Complete technical setup
- **[MCP Quick Start](../../docs/guides/MCP_QUICK_START.md)** - 5-minute setup guide  
- **[Claude Desktop Setup](../../docs/CLAUDE_DESKTOP_SETUP.md)** - Detailed configuration
- **[MCP Tools Reference](../../docs/api/MCP_TOOLS_REFERENCE.md)** - Complete tool documentation

---

**Ready to test?** Start with `python test_runner.py` for comprehensive validation!