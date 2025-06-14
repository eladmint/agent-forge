#!/usr/bin/env python3
"""
Performance Validator
Validates performance aspects of Agent Forge installations.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

from .installation_validator import ValidationResult, ValidationSummary


class PerformanceValidator:
    """Performance-focused validator for Agent Forge installations."""
    
    def __init__(self, agent_forge_path: Optional[str] = None):
        """Initialize performance validator."""
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
    
    def run_benchmarks(self) -> ValidationSummary:
        """Run performance benchmarks."""
        print("⚡ Starting Performance Validation")
        print("=" * 40)
        
        self.results = []
        
        # Run performance tests
        try:
            performance_test_path = self.agent_forge_path / 'tests' / 'mcp' / 'test_mcp_performance_benchmarks.py'
            
            if performance_test_path.exists():
                # Run the performance test suite
                result = subprocess.run([
                    sys.executable, str(performance_test_path)
                ], capture_output=True, text=True, cwd=str(self.agent_forge_path))
                
                if result.returncode == 0:
                    self._add_result(True, "✅ Performance benchmarks passed")
                else:
                    self._add_result(False, f"❌ Performance benchmarks failed", severity="warning")
            else:
                # Run basic performance checks
                self._run_basic_performance_checks()
                
        except Exception as e:
            self._add_result(False, f"❌ Performance validation error: {e}", severity="error")
        
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
        
        return summary
    
    def _run_basic_performance_checks(self):
        """Run basic performance checks."""
        # Test agent discovery performance
        try:
            sys.path.insert(0, str(self.agent_forge_path))
            
            start_time = time.time()
            from mcp_auto_discovery import AgentDiscovery
            discovery = AgentDiscovery()
            agents = discovery.discover_agents()
            discovery_time = time.time() - start_time
            
            if discovery_time < 5.0:  # 5 second threshold
                self._add_result(
                    True,
                    f"✅ Agent discovery: {discovery_time:.2f}s ({len(agents)} agents)"
                )
            else:
                self._add_result(
                    False,
                    f"⚠️ Slow agent discovery: {discovery_time:.2f}s",
                    severity="warning"
                )
                
        except Exception as e:
            self._add_result(False, f"❌ Agent discovery performance test failed: {e}", severity="error")
        finally:
            if str(self.agent_forge_path) in sys.path:
                sys.path.remove(str(self.agent_forge_path))
        
        # Test MCP server import performance
        try:
            sys.path.insert(0, str(self.agent_forge_path))
            
            start_time = time.time()
            from mcp_server import mcp
            import_time = time.time() - start_time
            
            if import_time < 2.0:  # 2 second threshold
                self._add_result(True, f"✅ MCP server import: {import_time:.2f}s")
            else:
                self._add_result(
                    False,
                    f"⚠️ Slow MCP server import: {import_time:.2f}s",
                    severity="warning"
                )
                
        except Exception as e:
            self._add_result(False, f"❌ MCP server import performance test failed: {e}", severity="error")
        finally:
            if str(self.agent_forge_path) in sys.path:
                sys.path.remove(str(self.agent_forge_path))


def main():
    """Command-line interface for performance validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Agent Forge performance")
    parser.add_argument("--path", help="Path to Agent Forge installation")
    
    args = parser.parse_args()
    
    try:
        validator = PerformanceValidator(args.path)
        summary = validator.run_benchmarks()
        
        print(f"\n⚡ Performance validation: {summary.success_rate:.1f}% passed")
        sys.exit(0 if summary.all_passed else 1)
        
    except Exception as e:
        print(f"❌ Performance validation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()