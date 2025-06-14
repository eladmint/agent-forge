#!/usr/bin/env python3
"""
MCP Integration Validator
Specialized validation for Model Context Protocol (MCP) integration with Claude Desktop.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .installation_validator import ValidationResult, ValidationSummary


class MCPIntegrationValidator:
    """Specialized validator for MCP integration functionality."""
    
    def __init__(self, agent_forge_path: Optional[str] = None):
        """
        Initialize MCP validator.
        
        Args:
            agent_forge_path: Path to Agent Forge installation
        """
        self.agent_forge_path = Path(agent_forge_path) if agent_forge_path else self._detect_path()
        self.results: List[ValidationResult] = []
        
    def _detect_path(self) -> Path:
        """Auto-detect Agent Forge installation path."""
        current = Path.cwd()
        for path in [current] + list(current.parents):
            if (path / 'mcp_server.py').exists():
                return path
        raise FileNotFoundError("Agent Forge installation not found")
    
    def _add_result(self, passed: bool, message: str, details: Optional[Dict] = None, severity: str = "info"):
        """Add validation result."""
        self.results.append(ValidationResult(
            passed=passed,
            message=message,
            details=details,
            severity=severity
        ))
    
    def validate_mcp_server_functionality(self) -> None:
        """Validate MCP server core functionality."""
        print("🔌 Validating MCP server functionality...")
        
        try:
            # Add path temporarily for import
            sys.path.insert(0, str(self.agent_forge_path))
            
            # Test MCP server import
            from mcp_server import mcp
            
            # Validate server attributes
            server_name = getattr(mcp, 'name', None)
            if server_name:
                self._add_result(True, f"✅ MCP server name: {server_name}")
            else:
                self._add_result(False, "⚠️ MCP server name not defined", severity="warning")
            
            # Check for tools registration
            tools_found = 0
            tool_names = []
            
            # Try different ways to access tools
            if hasattr(mcp, '_tools'):
                tools_found = len(mcp._tools)
                tool_names = list(mcp._tools.keys()) if hasattr(mcp._tools, 'keys') else []
            elif hasattr(mcp, 'tools'):
                tools_found = len(mcp.tools)
                tool_names = list(mcp.tools.keys()) if hasattr(mcp.tools, 'keys') else []
            
            if tools_found > 0:
                self._add_result(
                    True, 
                    f"✅ MCP tools registered: {tools_found} tools",
                    details={"tool_count": tools_found, "tool_names": tool_names}
                )
            else:
                self._add_result(
                    False,
                    "❌ No MCP tools registered",
                    severity="error"
                )
                
        except ImportError as e:
            self._add_result(
                False,
                f"❌ Cannot import MCP server: {e}",
                severity="critical"
            )
        except Exception as e:
            self._add_result(
                False,
                f"❌ MCP server validation error: {e}",
                severity="error"
            )
        finally:
            # Clean up sys.path
            if str(self.agent_forge_path) in sys.path:
                sys.path.remove(str(self.agent_forge_path))
    
    def validate_agent_discovery_integration(self) -> None:
        """Validate agent discovery for MCP integration."""
        print("🤖 Validating agent discovery integration...")
        
        try:
            sys.path.insert(0, str(self.agent_forge_path))
            
            from mcp_auto_discovery import AgentDiscovery
            
            discovery = AgentDiscovery()
            agents = discovery.discover_agents()
            
            if isinstance(agents, dict) and agents:
                self._add_result(
                    True,
                    f"✅ Agent discovery successful: {len(agents)} agents",
                    details={"agent_count": len(agents), "agents": list(agents.keys())}
                )
                
                # Validate expected core agents
                expected_agents = [
                    'page_scraper',
                    'data_compiler', 
                    'enhanced_validation',
                    'external_site_scraper'
                ]
                
                found_expected = [agent for agent in expected_agents if agent in agents]
                missing_expected = [agent for agent in expected_agents if agent not in agents]
                
                if len(found_expected) >= 3:  # At least 3 of 4 expected agents
                    self._add_result(
                        True,
                        f"✅ Core agents found: {', '.join(found_expected)}"
                    )
                else:
                    self._add_result(
                        False,
                        f"⚠️ Missing core agents: {', '.join(missing_expected)}",
                        severity="warning"
                    )
                    
            else:
                self._add_result(
                    False,
                    "❌ Agent discovery failed: No agents found",
                    severity="error"
                )
                
        except Exception as e:
            self._add_result(
                False,
                f"❌ Agent discovery error: {e}",
                severity="error"
            )
        finally:
            if str(self.agent_forge_path) in sys.path:
                sys.path.remove(str(self.agent_forge_path))
    
    def validate_claude_desktop_configuration(self) -> None:
        """Validate Claude Desktop configuration for MCP."""
        print("🖥️ Validating Claude Desktop configuration...")
        
        config_file = self.agent_forge_path / 'claude_desktop_config_example.json'
        
        if not config_file.exists():
            self._add_result(
                False,
                "❌ claude_desktop_config_example.json not found",
                severity="error"
            )
            return
        
        try:
            config_data = json.loads(config_file.read_text())
            
            # Validate MCP servers section
            if 'mcpServers' not in config_data:
                self._add_result(
                    False,
                    "❌ mcpServers section missing",
                    severity="error"
                )
                return
            
            servers = config_data['mcpServers']
            
            # Check for agent-forge server configuration
            if 'agent-forge' not in servers:
                self._add_result(
                    False,
                    "❌ agent-forge server not configured",
                    severity="error"
                )
                return
            
            agent_forge_config = servers['agent-forge']
            
            # Validate required fields
            required_fields = ['command', 'args']
            missing_fields = [field for field in required_fields if field not in agent_forge_config]
            
            if missing_fields:
                self._add_result(
                    False,
                    f"❌ Missing configuration fields: {', '.join(missing_fields)}",
                    severity="error"
                )
            else:
                self._add_result(True, "✅ Required configuration fields present")
            
            # Validate command and args
            command = agent_forge_config.get('command', '')
            args = agent_forge_config.get('args', [])
            
            if 'python' in command.lower():
                self._add_result(True, "✅ Python command configured")
            else:
                self._add_result(
                    False,
                    f"⚠️ Unexpected command: {command}",
                    severity="warning"
                )
            
            if args and len(args) > 0:
                script_path = args[0]
                if 'mcp_server.py' in script_path:
                    self._add_result(True, "✅ MCP server script configured")
                else:
                    self._add_result(
                        False,
                        f"⚠️ Unexpected script: {script_path}",
                        severity="warning"
                    )
            
            # Check for environment variables if configured
            if 'env' in agent_forge_config:
                env_vars = agent_forge_config['env']
                self._add_result(
                    True,
                    f"✅ Environment variables configured: {len(env_vars)} variables",
                    details={"env_vars": list(env_vars.keys())}
                )
            
            self._add_result(True, "✅ Claude Desktop configuration is valid")
            
        except json.JSONDecodeError as e:
            self._add_result(
                False,
                f"❌ Invalid JSON in configuration: {e}",
                severity="error"
            )
        except Exception as e:
            self._add_result(
                False,
                f"❌ Configuration validation error: {e}",
                severity="error"
            )
    
    def validate_mcp_dependencies(self) -> None:
        """Validate MCP-specific dependencies."""
        print("📦 Validating MCP dependencies...")
        
        mcp_packages = [
            'fastmcp',
            'mcp',
            'aiohttp',
            'asyncio'
        ]
        
        import importlib.util
        
        missing_packages = []
        installed_packages = {}
        
        for package in mcp_packages:
            try:
                spec = importlib.util.find_spec(package)
                if spec is not None:
                    try:
                        module = importlib.import_module(package)
                        version = getattr(module, '__version__', 'unknown')
                        installed_packages[package] = version
                        self._add_result(True, f"✅ {package} ({version}) available")
                    except Exception:
                        installed_packages[package] = 'available'
                        self._add_result(True, f"✅ {package} available")
                else:
                    missing_packages.append(package)
                    self._add_result(False, f"❌ {package} not installed", severity="error")
            except Exception as e:
                missing_packages.append(package)
                self._add_result(False, f"❌ Error checking {package}: {e}", severity="error")
        
        if missing_packages:
            self._add_result(
                False,
                f"❌ Missing MCP packages: {', '.join(missing_packages)}",
                severity="critical"
            )
        else:
            self._add_result(True, "✅ All MCP dependencies satisfied")
    
    def test_mcp_server_startup(self) -> None:
        """Test MCP server startup process."""
        print("🚀 Testing MCP server startup...")
        
        try:
            # Try to start the MCP server briefly to test startup
            mcp_server_path = self.agent_forge_path / 'mcp_server.py'
            
            if not mcp_server_path.exists():
                self._add_result(
                    False,
                    "❌ mcp_server.py not found",
                    severity="error"
                )
                return
            
            # Test import without starting server
            import subprocess
            import time
            
            # Quick syntax check
            result = subprocess.run([
                sys.executable, '-m', 'py_compile', str(mcp_server_path)
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self._add_result(True, "✅ MCP server syntax is valid")
            else:
                self._add_result(
                    False,
                    f"❌ MCP server syntax error: {result.stderr}",
                    severity="error"
                )
                return
            
            # Test basic import
            test_script = f"""
import sys
sys.path.insert(0, r'{self.agent_forge_path}')
try:
    from mcp_server import mcp
    print("SUCCESS: MCP server imported")
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
"""
            
            result = subprocess.run([
                sys.executable, '-c', test_script
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and "SUCCESS" in result.stdout:
                self._add_result(True, "✅ MCP server imports successfully")
            else:
                self._add_result(
                    False,
                    f"❌ MCP server import failed: {result.stderr or result.stdout}",
                    severity="error"
                )
                
        except subprocess.TimeoutExpired:
            self._add_result(
                False,
                "❌ MCP server startup test timed out",
                severity="warning"
            )
        except Exception as e:
            self._add_result(
                False,
                f"❌ MCP server startup test error: {e}",
                severity="error"
            )
    
    def run_mcp_validation(self) -> ValidationSummary:
        """Run comprehensive MCP validation."""
        print("🔌 Starting MCP Integration Validation")
        print("=" * 50)
        
        self.results = []
        
        # Run all MCP validation checks
        validation_checks = [
            self.validate_mcp_dependencies,
            self.validate_mcp_server_functionality,
            self.validate_agent_discovery_integration,
            self.validate_claude_desktop_configuration,
            self.test_mcp_server_startup
        ]
        
        for check in validation_checks:
            try:
                check()
            except Exception as e:
                self._add_result(
                    False,
                    f"❌ Validation check failed: {e}",
                    severity="critical"
                )
        
        # Calculate summary
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r.passed)
        failed_checks = total_checks - passed_checks
        
        warnings = sum(1 for r in self.results if r.severity == "warning")
        errors = sum(1 for r in self.results if r.severity == "error") 
        critical_issues = sum(1 for r in self.results if r.severity == "critical")
        
        all_passed = failed_checks == 0
        
        summary = ValidationSummary(
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            errors=errors,
            critical_issues=critical_issues,
            all_passed=all_passed,
            results=self.results
        )
        
        # Print summary
        print("\n" + "=" * 50)
        print("🔌 MCP VALIDATION SUMMARY")
        print("=" * 50)
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {failed_checks}")
        print(f"Success Rate: {summary.success_rate:.1f}%")
        print(f"Warnings: {warnings}")
        print(f"Errors: {errors}")
        print(f"Critical Issues: {critical_issues}")
        
        if all_passed:
            print("\n🎉 MCP INTEGRATION READY FOR CLAUDE DESKTOP!")
        else:
            print(f"\n⚠️ {failed_checks} MCP VALIDATION(S) FAILED")
            
            # Show failed checks
            failed_results = [r for r in self.results if not r.passed]
            for result in failed_results:
                severity_icon = {
                    "warning": "⚠️",
                    "error": "❌",
                    "critical": "🚨"
                }.get(result.severity, "❓")
                print(f"   {severity_icon} {result.message}")
        
        return summary


def main():
    """Command-line interface for MCP validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Agent Forge MCP integration")
    parser.add_argument(
        "--path",
        help="Path to Agent Forge installation"
    )
    parser.add_argument(
        "--json",
        action="store_true", 
        help="Output results in JSON format"
    )
    
    args = parser.parse_args()
    
    try:
        validator = MCPIntegrationValidator(args.path)
        summary = validator.run_mcp_validation()
        
        if args.json:
            json_results = {
                "summary": {
                    "total_checks": summary.total_checks,
                    "passed_checks": summary.passed_checks,
                    "failed_checks": summary.failed_checks,
                    "success_rate": summary.success_rate,
                    "all_passed": summary.all_passed,
                    "warnings": summary.warnings,
                    "errors": summary.errors,
                    "critical_issues": summary.critical_issues
                },
                "results": [
                    {
                        "passed": r.passed,
                        "message": r.message,
                        "severity": r.severity,
                        "details": r.details
                    }
                    for r in summary.results
                ]
            }
            print(json.dumps(json_results, indent=2))
        
        sys.exit(0 if summary.all_passed else 1)
        
    except Exception as e:
        print(f"❌ MCP validation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()