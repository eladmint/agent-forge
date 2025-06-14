#!/usr/bin/env python3
"""
Agent Forge Validation CLI
=========================

Command-line interface for validating Agent Forge installations and MCP integrations.

Usage:
    python -m agent_forge_tests.cli.validate                    # Quick validation
    python -m agent_forge_tests.cli.validate --comprehensive    # Full validation
    python -m agent_forge_tests.cli.validate --mcp-only        # MCP-specific validation
    python -m agent_forge_tests.cli.validate --security-only   # Security validation
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# Add parent directories to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))
sys.path.insert(0, str(current_dir.parent.parent))

from validators.installation_validator import AgentForgeValidator
from validators.mcp_validator import MCPIntegrationValidator  
from examples.quick_start import QuickStartTestSuite


def print_banner():
    """Print CLI banner."""
    print("""
🚀 Agent Forge Validation CLI
=============================
Comprehensive validation for Agent Forge installations and MCP integrations.
""")


def run_quick_validation(path: Optional[str], output_file: Optional[str] = None) -> bool:
    """Run quick validation suitable for end users."""
    print("🎯 Running Quick Validation (recommended for most users)")
    print("-" * 60)
    
    try:
        suite = QuickStartTestSuite(path)
        results = suite.run_all_tests()
        
        if output_file:
            save_results_to_file(results, output_file, "quick_validation")
            
        return results.all_passed
        
    except Exception as e:
        print(f"❌ Quick validation failed: {e}")
        return False


def run_comprehensive_validation(path: Optional[str], output_file: Optional[str] = None) -> bool:
    """Run comprehensive validation for developers and production."""
    print("🔧 Running Comprehensive Validation (for developers and production)")
    print("-" * 70)
    
    try:
        validator = AgentForgeValidator(path)
        results = validator.run_comprehensive_validation()
        
        if output_file:
            save_results_to_file(results, output_file, "comprehensive_validation")
            
        return results.all_passed
        
    except Exception as e:
        print(f"❌ Comprehensive validation failed: {e}")
        return False


def run_mcp_validation(path: Optional[str], output_file: Optional[str] = None) -> bool:
    """Run MCP-specific validation."""
    print("🔌 Running MCP Integration Validation")
    print("-" * 50)
    
    try:
        validator = MCPIntegrationValidator(path)
        results = validator.run_mcp_validation()
        
        if output_file:
            save_results_to_file(results, output_file, "mcp_validation")
            
        return results.all_passed
        
    except Exception as e:
        print(f"❌ MCP validation failed: {e}")
        return False


def run_security_validation(path: Optional[str], output_file: Optional[str] = None) -> bool:
    """Run security-focused validation."""
    print("🔒 Running Security Validation")
    print("-" * 40)
    
    try:
        # Import and run security tests
        import subprocess
        import tempfile
        
        # Get the security test file path
        agent_forge_path = Path(path) if path else Path.cwd()
        security_test_path = agent_forge_path / 'tests' / 'security' / 'test_credential_security.py'
        
        if not security_test_path.exists():
            print("⚠️ Security tests not found. Running basic security checks...")
            
            # Run basic security validation as part of quick start
            suite = QuickStartTestSuite(path)
            result = suite.test_basic_security()
            
            if result['passed']:
                print("✅ Basic security checks passed")
                return True
            else:
                print(f"❌ Security issues found: {result['message']}")
                return False
        else:
            # Run the comprehensive security test suite
            result = subprocess.run([
                sys.executable, str(security_test_path)
            ], capture_output=True, text=True, cwd=str(agent_forge_path))
            
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
                
            if result.returncode == 0:
                print("✅ Security validation completed successfully")
                return True
            else:
                print("❌ Security validation found issues")
                return False
                
    except Exception as e:
        print(f"❌ Security validation failed: {e}")
        return False


def save_results_to_file(results, output_file: str, validation_type: str):
    """Save validation results to file."""
    try:
        # Convert results to JSON-serializable format
        if hasattr(results, 'results'):
            # ValidationSummary object
            data = {
                "validation_type": validation_type,
                "summary": {
                    "total_checks": results.total_checks,
                    "passed_checks": results.passed_checks,
                    "failed_checks": results.failed_checks,
                    "success_rate": results.success_rate,
                    "all_passed": results.all_passed
                },
                "results": [
                    {
                        "passed": r.passed,
                        "message": r.message,
                        "severity": getattr(r, 'severity', 'info'),
                        "details": getattr(r, 'details', None)
                    }
                    for r in results.results
                ]
            }
        else:
            # TestSuiteResults object
            data = {
                "validation_type": validation_type,
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
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"\n💾 Results saved to: {output_file}")
        
    except Exception as e:
        print(f"⚠️ Could not save results to file: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Agent Forge Validation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m agent_forge_tests.cli.validate                     # Quick validation
  python -m agent_forge_tests.cli.validate --comprehensive     # Full validation
  python -m agent_forge_tests.cli.validate --mcp-only         # MCP validation only
  python -m agent_forge_tests.cli.validate --security-only    # Security validation only
  python -m agent_forge_tests.cli.validate --output results.json  # Save to file
  python -m agent_forge_tests.cli.validate --path /custom/path    # Custom path

Validation Types:
  Quick: Fast validation for end users (5-10 tests, ~2 seconds)
  Comprehensive: Complete validation for developers (20+ tests, ~10 seconds)  
  MCP: Claude Desktop integration validation (15+ tests, ~5 seconds)
  Security: Security and credential validation (8+ tests, ~3 seconds)
        """
    )
    
    # Validation type options (mutually exclusive)
    validation_group = parser.add_mutually_exclusive_group()
    validation_group.add_argument(
        "--quick",
        action="store_true",
        help="Run quick validation (default, suitable for end users)"
    )
    validation_group.add_argument(
        "--comprehensive", 
        action="store_true",
        help="Run comprehensive validation (for developers and production)"
    )
    validation_group.add_argument(
        "--mcp-only",
        action="store_true", 
        help="Run MCP integration validation only"
    )
    validation_group.add_argument(
        "--security-only",
        action="store_true",
        help="Run security validation only"
    )
    
    # Common options
    parser.add_argument(
        "--path",
        help="Path to Agent Forge installation (auto-detect if not specified)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save results to JSON file"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output (only show final result)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Agent Forge Validation CLI 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Show banner unless quiet mode
    if not args.quiet:
        print_banner()
    
    # Determine validation type (default to quick)
    if args.comprehensive:
        validation_func = run_comprehensive_validation
        validation_name = "Comprehensive"
    elif args.mcp_only:
        validation_func = run_mcp_validation
        validation_name = "MCP Integration"
    elif args.security_only:
        validation_func = run_security_validation
        validation_name = "Security"
    else:
        validation_func = run_quick_validation
        validation_name = "Quick"
    
    if not args.quiet:
        print(f"🎯 Starting {validation_name} Validation...")
        if args.path:
            print(f"📁 Using path: {args.path}")
        print()
    
    # Run validation
    try:
        success = validation_func(args.path, args.output)
        
        if not args.quiet:
            print("\n" + "=" * 60)
            if success:
                print("🎉 VALIDATION SUCCESSFUL!")
                print("✅ Agent Forge is ready to use!")
                
                if validation_name == "Quick":
                    print("\n📋 Next Steps:")
                    print("   1. Copy claude_desktop_config_example.json to Claude Desktop")
                    print("   2. Update file paths in the configuration")
                    print("   3. Restart Claude Desktop")
                    print("   4. Test: 'Can you help me navigate to example.com?'")
                elif validation_name == "MCP Integration":
                    print("\n📋 MCP Integration Ready:")
                    print("   • Claude Desktop configuration is valid")
                    print("   • MCP server and tools are functional")  
                    print("   • Agent discovery is working")
                elif validation_name == "Security":
                    print("\n📋 Security Validation Complete:")
                    print("   • Credential handling is secure")
                    print("   • Input validation is working")
                    print("   • File permissions are appropriate")
                    
            else:
                print("❌ VALIDATION FAILED!")
                print("⚠️ Please fix the issues before proceeding")
                
                print("\n💡 Troubleshooting Tips:")
                print("   • Run with --comprehensive for detailed diagnostics")
                print("   • Check the Agent Forge documentation")
                print("   • Ensure all dependencies are installed")
                print("   • Verify file permissions and paths")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        if not args.quiet:
            print("\n\n⚠️ Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        if not args.quiet:
            print(f"\n❌ Validation failed with error: {e}")
            print("\n💡 Try running with --comprehensive for more details")
        sys.exit(1)


if __name__ == '__main__':
    main()