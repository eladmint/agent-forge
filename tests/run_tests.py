#!/usr/bin/env python3
"""
Agent Forge Test Runner

Comprehensive test execution script for the Agent Forge framework.
Provides different test execution modes and reporting options.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Any


class TestRunner:
    """Agent Forge test execution manager."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests"
        
    def run_tests(self, test_type: str = "all", verbose: bool = False, 
                  coverage: bool = True, parallel: bool = False) -> Dict[str, Any]:
        """
        Run tests with specified configuration.
        
        Args:
            test_type: Type of tests to run ('unit', 'integration', 'e2e', 'all')
            verbose: Enable verbose output
            coverage: Enable coverage reporting
            parallel: Enable parallel test execution
            
        Returns:
            Test execution results
        """
        print(f"🧪 Running Agent Forge {test_type} tests...")
        print(f"📁 Project root: {self.project_root}")
        print(f"🔍 Test directory: {self.test_dir}")
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
        # Add test path based on type
        if test_type == "unit":
            cmd.append(str(self.test_dir / "unit"))
        elif test_type == "integration":
            cmd.append(str(self.test_dir / "integration"))
        elif test_type == "e2e":
            cmd.append(str(self.test_dir / "e2e"))
        elif test_type == "all":
            cmd.append(str(self.test_dir))
        else:
            raise ValueError(f"Unknown test type: {test_type}")
        
        # Add markers for test filtering
        if test_type != "all":
            cmd.extend(["-m", test_type])
        
        # Add verbose flag
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Add coverage options
        if coverage:
            cmd.extend([
                "--cov=core",
                "--cov=examples", 
                "--cov-report=term-missing",
                "--cov-report=html:tests/reports/coverage",
                "--cov-fail-under=70"
            ])
        
        # Add parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add additional options
        cmd.extend([
            "--tb=short",
            "--strict-markers",
            "--disable-warnings"
        ])
        
        # Create reports directory
        reports_dir = self.test_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        print(f"▶️ Executing: {' '.join(cmd)}")
        print("-" * 60)
        
        start_time = time.time()
        
        # Execute tests
        result = subprocess.run(
            cmd,
            cwd=self.project_root,
            capture_output=False,
            text=True
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print("-" * 60)
        print(f"⏱️ Test execution completed in {execution_time:.2f} seconds")
        
        # Determine result status
        if result.returncode == 0:
            print("✅ All tests passed!")
            status = "success"
        else:
            print("❌ Some tests failed!")
            status = "failed"
        
        return {
            "status": status,
            "return_code": result.returncode,
            "execution_time": execution_time,
            "test_type": test_type,
            "verbose": verbose,
            "coverage": coverage
        }
    
    def run_quick_tests(self) -> Dict[str, Any]:
        """Run quick test suite for rapid feedback."""
        print("🚀 Running quick test suite...")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir / "unit"),
            "-q",
            "--tb=line",
            "--disable-warnings",
            "-x"  # Stop on first failure
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, cwd=self.project_root)
        end_time = time.time()
        
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "return_code": result.returncode,
            "execution_time": end_time - start_time,
            "test_type": "quick"
        }
    
    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run smoke tests to verify basic functionality."""
        print("💨 Running smoke tests...")
        
        smoke_tests = [
            self._test_imports(),
            self._test_cli_help(),
            self._test_agent_discovery()
        ]
        
        all_passed = all(test["passed"] for test in smoke_tests)
        
        print(f"\n📊 Smoke test results:")
        for test in smoke_tests:
            status = "✅" if test["passed"] else "❌"
            print(f"  {status} {test['name']}: {test['message']}")
        
        return {
            "status": "success" if all_passed else "failed",
            "tests": smoke_tests,
            "test_type": "smoke"
        }
    
    def _test_imports(self) -> Dict[str, Any]:
        """Test that core imports work."""
        try:
            # Add project root to Python path
            import sys
            sys.path.insert(0, str(self.project_root))
            
            import core.agents.base
            import examples.simple_navigation_agent
            import examples.nmkr_auditor_agent
            import cli
            
            return {
                "name": "Core Imports",
                "passed": True,
                "message": "All core modules imported successfully"
            }
        except Exception as e:
            return {
                "name": "Core Imports", 
                "passed": False,
                "message": f"Import failed: {e}"
            }
    
    def _test_cli_help(self) -> Dict[str, Any]:
        """Test that CLI help works."""
        try:
            result = subprocess.run(
                ["python", "cli.py", "--help"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "Agent Forge" in result.stdout:
                return {
                    "name": "CLI Help",
                    "passed": True,
                    "message": "CLI help command working"
                }
            else:
                return {
                    "name": "CLI Help",
                    "passed": False,
                    "message": f"CLI help failed: {result.stderr}"
                }
        except Exception as e:
            return {
                "name": "CLI Help",
                "passed": False,
                "message": f"CLI help error: {e}"
            }
    
    def _test_agent_discovery(self) -> Dict[str, Any]:
        """Test that agent discovery works."""
        try:
            result = subprocess.run(
                ["python", "cli.py", "list"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0 and "Available agents:" in result.stdout:
                agent_count = result.stdout.count("  ")  # Count indented agent entries
                return {
                    "name": "Agent Discovery",
                    "passed": True,
                    "message": f"Discovered {agent_count} agents"
                }
            else:
                return {
                    "name": "Agent Discovery", 
                    "passed": False,
                    "message": f"Discovery failed: {result.stderr}"
                }
        except Exception as e:
            return {
                "name": "Agent Discovery",
                "passed": False,
                "message": f"Discovery error: {e}"
            }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance benchmarks."""
        print("⚡ Running performance tests...")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "-m", "slow",
            "-v",
            "--tb=short"
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, cwd=self.project_root)
        end_time = time.time()
        
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "return_code": result.returncode,
            "execution_time": end_time - start_time,
            "test_type": "performance"
        }
    
    def generate_test_report(self) -> None:
        """Generate comprehensive test report."""
        print("📋 Generating test report...")
        
        cmd = [
            "python", "-m", "pytest",
            str(self.test_dir),
            "--cov=core",
            "--cov=examples",
            "--cov-report=html:tests/reports/coverage",
            "--cov-report=xml:tests/reports/coverage.xml",
            "--html=tests/reports/report.html",
            "--self-contained-html",
            "--tb=short"
        ]
        
        subprocess.run(cmd, cwd=self.project_root)
        
        print("📊 Test report generated:")
        print(f"  📄 HTML Report: {self.test_dir}/reports/report.html")
        print(f"  📈 Coverage Report: {self.test_dir}/reports/coverage/index.html")


def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(
        description="Agent Forge Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/run_tests.py                    # Run all tests
  python tests/run_tests.py --type unit        # Run unit tests only
  python tests/run_tests.py --quick            # Run quick test suite
  python tests/run_tests.py --smoke            # Run smoke tests
  python tests/run_tests.py --performance      # Run performance tests
  python tests/run_tests.py --report           # Generate test report
        """
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["unit", "integration", "e2e", "all"],
        default="all",
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Enable parallel test execution"
    )
    
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Run quick test suite"
    )
    
    parser.add_argument(
        "--smoke", "-s",
        action="store_true",
        help="Run smoke tests only"
    )
    
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run performance tests"
    )
    
    parser.add_argument(
        "--report", "-r",
        action="store_true",
        help="Generate comprehensive test report"
    )
    
    args = parser.parse_args()
    
    # Get project root (parent of tests directory)
    project_root = Path(__file__).parent.parent
    runner = TestRunner(project_root)
    
    try:
        if args.smoke:
            result = runner.run_smoke_tests()
        elif args.quick:
            result = runner.run_quick_tests()
        elif args.performance:
            result = runner.run_performance_tests()
        elif args.report:
            runner.generate_test_report()
            return 0
        else:
            result = runner.run_tests(
                test_type=args.type,
                verbose=args.verbose,
                coverage=not args.no_coverage,
                parallel=args.parallel
            )
        
        # Exit with appropriate code
        if result["status"] == "success":
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())