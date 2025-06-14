#!/usr/bin/env python3
"""
Test Environment Validation Script
Validates the complete test environment setup for Nuru AI
"""

import asyncio
import importlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class TestEnvironmentValidator:
    def __init__(self):
        # Load environment variables from .env file
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass  # dotenv not available, continue with system env vars

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "validations": {},
            "errors": [],
            "warnings": [],
            "recommendations": [],
        }

    def log_result(self, category, test_name, status, message="", error=None):
        """Log validation result"""
        if category not in self.results["validations"]:
            self.results["validations"][category] = {}

        self.results["validations"][category][test_name] = {
            "status": status,
            "message": message,
            "error": str(error) if error else None,
        }

        if status == "error":
            self.results["errors"].append(f"{category}.{test_name}: {message}")
        elif status == "warning":
            self.results["warnings"].append(f"{category}.{test_name}: {message}")

    def validate_python_environment(self):
        """Validate Python environment and basic requirements"""
        print("🐍 Validating Python Environment...")

        # Check Python version
        try:
            major, minor = sys.version_info[:2]
            if major >= 3 and minor >= 11:
                self.log_result(
                    "python", "version", "success", f"Python {major}.{minor}"
                )
            else:
                self.log_result(
                    "python", "version", "error", f"Python {major}.{minor} < 3.11"
                )
        except Exception as e:
            self.log_result(
                "python", "version", "error", "Could not determine Python version", e
            )

        # Check pip
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.log_result("python", "pip", "success", "pip available")
        except Exception as e:
            self.log_result("python", "pip", "error", "pip not available", e)

    def validate_core_dependencies(self):
        """Validate core Python package dependencies"""
        print("📦 Validating Core Dependencies...")

        # Map package names to import names
        core_packages = {
            "pytest": "pytest",
            "pytest_asyncio": "pytest_asyncio",
            "pytest_mock": "pytest_mock",
            "pytest_benchmark": "pytest_benchmark",
            "httpx": "httpx",
            "requests": "requests",
            "beautifulsoup4": "bs4",
            "python_dotenv": "dotenv",
            "docker": "docker",
            "psycopg2": "psycopg2",
            "playwright": "playwright",
        }

        for package_name, import_name in core_packages.items():
            try:
                importlib.import_module(import_name)
                self.log_result(
                    "dependencies", package_name, "success", "Imported successfully"
                )
            except ImportError as e:
                self.log_result(
                    "dependencies", package_name, "error", f"Import failed: {e}"
                )

    def validate_ai_dependencies(self):
        """Validate AI and ML dependencies"""
        print("🤖 Validating AI Dependencies...")

        ai_packages = [
            ("google.generativeai", "Google Generative AI"),
            ("google.cloud.aiplatform", "Google Cloud AI Platform"),
            ("supabase", "Supabase client"),
        ]

        for package, description in ai_packages:
            try:
                importlib.import_module(package)
                self.log_result(
                    "ai_dependencies", package, "success", f"{description} available"
                )
            except ImportError as e:
                self.log_result(
                    "ai_dependencies",
                    package,
                    "warning",
                    f"{description} not available: {e}",
                )

    def validate_environment_variables(self):
        """Validate required environment variables"""
        print("🔧 Validating Environment Variables...")

        required_vars = [
            ("GOOGLE_API_KEY", "Google API authentication"),
            ("SUPABASE_URL", "Database connection"),
            ("SUPABASE_KEY", "Database authentication"),
        ]

        optional_vars = [
            ("TELEGRAM_BOT_TOKEN", "Telegram bot integration"),
            ("TELEGRAM_TEST_BOT_TOKEN", "Telegram bot testing"),
            ("TELEGRAM_TEST_CHAT_ID", "Telegram testing chat"),
            ("BACKEND_API_URL", "API integration testing"),
            ("VERTEX_PROJECT_ID", "Vertex AI integration"),
            ("VERTEX_LOCATION", "Vertex AI region"),
        ]

        for var, description in required_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                masked_value = f"***{value[-4:]}" if len(value) > 4 else "***"
                self.log_result(
                    "environment", var, "success", f"{description}: {masked_value}"
                )
            else:
                self.log_result("environment", var, "error", f"{description}: Not set")

        for var, description in optional_vars:
            value = os.getenv(var)
            if value:
                masked_value = f"***{value[-4:]}" if len(value) > 4 else "***"
                self.log_result(
                    "environment", var, "success", f"{description}: {masked_value}"
                )
            else:
                self.log_result(
                    "environment", var, "warning", f"{description}: Not set (optional)"
                )

    def validate_database_connectivity(self):
        """Validate database connections"""
        print("🗄️ Validating Database Connectivity...")

        # Test Supabase connection
        try:
            import supabase

            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            if supabase_url and supabase_key:
                client = supabase.create_client(supabase_url, supabase_key)
                # Simple test query
                result = client.table("events").select("id").limit(1).execute()
                self.log_result(
                    "database",
                    "supabase",
                    "success",
                    f"Connected, {len(result.data)} test records",
                )
            else:
                self.log_result(
                    "database", "supabase", "warning", "Credentials not configured"
                )
        except Exception as e:
            self.log_result("database", "supabase", "error", "Connection failed", e)

        # Test Docker availability for testing
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, check=True
            )
            self.log_result(
                "database", "docker", "success", "Docker available for testing"
            )
        except Exception as e:
            self.log_result("database", "docker", "warning", "Docker not available", e)

    def validate_browser_automation(self):
        """Validate browser automation setup"""
        print("🌐 Validating Browser Automation...")

        try:
            from playwright.async_api import async_playwright

            async def test_browser():
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page()
                    await page.goto("data:text/html,<h1>Test</h1>")
                    title = await page.title()
                    await browser.close()
                    return title

            title = asyncio.run(test_browser())
            self.log_result(
                "browser", "playwright", "success", "Browser automation functional"
            )
        except Exception as e:
            self.log_result(
                "browser", "playwright", "error", "Browser automation failed", e
            )
            self.results["recommendations"].append(
                "Run 'playwright install chromium' to install browser binaries"
            )

    def validate_api_connectivity(self):
        """Validate API connectivity"""
        print("🔗 Validating API Connectivity...")

        # Test Google AI API
        try:
            import google.generativeai as genai

            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                # Simple test
                model = genai.GenerativeModel("gemini-pro")
                self.log_result(
                    "api", "google_ai", "success", "Google AI API accessible"
                )
            else:
                self.log_result("api", "google_ai", "warning", "API key not configured")
        except Exception as e:
            self.log_result("api", "google_ai", "error", "Google AI API test failed", e)

        # Test Telegram API
        telegram_token = os.getenv("TELEGRAM_TEST_BOT_TOKEN") or os.getenv(
            "TELEGRAM_BOT_TOKEN"
        )
        if telegram_token:
            try:
                import requests

                response = requests.get(
                    f"https://api.telegram.org/bot{telegram_token}/getMe", timeout=10
                )
                if response.status_code == 200:
                    self.log_result(
                        "api", "telegram", "success", "Telegram API accessible"
                    )
                else:
                    self.log_result(
                        "api",
                        "telegram",
                        "error",
                        f"Telegram API error: {response.status_code}",
                    )
            except Exception as e:
                self.log_result(
                    "api", "telegram", "error", "Telegram API test failed", e
                )
        else:
            self.log_result(
                "api", "telegram", "warning", "Telegram token not configured"
            )

    def validate_test_framework(self):
        """Validate test framework functionality"""
        print("🧪 Validating Test Framework...")

        # Check pytest functionality
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.log_result("testing", "pytest", "success", "pytest functional")
        except Exception as e:
            self.log_result("testing", "pytest", "error", "pytest not functional", e)

        # Check test files exist
        test_paths = [
            "tests/unit/",
            "tests/integration/",
            "tests/security/",
            "tests/performance/",
        ]

        for path in test_paths:
            if Path(path).exists():
                test_files = list(Path(path).glob("test_*.py"))
                self.log_result(
                    "testing",
                    f"tests_{path.split('/')[1]}",
                    "success",
                    f"{len(test_files)} test files found",
                )
            else:
                self.log_result(
                    "testing",
                    f"tests_{path.split('/')[1]}",
                    "warning",
                    f"Test directory {path} not found",
                )

    def validate_configuration_files(self):
        """Validate configuration files"""
        print("📄 Validating Configuration Files...")

        config_files = [
            ("pytest.ini", "pytest configuration"),
            (".env", "environment configuration"),
            ("requirements.txt", "main requirements"),
            ("config/test_requirements.txt", "test requirements"),
        ]

        for file_path, description in config_files:
            if Path(file_path).exists():
                self.log_result(
                    "configuration",
                    file_path.replace("/", "_"),
                    "success",
                    f"{description} exists",
                )
            else:
                self.log_result(
                    "configuration",
                    file_path.replace("/", "_"),
                    "warning",
                    f"{description} not found",
                )

    def generate_recommendations(self):
        """Generate setup recommendations based on validation results"""
        print("💡 Generating Recommendations...")

        error_count = len(self.results["errors"])
        warning_count = len(self.results["warnings"])

        if error_count == 0 and warning_count == 0:
            self.results["overall_status"] = "excellent"
            self.results["recommendations"].append(
                "✅ Test environment is fully configured and ready for comprehensive testing!"
            )
        elif error_count == 0:
            self.results["overall_status"] = "good"
            self.results["recommendations"].extend(
                [
                    "✅ Core test environment is functional",
                    "⚠️ Some optional features may not be available",
                    "📋 Review warnings for enhanced testing capabilities",
                ]
            )
        else:
            self.results["overall_status"] = "needs_work"
            self.results["recommendations"].extend(
                [
                    "❌ Critical issues found that need to be resolved",
                    "🔧 Install missing dependencies with: pip install -r config/test_requirements.txt",
                    "🔧 Configure missing environment variables",
                    "📖 Review TEST_ENVIRONMENT_SETUP_GUIDE.md for detailed instructions",
                ]
            )

    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 80)
        print("🧪 TEST ENVIRONMENT VALIDATION SUMMARY")
        print("=" * 80)

        # Overall status
        status_emoji = {
            "excellent": "✅",
            "good": "⚠️",
            "needs_work": "❌",
            "unknown": "❓",
        }

        print(
            f"\n{status_emoji.get(self.results['overall_status'], '❓')} "
            f"Overall Status: {self.results['overall_status'].upper()}"
        )

        # Category summary
        print("\n📊 Validation Results:")
        for category, tests in self.results["validations"].items():
            success_count = sum(1 for t in tests.values() if t["status"] == "success")
            total_count = len(tests)
            print(f"  {category.title()}: {success_count}/{total_count} passed")

        # Errors and warnings
        if self.results["errors"]:
            print(f"\n❌ Errors ({len(self.results['errors'])}):")
            for error in self.results["errors"][:5]:  # Show first 5
                print(f"  • {error}")
            if len(self.results["errors"]) > 5:
                print(f"  ... and {len(self.results['errors']) - 5} more")

        if self.results["warnings"]:
            print(f"\n⚠️ Warnings ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"][:5]:  # Show first 5
                print(f"  • {warning}")
            if len(self.results["warnings"]) > 5:
                print(f"  ... and {len(self.results['warnings']) - 5} more")

        # Recommendations
        if self.results["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in self.results["recommendations"]:
                print(f"  • {rec}")

        print("\n📄 Detailed report saved to: test_environment_validation_report.json")
        print("=" * 80)

    def save_report(self):
        """Save detailed validation report"""
        with open("test_environment_validation_report.json", "w") as f:
            json.dump(self.results, f, indent=2)

    def run_all_validations(self):
        """Run all validation checks"""
        print("🧪 NURU AI TEST ENVIRONMENT VALIDATION")
        print("=" * 50)

        try:
            self.validate_python_environment()
            self.validate_core_dependencies()
            self.validate_ai_dependencies()
            self.validate_environment_variables()
            self.validate_database_connectivity()
            self.validate_browser_automation()
            self.validate_api_connectivity()
            self.validate_test_framework()
            self.validate_configuration_files()
            self.generate_recommendations()

        except KeyboardInterrupt:
            print("\n\n⚠️ Validation interrupted by user")
            self.results["overall_status"] = "interrupted"

        except Exception as e:
            print(f"\n\n❌ Validation failed with error: {e}")
            self.results["overall_status"] = "failed"
            self.results["errors"].append(f"Validation process error: {e}")

        finally:
            self.print_summary()
            self.save_report()

        return self.results["overall_status"] in ["excellent", "good"]


def main():
    """Main entry point"""
    validator = TestEnvironmentValidator()
    success = validator.run_all_validations()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
