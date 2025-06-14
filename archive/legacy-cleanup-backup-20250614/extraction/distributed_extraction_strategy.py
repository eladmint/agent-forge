#!/usr/bin/env python3
"""
🌐 Distributed Extraction Strategy - Multi-Region Rate Limiting Evasion

This module implements a sophisticated distributed extraction approach using:
1. Google Cloud multi-region deployment
2. Steel Browser MCP integration for enterprise-grade scraping
3. VPN-like IP rotation through different Cloud Run regions
4. Agent workload distribution and coordination
5. Rate limiting evasion through geographic distribution

Architecture:
- Multiple Cloud Run services across different regions (us-central1, europe-west1, asia-east1)
- Each region has dedicated extraction workers with different IP ranges
- Steel Browser MCP provides enterprise-grade browser automation
- Intelligent work distribution based on rate limiting feedback
- Fallback mechanisms and graceful degradation
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


# Custom exceptions for extraction handling
class ExtractionException(Exception):
    """Base exception for extraction errors"""

    pass


class RateLimitException(ExtractionException):
    """Exception raised when rate limiting is detected"""

    def __init__(self, message: str, region: str = None, retry_after: int = None):
        super().__init__(message)
        self.region = region
        self.retry_after = retry_after


class RegionUnavailableException(ExtractionException):
    """Exception raised when no regions are available"""

    pass


class RegionStatus(Enum):
    """Status of a region for extraction"""

    AVAILABLE = "available"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ExtractionRegion:
    """Configuration for a regional extraction service"""

    name: str
    cloud_run_url: str
    region_code: str
    ip_ranges: List[str]  # Updated to support multiple IP ranges
    cost_tier: int  # 1 = cheapest, 3 = most expensive
    cost_per_extraction: float  # USD cost per extraction
    max_concurrent: int  # Maximum concurrent extractions for this region
    enhanced_service: bool = True  # True = production enhanced, False = test simplified
    status: RegionStatus = RegionStatus.AVAILABLE
    last_success: Optional[datetime] = None
    last_rate_limit: Optional[datetime] = None
    success_count: int = 0
    error_count: int = 0
    rate_limit_count: int = 0
    current_load: int = 0
    total_cost: float = 0.0
    cooldown_minutes: int = 30


@dataclass
class SteelBrowserConfig:
    """Configuration for Steel Browser enterprise automation"""

    api_key: str
    session_duration: int = 3600  # 1 hour
    proxy_rotation: bool = True
    anti_detection: bool = True
    residential_proxies: bool = True
    js_rendering: bool = True
    captcha_solving: bool = True


class DistributedExtractionOrchestrator:
    """
    Orchestrates distributed extraction across multiple Google Cloud regions
    with Steel Browser integration for advanced rate limiting evasion
    """

    def __init__(self, steel_config: Optional[SteelBrowserConfig] = None):
        self.regions = self._initialize_regions()
        self.steel_config = steel_config
        self.session = None
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "rate_limited_requests": 0,
            "failed_requests": 0,
            "regions_used": set(),
            "average_response_time": 0.0,
        }

    def _initialize_regions(self) -> List[ExtractionRegion]:
        """Initialize available Google Cloud regions for distributed extraction"""
        return [
            # DEPLOYED REGIONS (Active)
            # ENHANCED SERVICES (Production) - PREFERRED
            ExtractionRegion(
                name="US Central Enhanced",
                cloud_run_url="https://enhanced-multi-region-us-central-867263134607.us-central1.run.app",
                region_code="us-central1",
                ip_ranges=["34.102.0.0/16", "34.104.0.0/16"],
                cost_tier=2,
                cost_per_extraction=0.0018,
                max_concurrent=8,
                enhanced_service=True,
            ),
            ExtractionRegion(
                name="Europe West Enhanced",
                cloud_run_url="https://enhanced-multi-region-europe-west-867263134607.europe-west1.run.app",
                region_code="europe-west1",
                ip_ranges=["34.76.0.0/16", "34.78.0.0/16"],
                cost_tier=3,
                cost_per_extraction=0.0020,
                max_concurrent=6,
                enhanced_service=True,
            ),
            # FALLBACK TEST SERVICES (Limited Functionality) - USE ONLY IF ENHANCED NOT AVAILABLE
            ExtractionRegion(
                name="US Central (Test)",
                cloud_run_url="https://multi-region-test-867263134607.us-central1.run.app",
                region_code="us-central1-test",
                ip_ranges=["34.102.0.0/16", "34.104.0.0/16"],
                cost_tier=2,
                cost_per_extraction=0.0018,
                max_concurrent=8,
                enhanced_service=False,
                status=RegionStatus.MAINTENANCE,  # Prefer enhanced services
            ),
            ExtractionRegion(
                name="Europe West (Test)",
                cloud_run_url="https://multi-region-test-eu-867263134607.europe-west1.run.app",
                region_code="europe-west1-test",
                ip_ranges=["34.76.0.0/16", "34.78.0.0/16"],
                cost_tier=3,
                cost_per_extraction=0.0020,
                max_concurrent=6,
                enhanced_service=False,
                status=RegionStatus.MAINTENANCE,  # Prefer enhanced services
            ),
            # PLANNED REGIONS (Future deployment)
            ExtractionRegion(
                name="Asia Southeast",
                cloud_run_url="https://multi-region-test-asia-867263134607.asia-southeast1.run.app",
                region_code="asia-southeast1",
                ip_ranges=["34.126.0.0/16", "34.128.0.0/16"],
                cost_tier=1,  # Cheapest tier
                cost_per_extraction=0.0015,
                max_concurrent=4,
                status=RegionStatus.MAINTENANCE,  # Not deployed yet
            ),
            ExtractionRegion(
                name="US West",
                cloud_run_url="https://multi-region-test-usw-867263134607.us-west1.run.app",
                region_code="us-west1",
                ip_ranges=["34.105.0.0/16", "34.127.0.0/16"],
                cost_tier=2,
                cost_per_extraction=0.0018,
                max_concurrent=6,
                status=RegionStatus.MAINTENANCE,  # Not deployed yet
            ),
            ExtractionRegion(
                name="Australia",
                cloud_run_url="https://multi-region-test-au-867263134607.australia-southeast1.run.app",
                region_code="australia-southeast1",
                ip_ranges=["34.151.0.0/16", "34.152.0.0/16"],
                cost_tier=1,
                cost_per_extraction=0.0015,
                max_concurrent=3,
                status=RegionStatus.MAINTENANCE,  # Not deployed yet
            ),
        ]

    async def start(self):
        """Initialize the distributed extraction system"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=120),
            connector=aiohttp.TCPConnector(limit=100),
        )

        # Health check all regions
        await self._health_check_regions()
        logger.info(
            f"Distributed extraction system started with {len(self._available_regions())} available regions"
        )

    async def stop(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

    def _available_regions(self) -> List[ExtractionRegion]:
        """Get regions that are currently available for extraction"""
        available = []
        current_time = datetime.now()

        for region in self.regions:
            if region.status == RegionStatus.RATE_LIMITED:
                # Check if cooldown period has passed
                if (
                    region.last_rate_limit
                    and current_time - region.last_rate_limit
                    > timedelta(minutes=region.cooldown_minutes)
                ):
                    region.status = RegionStatus.AVAILABLE
                    logger.info(
                        f"Region {region.name} cooldown completed - back online"
                    )

            if (
                region.status == RegionStatus.AVAILABLE
                and region.current_load < region.max_concurrent
            ):
                available.append(region)

        return available

    def _select_optimal_region(
        self,
        url: str,
        budget_limit: float = None,
        prefer_cost_optimization: bool = True,
    ) -> Optional[ExtractionRegion]:
        """Select the best region for extraction based on load, success rate, and cost optimization"""
        available_regions = self._available_regions()

        if not available_regions:
            logger.warning("No available regions for extraction")
            return None

        # Score regions based on multiple factors
        scored_regions = []
        for region in available_regions:
            # Calculate success rate
            total_attempts = (
                region.success_count + region.rate_limit_count + region.error_count
            )
            success_rate = region.success_count / max(total_attempts, 1)

            # Calculate load factor (lower is better)
            load_factor = region.current_load / region.max_concurrent

            # Calculate recency bonus (recent success is good)
            recency_bonus = 0.0
            if region.last_success:
                # Ensure last_success is a datetime object
                if isinstance(region.last_success, datetime):
                    hours_since_success = (
                        datetime.now() - region.last_success
                    ).total_seconds() / 3600
                else:
                    hours_since_success = (time.time() - region.last_success) / 3600
                recency_bonus = max(
                    0, 1.0 - (hours_since_success / 24)
                )  # Decay over 24 hours

            # Rate limiting penalty (recent rate limits are bad)
            rate_limit_penalty = 0.0
            if region.last_rate_limit:
                # Ensure last_rate_limit is a datetime object
                if isinstance(region.last_rate_limit, datetime):
                    hours_since_rate_limit = (
                        datetime.now() - region.last_rate_limit
                    ).total_seconds() / 3600
                else:
                    hours_since_rate_limit = (
                        time.time() - region.last_rate_limit
                    ) / 3600

                if hours_since_rate_limit < region.cooldown_minutes / 60:
                    rate_limit_penalty = 0.5  # Heavy penalty for recent rate limits
                else:
                    rate_limit_penalty = max(
                        0, 0.3 - (hours_since_rate_limit / 24)
                    )  # Gradual recovery

            # Cost optimization factor (lower cost tier is better)
            cost_factor = 0.0
            if prefer_cost_optimization:
                # Cost tier 1 = best, tier 3 = worst
                cost_factor = (4 - region.cost_tier) / 3  # Normalize to 0-1 range

            # Geographic optimization for specific platforms
            geo_bonus = 0.0
            if "luma" in url.lower() or "lu.ma" in url.lower():
                # Luma works better from Europe
                geo_bonus = 0.15 if "europe" in region.region_code.lower() else 0.0
            elif "token2049" in url.lower():
                # Token2049 events often in Asia
                geo_bonus = 0.15 if "asia" in region.region_code.lower() else 0.0

            # Budget check - exclude regions that would exceed budget
            budget_compatible = True
            if budget_limit and region.cost_per_extraction > budget_limit:
                budget_compatible = False
                continue

            # Calculate composite score
            score = (
                success_rate * 0.30  # Success rate is very important
                + (1 - load_factor) * 0.25  # Lower load is better
                + recency_bonus * 0.15  # Recent success is good
                + cost_factor * 0.15  # Lower cost is better
                + geo_bonus * 0.10  # Geographic optimization
                + (1 - rate_limit_penalty) * 0.05  # Rate limit penalty
            )

            scored_regions.append((score, region))

            logger.debug(
                f"Region {region.name}: score={score:.3f}, success_rate={success_rate:.3f}, "
                f"load={load_factor:.3f}, cost_tier={region.cost_tier}, "
                f"rate_limit_penalty={rate_limit_penalty:.3f}"
            )

        if not scored_regions:
            logger.warning("No budget-compatible regions available")
            return None

        # Sort by score and return the best region
        scored_regions.sort(reverse=True)
        selected_region = scored_regions[0][1]

        logger.info(
            f"Selected region {selected_region.name} (score: {scored_regions[0][0]:.3f}, "
            f"cost: ${selected_region.cost_per_extraction:.4f})"
        )
        return selected_region

    async def _health_check_regions(self):
        """Check health of all regions"""
        tasks = []
        for region in self.regions:
            tasks.append(self._check_region_health(region))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_region_health(self, region: ExtractionRegion):
        """Check if a specific region is healthy"""
        try:
            async with self.session.get(
                f"{region.cloud_run_url}/health",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    region.status = RegionStatus.AVAILABLE
                    logger.debug(f"Region {region.name} is healthy")
                else:
                    region.status = RegionStatus.ERROR
                    logger.warning(
                        f"Region {region.name} health check failed: {response.status}"
                    )
        except Exception as e:
            region.status = RegionStatus.ERROR
            logger.warning(f"Region {region.name} health check error: {e}")

    async def extract_with_steel_browser(
        self, url: str, region: ExtractionRegion, use_steel: bool = True
    ) -> Dict[str, Any]:
        """
        Extract content using Steel Browser through a specific region
        """
        region.current_load += 1
        start_time = time.time()

        try:
            if use_steel and self.steel_config:
                # Use Steel Browser for enterprise-grade extraction
                result = await self._steel_browser_extract(url, region)
            else:
                # Fallback to standard extraction
                result = await self._standard_extract(url, region)

            # Update region stats on success
            region.success_count += 1
            region.last_success = datetime.now()
            self.stats["successful_requests"] += 1
            self.stats["regions_used"].add(region.name)

            return result

        except RateLimitException:
            # Handle rate limiting
            region.status = RegionStatus.RATE_LIMITED
            region.last_rate_limit = datetime.now()
            region.rate_limit_count += 1
            self.stats["rate_limited_requests"] += 1

            logger.warning(f"Region {region.name} rate limited - entering cooldown")
            raise

        except Exception as e:
            region.status = RegionStatus.ERROR
            self.stats["failed_requests"] += 1
            logger.error(f"Extraction failed in region {region.name}: {e}")
            raise

        finally:
            region.current_load -= 1

            # Update average response time
            response_time = time.time() - start_time
            self.stats["total_requests"] += 1
            current_avg = self.stats["average_response_time"]
            total_requests = self.stats["total_requests"]
            self.stats["average_response_time"] = (
                current_avg * (total_requests - 1) + response_time
            ) / total_requests

    async def _steel_browser_extract(
        self, url: str, region: ExtractionRegion
    ) -> Dict[str, Any]:
        """
        Extract using Steel Browser with enterprise features:
        - Residential proxy rotation
        - Anti-detection measures
        - CAPTCHA solving
        - JavaScript rendering
        """
        steel_payload = {
            "url": url,
            "method": "extract_comprehensive",
            "config": {
                "region": region.region_code,
                "proxy_type": "residential",
                "anti_detection": True,
                "js_rendering": True,
                "wait_for_selector": "a.event-link.content-link",
                "scroll_behavior": "intelligent",
                "captcha_solving": True,
                "session_duration": self.steel_config.session_duration,
                "user_agent_rotation": True,
                "browser_fingerprint_randomization": True,
            },
        }

        async with self.session.post(
            f"{region.cloud_run_url}/extract/steel",
            json=steel_payload,
            headers={
                "Authorization": f"Bearer {self.steel_config.api_key}",
                "X-Region": region.region_code,
                "X-Extraction-Type": "steel-browser",
            },
        ) as response:
            if response.status == 429:
                raise RateLimitException(f"Rate limited in region {region.name}")
            elif response.status != 200:
                raise ExtractionException(f"Steel extraction failed: {response.status}")

            result = await response.json()
            return {
                "status": "success",
                "method": "steel_browser",
                "region": region.name,
                "data": result,
                "meta": {
                    "proxy_used": result.get("proxy_info"),
                    "captcha_solved": result.get("captcha_solved", False),
                    "js_events_triggered": result.get("js_events", 0),
                },
            }

    async def _standard_extract(
        self, url: str, region: ExtractionRegion, budget_limit: float = 1.0
    ) -> Dict[str, Any]:
        """Standard extraction through deployed regional Cloud Run service"""

        # Enhanced services support calendar discovery and full agent processing
        if region.enhanced_service:
            payload = {
                "urls": [url],
                "calendar_discovery": True,  # Enable calendar discovery for enhanced services
                "budget": budget_limit,
                "mode": "enhanced",
                "options": {
                    "timeout": 120,  # Longer timeout for enhanced processing
                    "user_agent_rotation": True,
                    "include_metadata": True,
                    "visual_intelligence": True,
                    "save_to_database": False,  # Let caller decide
                    "agent_processing": True,
                },
            }
        else:
            # Test services - limited functionality
            payload = {
                "urls": [url],
                "budget": budget_limit,
                "mode": "test",
                "options": {
                    "timeout": 60,
                    "user_agent_rotation": True,
                    "include_metadata": True,
                },
            }

        # Call the actual deployed multi-region service
        async with self.session.post(
            f"{region.cloud_run_url}/extract",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Region": region.region_code,
                "X-Source": "distributed-orchestrator",
            },
            timeout=aiohttp.ClientTimeout(total=120),
        ) as response:
            # Rate limiting detection
            if response.status == 429:
                retry_after = response.headers.get(
                    "Retry-After", 1800
                )  # Default 30 min
                raise RateLimitException(
                    f"Rate limited in region {region.name}",
                    region=region.name,
                    retry_after=int(retry_after),
                )
            elif response.status == 400:
                # Budget exceeded or invalid request
                error_text = await response.text()
                if "budget" in error_text.lower():
                    raise ExtractionException(
                        f"Budget exceeded in region {region.name}: {error_text}"
                    )
                else:
                    raise ExtractionException(
                        f"Bad request in region {region.name}: {error_text}"
                    )
            elif response.status != 200:
                error_text = await response.text()
                raise ExtractionException(
                    f"Extraction failed in region {region.name}: {response.status} - {error_text}"
                )

            result = await response.json()

            # Update region cost tracking
            region.total_cost += result.get("cost", region.cost_per_extraction)

            return {
                "status": "success",
                "method": (
                    "enhanced_multi_region_service"
                    if region.enhanced_service
                    else "test_multi_region_service"
                ),
                "region": region.name,
                "region_code": region.region_code,
                "cost": result.get("cost", region.cost_per_extraction),
                "ip_ranges": region.ip_ranges,
                "data": result.get("results", []),
                "events_found": len(result.get("results", [])),
                "processing_time": result.get("processing_time", 0),
                "enhanced_service": region.enhanced_service,
                "metadata": {
                    "source_ips": result.get("source_ips", region.ip_ranges),
                    "extraction_timestamp": datetime.now().isoformat(),
                    "cost_tier": region.cost_tier,
                    "calendar_discovery": region.enhanced_service,
                    "agent_processing": region.enhanced_service,
                },
            }

    async def extract_distributed(
        self, urls: List[str], max_retries: int = 3, use_steel: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract multiple URLs using distributed regions with intelligent routing
        """
        if not urls:
            return []

        logger.info(f"Starting distributed extraction for {len(urls)} URLs")

        # Create tasks with region selection
        tasks = []
        for url in urls:
            tasks.append(self._extract_with_retry(url, max_retries, use_steel))

        # Execute with controlled concurrency
        semaphore = asyncio.Semaphore(15)  # Limit global concurrency

        async def limited_extract(task):
            async with semaphore:
                return await task

        results = await asyncio.gather(
            *[limited_extract(task) for task in tasks], return_exceptions=True
        )

        # Process results
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"URL {urls[i]} failed completely: {result}")
                continue
            successful_results.append(result)

        logger.info(
            f"Distributed extraction completed: {len(successful_results)}/{len(urls)} successful"
        )
        self._log_extraction_stats()

        return successful_results

    async def _extract_with_retry(
        self, url: str, max_retries: int, use_steel: bool
    ) -> Dict[str, Any]:
        """Extract a single URL with retry logic across different regions"""

        for attempt in range(max_retries + 1):
            region = self._select_optimal_region(url)

            if not region:
                if attempt < max_retries:
                    # Wait for regions to become available
                    await asyncio.sleep(random.uniform(30, 60))
                    continue
                else:
                    raise ExtractionException("No available regions after all retries")

            try:
                result = await self.extract_with_steel_browser(url, region, use_steel)
                return result

            except RateLimitException:
                logger.warning(f"Rate limited on attempt {attempt + 1} for {url}")
                if attempt < max_retries:
                    # Try different region on next attempt
                    await asyncio.sleep(random.uniform(10, 30))
                    continue
                else:
                    raise

            except Exception as e:
                logger.error(
                    f"Extraction failed on attempt {attempt + 1} for {url}: {e}"
                )
                if attempt < max_retries:
                    await asyncio.sleep(random.uniform(5, 15))
                    continue
                else:
                    raise

    def _log_extraction_stats(self):
        """Log comprehensive extraction statistics"""
        stats = self.stats
        total = stats["total_requests"]

        if total > 0:
            success_rate = (stats["successful_requests"] / total) * 100
            rate_limit_rate = (stats["rate_limited_requests"] / total) * 100

            logger.info("🌐 DISTRIBUTED EXTRACTION STATISTICS:")
            logger.info(f"   📊 Total Requests: {total}")
            logger.info(f"   ✅ Success Rate: {success_rate:.1f}%")
            logger.info(f"   🚫 Rate Limited: {rate_limit_rate:.1f}%")
            logger.info(
                f"   ⏱️  Average Response Time: {stats['average_response_time']:.2f}s"
            )
            logger.info(f"   🗺️  Regions Used: {', '.join(stats['regions_used'])}")
            logger.info(f"   🔄 Available Regions: {len(self._available_regions())}")

    def get_cost_optimization_strategy(
        self, total_budget: float, estimated_urls: int
    ) -> Dict[str, Any]:
        """
        🏦 Cost Optimization Engine - Intelligent Regional Selection for Budget Management

        This engine analyzes regional pricing tiers and current availability to recommend
        the most cost-effective extraction strategy within budget constraints.
        """
        available_regions = self._available_regions()

        if not available_regions:
            return {
                "status": "error",
                "message": "No available regions for cost optimization",
                "recommendation": None,
            }

        # Calculate cost estimates for each region
        region_analysis = []
        for region in available_regions:
            estimated_cost = region.cost_per_extraction * estimated_urls
            urls_within_budget = int(total_budget / region.cost_per_extraction)

            # Factor in success rate for actual cost calculation
            total_attempts = (
                region.success_count + region.rate_limit_count + region.error_count
            )
            success_rate = (
                region.success_count / max(total_attempts, 1)
                if total_attempts > 0
                else 0.8
            )

            # Adjust for expected retries
            expected_extraction_cost = estimated_cost / max(
                success_rate, 0.3
            )  # Minimum 30% success assumption

            region_analysis.append(
                {
                    "region": region,
                    "estimated_cost": estimated_cost,
                    "expected_cost_with_retries": expected_extraction_cost,
                    "urls_within_budget": urls_within_budget,
                    "cost_per_url": region.cost_per_extraction,
                    "success_rate": success_rate,
                    "cost_efficiency_score": success_rate
                    / region.cost_per_extraction,  # Higher is better
                    "budget_utilization": min(
                        1.0, expected_extraction_cost / total_budget
                    ),
                }
            )

        # Sort by cost efficiency (success rate per dollar)
        region_analysis.sort(key=lambda x: x["cost_efficiency_score"], reverse=True)

        # Select optimal strategy
        if total_budget >= max(
            r["expected_cost_with_retries"] for r in region_analysis
        ):
            # Budget allows any region - choose most cost efficient
            recommended_region = region_analysis[0]["region"]
            strategy = "cost_efficient"
            message = f"Budget sufficient for any region. Recommending {recommended_region.name} for best cost efficiency."

        elif any(
            r["expected_cost_with_retries"] <= total_budget for r in region_analysis
        ):
            # Budget constrains options - choose cheapest that fits
            viable_regions = [
                r
                for r in region_analysis
                if r["expected_cost_with_retries"] <= total_budget
            ]
            recommended_region = min(
                viable_regions, key=lambda x: x["expected_cost_with_retries"]
            )["region"]
            strategy = "budget_constrained"
            message = f"Budget constrains options. Recommending {recommended_region.name} as most affordable option."

        else:
            # Budget insufficient for full extraction - recommend cheapest region with partial extraction
            cheapest_region = min(region_analysis, key=lambda x: x["cost_per_url"])[
                "region"
            ]
            max_urls = int(total_budget / cheapest_region.cost_per_extraction)
            recommended_region = cheapest_region
            strategy = "partial_extraction"
            message = f"Budget insufficient for full extraction. Recommending {recommended_region.name} for {max_urls}/{estimated_urls} URLs."

        return {
            "status": "success",
            "strategy": strategy,
            "message": message,
            "recommended_region": {
                "name": recommended_region.name,
                "region_code": recommended_region.region_code,
                "cost_per_extraction": recommended_region.cost_per_extraction,
                "cost_tier": recommended_region.cost_tier,
                "ip_ranges": recommended_region.ip_ranges,
            },
            "budget_analysis": {
                "total_budget": total_budget,
                "estimated_urls": estimated_urls,
                "estimated_cost": recommended_region.cost_per_extraction
                * estimated_urls,
                "budget_utilization": min(
                    1.0,
                    (recommended_region.cost_per_extraction * estimated_urls)
                    / total_budget,
                ),
                "remaining_budget": max(
                    0,
                    total_budget
                    - (recommended_region.cost_per_extraction * estimated_urls),
                ),
            },
            "all_regions_analysis": [
                {
                    "name": r["region"].name,
                    "cost_tier": r["region"].cost_tier,
                    "cost_per_url": r["cost_per_url"],
                    "estimated_total_cost": r["expected_cost_with_retries"],
                    "urls_within_budget": r["urls_within_budget"],
                    "cost_efficiency_score": r["cost_efficiency_score"],
                    "success_rate": r["success_rate"],
                    "available": r["region"].status == RegionStatus.AVAILABLE,
                }
                for r in region_analysis
            ],
        }

    def get_regional_cost_breakdown(self) -> Dict[str, Any]:
        """
        📊 Regional Cost Analytics - Comprehensive cost analysis across all regions
        """
        breakdown = {
            "total_cost_incurred": 0.0,
            "total_extractions": 0,
            "average_cost_per_extraction": 0.0,
            "cost_by_region": {},
            "cost_efficiency_by_region": {},
            "recommendations": [],
        }

        total_extractions = 0
        total_cost = 0.0

        for region in self.regions:
            region_extractions = region.success_count
            region_cost = region.total_cost

            if region_extractions > 0:
                avg_cost_per_extraction = region_cost / region_extractions
                cost_efficiency = region_extractions / max(
                    region_cost, 0.001
                )  # Avoid division by zero
            else:
                avg_cost_per_extraction = region.cost_per_extraction
                cost_efficiency = 0.0

            breakdown["cost_by_region"][region.name] = {
                "total_cost": region_cost,
                "extractions": region_extractions,
                "avg_cost_per_extraction": avg_cost_per_extraction,
                "theoretical_cost_per_extraction": region.cost_per_extraction,
                "cost_tier": region.cost_tier,
                "efficiency_score": cost_efficiency,
            }

            total_extractions += region_extractions
            total_cost += region_cost

        breakdown["total_cost_incurred"] = total_cost
        breakdown["total_extractions"] = total_extractions
        breakdown["average_cost_per_extraction"] = total_cost / max(
            total_extractions, 1
        )

        # Generate recommendations
        if breakdown["cost_by_region"]:
            # Find most cost-efficient region
            most_efficient = max(
                breakdown["cost_by_region"].items(),
                key=lambda x: x[1]["efficiency_score"],
            )

            # Find cheapest region (by tier)
            available_regions = [
                r for r in self.regions if r.status == RegionStatus.AVAILABLE
            ]
            if available_regions:
                cheapest_region = min(available_regions, key=lambda x: x.cost_tier)

                breakdown["recommendations"] = [
                    f"Most cost-efficient region: {most_efficient[0]} (efficiency score: {most_efficient[1]['efficiency_score']:.2f})",
                    f"Cheapest available region: {cheapest_region.name} (tier {cheapest_region.cost_tier}, ${cheapest_region.cost_per_extraction:.4f}/extraction)",
                    f"Total cost savings potential: ${(breakdown['average_cost_per_extraction'] - cheapest_region.cost_per_extraction) * total_extractions:.2f}",
                ]

        return breakdown

    async def benchmark_steel_browser(self, test_urls: List[str]) -> Dict[str, Any]:
        """
        Benchmark Steel Browser performance against standard extraction
        """
        logger.info("🔧 Starting Steel Browser benchmark")

        # Test with Steel Browser
        start_time = time.time()
        steel_results = await self.extract_distributed(test_urls, use_steel=True)
        steel_time = time.time() - start_time

        # Reset stats for standard test
        steel_stats = dict(self.stats)
        self.stats = {
            key: (
                0
                if isinstance(val, (int, float))
                else set() if isinstance(val, set) else val
            )
            for key, val in self.stats.items()
        }

        # Test with standard extraction
        start_time = time.time()
        standard_results = await self.extract_distributed(test_urls, use_steel=False)
        standard_time = time.time() - start_time

        return {
            "steel_browser": {
                "total_time": steel_time,
                "success_count": len(steel_results),
                "stats": steel_stats,
            },
            "standard": {
                "total_time": standard_time,
                "success_count": len(standard_results),
                "stats": dict(self.stats),
            },
            "improvement": {
                "success_rate_improvement": len(steel_results) - len(standard_results),
                "time_difference": steel_time - standard_time,
                "recommendation": (
                    "steel"
                    if len(steel_results) > len(standard_results)
                    else "standard"
                ),
            },
        }


# Custom exceptions
class RateLimitException(Exception):
    """Raised when rate limiting is detected"""

    pass


class ExtractionException(Exception):
    """Raised when extraction fails"""

    pass


# Example usage
async def main():
    """Example of distributed extraction with Steel Browser"""

    # Configure Steel Browser (requires Steel API key)
    steel_config = SteelBrowserConfig(
        api_key="your_steel_api_key_here",
        session_duration=3600,
        proxy_rotation=True,
        anti_detection=True,
        residential_proxies=True,
    )

    # Initialize distributed orchestrator
    orchestrator = DistributedExtractionOrchestrator(steel_config)
    await orchestrator.start()

    try:
        # Test URLs for EthCC events
        test_urls = [
            "https://lu.ma/ethcc",
            "https://lu.ma/cymcvco8",
            "https://lu.ma/91fw4m6t",
            "https://lu.ma/FOIS_ETHCC",
        ]

        # Run benchmark to compare Steel vs standard
        benchmark_results = await orchestrator.benchmark_steel_browser(test_urls[:2])
        print("🔧 Benchmark Results:")
        print(json.dumps(benchmark_results, indent=2))

        # Run full distributed extraction
        results = await orchestrator.extract_distributed(test_urls, use_steel=True)
        print(f"✅ Extracted {len(results)} events successfully")

        # Example of processing specific calendar for full event discovery
        calendar_urls = ["https://lu.ma/ethcc"]
        calendar_results = await orchestrator.extract_distributed(
            calendar_urls, use_steel=True
        )

        for result in calendar_results:
            if result["status"] == "success":
                events_found = len(result["data"].get("events", []))
                print(f"📅 Found {events_found} events from calendar")
                print(f"🌐 Extracted via {result['region']} using {result['method']}")

    finally:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())
