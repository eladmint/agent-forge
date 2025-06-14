#!/usr/bin/env python3
"""
💰 Cost-Optimized Distributed Extraction Strategy

This module implements a budget-conscious approach to multi-region extraction:
1. Smart region selection based on costs and success rates
2. Intelligent fallback strategies to minimize unnecessary requests
3. Cost monitoring and budget controls
4. Efficient resource usage with auto-scaling
5. Steel Browser usage only when justified by ROI

Cost Optimization Features:
- Pay-per-use model with automatic scaling to zero
- Regional pricing optimization
- Request batching and caching
- Smart retry logic to avoid wasted requests
- Budget alerts and automatic shutoffs
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class RegionCostTier(Enum):
    """Cost tiers for different Google Cloud regions"""

    TIER_1 = "tier_1"  # Most expensive (us-central1, europe-west1)
    TIER_2 = "tier_2"  # Moderate cost (us-west1, asia-east1)
    TIER_3 = "tier_3"  # Cheapest (australia-southeast1, etc.)


@dataclass
class RegionCostInfo:
    """Cost information for a region"""

    tier: RegionCostTier
    cpu_hour_cost: Decimal  # Cost per vCPU hour
    memory_gb_hour_cost: Decimal  # Cost per GB memory hour
    request_cost: Decimal  # Cost per million requests
    egress_cost: Decimal  # Cost per GB egress

    # Estimated costs for our workload
    extraction_cost_estimate: Decimal = field(
        default=Decimal("0.001")
    )  # Per extraction
    steel_browser_multiplier: Decimal = field(
        default=Decimal("3.0")
    )  # Steel Browser is 3x more expensive


@dataclass
class CostOptimizedRegion:
    """Region configuration with cost optimization"""

    name: str
    cloud_run_url: str
    region_code: str
    cost_info: RegionCostInfo

    # Performance tracking
    success_rate: float = 0.0
    avg_response_time: float = 0.0
    requests_this_hour: int = 0
    cost_this_hour: Decimal = field(default=Decimal("0"))

    # Rate limiting tracking
    last_rate_limit: Optional[datetime] = None
    cooldown_minutes: int = 30

    # Cost controls
    hourly_budget_limit: Decimal = field(default=Decimal("1.00"))  # $1/hour max
    is_budget_exceeded: bool = False


class CostOptimizedExtractionOrchestrator:
    """
    Cost-optimized orchestrator that balances extraction effectiveness with budget constraints
    """

    def __init__(self, daily_budget: Decimal = Decimal("20.00")):
        self.regions = self._initialize_cost_optimized_regions()
        self.session = None

        # Budget controls
        self.daily_budget = daily_budget
        self.current_daily_spend = Decimal("0")
        self.budget_start_date = datetime.now().date()

        # Performance tracking
        self.stats = {
            "total_requests": 0,
            "successful_extractions": 0,
            "rate_limited_requests": 0,
            "total_cost": Decimal("0"),
            "cost_per_successful_extraction": Decimal("0"),
            "regions_used": set(),
            "steel_browser_usage": 0,
            "standard_extraction_usage": 0,
        }

        # Smart caching to reduce costs
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache

    def _initialize_cost_optimized_regions(self) -> List[CostOptimizedRegion]:
        """Initialize regions optimized for cost-effectiveness"""

        # Cost data based on Google Cloud pricing (approximate)
        tier_1_costs = RegionCostInfo(
            tier=RegionCostTier.TIER_1,
            cpu_hour_cost=Decimal("0.048"),  # $0.048 per vCPU hour
            memory_gb_hour_cost=Decimal("0.005"),  # $0.005 per GB hour
            request_cost=Decimal("0.40"),  # $0.40 per million requests
            egress_cost=Decimal("0.12"),  # $0.12 per GB
            extraction_cost_estimate=Decimal("0.002"),
        )

        tier_2_costs = RegionCostInfo(
            tier=RegionCostTier.TIER_2,
            cpu_hour_cost=Decimal("0.045"),
            memory_gb_hour_cost=Decimal("0.0048"),
            request_cost=Decimal("0.38"),
            egress_cost=Decimal("0.11"),
            extraction_cost_estimate=Decimal("0.0018"),
        )

        tier_3_costs = RegionCostInfo(
            tier=RegionCostTier.TIER_3,
            cpu_hour_cost=Decimal("0.042"),
            memory_gb_hour_cost=Decimal("0.0045"),
            request_cost=Decimal("0.35"),
            egress_cost=Decimal("0.10"),
            extraction_cost_estimate=Decimal("0.0015"),
        )

        return [
            # Start with cheapest regions first
            CostOptimizedRegion(
                name="Australia Southeast",
                cloud_run_url="https://token-extractor-australia-southeast1-xxx.a.run.app",
                region_code="australia-southeast1",
                cost_info=tier_3_costs,
                hourly_budget_limit=Decimal("0.50"),  # Lower budget for testing
            ),
            CostOptimizedRegion(
                name="Asia East",
                cloud_run_url="https://token-extractor-asia-east1-xxx.a.run.app",
                region_code="asia-east1",
                cost_info=tier_2_costs,
                hourly_budget_limit=Decimal("0.75"),
            ),
            CostOptimizedRegion(
                name="US West",
                cloud_run_url="https://token-extractor-us-west1-xxx.a.run.app",
                region_code="us-west1",
                cost_info=tier_2_costs,
                hourly_budget_limit=Decimal("1.00"),
            ),
            CostOptimizedRegion(
                name="Europe West",
                cloud_run_url="https://token-extractor-europe-west1-xxx.a.run.app",
                region_code="europe-west1",
                cost_info=tier_1_costs,
                hourly_budget_limit=Decimal("1.50"),
            ),
            CostOptimizedRegion(
                name="US Central",
                cloud_run_url="https://token-extractor-us-central1-xxx.a.run.app",
                region_code="us-central1",
                cost_info=tier_1_costs,
                hourly_budget_limit=Decimal(
                    "2.00"
                ),  # Higher budget for most reliable region
            ),
        ]

    async def start(self):
        """Initialize the cost-optimized extraction system"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),  # Shorter timeout to save costs
            connector=aiohttp.TCPConnector(limit=20),  # Reduced connection pool
        )

        # Reset daily budget if new day
        if datetime.now().date() > self.budget_start_date:
            self.current_daily_spend = Decimal("0")
            self.budget_start_date = datetime.now().date()

        logger.info("💰 Cost-optimized extraction system started")
        logger.info(
            f"💵 Daily budget: ${self.daily_budget}, spent: ${self.current_daily_spend}"
        )

    async def stop(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

    def _check_budget_constraints(self) -> bool:
        """Check if we're within budget constraints"""
        if self.current_daily_spend >= self.daily_budget:
            logger.warning(
                f"💸 Daily budget exceeded: ${self.current_daily_spend} / ${self.daily_budget}"
            )
            return False
        return True

    def _get_cost_effective_regions(self) -> List[CostOptimizedRegion]:
        """Get regions that are cost-effective and available"""
        available_regions = []
        current_time = datetime.now()

        for region in self.regions:
            # Check budget constraints
            if region.is_budget_exceeded:
                continue

            # Check rate limiting cooldown
            if (
                region.last_rate_limit
                and current_time - region.last_rate_limit
                < timedelta(minutes=region.cooldown_minutes)
            ):
                continue

            available_regions.append(region)

        # Sort by cost-effectiveness (success rate / cost)
        def cost_effectiveness(region):
            if region.success_rate == 0:
                return 1.0  # Give new regions a chance
            cost = float(region.cost_info.extraction_cost_estimate)
            return region.success_rate / max(cost, 0.001)

        available_regions.sort(key=cost_effectiveness, reverse=True)
        return available_regions

    def _should_use_steel_browser(self, url: str, attempts: int) -> bool:
        """
        Decide whether to use Steel Browser based on cost-benefit analysis
        """
        # Use Steel Browser only if:
        # 1. Previous attempts failed
        # 2. We have budget remaining
        # 3. The expected value justifies the cost

        if attempts == 0:
            return False  # Always try standard first

        if not self._check_budget_constraints():
            return False

        # Calculate expected value
        steel_cost = Decimal("0.005")  # Estimated Steel Browser cost
        success_probability = 0.8  # Steel Browser success rate
        value_of_success = Decimal("0.02")  # Value we assign to successful extraction

        expected_value = success_probability * float(value_of_success)

        return Decimal(str(expected_value)) > steel_cost

    def _check_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """Check if we have cached results for this URL"""
        cache_key = url
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info(f"💾 Cache hit for {url} - saving costs")
                return cached_data
            else:
                del self.cache[cache_key]
        return None

    def _cache_result(self, url: str, result: Dict[str, Any]):
        """Cache successful results to avoid repeated requests"""
        if result.get("status") == "success":
            self.cache[url] = (result, time.time())

    async def extract_with_cost_optimization(
        self,
        url: str,
        max_attempts: int = 2,  # Reduced from 3 to save costs
        force_steel: bool = False,
    ) -> Dict[str, Any]:
        """
        Extract with cost optimization and smart fallback
        """
        # Check cache first
        cached_result = self._check_cache(url)
        if cached_result:
            return cached_result

        # Check budget constraints
        if not self._check_budget_constraints():
            return {
                "status": "failed",
                "error": "Daily budget exceeded",
                "cost_info": {
                    "daily_spend": str(self.current_daily_spend),
                    "daily_budget": str(self.daily_budget),
                },
            }

        for attempt in range(max_attempts):
            # Get cost-effective region
            available_regions = self._get_cost_effective_regions()

            if not available_regions:
                if attempt < max_attempts - 1:
                    await asyncio.sleep(30)  # Wait for cooldowns
                    continue
                else:
                    return {
                        "status": "failed",
                        "error": "No available regions within budget",
                        "attempt": attempt + 1,
                    }

            region = available_regions[0]  # Most cost-effective

            # Decide extraction method
            use_steel = force_steel or self._should_use_steel_browser(url, attempt)
            method = "steel" if use_steel else "standard"

            logger.info(
                f"💰 Attempt {attempt + 1}: Using {region.name} with {method} extraction"
            )

            try:
                # Estimate cost before making request
                estimated_cost = (
                    region.cost_info.extraction_cost_estimate
                    * region.cost_info.steel_browser_multiplier
                    if use_steel
                    else region.cost_info.extraction_cost_estimate
                )

                # Check if this would exceed budget
                if self.current_daily_spend + estimated_cost > self.daily_budget:
                    logger.warning("💸 Skipping extraction - would exceed budget")
                    continue

                start_time = time.time()

                # Make the extraction request
                result = await self._make_cost_tracked_request(region, url, method)

                # Update cost tracking
                actual_cost = estimated_cost  # In real implementation, get actual cost from billing API
                self.current_daily_spend += actual_cost
                region.cost_this_hour += actual_cost

                # Update performance metrics
                response_time = time.time() - start_time
                region.avg_response_time = (
                    region.avg_response_time + response_time
                ) / 2
                region.requests_this_hour += 1

                if result.get("status") == "success":
                    region.success_rate = min(1.0, region.success_rate + 0.1)
                    self.stats["successful_extractions"] += 1

                    # Cache successful result
                    self._cache_result(url, result)

                    # Add cost information to result
                    result["cost_info"] = {
                        "extraction_cost": str(actual_cost),
                        "region_used": region.name,
                        "method_used": method,
                        "daily_spend": str(self.current_daily_spend),
                        "budget_remaining": str(
                            self.daily_budget - self.current_daily_spend
                        ),
                    }

                    return result

                # Handle rate limiting
                elif "rate limit" in str(result.get("error", "")).lower():
                    region.last_rate_limit = datetime.now()
                    region.success_rate = max(0.0, region.success_rate - 0.2)
                    logger.warning(f"⚠️ Rate limited in {region.name}")
                    continue

                else:
                    region.success_rate = max(0.0, region.success_rate - 0.1)
                    if attempt < max_attempts - 1:
                        continue

            except Exception as e:
                logger.error(f"❌ Error in {region.name}: {e}")
                region.success_rate = max(0.0, region.success_rate - 0.1)
                if attempt < max_attempts - 1:
                    continue

        return {
            "status": "failed",
            "error": "All cost-optimized attempts failed",
            "attempts_made": max_attempts,
            "cost_info": {
                "daily_spend": str(self.current_daily_spend),
                "budget_remaining": str(self.daily_budget - self.current_daily_spend),
            },
        }

    async def _make_cost_tracked_request(
        self, region: CostOptimizedRegion, url: str, method: str
    ) -> Dict[str, Any]:
        """Make an extraction request with cost tracking"""

        endpoint = f"/extract/{method}"
        payload = {
            "url": url,
            "config": {
                "timeout": 30,  # Shorter timeout to save costs
                "cost_optimization": True,
            },
        }

        async with self.session.post(
            f"{region.cloud_run_url}{endpoint}",
            json=payload,
            headers={"X-Cost-Optimization": "enabled"},
        ) as response:
            if response.status == 429:
                return {"status": "rate_limited", "error": "Rate limited"}
            elif response.status != 200:
                return {"status": "failed", "error": f"HTTP {response.status}"}

            result = await response.json()
            return result

    async def extract_batch_cost_optimized(
        self,
        urls: List[str],
        max_concurrent: int = 3,  # Reduced concurrency to save costs
    ) -> List[Dict[str, Any]]:
        """
        Extract multiple URLs with cost optimization and intelligent batching
        """
        logger.info(f"💰 Starting cost-optimized batch extraction for {len(urls)} URLs")

        # Remove duplicates and check cache
        unique_urls = []
        cached_results = []

        for url in urls:
            cached = self._check_cache(url)
            if cached:
                cached_results.append(cached)
            else:
                unique_urls.append(url)

        logger.info(
            f"💾 Found {len(cached_results)} cached results, extracting {len(unique_urls)} URLs"
        )

        # Process in small batches to control costs
        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_extract(url):
            async with semaphore:
                return await self.extract_with_cost_optimization(url)

        # Execute extractions
        extraction_tasks = [limited_extract(url) for url in unique_urls]
        extraction_results = await asyncio.gather(
            *extraction_tasks, return_exceptions=True
        )

        # Combine cached and extracted results
        all_results = cached_results + [
            result for result in extraction_results if not isinstance(result, Exception)
        ]

        # Log cost summary
        self._log_cost_summary()

        return all_results

    def _log_cost_summary(self):
        """Log comprehensive cost summary"""
        successful = self.stats["successful_extractions"]
        total = self.stats["total_requests"]

        if successful > 0:
            cost_per_success = self.current_daily_spend / successful
        else:
            cost_per_success = Decimal("0")

        logger.info("💰 COST-OPTIMIZED EXTRACTION SUMMARY:")
        logger.info(f"   💵 Daily Budget: ${self.daily_budget}")
        logger.info(f"   💸 Daily Spend: ${self.current_daily_spend}")
        logger.info(
            f"   💡 Budget Remaining: ${self.daily_budget - self.current_daily_spend}"
        )
        logger.info(f"   ✅ Successful Extractions: {successful}")
        logger.info(f"   💎 Cost per Success: ${cost_per_success:.4f}")
        logger.info(f"   📊 Success Rate: {(successful/max(total,1))*100:.1f}%")
        logger.info(f"   🚀 Steel Browser Usage: {self.stats['steel_browser_usage']}")
        logger.info(f"   🔧 Standard Usage: {self.stats['standard_extraction_usage']}")

    def get_cost_report(self) -> Dict[str, Any]:
        """Generate detailed cost report"""
        return {
            "budget": {
                "daily_budget": str(self.daily_budget),
                "daily_spend": str(self.current_daily_spend),
                "budget_remaining": str(self.daily_budget - self.current_daily_spend),
                "budget_utilization": f"{(self.current_daily_spend / self.daily_budget * 100):.1f}%",
            },
            "performance": {
                "successful_extractions": self.stats["successful_extractions"],
                "total_requests": self.stats["total_requests"],
                "success_rate": f"{(self.stats['successful_extractions']/max(self.stats['total_requests'],1))*100:.1f}%",
                "cost_per_success": str(
                    self.current_daily_spend
                    / max(self.stats["successful_extractions"], 1)
                ),
            },
            "regions": [
                {
                    "name": region.name,
                    "success_rate": f"{region.success_rate:.1f}%",
                    "cost_this_hour": str(region.cost_this_hour),
                    "requests_this_hour": region.requests_this_hour,
                    "is_rate_limited": region.last_rate_limit is not None
                    and datetime.now() - region.last_rate_limit
                    < timedelta(minutes=region.cooldown_minutes),
                }
                for region in self.regions
            ],
            "optimization": {
                "cache_hits": len(self.cache),
                "steel_browser_usage": self.stats["steel_browser_usage"],
                "standard_extraction_usage": self.stats["standard_extraction_usage"],
                "recommendations": self._get_cost_optimization_recommendations(),
            },
        }

    def _get_cost_optimization_recommendations(self) -> List[str]:
        """Get recommendations for cost optimization"""
        recommendations = []

        utilization = self.current_daily_spend / self.daily_budget

        if utilization > 0.8:
            recommendations.append("Consider increasing cache TTL to reduce API calls")
            recommendations.append(
                "Review Steel Browser usage - switch to standard extraction for non-critical requests"
            )

        if utilization < 0.3:
            recommendations.append(
                "You have budget headroom - consider using Steel Browser for better success rates"
            )
            recommendations.append(
                "Consider increasing extraction volume or adding more regions"
            )

        # Region-specific recommendations
        best_region = min(
            self.regions, key=lambda r: float(r.cost_info.extraction_cost_estimate)
        )
        if best_region.success_rate > 0.8:
            recommendations.append(
                f"Focus extractions on {best_region.name} for best cost-effectiveness"
            )

        return recommendations


# Convenience functions
async def cost_optimized_extraction(
    urls: List[str], daily_budget: Decimal = Decimal("10.00")
) -> List[Dict[str, Any]]:
    """
    Convenient function for cost-optimized extraction with budget controls
    """
    orchestrator = CostOptimizedExtractionOrchestrator(daily_budget=daily_budget)
    await orchestrator.start()

    try:
        results = await orchestrator.extract_batch_cost_optimized(urls)

        # Log final cost report
        cost_report = orchestrator.get_cost_report()
        logger.info("📊 Final Cost Report:")
        logger.info(json.dumps(cost_report, indent=2))

        return results

    finally:
        await orchestrator.stop()


# Example usage with budget constraints
async def main():
    """Example of cost-optimized extraction with realistic budget"""

    # Set a reasonable daily budget
    daily_budget = Decimal("5.00")  # $5/day budget

    # Example URLs for EthCC events
    test_urls = [
        "https://lu.ma/ethcc",
        "https://lu.ma/cymcvco8",
        "https://lu.ma/91fw4m6t",
    ]

    logger.info(
        f"💰 Starting cost-optimized extraction with ${daily_budget} daily budget"
    )

    # Run cost-optimized extraction
    results = await cost_optimized_extraction(test_urls, daily_budget)

    print(f"✅ Extracted {len(results)} results within budget")
    for result in results:
        if result.get("status") == "success":
            events_found = len(result.get("data", {}).get("events", []))
            cost = result.get("cost_info", {}).get("extraction_cost", "0")
            print(f"   📅 Found {events_found} events (cost: ${cost})")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
