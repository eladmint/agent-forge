# Contributing to Agent Forge

We welcome contributions to Agent Forge! This document provides guidelines for contributing to the project.

## 🎯 **How to Contribute**

### **🐛 Bug Reports**
- Use the GitHub issue tracker
- Include detailed reproduction steps
- Provide environment information
- Run the testing framework to validate the issue

### **✨ Feature Requests**
- Submit feature requests via GitHub issues
- Describe the use case and expected behavior
- Consider if the feature fits the framework's mission

### **🔧 Code Contributions**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the comprehensive test suite: `python -m agent_forge_tests.cli.validate --comprehensive`
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 🧪 **Testing Requirements**

### **Before Submitting**
- **Run Full Test Suite**: `python -m agent_forge_tests.cli.validate --comprehensive`
- **Security Tests**: Ensure all security tests pass
- **Performance Tests**: Validate no performance regressions
- **MCP Integration**: Test MCP server functionality if applicable

### **Test Coverage**
- Maintain 90%+ test coverage for new code
- Add security tests for any credential handling
- Include production resilience tests for critical paths
- Add multi-agent coordination tests for agent interactions

## 📝 **Code Standards**

### **Code Quality**
- Follow Python PEP 8 style guidelines
- Use type hints for all functions
- Include comprehensive docstrings
- Ensure code is formatted with `black` and linted with `ruff`

### **Security-First Development**
- Never commit credentials or API keys
- Use environment variables for sensitive configuration
- Validate all user inputs
- Follow secure coding practices

### **Documentation**
- Update relevant documentation for any changes
- Include examples for new features
- Update API references for interface changes
- Maintain the testing framework documentation

## 🏗️ **Development Setup**

### **Prerequisites**
- Python 3.8+
- pip or poetry for dependency management

### **Setup Steps**
1. Clone your fork: `git clone https://github.com/YOUR_USERNAME/agent-forge.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Install development dependencies: `pip install -r mcp_requirements.txt`
4. Run initial validation: `python -m agent_forge_tests.examples.quick_start`

### **Testing Your Setup**
```bash
# Quick validation (5 minutes)
python -m agent_forge_tests.examples.quick_start

# Comprehensive validation (15-20 minutes)
python -m agent_forge_tests.cli.validate --comprehensive

# Security-only tests
python -m agent_forge_tests.cli.validate --security-only

# MCP integration tests
python -m agent_forge_tests.cli.validate --mcp-only
```

## 🎨 **Architecture Guidelines**

### **Framework Principles**
- **Production-Ready**: All code must be enterprise-grade
- **Security-First**: Security considerations in every component
- **MCP Integration**: Maintain Claude Desktop compatibility
- **Modularity**: Components should be independently testable
- **Documentation**: Comprehensive documentation for all features

### **Agent Development**
- Extend `BaseAgent` for all new agents
- Implement proper async patterns
- Include comprehensive error handling
- Add appropriate logging and monitoring
- Follow the established agent patterns

## 📚 **Documentation Guidelines**

### **Types of Documentation**
- **API Documentation**: Complete function and class references
- **User Guides**: Step-by-step tutorials and examples
- **Architecture Docs**: System design and patterns
- **Testing Docs**: Validation and testing procedures

### **Documentation Standards**
- Use clear, concise language
- Include practical examples
- Maintain consistency with existing docs
- Update multiple related documents when making changes

## 🚀 **Release Process**

### **Version Management**
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version in relevant files
- Create release notes highlighting changes
- Tag releases in git

### **Quality Gates**
- All tests must pass (182+ test suite)
- Security validation required
- Performance benchmarks maintained
- Documentation updated
- MCP integration validated

## 🤝 **Community Guidelines**

### **Code of Conduct**
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

### **Getting Help**
- Check existing documentation first
- Search GitHub issues for similar problems
- Run the testing framework for diagnostic information
- Provide detailed context when asking questions

## 🏆 **Recognition**

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributor graphs
- Project documentation

Thank you for contributing to Agent Forge! 🎉

---

**Last Updated:** June 14, 2025  
**Framework Version:** 1.0  
**Testing Framework:** 182+ Tests Complete