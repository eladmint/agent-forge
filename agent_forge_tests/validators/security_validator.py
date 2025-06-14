#!/usr/bin/env python3
"""
Security Validator
Validates security aspects of Agent Forge installations.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

from .installation_validator import ValidationResult, ValidationSummary


class SecurityValidator:
    """Security-focused validator for Agent Forge installations."""
    
    def __init__(self, agent_forge_path: Optional[str] = None):
        """Initialize security validator."""
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
    
    def run_security_tests(self) -> ValidationSummary:
        """Run security validation tests."""
        print("🔒 Starting Security Validation")
        print("=" * 40)
        
        self.results = []
        
        # Run security tests by importing and running the security test suite
        try:
            security_test_path = self.agent_forge_path / 'tests' / 'security' / 'test_credential_security.py'
            
            if security_test_path.exists():
                # Run the security test suite
                result = subprocess.run([
                    sys.executable, str(security_test_path)
                ], capture_output=True, text=True, cwd=str(self.agent_forge_path))
                
                if result.returncode == 0:
                    self._add_result(True, "✅ Security test suite passed")
                else:
                    self._add_result(False, f"❌ Security test suite failed", severity="error")
            else:
                # Run basic security checks
                self._run_basic_security_checks()
                
        except Exception as e:
            self._add_result(False, f"❌ Security validation error: {e}", severity="error")
        
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
    
    def _run_basic_security_checks(self):
        """Run basic security checks."""
        # Check for sensitive data in config files
        config_file = self.agent_forge_path / 'claude_desktop_config_example.json'
        if config_file.exists():
            content = config_file.read_text().lower()
            sensitive_patterns = ['api_key', 'password', 'secret', 'token']
            found_patterns = [p for p in sensitive_patterns if p in content]
            
            if found_patterns:
                self._add_result(
                    False,
                    f"⚠️ Sensitive patterns in config: {found_patterns}",
                    severity="warning"
                )
            else:
                self._add_result(True, "✅ No sensitive data in config files")
        
        # Check file permissions
        if hasattr(os, 'stat'):
            sensitive_files = ['mcp_server.py', 'mcp_auto_discovery.py']
            permission_issues = []
            
            for file_name in sensitive_files:
                file_path = self.agent_forge_path / file_name
                if file_path.exists():
                    file_stat = file_path.stat()
                    if file_stat.st_mode & 0o022:  # world-writable
                        permission_issues.append(f"{file_name} is world-writable")
            
            if permission_issues:
                self._add_result(
                    False,
                    f"⚠️ File permission issues: {'; '.join(permission_issues)}",
                    severity="warning"
                )
            else:
                self._add_result(True, "✅ File permissions are appropriate")


def main():
    """Command-line interface for security validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Agent Forge security")
    parser.add_argument("--path", help="Path to Agent Forge installation")
    
    args = parser.parse_args()
    
    try:
        validator = SecurityValidator(args.path)
        summary = validator.run_security_tests()
        
        print(f"\n🔒 Security validation: {summary.success_rate:.1f}% passed")
        sys.exit(0 if summary.all_passed else 1)
        
    except Exception as e:
        print(f"❌ Security validation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()