#!/usr/bin/env python3
"""
Agent Forge Quick Start Test Suite
==================================

Ready-to-run test suite for validating your Agent Forge installation.

This suite provides:
- Basic functionality validation
- MCP integration verification
- Claude Desktop compatibility checks
- Essential security validation

Usage:
------
```bash
# Run quick validation
python agent_forge_tests/examples/quick_start.py

# Run with detailed output
python agent_forge_tests/examples/quick_start.py --verbose

# Save results to file
python agent_forge_tests/examples/quick_start.py --output results.json
```

Python API:
-----------
```python
from agent_forge_tests.examples.quick_start import QuickStartTestSuite

# Run basic validation
suite = QuickStartTestSuite()
results = suite.run_all_tests()

if results.all_passed:
    print("✅ Ready for Claude Desktop!")
else:
    print("❌ Issues found:", results.summary)
```
"""

import os
import sys
import json
import time
import unittest
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass 
class TestResult:
    """Result of a test execution."""
    test_name: str
    passed: bool
    message: str
    duration_seconds: float
    details: Optional[Dict[str, Any]] = None


@dataclass
class TestSuiteResults:
    """Results from running the test suite."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_duration: float
    all_passed: bool
    results: List[TestResult]
    
    @property
    def success_rate(self) -> float:
        return (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
    
    @property
    def summary(self) -> str:
        return f"{self.passed_tests}/{self.total_tests} tests passed ({self.success_rate:.1f}%)"


class QuickStartTestSuite:
    """Quick start test suite for Agent Forge validation."""
    
    def __init__(self, agent_forge_path: Optional[str] = None):
        """
        Initialize test suite.
        
        Args:
            agent_forge_path: Path to Agent Forge installation
        """
        self.agent_forge_path = self._detect_path(agent_forge_path)
        self.results: List[TestResult] = []
        
    def _detect_path(self, provided_path: Optional[str]) -> Path:
        """Detect Agent Forge installation path."""
        if provided_path:
            return Path(provided_path)
            
        # Try current directory and parents
        current = Path.cwd()
        for path in [current] + list(current.parents):
            if (path / 'mcp_server.py').exists():
                return path
                
        raise FileNotFoundError("Agent Forge installation not found")
    
    def _run_test(self, test_name: str, test_func) -> TestResult:
        """Run a single test and record results."""
        print(f"🧪 {test_name}...")
        start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start_time
            
            if isinstance(result, dict):
                passed = result.get('passed', False)
                message = result.get('message', 'Test completed')
                details = result.get('details')
            else:
                passed = bool(result)
                message = 'Test passed' if passed else 'Test failed'
                details = None
                
            test_result = TestResult(
                test_name=test_name,
                passed=passed,
                message=message,
                duration_seconds=duration,
                details=details
            )
            
            status = "✅" if passed else "❌"
            print(f"   {status} {message} ({duration:.2f}s)")
            
            return test_result
            
        except Exception as e:
            duration = time.time() - start_time
            test_result = TestResult(
                test_name=test_name,
                passed=False,
                message=f"Test error: {str(e)}",
                duration_seconds=duration,
                details={'exception': str(e)}
            )
            
            print(f"   ❌ {test_result.message} ({duration:.2f}s)")
            return test_result
    
    def test_installation_structure(self) -> Dict[str, Any]:
        """Test basic installation structure."""
        required_files = [
            'mcp_server.py',
            'mcp_auto_discovery.py',
            'claude_desktop_config_example.json'
        ]
        
        missing_files = []
        for file_name in required_files:
            if not (self.agent_forge_path / file_name).exists():
                missing_files.append(file_name)
        
        if missing_files:
            return {
                'passed': False,
                'message': f"Missing files: {', '.join(missing_files)}",
                'details': {'missing_files': missing_files}
            }
        
        return {
            'passed': True,
            'message': 'All required files found',
            'details': {'checked_files': required_files}
        }
    
    def test_python_dependencies(self) -> Dict[str, Any]:
        """Test Python dependencies."""
        import importlib.util
        
        required_packages = ['fastmcp', 'mcp', 'aiohttp', 'requests']
        missing_packages = []
        
        for package in required_packages:
            spec = importlib.util.find_spec(package)
            if spec is None:
                missing_packages.append(package)
        
        if missing_packages:
            return {
                'passed': False,
                'message': f"Missing packages: {', '.join(missing_packages)}",
                'details': {'missing_packages': missing_packages}
            }
        
        return {
            'passed': True,
            'message': f'All {len(required_packages)} dependencies available',
            'details': {'packages': required_packages}
        }
    
    def test_agent_discovery(self) -> Dict[str, Any]:
        """Test agent discovery functionality."""
        # Add path to sys.path temporarily
        original_path = sys.path.copy()
        try:
            sys.path.insert(0, str(self.agent_forge_path))
            
            from mcp_auto_discovery import AgentDiscovery
            
            discovery = AgentDiscovery()
            agents = discovery.discover_agents()
            
            if not agents or len(agents) == 0:
                return {
                    'passed': False,
                    'message': 'No agents discovered',
                    'details': {'agents_found': 0}
                }
            
            return {
                'passed': True,
                'message': f'Discovered {len(agents)} agents',
                'details': {
                    'agents_found': len(agents),
                    'agent_names': list(agents.keys())
                }
            }
            
        finally:
            sys.path = original_path
    
    def test_mcp_server_import(self) -> Dict[str, Any]:
        """Test MCP server import."""
        original_path = sys.path.copy()
        try:
            sys.path.insert(0, str(self.agent_forge_path))
            
            from mcp_server import mcp
            
            # Check basic server attributes
            server_name = getattr(mcp, 'name', 'Unknown')
            
            return {
                'passed': True,
                'message': f'MCP server imported successfully: {server_name}',
                'details': {'server_name': server_name}
            }
            
        finally:
            sys.path = original_path
    
    def test_claude_desktop_config(self) -> Dict[str, Any]:
        """Test Claude Desktop configuration."""
        config_file = self.agent_forge_path / 'claude_desktop_config_example.json'
        
        if not config_file.exists():
            return {
                'passed': False,
                'message': 'Claude Desktop config file not found'
            }
        
        try:
            config_data = json.loads(config_file.read_text())
            
            # Basic validation
            if 'mcpServers' not in config_data:
                return {
                    'passed': False,
                    'message': 'mcpServers section missing from config'
                }
            
            if 'agent-forge' not in config_data['mcpServers']:
                return {
                    'passed': False,
                    'message': 'agent-forge server not configured'
                }
            
            return {
                'passed': True,
                'message': 'Claude Desktop configuration is valid',
                'details': {'servers_configured': len(config_data['mcpServers'])}
            }
            
        except json.JSONDecodeError as e:
            return {
                'passed': False,
                'message': f'Invalid JSON in config: {e}'
            }
    
    def test_basic_security(self) -> Dict[str, Any]:
        """Basic security validation."""
        security_checks = []
        
        # Check that no credentials are in config files
        config_file = self.agent_forge_path / 'claude_desktop_config_example.json'
        if config_file.exists():
            config_content = config_file.read_text().lower()
            sensitive_patterns = ['api_key', 'password', 'secret', 'token']
            
            found_patterns = [p for p in sensitive_patterns if p in config_content]
            if found_patterns:
                security_checks.append(f"Sensitive patterns in config: {found_patterns}")
        
        # Check file permissions (Unix-like systems)
        if hasattr(os, 'stat'):
            sensitive_files = ['mcp_server.py', 'mcp_auto_discovery.py']
            for file_name in sensitive_files:
                file_path = self.agent_forge_path / file_name
                if file_path.exists():
                    file_stat = file_path.stat()
                    # Check if file is readable by others (world-readable)
                    if file_stat.st_mode & 0o044:  # others read permission
                        security_checks.append(f"{file_name} is world-readable")
        
        if security_checks:
            return {
                'passed': False,
                'message': f'Security issues: {"; ".join(security_checks)}',
                'details': {'issues': security_checks}
            }
        
        return {
            'passed': True,
            'message': 'Basic security checks passed',
            'details': {'checks_performed': ['credential_exposure', 'file_permissions']}
        }
    
    def run_all_tests(self, verbose: bool = False) -> TestSuiteResults:
        """Run all quick start tests."""
        print("🚀 Agent Forge Quick Start Test Suite")
        print("=" * 50)
        print(f"📁 Testing installation at: {self.agent_forge_path}")
        print()
        
        # Define test methods
        tests = [
            ("Installation Structure", self.test_installation_structure),
            ("Python Dependencies", self.test_python_dependencies),
            ("Agent Discovery", self.test_agent_discovery),
            ("MCP Server Import", self.test_mcp_server_import),
            ("Claude Desktop Config", self.test_claude_desktop_config),
            ("Basic Security", self.test_basic_security)
        ]
        
        # Run tests
        start_time = time.time()
        self.results = []
        
        for test_name, test_func in tests:
            result = self._run_test(test_name, test_func)
            self.results.append(result)
        
        total_duration = time.time() - start_time
        
        # Calculate summary
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = len(self.results) - passed_tests
        all_passed = failed_tests == 0
        
        # Create results object
        suite_results = TestSuiteResults(
            total_tests=len(self.results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_duration=total_duration,
            all_passed=all_passed,
            results=self.results
        )
        
        # Print summary
        print("\n" + "=" * 50)
        print("🎯 QUICK START TEST RESULTS")
        print("=" * 50)
        print(f"Total Tests: {suite_results.total_tests}")
        print(f"Passed: {suite_results.passed_tests}")
        print(f"Failed: {suite_results.failed_tests}")
        print(f"Success Rate: {suite_results.success_rate:.1f}%")
        print(f"Total Duration: {suite_results.total_duration:.2f}s")
        
        if suite_results.all_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Agent Forge is ready for Claude Desktop integration!")
            print("\n📋 Next Steps:")
            print("   1. Copy claude_desktop_config_example.json to your Claude Desktop config")
            print("   2. Update the file paths in the configuration")
            print("   3. Restart Claude Desktop")
            print("   4. Test with: 'Can you help me navigate to example.com?'")
        else:
            print(f"\n⚠️ {suite_results.failed_tests} TEST(S) FAILED")
            print("❌ Please fix the issues before using with Claude Desktop")
            
            if verbose:
                print("\nFailed Tests:")
                for result in self.results:
                    if not result.passed:
                        print(f"   ❌ {result.test_name}: {result.message}")
                        if result.details:
                            print(f"      Details: {result.details}")
        
        return suite_results


def main():
    """Command-line interface for quick start tests."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Agent Forge Quick Start Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quick_start.py                    # Run basic tests
  python quick_start.py --verbose          # Show detailed output
  python quick_start.py --output results.json  # Save results to file
  python quick_start.py --path /path/to/agent_forge  # Custom installation path
        """
    )
    
    parser.add_argument(
        "--path",
        help="Path to Agent Forge installation (auto-detect if not specified)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output for failed tests"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save results to JSON file"
    )
    
    args = parser.parse_args()
    
    try:
        # Run tests
        suite = QuickStartTestSuite(args.path)
        results = suite.run_all_tests(verbose=args.verbose)
        
        # Save output if requested
        if args.output:
            output_data = {
                "summary": {
                    "total_tests": results.total_tests,
                    "passed_tests": results.passed_tests,
                    "failed_tests": results.failed_tests,
                    "success_rate": results.success_rate,
                    "all_passed": results.all_passed,
                    "total_duration": results.total_duration
                },
                "test_results": [
                    {
                        "test_name": r.test_name,
                        "passed": r.passed,
                        "message": r.message,
                        "duration_seconds": r.duration_seconds,
                        "details": r.details
                    }
                    for r in results.results
                ]
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n💾 Results saved to {args.output}")
        
        # Exit with appropriate code
        sys.exit(0 if results.all_passed else 1)
        
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Tip: Run this from your Agent Forge directory or use --path")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()