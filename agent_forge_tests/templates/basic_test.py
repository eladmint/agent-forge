#!/usr/bin/env python3
"""
Basic Agent Test Template
========================

Base template for creating custom Agent Forge tests.

Usage:
------
```python
from agent_forge_tests.templates import BasicAgentTest

class MyCustomTest(BasicAgentTest):
    def test_my_agent_feature(self):
        # Test your agent functionality
        result = self.run_agent_operation('my_agent', {'param': 'value'})
        self.assertTrue(result['success'])
        
    def test_my_validation(self):
        # Test custom validation logic
        data = self.get_test_data()
        self.validate_agent_response(data)

# Run your test
suite = unittest.TestLoader().loadTestsFromTestCase(MyCustomTest)
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
```
"""

import os
import sys
import unittest
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, patch


class BasicAgentTest(unittest.TestCase):
    """Base class for Agent Forge tests."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - called once before all tests."""
        cls.agent_forge_path = cls._detect_agent_forge_path()
        cls._add_agent_forge_to_path()
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test class - called once after all tests."""
        cls._remove_agent_forge_from_path()
    
    def setUp(self):
        """Set up individual test - called before each test method."""
        self.test_start_time = time.time()
        
    def tearDown(self):
        """Clean up individual test - called after each test method."""
        self.test_duration = time.time() - self.test_start_time
    
    @classmethod
    def _detect_agent_forge_path(cls) -> Path:
        """Detect Agent Forge installation path."""
        current = Path.cwd()
        
        # Check current directory and parents for mcp_server.py
        for path in [current] + list(current.parents):
            if (path / 'mcp_server.py').exists():
                return path
                
        # Check common installation paths
        common_paths = [
            Path.home() / 'agent_forge',
            Path('/opt/agent_forge'),
            Path('/usr/local/agent_forge')
        ]
        
        for path in common_paths:
            if path.exists() and (path / 'mcp_server.py').exists():
                return path
                
        raise FileNotFoundError(
            "Agent Forge installation not found. "
            "Ensure mcp_server.py exists in your Agent Forge directory."
        )
    
    @classmethod
    def _add_agent_forge_to_path(cls):
        """Add Agent Forge to Python path."""
        agent_forge_str = str(cls.agent_forge_path)
        if agent_forge_str not in sys.path:
            sys.path.insert(0, agent_forge_str)
            cls._path_added = True
        else:
            cls._path_added = False
    
    @classmethod 
    def _remove_agent_forge_from_path(cls):
        """Remove Agent Forge from Python path."""
        if hasattr(cls, '_path_added') and cls._path_added:
            agent_forge_str = str(cls.agent_forge_path)
            if agent_forge_str in sys.path:
                sys.path.remove(agent_forge_str)
    
    def get_agent_forge_path(self) -> Path:
        """Get Agent Forge installation path."""
        return self.agent_forge_path
    
    def import_agent_module(self, module_name: str):
        """Import an Agent Forge module safely."""
        try:
            return __import__(module_name)
        except ImportError as e:
            self.fail(f"Failed to import {module_name}: {e}")
    
    def load_agent_discovery(self):
        """Load the agent discovery module."""
        try:
            from mcp_auto_discovery import AgentDiscovery
            return AgentDiscovery()
        except ImportError as e:
            self.fail(f"Failed to import AgentDiscovery: {e}")
    
    def load_mcp_server(self):
        """Load the MCP server module."""
        try:
            from mcp_server import mcp
            return mcp
        except ImportError as e:
            self.fail(f"Failed to import MCP server: {e}")
    
    def discover_agents(self) -> Dict[str, Any]:
        """Discover available agents."""
        discovery = self.load_agent_discovery()
        agents = discovery.discover_agents()
        
        self.assertIsInstance(agents, dict, "Agent discovery should return a dictionary")
        self.assertGreater(len(agents), 0, "Should discover at least one agent")
        
        return agents
    
    def run_agent_operation(self, agent_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock an agent operation for testing.
        
        Override this method in your test class to implement actual agent operations.
        """
        # Default mock implementation
        return {
            'success': True,
            'agent': agent_name,
            'parameters': parameters,
            'result': f'Mock result for {agent_name}',
            'timestamp': time.time()
        }
    
    def validate_agent_response(self, response: Dict[str, Any]) -> None:
        """Validate a standard agent response structure."""
        required_fields = ['success', 'agent']
        
        for field in required_fields:
            self.assertIn(field, response, f"Response missing required field: {field}")
        
        self.assertIsInstance(response['success'], bool, "success field should be boolean")
        self.assertIsInstance(response['agent'], str, "agent field should be string")
        
        if response['success']:
            # For successful responses, expect some result
            self.assertIn('result', response, "Successful response should have result field")
        else:
            # For failed responses, expect error information
            self.assertIn('error', response, "Failed response should have error field")
    
    def validate_mcp_tool_response(self, response: Dict[str, Any]) -> None:
        """Validate an MCP tool response structure."""
        # MCP tool responses should have specific structure
        self.assertIsInstance(response, dict, "MCP tool response should be dictionary")
        
        # Check for standard MCP response fields
        if 'content' in response:
            self.assertIsInstance(response['content'], list, "content should be list")
        
        if 'isError' in response:
            self.assertIsInstance(response['isError'], bool, "isError should be boolean")
    
    def create_test_parameters(self, **kwargs) -> Dict[str, Any]:
        """Create standardized test parameters."""
        default_params = {
            'test_mode': True,
            'timeout': 30,
            'retry_count': 3
        }
        default_params.update(kwargs)
        return default_params
    
    def assert_agent_exists(self, agent_name: str) -> None:
        """Assert that a specific agent exists."""
        agents = self.discover_agents()
        self.assertIn(agent_name, agents, f"Agent '{agent_name}' not found in discovered agents")
    
    def assert_mcp_server_functional(self) -> None:
        """Assert that MCP server is functional."""
        mcp = self.load_mcp_server()
        
        # Check basic server attributes
        self.assertTrue(hasattr(mcp, 'name'), "MCP server should have name attribute")
        
        # Check for tools if available
        if hasattr(mcp, '_tools') or hasattr(mcp, 'tools'):
            tools_attr = getattr(mcp, '_tools', getattr(mcp, 'tools', None))
            if tools_attr:
                self.assertGreater(len(tools_attr), 0, "MCP server should have registered tools")
    
    def measure_performance(self, operation_func, *args, **kwargs) -> Dict[str, Any]:
        """Measure performance of an operation."""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            result = operation_func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        return {
            'success': success,
            'result': result,
            'error': error,
            'duration_seconds': end_time - start_time,
            'memory_delta_mb': end_memory - start_memory,
            'start_memory_mb': start_memory,
            'end_memory_mb': end_memory
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            # Fallback if psutil not available
            import resource
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # Convert to MB
    
    def create_mock_response(self, success: bool = True, **kwargs) -> Dict[str, Any]:
        """Create a mock response for testing."""
        response = {
            'success': success,
            'agent': 'test_agent',
            'timestamp': time.time()
        }
        
        if success:
            response.update({
                'result': 'Test operation successful',
                'data': kwargs.get('data', {})
            })
        else:
            response.update({
                'error': kwargs.get('error', 'Test operation failed'),
                'error_code': kwargs.get('error_code', 'TEST_ERROR')
            })
        
        response.update(kwargs)
        return response
    
    def skip_if_agent_missing(self, agent_name: str):
        """Skip test if specific agent is not available."""
        try:
            agents = self.discover_agents()
            if agent_name not in agents:
                self.skipTest(f"Agent '{agent_name}' not available")
        except Exception:
            self.skipTest(f"Could not check for agent '{agent_name}'")
    
    def skip_if_module_missing(self, module_name: str):
        """Skip test if specific module is not available."""
        try:
            __import__(module_name)
        except ImportError:
            self.skipTest(f"Module '{module_name}' not available")


# Example usage and test template
class ExampleAgentTest(BasicAgentTest):
    """Example test class showing how to use BasicAgentTest."""
    
    def test_agent_discovery(self):
        """Test that agent discovery works."""
        agents = self.discover_agents()
        self.assertIsInstance(agents, dict)
        self.assertGreater(len(agents), 0)
        
    def test_mcp_server_import(self):
        """Test that MCP server can be imported."""
        mcp = self.load_mcp_server()
        self.assertIsNotNone(mcp)
        
    def test_specific_agent_exists(self):
        """Test that a specific agent exists."""
        # Skip if page_scraper not available
        self.skip_if_agent_missing('page_scraper')
        
        # If we get here, agent exists
        agents = self.discover_agents()
        self.assertIn('page_scraper', agents)
    
    def test_mock_agent_operation(self):
        """Test a mock agent operation."""
        parameters = self.create_test_parameters(url='http://example.com')
        response = self.run_agent_operation('test_agent', parameters)
        
        self.validate_agent_response(response)
        self.assertTrue(response['success'])
    
    def test_performance_measurement(self):
        """Test performance measurement."""
        def test_operation():
            time.sleep(0.01)  # Simulate work
            return "operation complete"
        
        performance = self.measure_performance(test_operation)
        
        self.assertTrue(performance['success'])
        self.assertGreater(performance['duration_seconds'], 0)
        self.assertEqual(performance['result'], "operation complete")


if __name__ == '__main__':
    # Run the example tests
    unittest.main(verbosity=2)