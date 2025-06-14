# Agent Forge Testing Framework

A comprehensive testing framework for Agent Forge MCP integration, production deployments, and open source distributions.

## 🚀 Quick Start

### Installation Validation
```bash
# Run comprehensive installation validation
python agent_forge_tests/examples/quick_start.py

# Save results to file
python agent_forge_tests/examples/quick_start.py --output validation_results.json
```

### Python API Usage
```python
from agent_forge_tests import AgentForgeValidator, QuickStartTestSuite

# Quick validation for end users
suite = QuickStartTestSuite()
results = suite.run_all_tests()

if results.all_passed:
    print("✅ Ready for Claude Desktop!")
else:
    print("❌ Issues found:", results.summary)

# Comprehensive validation for developers
validator = AgentForgeValidator()
detailed_results = validator.run_comprehensive_validation()
```

## 📋 Test Categories

### 🔌 MCP Integration Tests
- **Location**: `tests/mcp/`
- **Purpose**: Validate Claude Desktop integration
- **Tests**: 26 tests across 3 suites
- **Usage**: `python test_runner.py`

### 🔒 Security Tests  
- **Location**: `tests/security/`
- **Purpose**: Credential security, input validation, permission enforcement
- **Tests**: 8 critical security validation tests
- **Usage**: `python tests/security/test_credential_security.py`

### 💥 Failure Scenario Tests
- **Location**: `tests/integration/test_failure_scenarios.py`
- **Purpose**: Network failures, service downtime, resource exhaustion
- **Tests**: 9 production resilience tests
- **Usage**: `python tests/integration/test_failure_scenarios.py`

### 🤝 Multi-Agent Coordination Tests
- **Location**: `tests/integration/test_agent_coordination.py`
- **Purpose**: Agent communication, resource conflicts, workflow coordination
- **Tests**: 6 coordination validation tests  
- **Usage**: `python tests/integration/test_agent_coordination.py`

### ⚡ Performance Tests
- **Location**: `tests/mcp/test_mcp_performance_benchmarks.py`
- **Purpose**: Load testing, memory management, response time validation
- **Tests**: 7 performance benchmark tests
- **Usage**: Included in `test_runner.py`

## 🎯 Test Framework Features

### ✅ Production Readiness Validation
- **Installation Structure**: Validates all required files and directories
- **Dependencies**: Checks Python packages and versions
- **Configuration**: Validates Claude Desktop config files
- **Security**: Credential handling, input validation, file permissions
- **Performance**: Response times, memory usage, concurrent operations
- **Reliability**: Error handling, recovery mechanisms, failure scenarios

### 🛡️ Security Testing
- **Credential Protection**: API key redaction, secure storage validation
- **Input Validation**: XSS, SQL injection, command injection prevention
- **Permission Enforcement**: File system access, URL validation
- **Environment Security**: Environment variable handling, configuration security

### 🔄 Real-World Scenarios
- **Network Failures**: Timeouts, DNS resolution, partial connectivity
- **Service Dependencies**: Steel Browser, NMKR API, Masumi Network downtime
- **Resource Management**: Memory exhaustion, concurrent requests, disk space
- **Multi-Agent Workflows**: Data handoffs, resource conflicts, error propagation

## 📁 Package Structure

```
agent_forge_tests/
├── 📄 README.md                           # This documentation
├── 📄 __init__.py                         # Package initialization
├── 🔧 validators/                         # Validation tools
│   ├── installation_validator.py          # Comprehensive installation validation
│   ├── mcp_validator.py                   # MCP-specific validation
│   ├── security_validator.py              # Security validation tools
│   └── performance_validator.py           # Performance validation tools
├── 📚 examples/                          # Ready-to-use examples
│   ├── quick_start.py                     # Quick validation for end users
│   ├── production_readiness.py            # Comprehensive production validation
│   └── custom_test_template.py            # Template for custom tests
├── 🏗️ templates/                          # Test templates
│   ├── basic_test.py                      # Basic test template
│   ├── mcp_test.py                        # MCP integration test template
│   ├── security_test.py                   # Security test template
│   └── performance_test.py                # Performance test template
└── 📖 documentation/                      # Detailed documentation
    ├── testing_guide.md                   # Comprehensive testing guide
    ├── security_guidelines.md             # Security testing guidelines
    ├── performance_benchmarks.md          # Performance testing standards
    └── troubleshooting.md                 # Common issues and solutions
```

## 🎯 For Open Source Users

### Quick Validation (5 minutes)
```bash
# Clone or download Agent Forge
git clone https://github.com/your-org/agent-forge.git
cd agent-forge

# Run quick validation
python agent_forge_tests/examples/quick_start.py

# Expected output:
# 🎉 ALL TESTS PASSED!
# ✅ Agent Forge is ready for Claude Desktop integration!
```

### Production Deployment (15 minutes)  
```bash
# Comprehensive validation
python agent_forge_tests/examples/production_readiness.py

# Run specific test categories
python tests/security/test_credential_security.py      # Security validation
python tests/integration/test_failure_scenarios.py     # Resilience testing
python tests/integration/test_agent_coordination.py    # Multi-agent testing
```

### Custom Testing
```python
# Create custom test using templates
from agent_forge_tests.templates import BasicAgentTest

class MyCustomTest(BasicAgentTest):
    def test_my_feature(self):
        # Your test logic here
        result = self.run_agent_operation('my_agent', {'url': 'example.com'})
        self.assertTrue(result['success'])

# Run your test
suite = unittest.TestLoader().loadTestsFromTestCase(MyCustomTest)
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
```

## 📊 Test Statistics

| Test Category          | Tests | Coverage Area              | Execution Time | Status |
|------------------------|-------|----------------------------|----------------|--------|
| **MCP Integration**    | 26    | Claude Desktop integration | ~16s           | ✅ Ready |
| **Security**           | 8     | Credential & input safety  | ~3s            | ✅ Ready |
| **Failure Scenarios**  | 9     | Production resilience      | ~8s            | ✅ Ready |
| **Agent Coordination** | 6     | Multi-agent workflows      | ~4s            | ✅ Ready |
| **Performance**        | 7     | Load & memory testing      | ~14s           | ✅ Ready |
| **Installation**       | 6     | Setup validation           | ~2s            | ✅ Ready |
| **Total**              | **62** | **Complete framework**     | **~47s**       | ✅ **Production Ready** |

## 🔍 Test Execution Options

### Command Line
```bash
# Quick validation (recommended for users)
python agent_forge_tests/examples/quick_start.py

# Comprehensive test suite (for developers)
python test_runner.py

# Specific test categories
python tests/security/test_credential_security.py
python tests/integration/test_failure_scenarios.py  
python tests/integration/test_agent_coordination.py
```

### Python API
```python
# Import validators
from agent_forge_tests import (
    AgentForgeValidator,
    QuickStartTestSuite, 
    SecurityValidator,
    PerformanceValidator
)

# Quick validation
quick_results = QuickStartTestSuite().run_all_tests()

# Detailed validation  
detailed_results = AgentForgeValidator().run_comprehensive_validation()

# Security-focused validation
security_results = SecurityValidator().run_security_tests()

# Performance validation
performance_results = PerformanceValidator().run_benchmarks()
```

## 🎯 Success Criteria

### ✅ Ready for Claude Desktop
- Installation structure complete
- All dependencies installed
- MCP server imports successfully
- Agent discovery functional
- Claude Desktop config valid
- Basic security checks pass

### ✅ Ready for Production
- All quick start tests pass
- Security tests pass (credential protection, input validation)
- Failure scenario tests pass (resilience, error handling)
- Performance benchmarks meet thresholds
- Multi-agent coordination functional

### ✅ Ready for Open Source Release
- Comprehensive test coverage (90%+ pass rate)
- Security validation complete
- Documentation comprehensive
- User-friendly validation tools
- Production deployment guides

## 🚨 Common Issues & Solutions

### Installation Issues
```bash
# Missing dependencies
pip install -r mcp_requirements.txt

# Path issues
python agent_forge_tests/examples/quick_start.py --path /path/to/agent-forge

# Permission issues (Unix)
chmod 644 mcp_server.py mcp_auto_discovery.py
```

### Security Issues
```bash
# Remove sensitive data from config files
# Use environment variables for credentials
export NMKR_API_KEY="your_api_key_here"

# Fix file permissions  
chmod 644 *.py  # Remove world-write permissions
```

### Performance Issues
```bash
# Monitor memory usage
python tests/mcp/test_mcp_performance_benchmarks.py

# Check agent discovery performance
python -c "from mcp_auto_discovery import AgentDiscovery; print(AgentDiscovery().discover_agents())"
```

## 📞 Support & Contributions

### Getting Help
- **Documentation**: See `agent_forge_tests/documentation/`
- **Issues**: Check troubleshooting guide first
- **Community**: Agent Forge community forums
- **Security**: Report security issues privately

### Contributing Tests
```bash
# Add new test categories
mkdir tests/my_new_category/
cp agent_forge_tests/templates/basic_test.py tests/my_new_category/

# Follow existing patterns
# - Use descriptive test names
# - Include comprehensive assertions
# - Add proper error handling
# - Document test purpose

# Submit PR with:
# - Test description
# - Expected pass/fail criteria  
# - Integration with test_runner.py
```

## 🏆 Test Quality Standards

### ✅ Required for All Tests
- **Clear Purpose**: Each test has a specific validation target
- **Comprehensive Assertions**: Multiple validation points per test
- **Error Handling**: Graceful handling of all failure modes
- **Documentation**: Clear docstrings and comments
- **Performance**: Tests complete within reasonable time limits
- **Reliability**: Tests pass consistently across environments

### ✅ Security Test Standards
- **No Credential Exposure**: Tests never expose real credentials
- **Input Validation**: All user inputs validated for malicious content
- **Permission Enforcement**: File system and network access properly restricted
- **Error Message Safety**: Sensitive data never appears in error messages

### ✅ Production Readiness Standards
- **Real-World Scenarios**: Tests reflect actual production usage patterns
- **Failure Recovery**: Validation of graceful degradation and recovery
- **Performance Thresholds**: Clear benchmarks for acceptable performance
- **Monitoring Integration**: Tests provide actionable monitoring metrics

---

## 🎉 Ready to Test?

Start with the quick validation:

```bash
python agent_forge_tests/examples/quick_start.py
```

Expected output for a healthy installation:
```
🚀 Agent Forge Quick Start Test Suite
==================================================
📁 Testing installation at: /path/to/agent_forge

🧪 Installation Structure...
   ✅ All required files found (0.00s)
🧪 Python Dependencies...
   ✅ All 4 dependencies available (0.00s)  
🧪 Agent Discovery...
   ✅ Discovered 8 agents (1.12s)
🧪 MCP Server Import...
   ✅ MCP server imported successfully: Agent Forge (0.58s)
🧪 Claude Desktop Config...
   ✅ Claude Desktop configuration is valid (0.00s)
🧪 Basic Security...
   ✅ Basic security checks passed (0.00s)

==================================================
🎯 QUICK START TEST RESULTS
==================================================
Total Tests: 6
Passed: 6
Failed: 0
Success Rate: 100.0%
Total Duration: 1.70s

🎉 ALL TESTS PASSED!
✅ Agent Forge is ready for Claude Desktop integration!
```

**Agent Forge Testing Framework - Making AI agents production-ready! 🚀**