"""
Agent Forge Testing Framework
============================

A comprehensive testing framework for Agent Forge MCP integration and production deployments.

This package provides:
- Ready-to-use test templates for common scenarios
- Validation tools for Agent Forge installations  
- Security testing utilities
- Performance benchmarking tools
- Multi-agent coordination tests

Quick Start:
-----------
```python
from agent_forge_tests import AgentForgeValidator

# Validate your Agent Forge installation
validator = AgentForgeValidator()
results = validator.run_comprehensive_validation()

if results.all_passed:
    print("✅ Agent Forge is ready for production!")
else:
    print("⚠️ Issues found:", results.failures)
```

Testing Categories:
------------------
- **MCP Integration**: Claude Desktop integration tests
- **Security**: Credential handling, input validation, permission checks
- **Performance**: Load testing, memory management, response times
- **Reliability**: Failure scenarios, recovery mechanisms, error handling
- **Coordination**: Multi-agent workflows, resource management
- **Compliance**: Production readiness, best practices validation

For detailed documentation, see: https://docs.agent-forge.ai/testing
"""

__version__ = "1.0.0"
__author__ = "Agent Forge Team"

# Import main validation classes
from .validators.installation_validator import AgentForgeValidator
from .validators.mcp_validator import MCPIntegrationValidator
from .validators.security_validator import SecurityValidator
from .validators.performance_validator import PerformanceValidator

# Import test templates
from .templates.basic_test import BasicAgentTest
from .templates.mcp_test import MCPIntegrationTest
from .templates.security_test import SecurityTest
from .templates.performance_test import PerformanceTest

# Import example test suites
from .examples.quick_start import QuickStartTestSuite
from .examples.production_readiness import ProductionReadinessTestSuite

__all__ = [
    # Validators
    'AgentForgeValidator',
    'MCPIntegrationValidator', 
    'SecurityValidator',
    'PerformanceValidator',
    
    # Templates
    'BasicAgentTest',
    'MCPIntegrationTest',
    'SecurityTest', 
    'PerformanceTest',
    
    # Examples
    'QuickStartTestSuite',
    'ProductionReadinessTestSuite'
]