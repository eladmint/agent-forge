#!/usr/bin/env python3
"""
Agent Forge Installation Validator
Comprehensive validation tool for Agent Forge installations.
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    severity: str = "info"  # info, warning, error, critical


@dataclass
class ValidationSummary:
    """Summary of all validation results."""
    total_checks: int
    passed_checks: int
    failed_checks: int
    warnings: int
    errors: int
    critical_issues: int
    all_passed: bool
    results: List[ValidationResult]
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        return (self.passed_checks / self.total_checks) * 100 if self.total_checks > 0 else 0


class AgentForgeValidator:
    """Comprehensive Agent Forge installation validator."""
    
    def __init__(self, agent_forge_path: Optional[str] = None):
        """
        Initialize validator.
        
        Args:
            agent_forge_path: Path to Agent Forge installation. If None, auto-detect.
        """
        self.agent_forge_path = Path(agent_forge_path) if agent_forge_path else self._detect_agent_forge_path()
        self.results: List[ValidationResult] = []
        
    def _detect_agent_forge_path(self) -> Path:
        """Auto-detect Agent Forge installation path."""
        # Check current directory
        current_dir = Path.cwd()
        if (current_dir / 'mcp_server.py').exists():
            return current_dir
            
        # Check parent directories
        for parent in current_dir.parents:
            if (parent / 'mcp_server.py').exists():
                return parent
                
        # Check common installation paths
        common_paths = [
            Path.home() / 'agent_forge',
            Path('/opt/agent_forge'),
            Path('/usr/local/agent_forge')
        ]
        
        for path in common_paths:
            if path.exists() and (path / 'mcp_server.py').exists():
                return path
                
        raise FileNotFoundError("Agent Forge installation not found. Please specify path manually.")
    
    def _add_result(self, passed: bool, message: str, details: Optional[Dict] = None, severity: str = "info"):
        """Add validation result."""
        self.results.append(ValidationResult(
            passed=passed,
            message=message,
            details=details,
            severity=severity
        ))
    
    def validate_installation_structure(self) -> None:
        """Validate Agent Forge installation structure."""
        print("🔍 Validating installation structure...")
        
        required_files = [
            'mcp_server.py',
            'mcp_auto_discovery.py', 
            'mcp_requirements.txt',
            'claude_desktop_config_example.json'
        ]
        
        required_directories = [
            'agents',
            'core', 
            'tests'
        ]
        
        # Check required files
        missing_files = []
        for file_name in required_files:
            file_path = self.agent_forge_path / file_name
            if file_path.exists():
                self._add_result(True, f"✅ Found {file_name}")
            else:
                missing_files.append(file_name)
                self._add_result(False, f"❌ Missing {file_name}", severity="error")
        
        # Check required directories
        missing_dirs = []
        for dir_name in required_directories:
            dir_path = self.agent_forge_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self._add_result(True, f"✅ Found {dir_name}/ directory")
            else:
                missing_dirs.append(dir_name)
                self._add_result(False, f"❌ Missing {dir_name}/ directory", severity="error")
        
        if not missing_files and not missing_dirs:
            self._add_result(True, "✅ Installation structure is complete")
        else:
            self._add_result(
                False, 
                f"❌ Installation incomplete: {len(missing_files)} missing files, {len(missing_dirs)} missing directories",
                details={"missing_files": missing_files, "missing_dirs": missing_dirs},
                severity="critical"
            )
    
    def validate_python_dependencies(self) -> None:
        """Validate Python dependencies."""
        print("🐍 Validating Python dependencies...")
        
        required_packages = [
            'fastmcp',
            'mcp', 
            'aiohttp',
            'requests',
            'playwright',
            'python-dotenv'
        ]
        
        missing_packages = []
        installed_packages = {}
        
        for package in required_packages:
            try:
                spec = importlib.util.find_spec(package)
                if spec is not None:
                    # Try to get version
                    try:
                        module = importlib.import_module(package)
                        version = getattr(module, '__version__', 'unknown')
                        installed_packages[package] = version
                        self._add_result(True, f"✅ {package} ({version}) installed")
                    except Exception:
                        installed_packages[package] = 'unknown'
                        self._add_result(True, f"✅ {package} installed (version unknown)")
                else:
                    missing_packages.append(package)
                    self._add_result(False, f"❌ {package} not installed", severity="error")
            except Exception as e:
                missing_packages.append(package)
                self._add_result(False, f"❌ Error checking {package}: {e}", severity="error")
        
        if missing_packages:
            self._add_result(
                False,
                f"❌ Missing {len(missing_packages)} required packages",
                details={"missing": missing_packages, "installed": installed_packages},
                severity="critical"
            )
        else:
            self._add_result(True, "✅ All Python dependencies satisfied")
    
    def validate_agent_discovery(self) -> None:
        """Validate agent discovery functionality."""
        print("🤖 Validating agent discovery...")
        
        try:
            # Add agent forge path to Python path
            sys.path.insert(0, str(self.agent_forge_path))
            
            # Try to import and run agent discovery
            from mcp_auto_discovery import AgentDiscovery
            
            discovery = AgentDiscovery()
            agents = discovery.discover_agents()
            
            if isinstance(agents, dict) and len(agents) > 0:
                self._add_result(
                    True,
                    f"✅ Agent discovery successful: {len(agents)} agents found",
                    details={"agents": list(agents.keys())}
                )
                
                # Validate specific expected agents
                expected_agents = ['page_scraper', 'data_compiler', 'enhanced_validation']
                missing_agents = [agent for agent in expected_agents if agent not in agents]
                
                if missing_agents:
                    self._add_result(
                        False,
                        f"⚠️ Missing expected agents: {', '.join(missing_agents)}",
                        severity="warning"
                    )
                else:
                    self._add_result(True, "✅ All expected agents found")
                    
            else:
                self._add_result(
                    False,
                    "❌ Agent discovery failed: No agents found",
                    severity="error"
                )
                
        except ImportError as e:
            self._add_result(
                False,
                f"❌ Cannot import agent discovery module: {e}",
                severity="critical"
            )
        except Exception as e:
            self._add_result(
                False,
                f"❌ Agent discovery error: {e}",
                severity="error"
            )
        finally:
            # Clean up sys.path
            if str(self.agent_forge_path) in sys.path:
                sys.path.remove(str(self.agent_forge_path))
    
    def validate_mcp_server(self) -> None:
        """Validate MCP server functionality."""
        print("🔌 Validating MCP server...")
        
        try:
            # Add agent forge path to Python path
            sys.path.insert(0, str(self.agent_forge_path))
            
            # Try to import MCP server
            from mcp_server import mcp
            
            # Check server attributes
            if hasattr(mcp, 'name'):
                self._add_result(True, f"✅ MCP server loaded: {mcp.name}")
            else:
                self._add_result(True, "✅ MCP server loaded (name unknown)")
            
            # Check if server has tools
            tools_count = 0
            if hasattr(mcp, '_tools'):
                tools_count = len(mcp._tools)
            elif hasattr(mcp, 'tools'):
                tools_count = len(mcp.tools)
                
            if tools_count > 0:
                self._add_result(
                    True,
                    f"✅ MCP server has {tools_count} tools registered"
                )
            else:
                self._add_result(
                    False,
                    "⚠️ MCP server has no tools registered",
                    severity="warning"
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
    
    def validate_claude_desktop_config(self) -> None:
        """Validate Claude Desktop configuration."""
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
            
            # Validate config structure
            if 'mcpServers' in config_data:
                servers = config_data['mcpServers']
                
                if 'agent-forge' in servers:
                    agent_forge_config = servers['agent-forge']
                    
                    # Check required fields
                    required_fields = ['command', 'args']
                    missing_fields = [field for field in required_fields if field not in agent_forge_config]
                    
                    if missing_fields:
                        self._add_result(
                            False,
                            f"❌ Missing config fields: {', '.join(missing_fields)}",
                            severity="error"
                        )
                    else:
                        # Validate paths in config
                        command_path = agent_forge_config.get('command', '')
                        if 'python' in command_path.lower():
                            self._add_result(True, "✅ Python command configured")
                        else:
                            self._add_result(
                                False,
                                f"⚠️ Unexpected command: {command_path}",
                                severity="warning"
                            )
                        
                        # Check if script path exists
                        args = agent_forge_config.get('args', [])
                        if args and args[0]:
                            script_path = Path(args[0])
                            if script_path.is_absolute():
                                # Absolute path - check if exists
                                if script_path.exists():
                                    self._add_result(True, "✅ MCP server script path exists")
                                else:
                                    self._add_result(
                                        False,
                                        f"❌ MCP server script not found: {script_path}",
                                        severity="error"
                                    )
                            else:
                                # Relative path - assume it's correct
                                self._add_result(True, "✅ MCP server script path configured")
                        
                        self._add_result(True, "✅ Claude Desktop configuration is valid")
                        
                else:
                    self._add_result(
                        False,
                        "❌ 'agent-forge' server not found in mcpServers",
                        severity="error"
                    )
            else:
                self._add_result(
                    False,
                    "❌ 'mcpServers' section missing from config",
                    severity="error"
                )
                
        except json.JSONDecodeError as e:
            self._add_result(
                False,
                f"❌ Invalid JSON in config file: {e}",
                severity="error"
            )
        except Exception as e:
            self._add_result(
                False,
                f"❌ Config validation error: {e}",
                severity="error"
            )
    
    def validate_environment_setup(self) -> None:
        """Validate environment setup."""
        print("🌍 Validating environment setup...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            self._add_result(
                True,
                f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} (supported)"
            )
        else:
            self._add_result(
                False,
                f"❌ Python {python_version.major}.{python_version.minor} is too old (requires 3.8+)",
                severity="critical"
            )
        
        # Check for virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self._add_result(True, "✅ Running in virtual environment")
        else:
            self._add_result(
                False,
                "⚠️ Not running in virtual environment (recommended)",
                severity="warning"
            )
        
        # Check environment variables
        important_env_vars = ['PATH', 'PYTHONPATH']
        for var in important_env_vars:
            if var in os.environ:
                self._add_result(True, f"✅ {var} environment variable is set")
            else:
                self._add_result(
                    False,
                    f"⚠️ {var} environment variable not set",
                    severity="warning"
                )
    
    def run_comprehensive_validation(self) -> ValidationSummary:
        """Run all validation checks."""
        print("🚀 Starting Agent Forge Comprehensive Validation")
        print("=" * 60)
        
        # Clear previous results
        self.results = []
        
        # Run all validation checks
        validation_checks = [
            self.validate_installation_structure,
            self.validate_python_dependencies,
            self.validate_environment_setup,
            self.validate_agent_discovery,
            self.validate_mcp_server,
            self.validate_claude_desktop_config
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
        print("\n" + "=" * 60)
        print("🎯 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {failed_checks}")
        print(f"Success Rate: {summary.success_rate:.1f}%")
        print(f"Warnings: {warnings}")
        print(f"Errors: {errors}")
        print(f"Critical Issues: {critical_issues}")
        
        if all_passed:
            print("\n🎉 ALL VALIDATIONS PASSED - AGENT FORGE IS READY!")
        else:
            print(f"\n⚠️ {failed_checks} VALIDATION(S) FAILED - REVIEW REQUIRED")
            
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
    """Command-line interface for Agent Forge validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Agent Forge installation")
    parser.add_argument(
        "--path",
        help="Path to Agent Forge installation (auto-detect if not specified)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    args = parser.parse_args()
    
    try:
        validator = AgentForgeValidator(args.path)
        summary = validator.run_comprehensive_validation()
        
        if args.json:
            # Output JSON results
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
        
        # Exit with appropriate code
        sys.exit(0 if summary.all_passed else 1)
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()