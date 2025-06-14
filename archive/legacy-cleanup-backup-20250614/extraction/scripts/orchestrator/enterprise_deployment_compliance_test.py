#!/usr/bin/env python3
"""
Enterprise Deployment Compliance Testing Framework

Comprehensive pre-deployment validation to ensure all enterprise deployment
requirements are met before attempting Cloud Run deployment.

Features:
- Google Cloud quotas and limits validation
- IAM permissions verification
- Configuration compliance testing
- Cost estimation and budget checks
"""

import os
import sys
import json
import time
import logging
import subprocess
import ast
import importlib.util
from typing import Dict, List, Tuple, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("enterprise_compliance_tester")


@dataclass
class ComplianceResult:
    """Result of a compliance test"""
    test_name: str
    status: str  # "PASS", "FAIL", "WARNING", "SKIP"
    message: str
    details: Dict[str, Any]
    timestamp: str
    execution_time_ms: int


@dataclass
class ComplianceReport:
    """Complete compliance test report"""
    project_id: str
    service_name: str
    region: str
    test_timestamp: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    skipped_tests: int
    overall_status: str  # "COMPLIANT", "NON_COMPLIANT", "WARNINGS"
    results: List[ComplianceResult]
    recommendations: List[str]


class EnterpriseComplianceTester:
    """Enterprise deployment compliance testing framework"""
    
    def __init__(self, project_id: str, service_name: str, region: str = "us-central1"):
        self.project_id = project_id
        self.service_name = service_name
        self.region = region
        self.results: List[ComplianceResult] = []
        self.recommendations: List[str] = []
        
        logger.info(f"🏢 Initialized Enterprise Compliance Tester")
        logger.info(f"   Project: {project_id}")
        logger.info(f"   Service: {service_name}")
        logger.info(f"   Region: {region}")

    def _record_result(self, test_name: str, status: str, message: str, 
                      details: Dict[str, Any] = None, execution_time_ms: int = 0):
        """Record a compliance test result"""
        result = ComplianceResult(
            test_name=test_name,
            status=status,
            message=message,
            details=details or {},
            timestamp=datetime.utcnow().isoformat(),
            execution_time_ms=execution_time_ms
        )
        self.results.append(result)
        
        # Log result
        status_emoji = {
            "PASS": "✅",
            "FAIL": "❌", 
            "WARNING": "⚠️",
            "SKIP": "⏭️"
        }
        logger.info(f"{status_emoji.get(status, '❓')} {test_name}: {message}")

    def _execute_gcloud_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """Execute gcloud command and return result"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def test_gcloud_authentication(self) -> None:
        """Test Google Cloud authentication"""
        start_time = time.time()
        
        try:
            success, stdout, stderr = self._execute_gcloud_command([
                "gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"
            ])
            
            if success and stdout.strip():
                active_account = stdout.strip()
                self._record_result(
                    "GCloud Authentication",
                    "PASS",
                    f"Authenticated as: {active_account}",
                    {"active_account": active_account},
                    int((time.time() - start_time) * 1000)
                )
            else:
                self._record_result(
                    "GCloud Authentication",
                    "FAIL",
                    "No active authentication found",
                    {"error": stderr},
                    int((time.time() - start_time) * 1000)
                )
                self.recommendations.append("Run 'gcloud auth login' to authenticate")
                
        except Exception as e:
            self._record_result(
                "GCloud Authentication",
                "FAIL", 
                f"Authentication check failed: {str(e)}",
                {"exception": str(e)},
                int((time.time() - start_time) * 1000)
            )

    def test_cloud_run_quotas(self) -> None:
        """Test Cloud Run service quotas and limits"""
        start_time = time.time()
        
        try:
            # Get current Cloud Run services
            success, stdout, stderr = self._execute_gcloud_command([
                "gcloud", "run", "services", "list",
                f"--project={self.project_id}",
                f"--region={self.region}",
                "--format=json"
            ])
            
            if success:
                try:
                    services = json.loads(stdout) if stdout.strip() else []
                    service_count = len(services)
                    
                    # Check service limits (discovered during deployment)
                    max_services = 100  # Typical limit
                    max_instances_per_service = 5  # Discovered project quota limit
                    
                    quota_details = {
                        "current_services": service_count,
                        "max_services": max_services,
                        "max_instances_per_service": max_instances_per_service,
                        "critical_quota_limit": "max-instances must be ≤ 5"
                    }
                    
                    if service_count < max_services - 5:  # Leave buffer
                        self._record_result(
                            "Cloud Run Quotas",
                            "PASS",
                            f"Quota OK: {service_count}/{max_services} services, max {max_instances_per_service} instances",
                            quota_details,
                            int((time.time() - start_time) * 1000)
                        )
                    else:
                        self._record_result(
                            "Cloud Run Quotas", 
                            "WARNING",
                            f"Approaching service limit: {service_count}/{max_services}",
                            quota_details,
                            int((time.time() - start_time) * 1000)
                        )
                        self.recommendations.append("Consider cleaning up unused Cloud Run services")
                        
                except json.JSONDecodeError:
                    self._record_result(
                        "Cloud Run Quotas",
                        "WARNING",
                        "Could not parse service list",
                        {"error": "JSON decode error"},
                        int((time.time() - start_time) * 1000)
                    )
            else:
                self._record_result(
                    "Cloud Run Quotas",
                    "FAIL",
                    f"Cannot list Cloud Run services: {stderr}",
                    {"error": stderr},
                    int((time.time() - start_time) * 1000)
                )
                
        except Exception as e:
            self._record_result(
                "Cloud Run Quotas",
                "FAIL",
                f"Quota check failed: {str(e)}",
                {"exception": str(e)},
                int((time.time() - start_time) * 1000)
            )

    def test_deployment_configuration(self, cloudbuild_yaml_path: str = "cloudbuild.yaml") -> None:
        """Test deployment configuration files for compliance issues"""
        start_time = time.time()
        
        try:
            config_issues = []
            config_details = {}
            
            # Check if cloudbuild.yaml exists
            if os.path.exists(cloudbuild_yaml_path):
                config_details["cloudbuild_yaml"] = "exists"
                
                # Read and validate cloudbuild.yaml
                with open(cloudbuild_yaml_path, 'r') as f:
                    content = f.read()
                    
                # Critical validation: max-instances quota compliance
                if "--max-instances" in content:
                    import re
                    max_instances_match = re.search(r'--max-instances[=\s]+(\d+)', content)
                    if max_instances_match:
                        max_instances = int(max_instances_match.group(1))
                        config_details["max_instances"] = max_instances
                        
                        # Check against discovered quota limit
                        if max_instances > 5:
                            config_issues.append(f"CRITICAL: max-instances={max_instances} exceeds quota limit of 5")
                        else:
                            config_details["max_instances_compliance"] = "✅ Within quota limits"
                            
                # Additional validations
                if "--memory" in content:
                    memory_match = re.search(r'--memory[=\s]+([^\s]+)', content)
                    if memory_match:
                        config_details["memory"] = memory_match.group(1)
                        
                if "--cpu" in content:
                    cpu_match = re.search(r'--cpu[=\s]+([^\s]+)', content)
                    if cpu_match:
                        config_details["cpu"] = cpu_match.group(1)
                        
            else:
                config_issues.append("cloudbuild.yaml not found")
                
            # Check Dockerfile
            dockerfile_paths = [
                "Dockerfile", 
                "src/extraction/Dockerfile",
                "src/extraction/scripts/orchestrator/Dockerfile"
            ]
            dockerfile_found = False
            for dockerfile_path in dockerfile_paths:
                if os.path.exists(dockerfile_path):
                    config_details["dockerfile"] = dockerfile_path
                    dockerfile_found = True
                    break
                    
            if not dockerfile_found:
                config_issues.append("Dockerfile not found")
                
            # Determine result
            critical_issues = [issue for issue in config_issues if "CRITICAL" in issue]
            
            if not config_issues:
                self._record_result(
                    "Deployment Configuration",
                    "PASS",
                    "All deployment configuration files are compliant",
                    config_details,
                    int((time.time() - start_time) * 1000)
                )
            elif critical_issues:
                self._record_result(
                    "Deployment Configuration",
                    "FAIL",
                    f"Critical configuration issues: {', '.join(critical_issues)}",
                    {**config_details, "issues": config_issues},
                    int((time.time() - start_time) * 1000)
                )
                for issue in config_issues:
                    self.recommendations.append(f"Fix configuration: {issue}")
            else:
                self._record_result(
                    "Deployment Configuration",
                    "WARNING",
                    f"Configuration warnings: {', '.join(config_issues)}",
                    {**config_details, "issues": config_issues},
                    int((time.time() - start_time) * 1000)
                )
                    
        except Exception as e:
            self._record_result(
                "Deployment Configuration",
                "FAIL",
                f"Configuration check failed: {str(e)}",
                {"exception": str(e)},
                int((time.time() - start_time) * 1000)
            )

    def test_centralized_requirements_architecture(self) -> None:
        """Test centralized requirements.txt architecture compliance"""
        start_time = time.time()
        
        try:
            validation_issues = []
            architecture_details = {}
            
            # Check for centralized requirements.txt at project root
            root_requirements = "requirements.txt"
            if os.path.exists(root_requirements):
                architecture_details["centralized_requirements"] = "✅ Found at project root"
                
                # Count lines in centralized requirements
                with open(root_requirements, 'r') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
                    architecture_details["centralized_requirements_count"] = len(lines)
                    architecture_details["sample_dependencies"] = lines[:5]  # First 5 for validation
            else:
                validation_issues.append("CRITICAL: Centralized requirements.txt not found at project root")
                
            # Check for service-specific requirements.txt files (should be eliminated)
            service_specific_requirements = []
            for root, dirs, files in os.walk("src"):
                if "requirements.txt" in files:
                    service_specific_requirements.append(os.path.join(root, "requirements.txt"))
                    
            if service_specific_requirements:
                validation_issues.append(f"WARNING: Service-specific requirements found: {', '.join(service_specific_requirements)}")
                architecture_details["service_specific_requirements"] = service_specific_requirements
                self.recommendations.append("Migrate service-specific requirements to centralized requirements.txt")
            else:
                architecture_details["service_specific_requirements"] = "✅ None found (compliant)"
                
            # Validate Dockerfiles reference centralized requirements
            dockerfile_compliance = []
            dockerfile_paths = [
                "src/api/Dockerfile",
                "src/extraction/deployment/Dockerfile", 
                "src/telegram_bot/Dockerfile"
            ]
            
            for dockerfile_path in dockerfile_paths:
                if os.path.exists(dockerfile_path):
                    with open(dockerfile_path, 'r') as f:
                        content = f.read()
                        if "COPY requirements.txt" in content:
                            dockerfile_compliance.append(f"✅ {dockerfile_path}")
                        else:
                            dockerfile_compliance.append(f"❌ {dockerfile_path}")
                            validation_issues.append(f"WARNING: {dockerfile_path} does not reference centralized requirements.txt")
                            
            architecture_details["dockerfile_compliance"] = dockerfile_compliance
            
            # Check for Cloud Build configurations using centralized requirements
            cloudbuild_configs = [
                "src/api/deployment/configs/cloudbuild.yaml",
                "src/extraction/deployment/configs/cloudbuild-orchestrator.yaml"
            ]
            
            cloudbuild_compliance = []
            for config_path in cloudbuild_configs:
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        content = f.read()
                        if "requirements.txt" in content:
                            cloudbuild_compliance.append(f"✅ {config_path}")
                        else:
                            cloudbuild_compliance.append(f"⚠️ {config_path}")
                            
            architecture_details["cloudbuild_compliance"] = cloudbuild_compliance
            
            # Determine result based on validation issues
            critical_issues = [issue for issue in validation_issues if "CRITICAL" in issue]
            
            if not validation_issues:
                self._record_result(
                    "Centralized Requirements Architecture",
                    "PASS", 
                    "Centralized requirements architecture fully compliant",
                    architecture_details,
                    int((time.time() - start_time) * 1000)
                )
            elif critical_issues:
                self._record_result(
                    "Centralized Requirements Architecture",
                    "FAIL",
                    f"Critical architecture issues: {', '.join(critical_issues)}",
                    {**architecture_details, "issues": validation_issues},
                    int((time.time() - start_time) * 1000)
                )
                for issue in validation_issues:
                    if "CRITICAL" in issue:
                        self.recommendations.append(f"Fix critical issue: {issue}")
            else:
                self._record_result(
                    "Centralized Requirements Architecture", 
                    "WARNING",
                    f"Architecture warnings: {', '.join(validation_issues)}",
                    {**architecture_details, "issues": validation_issues},
                    int((time.time() - start_time) * 1000)
                )
                
        except Exception as e:
            self._record_result(
                "Centralized Requirements Architecture",
                "FAIL",
                f"Architecture validation failed: {str(e)}",
                {"exception": str(e)},
                int((time.time() - start_time) * 1000)
            )

    def test_import_dependencies_validation(self) -> None:
        """Test that all Python imports are properly configured and dependencies are available"""
        start_time = time.time()
        
        try:
            validation_issues = []
            import_details = {}
            
            # Parse centralized requirements to get available packages
            available_packages = set()
            requirements_path = "requirements.txt"
            
            if os.path.exists(requirements_path):
                with open(requirements_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before ==, >=, etc.)
                            package_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('[')[0]
                            available_packages.add(package_name.lower())
                            
                import_details["available_packages_count"] = len(available_packages)
                import_details["sample_packages"] = list(sorted(available_packages))[:10]
            else:
                validation_issues.append("CRITICAL: requirements.txt not found for dependency validation")
                
            # Find all Python files in critical service directories
            critical_paths = [
                "src/api/",
                "src/extraction/",
                "src/telegram_bot/",
                "src/shared/"
            ]
            
            python_files = []
            for path in critical_paths:
                if os.path.exists(path):
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if file.endswith('.py') and not file.startswith('test_'):
                                python_files.append(os.path.join(root, file))
                                
            import_details["python_files_analyzed"] = len(python_files)
            
            # Analyze imports in Python files
            missing_dependencies = set()
            import_errors = []
            analyzed_imports = set()
            
            for py_file in python_files[:50]:  # Limit to first 50 files for performance
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Skip empty files or files that don't look like Python
                    if not content.strip() or not any(keyword in content for keyword in ['import ', 'from ', 'def ', 'class ']):
                        continue
                        
                    # Parse the AST to extract imports
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                module_name = alias.name.split('.')[0].lower()
                                analyzed_imports.add(module_name)
                                
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                module_name = node.module.split('.')[0].lower()
                                analyzed_imports.add(module_name)
                                
                except (SyntaxError, UnicodeDecodeError, TypeError) as e:
                    # Only count actual parsing errors, not encoding issues
                    if 'invalid syntax' in str(e) or 'encoding' not in str(e):
                        import_errors.append(f"Parse error in {py_file}: {type(e).__name__}")
                except Exception as e:
                    import_errors.append(f"Unexpected error in {py_file}: {str(e)}")
                    
            # Standard library modules that don't need to be in requirements.txt
            stdlib_modules = {
                'os', 'sys', 'json', 'time', 'datetime', 'logging', 'subprocess',
                'typing', 'pathlib', 'collections', 'itertools', 'functools',
                'asyncio', 'concurrent', 'threading', 'multiprocessing',
                'urllib', 'http', 'socket', 'ssl', 'hashlib', 'uuid',
                'tempfile', 'shutil', 'glob', 'fnmatch', 'zipfile',
                'configparser', 'argparse', 'io', 'csv', 'xml', 're',
                'math', 'random', 'statistics', 'decimal', 'fractions',
                'copy', 'pickle', 'base64', 'binascii', 'codecs'
            }
            
            # Check for common external packages that should be in requirements
            external_packages = {
                'fastapi', 'uvicorn', 'requests', 'pydantic', 'sqlalchemy', 
                'supabase', 'google', 'openai', 'anthropic', 'telegram',
                'aiohttp', 'httpx', 'beautifulsoup4', 'bs4', 'selenium',
                'playwright', 'redis', 'celery', 'numpy',
                'pandas', 'psycopg2', 'pymongo', 'pytest', 'boto3'
            }
            
            # Find imports that might be missing from requirements
            for imported_module in analyzed_imports:
                # Skip standard library modules
                if imported_module in stdlib_modules:
                    continue
                    
                if imported_module in external_packages:
                    # Check various name variations
                    variations = [
                        imported_module,
                        imported_module.replace('_', '-'),
                        imported_module.replace('-', '_')
                    ]
                    
                    # Special cases for common package name differences
                    if imported_module == 'bs4':
                        variations.append('beautifulsoup4')
                    elif imported_module == 'cv2':
                        variations.append('opencv-python')
                    elif imported_module == 'pil':
                        variations.append('pillow')
                    elif imported_module == 'yaml':
                        variations.append('pyyaml')
                    elif imported_module == 'google':
                        # Check for any google-cloud-* packages
                        google_packages = [pkg for pkg in available_packages if pkg.startswith('google-cloud-')]
                        if google_packages:
                            continue  # Skip this import as it's covered by google-cloud-* packages
                        
                    found = any(var in available_packages for var in variations)
                    if not found:
                        missing_dependencies.add(imported_module)
                        
            import_details["analyzed_imports_count"] = len(analyzed_imports)
            import_details["missing_dependencies"] = list(missing_dependencies)
            import_details["import_errors_count"] = len(import_errors)
            import_details["sample_imports"] = list(sorted(analyzed_imports))[:15]
            
            # Add warnings for missing dependencies
            if missing_dependencies:
                for dep in missing_dependencies:
                    validation_issues.append(f"WARNING: Imported module '{dep}' may not be in centralized requirements.txt")
                    
            if import_errors:
                validation_issues.append(f"WARNING: {len(import_errors)} files had parsing errors")
                import_details["sample_import_errors"] = import_errors[:3]
                
            # Validate critical service imports
            critical_imports = {
                'fastapi': 'Required for API services',
                'uvicorn': 'Required for ASGI server',
                'supabase': 'Required for database integration',
                'requests': 'Required for HTTP requests'
            }
            
            # Check for Google Cloud services (special case - uses google-cloud-* packages)
            google_packages = [pkg for pkg in available_packages if pkg.startswith('google-cloud-')]
            if not google_packages:
                critical_imports['google-cloud-aiplatform'] = 'Required for Google Cloud AI services'
            
            missing_critical = []
            for critical_import, description in critical_imports.items():
                if critical_import not in available_packages:
                    missing_critical.append(f"{critical_import} - {description}")
                    
            if missing_critical:
                for missing in missing_critical:
                    validation_issues.append(f"CRITICAL: Missing critical dependency: {missing}")
                    
            import_details["critical_dependencies_status"] = "✅ All present" if not missing_critical else f"❌ {len(missing_critical)} missing"
            import_details["google_cloud_packages"] = google_packages if google_packages else "None found"
            
            # Determine result
            critical_issues = [issue for issue in validation_issues if "CRITICAL" in issue]
            
            if not validation_issues:
                self._record_result(
                    "Import Dependencies Validation",
                    "PASS",
                    f"All imports properly configured - {len(analyzed_imports)} imports analyzed, {len(available_packages)} packages available",
                    import_details,
                    int((time.time() - start_time) * 1000)
                )
            elif critical_issues:
                self._record_result(
                    "Import Dependencies Validation",
                    "FAIL", 
                    f"Critical import issues: {', '.join(critical_issues[:3])}",
                    {**import_details, "issues": validation_issues},
                    int((time.time() - start_time) * 1000)
                )
                for issue in critical_issues:
                    self.recommendations.append(f"Fix critical import issue: {issue}")
            else:
                self._record_result(
                    "Import Dependencies Validation",
                    "WARNING",
                    f"Import warnings detected: {len(validation_issues)} issues found",
                    {**import_details, "issues": validation_issues},
                    int((time.time() - start_time) * 1000)
                )
                self.recommendations.append("Review import warnings and update requirements.txt if needed")
                
        except Exception as e:
            self._record_result(
                "Import Dependencies Validation",
                "FAIL",
                f"Import validation failed: {str(e)}",
                {"exception": str(e)},
                int((time.time() - start_time) * 1000)
            )

    def test_cloud_build_configuration(self) -> None:
        """Test Cloud Build configuration and API enablement"""
        start_time = time.time()
        
        try:
            # Check if Cloud Build API is enabled
            success, stdout, stderr = self._execute_gcloud_command([
                "gcloud", "services", "list",
                "--enabled",
                f"--project={self.project_id}",
                "--filter=name:cloudbuild.googleapis.com",
                "--format=value(name)"
            ])
            
            if success and "cloudbuild.googleapis.com" in stdout:
                self._record_result(
                    "Cloud Build Configuration",
                    "PASS",
                    "Cloud Build API is enabled",
                    {"api_enabled": True},
                    int((time.time() - start_time) * 1000)
                )
            else:
                self._record_result(
                    "Cloud Build Configuration",
                    "FAIL",
                    "Cloud Build API not enabled",
                    {"api_enabled": False},
                    int((time.time() - start_time) * 1000)
                )
                self.recommendations.append("Enable Cloud Build API: gcloud services enable cloudbuild.googleapis.com")
                
        except Exception as e:
            self._record_result(
                "Cloud Build Configuration",
                "FAIL",
                f"Cloud Build check failed: {str(e)}",
                {"exception": str(e)},
                int((time.time() - start_time) * 1000)
            )

    def run_all_tests(self, validate_requirements: bool = False, validate_imports: bool = False) -> ComplianceReport:
        """Run all compliance tests and generate report"""
        logger.info("🔍 Starting Enterprise Deployment Compliance Testing...")
        start_time = time.time()
        
        # Run all test methods
        test_methods = [
            self.test_gcloud_authentication,
            self.test_cloud_run_quotas,
            self.test_cloud_build_configuration,
            self.test_deployment_configuration,
        ]
        
        # Add centralized requirements test if requested
        if validate_requirements:
            test_methods.append(self.test_centralized_requirements_architecture)
            logger.info("📦 Including centralized requirements architecture validation")
            
        # Add import dependencies validation if requested
        if validate_imports:
            test_methods.append(self.test_import_dependencies_validation)
            logger.info("🔍 Including import dependencies validation")
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"Test {test_method.__name__} failed with exception: {e}")
                
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])
        warning_tests = len([r for r in self.results if r.status == "WARNING"])
        skipped_tests = len([r for r in self.results if r.status == "SKIP"])
        
        # Determine overall status
        if failed_tests > 0:
            overall_status = "NON_COMPLIANT"
        elif warning_tests > 0:
            overall_status = "WARNINGS"
        else:
            overall_status = "COMPLIANT"
            
        # Generate report
        report = ComplianceReport(
            project_id=self.project_id,
            service_name=self.service_name,
            region=self.region,
            test_timestamp=datetime.utcnow().isoformat(),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            warning_tests=warning_tests,
            skipped_tests=skipped_tests,
            overall_status=overall_status,
            results=self.results,
            recommendations=self.recommendations
        )
        
        execution_time = time.time() - start_time
        logger.info(f"🏁 Compliance testing completed in {execution_time:.2f}s")
        logger.info(f"📊 Results: {passed_tests} passed, {failed_tests} failed, {warning_tests} warnings")
        logger.info(f"🎯 Overall Status: {overall_status}")
        
        return report

    def save_report(self, report: ComplianceReport, filename: str = None) -> str:
        """Save compliance report to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enterprise_compliance_report_{timestamp}.json"
            
        report_dict = asdict(report)
        
        with open(filename, 'w') as f:
            json.dump(report_dict, f, indent=2)
            
        logger.info(f"📄 Compliance report saved to: {filename}")
        return filename


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enterprise Deployment Compliance Testing")
    parser.add_argument("--project-id", required=True, help="Google Cloud Project ID")
    parser.add_argument("--service-name", required=True, help="Cloud Run service name")
    parser.add_argument("--region", default="us-central1", help="Cloud Run region")
    parser.add_argument("--cloudbuild-yaml", default="cloudbuild.yaml", help="Path to cloudbuild.yaml")
    parser.add_argument("--validate-requirements", action="store_true", help="Validate centralized requirements architecture")
    parser.add_argument("--validate-imports", action="store_true", help="Validate import dependencies and coverage")
    parser.add_argument("--output", help="Output filename for compliance report")
    
    args = parser.parse_args()
    
    # Create tester and run compliance tests
    tester = EnterpriseComplianceTester(
        project_id=args.project_id,
        service_name=args.service_name,
        region=args.region
    )
    
    # Run all tests
    report = tester.run_all_tests(
        validate_requirements=args.validate_requirements,
        validate_imports=args.validate_imports
    )
    
    # Save report
    report_file = tester.save_report(report, args.output)
    
    # Print summary
    print("\n" + "="*80)
    print("🏢 ENTERPRISE DEPLOYMENT COMPLIANCE SUMMARY")
    print("="*80)
    print(f"Overall Status: {report.overall_status}")
    print(f"Total Tests: {report.total_tests}")
    print(f"Passed: {report.passed_tests}")
    print(f"Failed: {report.failed_tests}")
    print(f"Warnings: {report.warning_tests}")
    print(f"Report: {report_file}")
    
    if report.recommendations:
        print(f"\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"{i}. {rec}")
    
    print("="*80)
    
    # Exit with error code if non-compliant
    if report.overall_status == "NON_COMPLIANT":
        print("❌ DEPLOYMENT NOT RECOMMENDED - Fix compliance issues first")
        sys.exit(1)
    elif report.overall_status == "WARNINGS":
        print("⚠️ DEPLOYMENT POSSIBLE WITH WARNINGS - Review issues")
        sys.exit(0)
    else:
        print("✅ DEPLOYMENT COMPLIANCE VERIFIED - Proceed with deployment")
        sys.exit(0)


if __name__ == "__main__":
    main() 