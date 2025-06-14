"""
Agent Forge Test Templates
=========================

Ready-to-use test templates for creating custom Agent Forge tests.

Available Templates:
- BasicAgentTest: Base class for simple agent tests
- MCPIntegrationTest: Template for MCP integration tests
- SecurityTest: Template for security validation tests
- PerformanceTest: Template for performance testing
"""

from .basic_test import BasicAgentTest
from .mcp_test import MCPIntegrationTest
from .security_test import SecurityTest
from .performance_test import PerformanceTest

__all__ = [
    'BasicAgentTest',
    'MCPIntegrationTest', 
    'SecurityTest',
    'PerformanceTest'
]