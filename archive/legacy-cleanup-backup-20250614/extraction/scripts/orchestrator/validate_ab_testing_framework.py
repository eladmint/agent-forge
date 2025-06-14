#!/usr/bin/env python3
"""
Validate A/B Testing Framework for Production Orchestrator v2

This script validates the A/B testing framework functionality:
- Tests Multi-Agent Pipeline vs Legacy Orchestrator routing
- Validates performance metrics collection
- Confirms gradual rollout percentages work correctly
- Tests service health and configuration endpoints
"""

import os
import sys
import asyncio
import requests
import json
import time
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.getcwd())

from api.utils.logging_utils import get_logger

logger = get_logger("ab_testing_validator")


class ABTestingValidator:
    """Validate A/B testing framework functionality"""

    def __init__(self, service_url: str):
        self.service_url = service_url.rstrip("/")
        self.test_urls = [
            "https://lu.ma/ethcc",
            "https://lu.ma/ethdenver",
            "https://lu.ma/devcon",
        ]

    async def validate_health_endpoint(self) -> Dict[str, Any]:
        """Validate service health and A/B testing status"""
        logger.info("🏥 Validating health endpoint...")

        try:
            health_url = f"{self.service_url}/health"
            response = requests.get(health_url, timeout=30)

            if response.status_code != 200:
                raise Exception(f"Health check failed: {response.status_code}")

            health_data = response.json()

            logger.info("✅ Health endpoint validation passed:")
            logger.info(f"   Status: {health_data.get('status')}")
            logger.info(f"   Version: {health_data.get('version')}")
            logger.info(
                f"   Legacy Orchestrator: {health_data.get('main_extractor_status')}"
            )
            logger.info(
                f"   Multi-Agent Pipeline: {health_data.get('multi_agent_pipeline_status')}"
            )
            logger.info(f"   Database: {health_data.get('database_connection')}")

            # Validate A/B testing config in health response
            ab_config = health_data.get("ab_testing_config", {})
            logger.info(f"   A/B Testing Enabled: {ab_config.get('enabled')}")
            logger.info(f"   Multi-Agent Percentage: {ab_config.get('percentage')}%")

            return health_data

        except Exception as e:
            logger.error(f"❌ Health endpoint validation failed: {e}")
            raise

    async def validate_ab_testing_config(self) -> Dict[str, Any]:
        """Validate A/B testing configuration endpoints"""
        logger.info("⚗️ Validating A/B testing configuration...")

        try:
            # Get current config
            config_url = f"{self.service_url}/ab-testing/config"
            response = requests.get(config_url, timeout=30)

            if response.status_code != 200:
                raise Exception(f"A/B config retrieval failed: {response.status_code}")

            config = response.json()
            logger.info("✅ A/B testing configuration retrieved:")
            logger.info(f"   Enabled: {config.get('enabled')}")
            logger.info(f"   Percentage: {config.get('percentage')}%")
            logger.info(f"   Total Requests: {config.get('total_requests')}")
            logger.info(
                f"   Multi-Agent Requests: {config.get('multi_agent_requests')}"
            )

            # Test configuration update
            logger.info("🔧 Testing A/B configuration update...")
            update_url = f"{self.service_url}/ab-testing/update"

            # Test with 20% Multi-Agent Pipeline traffic
            update_response = requests.post(
                update_url, params={"enable": True, "percentage": 20}, timeout=30
            )

            if update_response.status_code == 200:
                logger.info("✅ A/B testing configuration update successful")
            else:
                logger.warning(
                    f"⚠️ A/B config update failed: {update_response.status_code}"
                )

            # Verify config was updated
            verify_response = requests.get(config_url, timeout=30)
            if verify_response.status_code == 200:
                new_config = verify_response.json()
                if new_config.get("percentage") == 20:
                    logger.info("✅ Configuration update verified")
                else:
                    logger.warning(
                        f"⚠️ Config not updated correctly: {new_config.get('percentage')}%"
                    )

            return config

        except Exception as e:
            logger.error(f"❌ A/B testing configuration validation failed: {e}")
            raise

    async def test_extraction_routing(self, num_requests: int = 10) -> Dict[str, Any]:
        """Test extraction requests to validate A/B routing"""
        logger.info(f"🔄 Testing extraction routing with {num_requests} requests...")

        results = {
            "total_requests": 0,
            "multi_agent_requests": 0,
            "legacy_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_processing_time": 0,
            "responses": [],
        }

        total_processing_time = 0

        for i in range(num_requests):
            try:
                logger.info(f"📤 Sending test request {i + 1}/{num_requests}...")

                # Use a small subset of test URLs for faster testing
                test_request = {
                    "urls": [self.test_urls[i % len(self.test_urls)]],
                    "save_to_database": False,  # Don't save test data
                    "debug_mode": False,
                    "timeout_per_event": 60,  # Shorter timeout for testing
                }

                extract_url = f"{self.service_url}/extract"
                start_time = time.time()

                response = requests.post(
                    extract_url, json=test_request, timeout=120  # 2 minute timeout
                )

                processing_time = time.time() - start_time
                total_processing_time += processing_time

                results["total_requests"] += 1

                if response.status_code == 200:
                    results["successful_requests"] += 1

                    response_data = response.json()
                    extraction_method = response_data.get("extraction_method", {})
                    method_name = extraction_method.get("method", "unknown")

                    if "multi_agent" in method_name.lower():
                        results["multi_agent_requests"] += 1
                        logger.info(
                            f"   ✅ Request {i + 1}: Multi-Agent Pipeline ({processing_time:.2f}s)"
                        )
                    else:
                        results["legacy_requests"] += 1
                        logger.info(
                            f"   ✅ Request {i + 1}: Legacy Orchestrator ({processing_time:.2f}s)"
                        )

                    results["responses"].append(
                        {
                            "request_id": i + 1,
                            "method": method_name,
                            "processing_time": processing_time,
                            "events_found": response_data.get("total_events", 0),
                            "success": True,
                        }
                    )

                else:
                    results["failed_requests"] += 1
                    logger.warning(
                        f"   ❌ Request {i + 1} failed: {response.status_code}"
                    )

                    results["responses"].append(
                        {
                            "request_id": i + 1,
                            "method": "unknown",
                            "processing_time": processing_time,
                            "success": False,
                            "error": f"HTTP {response.status_code}",
                        }
                    )

                # Small delay between requests
                await asyncio.sleep(1)

            except Exception as e:
                results["failed_requests"] += 1
                logger.error(f"❌ Request {i + 1} exception: {e}")

                results["responses"].append(
                    {
                        "request_id": i + 1,
                        "method": "unknown",
                        "processing_time": 0,
                        "success": False,
                        "error": str(e),
                    }
                )

        if results["successful_requests"] > 0:
            results["avg_processing_time"] = (
                total_processing_time / results["successful_requests"]
            )

        # Calculate routing percentages
        if results["total_requests"] > 0:
            multi_agent_percentage = (
                results["multi_agent_requests"] / results["total_requests"]
            ) * 100
            legacy_percentage = (
                results["legacy_requests"] / results["total_requests"]
            ) * 100

            logger.info("📊 Routing Results:")
            logger.info(f"   Total Requests: {results['total_requests']}")
            logger.info(
                f"   Multi-Agent Pipeline: {results['multi_agent_requests']} ({multi_agent_percentage:.1f}%)"
            )
            logger.info(
                f"   Legacy Orchestrator: {results['legacy_requests']} ({legacy_percentage:.1f}%)"
            )
            logger.info(
                f"   Success Rate: {(results['successful_requests'] / results['total_requests'] * 100):.1f}%"
            )
            logger.info(
                f"   Avg Processing Time: {results['avg_processing_time']:.2f}s"
            )

        return results

    async def validate_metrics_endpoint(self) -> Dict[str, Any]:
        """Validate metrics collection and reporting"""
        logger.info("📊 Validating metrics endpoint...")

        try:
            metrics_url = f"{self.service_url}/metrics"
            response = requests.get(metrics_url, timeout=30)

            if response.status_code != 200:
                raise Exception(f"Metrics retrieval failed: {response.status_code}")

            metrics = response.json()
            logger.info("✅ Metrics endpoint validation passed:")
            logger.info(f"   A/B Testing Metrics: {metrics.get('ab_testing', {})}")
            logger.info(f"   Performance Metrics: {metrics.get('performance', {})}")

            return metrics

        except Exception as e:
            logger.error(f"❌ Metrics endpoint validation failed: {e}")
            raise

    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive A/B testing framework validation"""
        logger.info("🚀 Starting comprehensive A/B testing validation...")
        logger.info(f"   Service URL: {self.service_url}")

        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "service_url": self.service_url,
            "health_check": None,
            "ab_config": None,
            "routing_test": None,
            "metrics": None,
            "overall_status": "unknown",
        }

        try:
            # 1. Validate health endpoint
            logger.info("\n" + "=" * 60)
            logger.info("1️⃣ HEALTH ENDPOINT VALIDATION")
            logger.info("=" * 60)
            validation_results["health_check"] = await self.validate_health_endpoint()

            # 2. Validate A/B testing configuration
            logger.info("\n" + "=" * 60)
            logger.info("2️⃣ A/B TESTING CONFIGURATION VALIDATION")
            logger.info("=" * 60)
            validation_results["ab_config"] = await self.validate_ab_testing_config()

            # 3. Test extraction routing
            logger.info("\n" + "=" * 60)
            logger.info("3️⃣ EXTRACTION ROUTING TEST")
            logger.info("=" * 60)
            validation_results["routing_test"] = await self.test_extraction_routing(10)

            # 4. Validate metrics endpoint
            logger.info("\n" + "=" * 60)
            logger.info("4️⃣ METRICS ENDPOINT VALIDATION")
            logger.info("=" * 60)
            validation_results["metrics"] = await self.validate_metrics_endpoint()

            # Determine overall status
            health_ok = validation_results["health_check"].get("status") == "healthy"
            routing_ok = validation_results["routing_test"]["successful_requests"] > 0

            if health_ok and routing_ok:
                validation_results["overall_status"] = "success"
                logger.info("\n🎉 A/B TESTING FRAMEWORK VALIDATION: SUCCESS!")
            else:
                validation_results["overall_status"] = "partial"
                logger.warning("\n⚠️ A/B TESTING FRAMEWORK VALIDATION: PARTIAL SUCCESS")

            return validation_results

        except Exception as e:
            validation_results["overall_status"] = "failed"
            validation_results["error"] = str(e)
            logger.error(f"\n❌ A/B TESTING FRAMEWORK VALIDATION: FAILED - {e}")
            raise


async def main():
    """Main validation execution"""
    if len(sys.argv) < 2:
        print("Usage: python validate_ab_testing_framework.py <service_url>")
        print(
            "Example: python validate_ab_testing_framework.py https://enhanced-orchestrator-v2-867263134607.us-central1.run.app"
        )
        sys.exit(1)

    service_url = sys.argv[1]

    validator = ABTestingValidator(service_url)

    try:
        results = await validator.run_comprehensive_validation()

        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"ab_testing_validation_{timestamp}.json"

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print("\n" + "=" * 80)
        print("🎉 VALIDATION COMPLETE!")
        print("=" * 80)
        print(f"Status: {results['overall_status'].upper()}")
        print(f"Results saved to: {results_file}")

        routing = results.get("routing_test", {})
        if routing:
            print(
                f"Routing Test: {routing['successful_requests']}/{routing['total_requests']} successful"
            )
            print(f"Multi-Agent Pipeline: {routing['multi_agent_requests']} requests")
            print(f"Legacy Orchestrator: {routing['legacy_requests']} requests")

        print("=" * 80)

    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
