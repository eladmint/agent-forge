#!/usr/bin/env python3
"""
Agent Forge MCP Integration Test Runner

Comprehensive test suite runner for all MCP integration tests including:
- Basic integration tests
- Claude Desktop scenario tests  
- Performance benchmark tests
- Error handling validation
- End-to-end integration validation
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
import json

class TestRunner:
    """Test runner for Agent Forge MCP integration."""
    
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.test_results = {}
        self.start_time = time.time()
    
    def run_test_suite(self, test_file: str, description: str) -> Tuple[bool, Dict]:
        """Run a specific test suite and return results."""
        print(f"\n{'='*60}")
        print(f"🧪 Running {description}")
        print(f"{'='*60}")
        
        test_path = self.current_dir / "tests" / test_file
        
        if not test_path.exists():
            print(f"❌ Test file not found: {test_path}")
            return False, {"error": "Test file not found"}
        
        try:
            # Run the test
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            
            # Parse output for summary
            output_lines = result.stdout.split('\n')
            error_lines = result.stderr.split('\n') if result.stderr else []
            
            test_summary = {
                "success": success,
                "return_code": result.returncode,
                "output_lines": len(output_lines),
                "error_lines": len(error_lines),
                "stdout_preview": '\n'.join(output_lines[:10]),
                "stderr_preview": '\n'.join(error_lines[:5]) if error_lines else ""
            }
            
            # Print results
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if success:
                print(f"✅ {description} - PASSED")
            else:
                print(f"❌ {description} - FAILED (return code: {result.returncode})")
            
            return success, test_summary
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT (exceeded 5 minutes)")
            return False, {"error": "Test timeout"}
        except Exception as e:
            print(f"💥 {description} - ERROR: {e}")
            return False, {"error": str(e)}
    
    def run_all_tests(self) -> Dict:
        """Run all test suites and generate comprehensive report."""
        print("🚀 Agent Forge MCP Integration - Comprehensive Test Suite")
        print("Starting comprehensive validation of MCP integration...")
        
        test_suites = [
            ("mcp/test_mcp_integration.py", "MCP Integration Tests"),
            ("mcp/test_claude_desktop_scenarios.py", "Claude Desktop Scenario Tests"),
            ("mcp/test_mcp_performance_benchmarks.py", "Performance Benchmark Tests")
        ]
        
        results_summary = {
            "total_suites": len(test_suites),
            "passed_suites": 0,
            "failed_suites": 0,
            "suite_results": {},
            "overall_success": False,
            "execution_time": 0
        }
        
        # Run each test suite
        for test_file, description in test_suites:
            suite_success, suite_details = self.run_test_suite(test_file, description)
            
            if suite_success:
                results_summary["passed_suites"] += 1
            else:
                results_summary["failed_suites"] += 1
            
            results_summary["suite_results"][description] = {
                "success": suite_success,
                "details": suite_details
            }
        
        # Calculate overall results
        results_summary["execution_time"] = time.time() - self.start_time
        results_summary["overall_success"] = results_summary["failed_suites"] == 0
        
        # Generate final report
        self._generate_final_report(results_summary)
        
        return results_summary
    
    def _generate_final_report(self, results: Dict):
        """Generate comprehensive final test report."""
        print("\n" + "="*80)
        print("🎯 AGENT FORGE MCP INTEGRATION - FINAL TEST REPORT")
        print("="*80)
        
        # Executive Summary
        print(f"\n📊 Executive Summary:")
        print(f"   Total Test Suites: {results['total_suites']}")
        print(f"   Passed: {results['passed_suites']}")
        print(f"   Failed: {results['failed_suites']}")
        print(f"   Success Rate: {results['passed_suites']/results['total_suites']:.1%}")
        print(f"   Execution Time: {results['execution_time']:.1f} seconds")
        
        # Detailed Results
        print(f"\n📋 Detailed Results:")
        for suite_name, suite_result in results['suite_results'].items():
            status = "✅ PASSED" if suite_result['success'] else "❌ FAILED"
            print(f"   {status} - {suite_name}")
            
            if not suite_result['success'] and 'error' in suite_result['details']:
                print(f"      Error: {suite_result['details']['error']}")
        
        # Overall Status
        print(f"\n🏆 Overall Status:")
        if results['overall_success']:
            print("   🎉 ALL TESTS PASSED - MCP INTEGRATION READY FOR PRODUCTION!")
            print("   ✅ Agent Forge is ready for Claude Desktop deployment")
            print("   ✅ All performance benchmarks meet production standards")
            print("   ✅ Error handling and edge cases properly covered")
        else:
            print("   ⚠️ SOME TESTS FAILED - REVIEW REQUIRED BEFORE DEPLOYMENT")
            print("   🔧 Check failed test suites and resolve issues")
            print("   📝 Review error messages and logs for specific problems")
        
        # Next Steps
        print(f"\n🚀 Next Steps:")
        if results['overall_success']:
            print("   1. ✅ Deploy MCP configuration to Claude Desktop")
            print("   2. ✅ Test with real users using provided test scenarios")
            print("   3. ✅ Monitor performance in production environment")
            print("   4. ✅ Proceed with open source release (MCP-First Launch)")
        else:
            print("   1. 🔧 Fix failing test suites")
            print("   2. 🧪 Re-run comprehensive test suite")
            print("   3. 📋 Validate all scenarios pass before deployment")
            print("   4. ⚠️ Do not proceed to production until all tests pass")
        
        # Production Readiness Checklist
        print(f"\n✅ Production Readiness Checklist:")
        checklist_items = [
            ("MCP Server Functionality", results['suite_results'].get('MCP Integration Tests', {}).get('success', False)),
            ("Claude Desktop Scenarios", results['suite_results'].get('Claude Desktop Scenario Tests', {}).get('success', False)),
            ("Performance Benchmarks", results['suite_results'].get('Performance Benchmark Tests', {}).get('success', False)),
            ("Overall Integration", results['overall_success'])
        ]
        
        for item_name, item_status in checklist_items:
            status_icon = "✅" if item_status else "❌"
            print(f"   {status_icon} {item_name}")
        
        # Save results to file
        self._save_test_results(results)
    
    def _save_test_results(self, results: Dict):
        """Save test results to JSON file for reference."""
        results_file = self.current_dir / "test_results.json"
        
        # Add timestamp and additional metadata
        results_with_metadata = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_runner_version": "1.0.0",
            "agent_forge_path": str(self.current_dir),
            **results
        }
        
        try:
            with open(results_file, 'w') as f:
                json.dump(results_with_metadata, f, indent=2)
            print(f"\n💾 Test results saved to: {results_file}")
        except Exception as e:
            print(f"\n⚠️ Failed to save test results: {e}")
    
    def run_quick_validation(self) -> bool:
        """Run quick validation checks before full test suite."""
        print("🔍 Running Quick Validation Checks...")
        
        checks = [
            ("Python Path", self._check_python_path),
            ("MCP Dependencies", self._check_mcp_dependencies),
            ("Agent Forge Structure", self._check_agent_forge_structure),
            ("Test Files", self._check_test_files)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            try:
                success = check_func()
                status = "✅" if success else "❌"
                print(f"   {status} {check_name}")
                if not success:
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {check_name} - Error: {e}")
                all_passed = False
        
        if all_passed:
            print("✅ All validation checks passed - proceeding with full test suite")
        else:
            print("❌ Some validation checks failed - fix issues before running tests")
        
        return all_passed
    
    def _check_python_path(self) -> bool:
        """Check Python path and imports."""
        try:
            sys.path.insert(0, str(self.current_dir))
            return True
        except Exception:
            return False
    
    def _check_mcp_dependencies(self) -> bool:
        """Check MCP dependencies are installed."""
        try:
            import fastmcp
            import mcp
            return True
        except ImportError:
            return False
    
    def _check_agent_forge_structure(self) -> bool:
        """Check Agent Forge directory structure."""
        required_files = [
            "mcp_server.py",
            "mcp_auto_discovery.py", 
            "mcp_requirements.txt"
        ]
        
        return all((self.current_dir / file).exists() for file in required_files)
    
    def _check_test_files(self) -> bool:
        """Check test files exist."""
        test_files = [
            "tests/mcp/test_mcp_integration.py",
            "tests/mcp/test_claude_desktop_scenarios.py",
            "tests/mcp/test_mcp_performance_benchmarks.py"
        ]
        
        return all((self.current_dir / file).exists() for file in test_files)


def main():
    """Main entry point for test runner."""
    runner = TestRunner()
    
    # Quick validation first
    if not runner.run_quick_validation():
        print("\n❌ Quick validation failed - cannot proceed with tests")
        sys.exit(1)
    
    # Run full test suite
    results = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_success'] else 1)


if __name__ == '__main__':
    main()