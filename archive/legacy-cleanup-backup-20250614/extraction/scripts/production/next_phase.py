#!/usr/bin/env python3
"""
Nuru AI - Next Phase Optimization Strategy
Extract remaining 16 events to achieve 100% of 90+ goal
"""

import asyncio
import json
import logging
from datetime import datetime

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NextPhaseOptimizer:
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.current_total = 74  # Current extracted events
        self.target_total = 90  # Target events
        self.remaining = 16  # Events still needed

        # Rate limiting strategy
        self.delays = [2, 5, 10, 15, 20]  # Progressive delays
        self.current_delay_index = 0

        # Alternative lu.ma sources
        self.sources = [
            "crypto-events",
            "blockchain",
            "web3",
            "defi",
            "ethereum",
            "dao",
            "nft",
            "consensus",
            "devcon",
        ]

        self.results = {
            "attempts": 0,
            "successes": 0,
            "events_found": 0,
            "rate_limited": 0,
            "start_time": datetime.now(),
        }

    async def health_check(self):
        """Check service health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        health = await response.json()
                        logger.info(
                            f"Service healthy: {health.get('region', 'unknown')}"
                        )
                        return True
                    return False
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def smart_delay(self, success=True):
        """Intelligent delay management"""
        if success and self.current_delay_index > 0:
            self.current_delay_index -= 1
        elif not success and self.current_delay_index < len(self.delays) - 1:
            self.current_delay_index += 1

        delay = self.delays[self.current_delay_index]
        logger.info(f"Applying {delay}s delay...")
        await asyncio.sleep(delay)

    async def extract_from_source(self, source):
        """Extract events from a specific source"""
        self.results["attempts"] += 1

        source_urls = [
            f"https://lu.ma/{source}",
            f"https://lu.ma/c/{source}",
            f"https://lu.ma/discover/{source}",
        ]

        async with aiohttp.ClientSession() as session:
            for url in source_urls:
                try:
                    logger.info(f"Trying: {url}")

                    async with session.post(
                        f"{self.base_url}/extract",
                        json={"calendar_url": url},
                        timeout=aiohttp.ClientTimeout(total=60),
                    ) as response:

                        if response.status == 429:
                            self.results["rate_limited"] += 1
                            logger.warning(f"Rate limited: {url}")
                            await self.smart_delay(success=False)
                            return 0

                        elif response.status == 200:
                            result = await response.json()
                            events = result.get("events", [])
                            count = len(events)

                            if count > 0:
                                self.results["successes"] += 1
                                self.results["events_found"] += count
                                logger.info(f"✅ Found {count} events from {url}")
                                await self.smart_delay(success=True)
                                return count
                            else:
                                logger.info(f"No events in {url}")

                        await asyncio.sleep(1)  # Brief pause between URLs

                except Exception as e:
                    logger.error(f"Error with {url}: {e}")

        return 0

    def print_progress(self):
        """Print current progress"""
        elapsed = (datetime.now() - self.results["start_time"]).total_seconds() / 60
        current_total = self.current_total + self.results["events_found"]
        remaining = max(0, self.target_total - current_total)

        print(f"\n{'='*50}")
        print("🎯 NURU AI OPTIMIZATION PROGRESS")
        print(f"{'='*50}")
        print(f"📊 Total Events: {current_total}/90 ({current_total/90*100:.1f}%)")
        print(f"🎯 Remaining: {remaining} events needed")
        print(f"📈 Session: +{self.results['events_found']} events")
        print(f"⏱️  Time: {elapsed:.1f} minutes")
        print(
            f"📊 Success Rate: {self.results['successes']}/{self.results['attempts']}"
        )
        print(f"⚠️  Rate Limited: {self.results['rate_limited']}")
        print(f"{'='*50}")

    async def run_optimization(self):
        """Execute optimization strategy"""
        logger.info("🚀 Starting Next Phase Optimization")

        # Health check
        if not await self.health_check():
            logger.error("Service not available!")
            return

        # Extract from sources
        for i, source in enumerate(self.sources):
            self.print_progress()

            if self.results["events_found"] >= self.remaining:
                logger.info("🎉 Target achieved!")
                break

            logger.info(f"Processing source {i+1}/{len(self.sources)}: {source}")
            count = await self.extract_from_source(source)

            # Longer delay between sources
            if i < len(self.sources) - 1:
                await asyncio.sleep(5)

        # Final status
        self.print_progress()

        # Save results
        final_results = {
            "timestamp": datetime.now().isoformat(),
            "session_results": self.results,
            "events_needed": self.remaining,
            "events_found": self.results["events_found"],
            "target_achieved": self.results["events_found"] >= self.remaining,
        }

        # Convert timedelta to string for JSON serialization
        final_results["session_results"]["start_time"] = self.results[
            "start_time"
        ].isoformat()

        with open("optimization_results.json", "w") as f:
            json.dump(final_results, f, indent=2)

        logger.info("Results saved to optimization_results.json")

        if final_results["target_achieved"]:
            logger.info("🎉 OPTIMIZATION SUCCESS!")
        else:
            logger.info(f"Progress: {self.results['events_found']}/{self.remaining}")


async def main():
    optimizer = NextPhaseOptimizer()
    await optimizer.run_optimization()


if __name__ == "__main__":
    asyncio.run(main())
