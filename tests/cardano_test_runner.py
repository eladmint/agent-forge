"""
Cardano Testing Suite Runner

Comprehensive test runner for all Cardano implementation tests including:
- Unit tests for Enhanced Cardano Client
- Integration tests for Cardano Enhanced Agent  
- End-to-end tests for complete AI agent economy workflow
- Performance tests for blockchain operations
- Security tests for staking and escrow systems

Usage:
    python tests/cardano_test_runner.py [--category] [--verbose] [--report]
    
Categories:
    --unit          Run unit tests only
    --integration   Run integration tests only
    --e2e           Run end-to-end tests only
    --performance   Run performance tests only
    --security      Run security tests only
    --all           Run all test categories (default)
"""

import argparse
import asyncio
import subprocess
import sys
import time
import json
from pathlib import Path
from datetime import datetime
import os


class CardanoTestRunner:
    """Comprehensive test runner for Cardano implementation."""
    
    def __init__(self, verbose: bool = False, generate_report: bool = False):
        self.verbose = verbose
        self.generate_report = generate_report
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
        # Test configuration
        self.test_categories = {
            "unit": {
                "name": "Unit Tests",
                "description": "Enhanced Cardano Client core functionality",
                "path": "tests/unit/test_cardano_enhanced_client.py",
                "estimated_duration": "2-3 minutes",
                "importance": "critical"
            },
            "integration": {
                "name": "Integration Tests", 
                "description": "Cardano Enhanced Agent integration",
                "path": "tests/integration/test_cardano_enhanced_agent.py",
                "estimated_duration": "3-5 minutes",
                "importance": "critical"
            },
            "e2e": {
                "name": "End-to-End Tests",
                "description": "Complete AI agent economy workflow",
                "path": "tests/e2e/test_cardano_ai_economy_workflow.py",
                "estimated_duration": "5-8 minutes", 
                "importance": "high"
            },
            "performance": {
                "name": "Performance Tests",
                "description": "Blockchain operations performance and scalability",
                "path": "tests/performance/test_cardano_blockchain_performance.py",
                "estimated_duration": "8-12 minutes",
                "importance": "medium"
            },
            "security": {
                "name": "Security Tests",
                "description": "Staking and escrow security validation",
                "path": "tests/security/test_cardano_security_features.py", 
                "estimated_duration": "4-6 minutes",
                "importance": "high"
            }
        }
    
    def print_header(self):
        """Print test runner header."""
        print("🎭" * 20)
        print("🏛️  CARDANO IMPLEMENTATION TEST SUITE")
        print("🎭" * 20)
        print("🚀 Agent Forge - Enhanced Cardano Integration Testing")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("📋 Test Categories Available:")
        for category, config in self.test_categories.items():
            print(f"   🔹 {config['name']}: {config['description']}")
            print(f"      ⏱️ Duration: {config['estimated_duration']}")
            print(f"      🎯 Importance: {config['importance']}")
            print()
    
    def run_pytest_category(self, category: str) -> dict:
        """Run pytest for a specific test category."""
        config = self.test_categories[category]
        test_path = config["path"]
        
        print(f"🧪 Running {config['name']}...")
        print(f"📂 Path: {test_path}")
        print(f"⏱️ Estimated Duration: {config['estimated_duration']}")
        print()
        
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            "python", "-m", "pytest",
            test_path,
            "-v",
            "--tb=short",
            "--no-header",
            "--no-summary"
        ]
        
        if self.verbose:
            cmd.extend(["-s", "--capture=no"])
        
        if self.generate_report:
            report_file = f"tests/reports/cardano_{category}_report.xml"
            cmd.extend([f"--junitxml={report_file}"])
        
        try:
            # Run pytest
            result = subprocess.run(
                cmd,
                capture_output=not self.verbose,
                text=True,
                cwd=Path.cwd(),
                timeout=600  # 10 minute timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse results
            test_result = {
                "category": category,
                "name": config["name"],
                "path": test_path,
                "duration": duration,
                "return_code": result.returncode,
                "success": result.returncode == 0,
                "stdout": result.stdout if not self.verbose else "",
                "stderr": result.stderr if not self.verbose else "",
                "importance": config["importance"]
            }
            
            # Print summary
            if test_result["success"]:
                print(f"✅ {config['name']} PASSED")
                print(f"   ⏱️ Duration: {duration:.1f}s")
                
                # Extract test counts from output
                if result.stdout:
                    if "passed" in result.stdout:
                        # Try to extract passed/failed counts
                        import re
                        passed_match = re.search(r'(\d+) passed', result.stdout)
                        failed_match = re.search(r'(\d+) failed', result.stdout)
                        
                        passed_count = int(passed_match.group(1)) if passed_match else 0
                        failed_count = int(failed_match.group(1)) if failed_match else 0
                        
                        test_result["tests_passed"] = passed_count
                        test_result["tests_failed"] = failed_count
                        
                        print(f"   📊 Tests: {passed_count} passed, {failed_count} failed")
                
            else:
                print(f"❌ {config['name']} FAILED")
                print(f"   ⏱️ Duration: {duration:.1f}s")
                print(f"   🔍 Return Code: {result.returncode}")
                
                if result.stderr and not self.verbose:
                    print(f"   ❗ Error: {result.stderr[:200]}...")
            
            print()
            return test_result
            
        except subprocess.TimeoutExpired:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏰ {config['name']} TIMEOUT")
            print(f"   ⏱️ Duration: {duration:.1f}s (exceeded 10 minutes)")
            print()
            
            return {
                "category": category,
                "name": config["name"],
                "path": test_path,
                "duration": duration,
                "return_code": -1,
                "success": False,
                "error": "Timeout after 10 minutes",
                "importance": config["importance"]
            }
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"💥 {config['name']} ERROR")
            print(f"   ❗ Exception: {str(e)}")
            print()
            
            return {
                "category": category,
                "name": config["name"],
                "path": test_path,
                "duration": duration,
                "return_code": -2,
                "success": False,
                "error": str(e),
                "importance": config["importance"]
            }
    
    def check_dependencies(self):
        """Check if required dependencies are available."""
        print("🔍 Checking Dependencies...")
        
        dependencies = [
            "pytest",
            "asyncio", 
            "aiohttp",
            "psutil"
        ]
        
        missing_deps = []
        
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"   ✅ {dep}")
            except ImportError:
                print(f"   ❌ {dep} (missing)")
                missing_deps.append(dep)
        
        if missing_deps:
            print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
            print("🔧 Install with: pip install pytest aiohttp psutil")
            return False
        
        print("✅ All dependencies available")
        print()
        return True
    
    def create_report_directory(self):
        """Create reports directory if it doesn't exist."""
        if self.generate_report:
            reports_dir = Path("tests/reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Reports directory: {reports_dir.absolute()}")
            print()
    
    def run_categories(self, categories: list):
        """Run specified test categories."""
        self.start_time = time.time()
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Create report directory
        self.create_report_directory()
        
        print(f"🎯 Running {len(categories)} test categories:")
        for category in categories:
            config = self.test_categories[category]
            print(f"   🔹 {config['name']} ({config['importance']} priority)")
        print()
        
        # Run each category
        for category in categories:
            if category not in self.test_categories:
                print(f"❌ Unknown test category: {category}")
                continue
                
            result = self.run_pytest_category(category)
            self.test_results[category] = result
        
        self.end_time = time.time()
        return True
    
    def print_summary(self):
        """Print comprehensive test summary."""
        if not self.test_results:
            print("❌ No test results to summarize")
            return
        
        total_duration = self.end_time - self.start_time
        
        print("📊" * 20)
        print("📊  CARDANO TEST SUITE SUMMARY")
        print("📊" * 20)
        print()
        
        # Overall statistics
        total_categories = len(self.test_results)
        successful_categories = sum(1 for r in self.test_results.values() if r["success"])
        failed_categories = total_categories - successful_categories
        
        print(f"⏱️ Total Duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
        print(f"📊 Test Categories: {total_categories}")
        print(f"✅ Successful: {successful_categories}")
        print(f"❌ Failed: {failed_categories}")
        print()
        
        # Category breakdown
        print("🔍 Category Results:")
        
        critical_passed = 0
        critical_total = 0
        high_passed = 0
        high_total = 0
        medium_passed = 0
        medium_total = 0
        
        for category, result in self.test_results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            duration = result["duration"]
            importance = result["importance"]
            
            print(f"   {status} {result['name']} ({duration:.1f}s) [{importance}]")
            
            # Count by importance
            if importance == "critical":
                critical_total += 1
                if result["success"]:
                    critical_passed += 1
            elif importance == "high":
                high_total += 1
                if result["success"]:
                    high_passed += 1
            elif importance == "medium":
                medium_total += 1
                if result["success"]:
                    medium_passed += 1
            
            # Show test counts if available
            if "tests_passed" in result and "tests_failed" in result:
                print(f"      📈 Tests: {result['tests_passed']} passed, {result['tests_failed']} failed")
            
            # Show errors if any
            if not result["success"] and "error" in result:
                print(f"      ❗ Error: {result['error']}")
        
        print()
        
        # Importance-based summary
        print("🎯 Results by Importance:")
        if critical_total > 0:
            print(f"   🔴 Critical: {critical_passed}/{critical_total} passed ({critical_passed/critical_total:.1%})")
        if high_total > 0:
            print(f"   🟡 High: {high_passed}/{high_total} passed ({high_passed/high_total:.1%})")
        if medium_total > 0:
            print(f"   🟢 Medium: {medium_passed}/{medium_total} passed ({medium_passed/medium_total:.1%})")
        print()
        
        # Overall assessment
        if failed_categories == 0:
            print("🎉 ALL TESTS PASSED! Cardano implementation is ready for production.")
        elif critical_passed == critical_total and high_passed == high_total:
            print("✅ CRITICAL AND HIGH PRIORITY TESTS PASSED! Ready for deployment with minor issues.")
        elif critical_passed == critical_total:
            print("⚠️ CRITICAL TESTS PASSED but some high/medium priority tests failed. Review required.")
        else:
            print("❌ CRITICAL TESTS FAILED! Do not deploy until issues are resolved.")
        
        print()
        
        # Recommendations
        print("💡 Recommendations:")
        if failed_categories == 0:
            print("   🚀 Ready for production deployment")
            print("   📚 Consider adding more edge case tests")
            print("   🔄 Set up continuous integration")
        else:
            failed_results = [r for r in self.test_results.values() if not r["success"]]
            critical_failures = [r for r in failed_results if r["importance"] == "critical"]
            high_failures = [r for r in failed_results if r["importance"] == "high"]
            
            if critical_failures:
                print("   🔴 Fix critical test failures immediately")
                for failure in critical_failures:
                    print(f"      - {failure['name']}")
            
            if high_failures:
                print("   🟡 Address high priority test failures")
                for failure in high_failures:
                    print(f"      - {failure['name']}")
            
            print("   🔍 Review test logs for detailed error information")
            print("   🧪 Run failing tests individually for debugging")
        
        print()
    
    def save_json_report(self):
        """Save detailed JSON report."""
        if not self.generate_report:
            return
        
        report_data = {
            "cardano_test_suite": {
                "timestamp": datetime.now().isoformat(),
                "total_duration": self.end_time - self.start_time,
                "categories_tested": len(self.test_results),
                "successful_categories": sum(1 for r in self.test_results.values() if r["success"]),
                "failed_categories": sum(1 for r in self.test_results.values() if not r["success"]),
                "overall_success": all(r["success"] for r in self.test_results.values()),
                "test_results": self.test_results,
                "environment": {
                    "python_version": sys.version,
                    "working_directory": str(Path.cwd()),
                    "test_runner_version": "1.0.0"
                }
            }
        }
        
        report_file = Path("tests/reports/cardano_test_suite_report.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"📄 JSON Report saved: {report_file.absolute()}")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Cardano Implementation Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python tests/cardano_test_runner.py                    # Run all tests
    python tests/cardano_test_runner.py --unit --verbose   # Run unit tests with verbose output
    python tests/cardano_test_runner.py --e2e --report     # Run E2E tests and generate report
    python tests/cardano_test_runner.py --security         # Run security tests only
        """
    )
    
    # Test category arguments
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--all", action="store_true", help="Run all test categories")
    
    # Options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--report", "-r", action="store_true", help="Generate test reports")
    
    args = parser.parse_args()
    
    # Determine which categories to run
    categories = []
    
    if args.unit:
        categories.append("unit")
    if args.integration:
        categories.append("integration")
    if args.e2e:
        categories.append("e2e")
    if args.performance:
        categories.append("performance")
    if args.security:
        categories.append("security")
    
    # If no specific categories or --all specified, run all
    if not categories or args.all:
        categories = ["unit", "integration", "e2e", "performance", "security"]
    
    # Create test runner
    runner = CardanoTestRunner(verbose=args.verbose, generate_report=args.report)
    
    # Print header
    runner.print_header()
    
    # Run tests
    success = runner.run_categories(categories)
    
    if success:
        # Print summary
        runner.print_summary()
        
        # Save JSON report
        if args.report:
            runner.save_json_report()
        
        # Exit with appropriate code
        all_passed = all(r["success"] for r in runner.test_results.values())
        critical_passed = all(
            r["success"] for r in runner.test_results.values() 
            if r["importance"] == "critical"
        )
        
        if all_passed:
            sys.exit(0)  # All tests passed
        elif critical_passed:
            sys.exit(1)  # Some non-critical tests failed
        else:
            sys.exit(2)  # Critical tests failed
    else:
        sys.exit(3)  # Setup/dependency issues


if __name__ == "__main__":
    main()