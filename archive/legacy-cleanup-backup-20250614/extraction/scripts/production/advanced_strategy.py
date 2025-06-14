#!/usr/bin/env python3
"""
Nuru AI - Advanced Optimization Strategy
Multi-platform extraction with intelligent rate limiting evasion
"""

import asyncio
import json
import logging
import random
from datetime import datetime
from typing import Any, Dict, List

import aiohttp

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AdvancedEventDiscovery:
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.current_total = 74  # Current extracted events
        self.target_total = 90  # Target events
        self.remaining = 16  # Events still needed

        # Alternative platforms beyond lu.ma
        self.platforms = [
            {
                "name": "Eventbrite",
                "base_urls": [
                    "https://www.eventbrite.com/d/online/blockchain/",
                    "https://www.eventbrite.com/d/online/cryptocurrency/",
                    "https://www.eventbrite.com/d/online/web3/",
                    "https://www.eventbrite.com/d/online/defi/",
                ],
                "delay": (10, 20),  # Conservative delays
            },
            {
                "name": "Meetup",
                "base_urls": [
                    "https://www.meetup.com/find/?keywords=blockchain",
                    "https://www.meetup.com/find/?keywords=cryptocurrency",
                    "https://www.meetup.com/find/?keywords=web3",
                    "https://www.meetup.com/find/?keywords=ethereum",
                ],
                "delay": (15, 25),
            },
            {
                "name": "Conference Websites",
                "base_urls": [
                    "https://2024.ethcc.io/",
                    "https://devcon.org/",
                    "https://consensus2024.coindesk.com/",
                    "https://www.permissionless.xyz/",
                    "https://www.token2049.com/",
                ],
                "delay": (5, 10),  # Direct conference sites are less restrictive
            },
            {
                "name": "Alternative Lu.ma Endpoints",
                "base_urls": [
                    "https://lu.ma/events",
                    "https://lu.ma/calendar",
                    "https://lu.ma/upcoming",
                    "https://lu.ma/featured",
                ],
                "delay": (30, 60),  # Very conservative for lu.ma
            },
        ]

        # Advanced rate limiting strategy
        self.rate_strategies = {
            "exponential_backoff": [2, 5, 10, 20, 40, 60],
            "random_intervals": lambda: random.uniform(3, 15),
            "success_based": {"base": 5, "multiplier": 0.8, "max_reduction": 2},
            "time_based": {
                "peak_hours": (9, 17),
                "off_peak_delay": 3,
                "peak_delay": 12,
            },
        }

        self.session_stats = {
            "attempts": 0,
            "successes": 0,
            "rate_limited": 0,
            "platform_success": {},
            "start_time": datetime.now(),
        }

    async def get_optimal_delay(
        self, platform_name: str, recent_success: bool = False
    ) -> float:
        """Calculate optimal delay based on platform and recent performance"""
        base_delay = random.uniform(*self.platforms[0]["delay"])  # Default

        # Find platform-specific delay
        for platform in self.platforms:
            if platform["name"] == platform_name:
                base_delay = random.uniform(*platform["delay"])
                break

        # Adjust based on success rate
        if recent_success and self.session_stats["successes"] > 0:
            success_rate = (
                self.session_stats["successes"] / self.session_stats["attempts"]
            )
            if success_rate > 0.5:
                base_delay *= 0.7  # Reduce delay if performing well

        # Time-based adjustment
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Peak hours
            base_delay *= 1.5

        return base_delay

    async def extract_from_url(self, url: str, platform_name: str) -> Dict[str, Any]:
        """Extract events from a single URL with advanced error handling"""
        try:
            # Get optimal delay
            delay = await self.get_optimal_delay(platform_name)
            await asyncio.sleep(delay)

            async with aiohttp.ClientSession() as session:
                payload = {
                    "url": url,
                    "use_steel_browser": True,  # Use advanced browser automation
                    "anti_bot_evasion": True,
                    "multiple_agents": True,
                    "platform_hint": platform_name.lower(),
                }

                async with session.post(
                    f"{self.base_url}/extract",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120),  # Extended timeout
                ) as response:

                    self.session_stats["attempts"] += 1

                    if response.status == 200:
                        data = await response.json()
                        events_count = len(data.get("events", []))

                        if events_count > 0:
                            self.session_stats["successes"] += 1

                            # Track platform performance
                            if (
                                platform_name
                                not in self.session_stats["platform_success"]
                            ):
                                self.session_stats["platform_success"][
                                    platform_name
                                ] = 0
                            self.session_stats["platform_success"][
                                platform_name
                            ] += events_count

                            logger.info(
                                f"✅ {platform_name}: Found {events_count} events from {url}"
                            )
                            return {
                                "success": True,
                                "events": data["events"],
                                "count": events_count,
                            }
                        else:
                            logger.info(f"⚠️ {platform_name}: No events found at {url}")
                            return {"success": False, "events": [], "count": 0}

                    elif response.status == 429:
                        self.session_stats["rate_limited"] += 1
                        logger.warning(f"🚫 {platform_name}: Rate limited for {url}")
                        return {
                            "success": False,
                            "rate_limited": True,
                            "events": [],
                            "count": 0,
                        }
                    else:
                        logger.error(
                            f"❌ {platform_name}: HTTP {response.status} for {url}"
                        )
                        return {"success": False, "events": [], "count": 0}

        except asyncio.TimeoutError:
            logger.error(f"⏰ {platform_name}: Timeout for {url}")
            return {"success": False, "timeout": True, "events": [], "count": 0}
        except Exception as e:
            logger.error(f"💥 {platform_name}: Error extracting from {url}: {e}")
            return {"success": False, "error": str(e), "events": [], "count": 0}

    async def process_platform(self, platform: Dict) -> List[Dict]:
        """Process all URLs for a single platform"""
        platform_name = platform["name"]
        logger.info(f"🎯 Processing platform: {platform_name}")

        all_events = []

        for url in platform["base_urls"]:
            result = await self.extract_from_url(url, platform_name)

            if result["success"] and result["count"] > 0:
                all_events.extend(result["events"])

            # Progress update
            await self.print_progress()

            # Check if we've reached our target
            total_found = len(all_events)
            if self.current_total + total_found >= self.target_total:
                logger.info(
                    f"🎉 Target reached! Found {total_found} events from {platform_name}"
                )
                break

        return all_events

    async def print_progress(self):
        """Print current optimization progress"""
        elapsed = (
            datetime.now() - self.session_stats["start_time"]
        ).total_seconds() / 60
        success_rate = (
            self.session_stats["successes"] / max(1, self.session_stats["attempts"])
        ) * 100

        print("\n" + "=" * 60)
        print("🚀 ADVANCED OPTIMIZATION PROGRESS")
        print("=" * 60)
        print(f"📊 Total Events: {self.current_total}/90 (82.2%)")
        print(f"🎯 Remaining: {self.remaining} events needed")
        print(f"⏱️  Session Time: {elapsed:.1f} minutes")
        print(
            f"📈 Success Rate: {success_rate:.1f}% ({self.session_stats['successes']}/{self.session_stats['attempts']})"
        )
        print(f"🚫 Rate Limited: {self.session_stats['rate_limited']} requests")

        # Platform performance
        if self.session_stats["platform_success"]:
            print("\n📋 Platform Performance:")
            for platform, count in self.session_stats["platform_success"].items():
                print(f"   {platform}: {count} events")
        print("=" * 60)

    async def run_optimization(self):
        """Run the complete advanced optimization strategy"""
        logger.info("🚀 Starting Advanced Multi-Platform Optimization")

        # Check service health
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(
                            f"✅ Service healthy: {data.get('region', 'unknown')}"
                        )
                    else:
                        logger.error("❌ Service not healthy")
                        return
        except Exception as e:
            logger.error(f"💥 Cannot connect to service: {e}")
            return

        await self.print_progress()

        all_discovered_events = []

        # Process each platform with intelligent ordering
        # Start with conference websites (most likely to work)
        platform_order = [
            2,
            0,
            1,
            3,
        ]  # Conference sites, Eventbrite, Meetup, Lu.ma alternatives

        for platform_idx in platform_order:
            platform = self.platforms[platform_idx]
            platform_events = await self.process_platform(platform)

            if platform_events:
                all_discovered_events.extend(platform_events)
                logger.info(
                    f"🎉 Platform {platform['name']}: +{len(platform_events)} events"
                )

                # Check if target achieved
                if len(all_discovered_events) >= self.remaining:
                    logger.info(
                        f"🏆 TARGET ACHIEVED! Found {len(all_discovered_events)} events!"
                    )
                    break

            # Longer delay between platforms
            if platform_idx < len(platform_order) - 1:
                logger.info("⏸️  Switching platforms... (30s delay)")
                await asyncio.sleep(30)

        # Final results
        await self.print_progress()

        results = {
            "timestamp": datetime.now().isoformat(),
            "session_results": self.session_stats,
            "total_events_found": len(all_discovered_events),
            "events_needed": self.remaining,
            "target_achieved": len(all_discovered_events) >= self.remaining,
            "platform_performance": self.session_stats["platform_success"],
            "new_events": all_discovered_events[
                : self.remaining
            ],  # Limit to what we need
        }

        # Save results
        with open("advanced_optimization_results.json", "w") as f:
            json.dump(results, f, indent=2)
        logger.info("📄 Results saved to advanced_optimization_results.json")

        return results


async def main():
    optimizer = AdvancedEventDiscovery()
    await optimizer.run_optimization()


if __name__ == "__main__":
    asyncio.run(main())
