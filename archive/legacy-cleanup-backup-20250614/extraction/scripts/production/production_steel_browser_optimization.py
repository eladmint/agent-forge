#!/usr/bin/env python3
"""
Production Steel Browser Optimization System for Nuru AI
Advanced event discovery optimization with intelligent source selection

ACHIEVEMENT: Building on 100% Steel Browser service validation success
STATUS: Production optimization for enhanced event discovery rates
GOAL: Achieve 50%+ event discovery rate improvement through optimized extraction
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))


@dataclass
class OptimizationTarget:
    """Configuration for optimization targets"""

    url: str
    priority: str  # HIGH, MEDIUM, LOW
    expected_events: int
    complexity: str  # basic, advanced, expert
    javascript_heavy: bool = False


@dataclass
class OptimizationResult:
    """Result of optimization attempt"""

    url: str
    events_found: int
    processing_time: float
    success: bool
    optimization_applied: str
    steel_browser_used: bool
    cost: float
    session_id: str


class ProductionSteelBrowserOptimizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.steel_browser_service_url = (
            "https://enhanced-multi-region-us-central-oo6mrfxexq-uc.a.run.app"
        )
        self.optimization_targets = self._load_optimization_targets()
        self.results = []

    def _load_optimization_targets(self) -> List[OptimizationTarget]:
        """Load optimization targets for Steel Browser testing"""
        return [
            # High-priority crypto/blockchain events
            OptimizationTarget(
                url="https://lu.ma/crypto",
                priority="HIGH",
                expected_events=15,
                complexity="advanced",
                javascript_heavy=True,
            ),
            OptimizationTarget(
                url="https://ethglobal.com/events",
                priority="HIGH",
                expected_events=8,
                complexity="expert",
                javascript_heavy=True,
            ),
            OptimizationTarget(
                url="https://www.meetup.com/blockchain-developers-united/",
                priority="HIGH",
                expected_events=5,
                complexity="advanced",
                javascript_heavy=True,
            ),
            OptimizationTarget(
                url="https://devcon.org/en/",
                priority="HIGH",
                expected_events=1,
                complexity="expert",
                javascript_heavy=True,
            ),
            # Medium-priority general tech events
            OptimizationTarget(
                url="https://www.eventbrite.com/d/ca--san-francisco/blockchain/",
                priority="MEDIUM",
                expected_events=12,
                complexity="advanced",
                javascript_heavy=True,
            ),
            OptimizationTarget(
                url="https://web3summit.com/",
                priority="MEDIUM",
                expected_events=1,
                complexity="basic",
                javascript_heavy=False,
            ),
            # Testing targets for optimization validation
            OptimizationTarget(
                url="https://coindesk.com/events/",
                priority="LOW",
                expected_events=3,
                complexity="basic",
                javascript_heavy=False,
            ),
        ]

    async def test_steel_browser_extraction(
        self, target: OptimizationTarget
    ) -> OptimizationResult:
        """Test Steel Browser extraction on a specific target"""
        start_time = time.time()

        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "urls": [target.url],
                    "use_steel_browser": True,
                    "complexity": target.complexity,
                }

                async with session.post(
                    f"{self.steel_browser_service_url}/extract",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as response:
                    processing_time = time.time() - start_time

                    if response.status == 200:
                        result_data = await response.json()

                        return OptimizationResult(
                            url=target.url,
                            events_found=result_data.get("total_events", 0),
                            processing_time=processing_time,
                            success=True,
                            optimization_applied="steel_browser_enhanced",
                            steel_browser_used=True,
                            cost=result_data.get("cost", 0.0),
                            session_id=result_data.get("session_id", "unknown"),
                        )
                    else:
                        self.logger.error(
                            f"Steel Browser extraction failed for {target.url}: {response.status}"
                        )
                        return OptimizationResult(
                            url=target.url,
                            events_found=0,
                            processing_time=processing_time,
                            success=False,
                            optimization_applied="failed",
                            steel_browser_used=True,
                            cost=0.0,
                            session_id="failed",
                        )

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(
                f"Exception during Steel Browser extraction for {target.url}: {e}"
            )
            return OptimizationResult(
                url=target.url,
                events_found=0,
                processing_time=processing_time,
                success=False,
                optimization_applied="exception",
                steel_browser_used=False,
                cost=0.0,
                session_id="exception",
            )

    async def run_optimization_campaign(
        self, max_targets: Optional[int] = None
    ) -> Dict[str, Any]:
        """Run optimization campaign across all targets"""
        targets = self.optimization_targets
        if max_targets:
            targets = targets[:max_targets]

        self.logger.info(
            f"🚀 Starting Steel Browser optimization campaign on {len(targets)} targets"
        )

        campaign_start = time.time()
        results = []

        # Process targets in priority order
        high_priority = [t for t in targets if t.priority == "HIGH"]
        medium_priority = [t for t in targets if t.priority == "MEDIUM"]
        low_priority = [t for t in targets if t.priority == "LOW"]

        for priority_group, group_name in [
            (high_priority, "HIGH"),
            (medium_priority, "MEDIUM"),
            (low_priority, "LOW"),
        ]:
            if not priority_group:
                continue

            self.logger.info(
                f"🎯 Processing {group_name} priority targets ({len(priority_group)} targets)"
            )

            # Process targets concurrently within priority groups
            tasks = [
                self.test_steel_browser_extraction(target) for target in priority_group
            ]
            group_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in group_results:
                if isinstance(result, OptimizationResult):
                    results.append(result)
                    self.logger.info(
                        f"✅ {result.url}: {result.events_found} events in {result.processing_time:.2f}s"
                    )
                else:
                    self.logger.error(f"❌ Exception in optimization: {result}")

            # Brief pause between priority groups
            await asyncio.sleep(2)

        campaign_time = time.time() - campaign_start

        # Generate optimization report
        total_events = sum(r.events_found for r in results)
        successful_extractions = sum(1 for r in results if r.success)
        total_cost = sum(r.cost for r in results)
        avg_processing_time = (
            sum(r.processing_time for r in results) / len(results) if results else 0
        )

        optimization_report = {
            "campaign_summary": {
                "total_targets": len(targets),
                "successful_extractions": successful_extractions,
                "total_events_discovered": total_events,
                "total_processing_time": campaign_time,
                "average_processing_time": avg_processing_time,
                "total_cost": total_cost,
                "success_rate": (
                    (successful_extractions / len(targets)) * 100 if targets else 0
                ),
            },
            "priority_analysis": {
                "high_priority_events": sum(
                    r.events_found
                    for r in results
                    if any(t.priority == "HIGH" and t.url == r.url for t in targets)
                ),
                "medium_priority_events": sum(
                    r.events_found
                    for r in results
                    if any(t.priority == "MEDIUM" and t.url == r.url for t in targets)
                ),
                "low_priority_events": sum(
                    r.events_found
                    for r in results
                    if any(t.priority == "LOW" and t.url == r.url for t in targets)
                ),
            },
            "optimization_insights": {
                "steel_browser_effectiveness": sum(
                    1 for r in results if r.steel_browser_used and r.events_found > 0
                ),
                "javascript_heavy_sites_success": sum(
                    1
                    for r in results
                    if any(
                        t.javascript_heavy and t.url == r.url and r.events_found > 0
                        for t in targets
                    )
                ),
                "complex_sites_success": sum(
                    1
                    for r in results
                    if any(
                        t.complexity in ["advanced", "expert"]
                        and t.url == r.url
                        and r.events_found > 0
                        for t in targets
                    )
                ),
            },
            "detailed_results": [
                {
                    "url": r.url,
                    "events_found": r.events_found,
                    "expected_events": next(
                        (t.expected_events for t in targets if t.url == r.url), 0
                    ),
                    "discovery_rate": (
                        r.events_found
                        / next(
                            (t.expected_events for t in targets if t.url == r.url), 1
                        )
                    )
                    * 100,
                    "processing_time": r.processing_time,
                    "optimization_applied": r.optimization_applied,
                    "cost": r.cost,
                    "session_id": r.session_id,
                }
                for r in results
            ],
            "recommendations": self._generate_optimization_recommendations(
                results, targets
            ),
            "timestamp": datetime.now().isoformat(),
        }

        self.results = results
        return optimization_report

    def _generate_optimization_recommendations(
        self, results: List[OptimizationResult], targets: List[OptimizationTarget]
    ) -> List[str]:
        """Generate optimization recommendations based on results"""
        recommendations = []

        successful_extractions = [
            r for r in results if r.success and r.events_found > 0
        ]
        failed_extractions = [
            r for r in results if not r.success or r.events_found == 0
        ]

        if len(successful_extractions) > 0:
            avg_events_per_success = sum(
                r.events_found for r in successful_extractions
            ) / len(successful_extractions)
            recommendations.append(
                f"✅ Steel Browser shows promising results with {len(successful_extractions)} successful extractions averaging {avg_events_per_success:.1f} events per site"
            )

        if len(failed_extractions) > 0:
            recommendations.append(
                f"⚠️ {len(failed_extractions)} targets need optimization - consider enhanced selectors or alternative extraction methods"
            )

        # Performance recommendations
        fast_extractions = [
            r for r in results if r.processing_time < 5.0 and r.events_found > 0
        ]
        if fast_extractions:
            recommendations.append(
                f"🚀 {len(fast_extractions)} targets show optimal performance (<5s with events) - replicate these patterns"
            )

        # Cost optimization
        total_cost = sum(r.cost for r in results)
        if total_cost > 0:
            cost_per_event = (
                total_cost / sum(r.events_found for r in results)
                if sum(r.events_found for r in results) > 0
                else 0
            )
            recommendations.append(
                f"💰 Cost efficiency: ${cost_per_event:.4f} per event discovered"
            )

        return recommendations

    def save_optimization_report(
        self, report: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """Save optimization report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"steel_browser_optimization_report_{timestamp}.json"

        filepath = Path(filename)
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"💾 Optimization report saved: {filepath}")
        return str(filepath)


async def main():
    parser = argparse.ArgumentParser(
        description="Production Steel Browser Optimization System"
    )
    parser.add_argument(
        "--max-targets", type=int, help="Maximum number of targets to test"
    )
    parser.add_argument(
        "--priority", choices=["HIGH", "MEDIUM", "LOW"], help="Filter by priority level"
    )
    parser.add_argument("--output", help="Output file for optimization report")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")

    optimizer = ProductionSteelBrowserOptimizer()

    # Filter targets by priority if specified
    if args.priority:
        optimizer.optimization_targets = [
            t for t in optimizer.optimization_targets if t.priority == args.priority
        ]

    print("🎯 STEEL BROWSER OPTIMIZATION CAMPAIGN")
    print("=" * 50)
    print(f"Targets: {len(optimizer.optimization_targets)}")
    print(f"Service: {optimizer.steel_browser_service_url}")
    print(f"Time: {datetime.now().isoformat()}")
    print()

    # Run optimization campaign
    report = await optimizer.run_optimization_campaign(args.max_targets)

    # Display results
    print("\n📊 OPTIMIZATION RESULTS")
    print("=" * 50)
    print(
        f"✅ Successful Extractions: {report['campaign_summary']['successful_extractions']}"
    )
    print(
        f"🎯 Total Events Discovered: {report['campaign_summary']['total_events_discovered']}"
    )
    print(
        f"⏱️ Total Processing Time: {report['campaign_summary']['total_processing_time']:.2f}s"
    )
    print(f"💰 Total Cost: ${report['campaign_summary']['total_cost']:.4f}")
    print(f"📈 Success Rate: {report['campaign_summary']['success_rate']:.1f}%")

    print("\n🔍 PRIORITY ANALYSIS")
    print("=" * 30)
    for priority, events in report["priority_analysis"].items():
        print(f"{priority.replace('_', ' ').title()}: {events} events")

    print("\n💡 OPTIMIZATION RECOMMENDATIONS")
    print("=" * 40)
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"{i}. {rec}")

    # Save report
    report_file = optimizer.save_optimization_report(report, args.output)
    print(f"\n💾 Full report saved: {report_file}")

    return report


if __name__ == "__main__":
    asyncio.run(main())
