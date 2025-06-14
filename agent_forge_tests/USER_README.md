# 🚀 Agent Forge Testing Framework - User Guide

**Welcome to Agent Forge!** This testing framework helps you validate your Agent Forge installation and ensure it's ready for use with Claude Desktop.

## 🎯 Quick Start (2 minutes)

### Step 1: Test Your Installation
```bash
# Navigate to your Agent Forge directory
cd /path/to/agent_forge

# Run quick validation (recommended for most users)
python agent_forge_tests/examples/quick_start.py
```

**Expected Output:**
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

🎉 ALL TESTS PASSED!
✅ Agent Forge is ready for Claude Desktop integration!
```

### Step 2: Set Up Claude Desktop
If all tests pass, follow these steps:

1. **Copy Configuration**:
   ```bash
   # Copy the example config to Claude Desktop
   cp claude_desktop_config_example.json ~/.config/Claude/claude_desktop_config.json
   ```

2. **Update Paths**: Edit the config file to use your actual Agent Forge path
3. **Restart Claude Desktop**
4. **Test**: Ask Claude "Can you help me navigate to example.com?"

## 🔧 Advanced Validation Options

### Command Line Interface
```bash
# Basic validation (fastest)
python -m agent_forge_tests.cli.validate

# Comprehensive validation (for developers)
python -m agent_forge_tests.cli.validate --comprehensive

# MCP integration only
python -m agent_forge_tests.cli.validate --mcp-only

# Security validation only  
python -m agent_forge_tests.cli.validate --security-only

# Save results to file
python -m agent_forge_tests.cli.validate --output my_results.json
```

### Python API
```python
from agent_forge_tests import QuickStartTestSuite, AgentForgeValidator

# Quick validation for end users
suite = QuickStartTestSuite()
results = suite.run_all_tests()

if results.all_passed:
    print("✅ Ready for Claude Desktop!")
else:
    print(f"❌ Issues found: {results.summary}")

# Detailed validation for troubleshooting
validator = AgentForgeValidator()
detailed_results = validator.run_comprehensive_validation()
```

## 🛠️ What Gets Tested

### ✅ Installation Structure
- Required files (mcp_server.py, agents/, etc.)
- Directory organization
- Configuration files

### ✅ Dependencies  
- Python packages (fastmcp, mcp, aiohttp, etc.)
- Version compatibility
- Import functionality

### ✅ Agent Discovery
- Agent detection and loading
- Expected agents (page_scraper, data_compiler, etc.)
- Agent functionality

### ✅ MCP Integration
- MCP server functionality  
- Tool registration
- Claude Desktop compatibility

### ✅ Security Basics
- Configuration safety
- File permissions
- Credential protection

### ✅ Performance
- Response times
- Memory usage
- Startup performance

## ❌ Common Issues & Solutions

### Issue: "Agent Forge installation not found"
**Solution:**
```bash
# Run from your Agent Forge directory
cd /path/to/your/agent_forge

# Or specify path manually
python agent_forge_tests/examples/quick_start.py --path /path/to/agent_forge
```

### Issue: "Missing dependencies"
**Solution:**
```bash
# Install required packages
pip install -r mcp_requirements.txt

# Or install individual packages
pip install fastmcp mcp aiohttp requests
```

### Issue: "No agents discovered"
**Solution:**
```bash
# Check agents directory exists
ls agents/

# Verify agent structure
python -c "from mcp_auto_discovery import AgentDiscovery; print(AgentDiscovery().discover_agents())"
```

### Issue: "MCP server import failed"
**Solution:**
```bash
# Test MCP server syntax
python -m py_compile mcp_server.py

# Check for import errors
python -c "from mcp_server import mcp; print('Success!')"
```

### Issue: "Security issues found"
**Solution:**
```bash
# Fix file permissions (Unix/Mac)
chmod 644 *.py

# Remove sensitive data from configs
# Use environment variables for API keys
export NMKR_API_KEY="your_key_here"
```

## 📋 Test Results Interpretation

### 🎉 All Tests Passed (Success Rate: 100%)
- ✅ **Ready for Production**: Your installation is complete and secure
- ✅ **Claude Desktop Ready**: MCP integration will work properly
- ✅ **Next Step**: Configure Claude Desktop and start using Agent Forge

### ⚠️ Some Tests Failed (Success Rate: 80-99%)
- 🔧 **Minor Issues**: Usually configuration or permission problems
- 🔧 **Action Required**: Fix the specific issues mentioned
- 🔧 **Still Usable**: Core functionality likely works, but not optimal

### ❌ Many Tests Failed (Success Rate: <80%)
- 🚨 **Major Issues**: Installation incomplete or corrupted
- 🚨 **Action Required**: Reinstall or fix major configuration problems
- 🚨 **Not Ready**: Do not use with Claude Desktop until fixed

## 🎯 For Different User Types

### 🏠 Home Users
```bash
# Quick validation is perfect for you
python agent_forge_tests/examples/quick_start.py

# If it passes, you're ready to use Agent Forge!
```

### 💼 Business Users
```bash
# Run comprehensive validation
python -m agent_forge_tests.cli.validate --comprehensive

# Also run security validation
python -m agent_forge_tests.cli.validate --security-only
```

### 👨‍💻 Developers
```bash
# Run all test suites
python test_runner.py

# Run specific categories
python tests/security/test_credential_security.py
python tests/integration/test_failure_scenarios.py
python tests/integration/test_agent_coordination.py
```

### 🏢 Enterprise Users
```bash
# Complete validation with documentation
python -m agent_forge_tests.cli.validate --comprehensive --output enterprise_validation.json

# Security audit
python tests/security/test_credential_security.py

# Performance benchmarking
python tests/mcp/test_mcp_performance_benchmarks.py
```

## 🔧 Custom Testing

### Create Your Own Tests
```python
from agent_forge_tests.templates import BasicAgentTest

class MyCustomTest(BasicAgentTest):
    def test_my_specific_need(self):
        # Test your specific requirements
        agents = self.discover_agents()
        self.assertIn('my_required_agent', agents)
        
    def test_my_workflow(self):
        # Test your specific workflow
        result = self.run_agent_operation('page_scraper', {
            'url': 'https://my-website.com'
        })
        self.assertTrue(result['success'])

# Run your custom test
if __name__ == '__main__':
    import unittest
    unittest.main()
```

### Use Test Templates
Available templates in `agent_forge_tests/templates/`:
- **BasicAgentTest**: General agent testing
- **MCPIntegrationTest**: MCP-specific testing
- **SecurityTest**: Security validation
- **PerformanceTest**: Performance benchmarking

## 📊 Understanding Performance

### Good Performance Indicators
- **Agent Discovery**: < 3 seconds
- **MCP Server Startup**: < 2 seconds  
- **Memory Usage**: < 500 MB
- **Tool Execution**: < 5 seconds

### Performance Issues
If tests show poor performance:
```bash
# Check system resources
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"

# Run performance benchmarks
python tests/mcp/test_mcp_performance_benchmarks.py
```

## 🆘 Getting Help

### Self-Diagnosis
```bash
# Run comprehensive validation for detailed diagnostics
python -m agent_forge_tests.cli.validate --comprehensive

# Check logs for errors
python agent_forge_tests/examples/quick_start.py --verbose
```

### Documentation
- **Testing Guide**: `agent_forge_tests/documentation/testing_guide.md`
- **Security Guidelines**: `agent_forge_tests/documentation/security_guidelines.md`
- **Troubleshooting**: `agent_forge_tests/documentation/troubleshooting.md`

### Community Support
- **GitHub Issues**: Report bugs and ask questions
- **Community Forums**: Get help from other users
- **Documentation**: Comprehensive guides and examples

## 🔒 Security Best Practices

### ✅ Do's
- ✅ Use environment variables for API keys
- ✅ Keep file permissions restrictive (644 for scripts)
- ✅ Run security validation regularly
- ✅ Update dependencies regularly

### ❌ Don'ts  
- ❌ Store API keys in configuration files
- ❌ Use world-writable permissions
- ❌ Skip security validation
- ❌ Ignore security warnings

## 🎉 Success! What's Next?

Once all tests pass:

### 1. **Configure Claude Desktop**
```bash
# Copy config to Claude Desktop
cp claude_desktop_config_example.json ~/.config/Claude/claude_desktop_config.json

# Edit paths to match your installation
nano ~/.config/Claude/claude_desktop_config.json
```

### 2. **Test Integration**
- Restart Claude Desktop
- Ask: "Can you help me navigate to example.com?"
- Expected: Claude will use Agent Forge to help you

### 3. **Explore Capabilities**
- Web navigation and scraping
- Data extraction and compilation
- Blockchain integration (NMKR)
- Multi-agent workflows

### 4. **Monitor Performance**
- Run tests periodically
- Monitor resource usage
- Update when new versions available

---

## 📞 Quick Reference

### Essential Commands
```bash
# Quick validation (most users)
python agent_forge_tests/examples/quick_start.py

# CLI validation with options
python -m agent_forge_tests.cli.validate [--comprehensive|--mcp-only|--security-only]

# Full test suite (developers)
python test_runner.py
```

### Expected Results
- **Success Rate**: 90-100% for production use
- **Duration**: 2-15 seconds depending on test type
- **Output**: Clear pass/fail status with specific issue details

### File Locations
- **Quick Start**: `agent_forge_tests/examples/quick_start.py`
- **CLI Tool**: `agent_forge_tests/cli/validate.py`
- **Templates**: `agent_forge_tests/templates/`
- **Documentation**: `agent_forge_tests/documentation/`

**Happy testing! 🚀 Agent Forge is ready to make your AI workflows more powerful.**