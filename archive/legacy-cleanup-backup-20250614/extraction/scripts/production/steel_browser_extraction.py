#!/usr/bin/env python3
"""
Steel Browser Enhanced Production Extraction Script
Leverages Steel Browser capabilities to bypass rate limiting and extract 90+ events

Key Steel Browser Capabilities:
- Advanced anti-bot evasion
- IP rotation via Google Cloud regions
- CAPTCHA solving
- Session persistence
- Rate limiting bypass
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List

import aiohttp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SteelBrowserOptimizedExtractor:
    """Steel Browser enhanced extractor with advanced capabilities"""

    def __init__(self):
        self.steel_browser_url = (
            "https://steel-browser-orchestrator-867263134607.us-central1.run.app"
        )
        self.session = None
        self.total_events = 0
        self.total_costs = 0.0

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def check_steel_browser_health(self) -> Dict[str, Any]:
        """Check Steel Browser service health and capabilities"""
        try:
            async with self.session.get(f"{self.steel_browser_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    logger.info(f"🚀 Steel Browser Health: {health_data['status']}")
                    logger.info(
                        f"🔧 Capabilities: Steel Browser={health_data['capabilities']['steel_browser']}"
                    )
                    logger.info(
                        f"🌍 IP Rotation: {health_data['capabilities']['ip_rotation']}"
                    )
                    logger.info(
                        f"🛡️ Rate Limiting Evasion: {health_data['capabilities']['rate_limiting_evasion']}"
                    )
                    return health_data
                else:
                    logger.error(
                        f"❌ Steel Browser health check failed: {response.status}"
                    )
                    return None
        except Exception as e:
            logger.error(f"❌ Steel Browser health check error: {e}")
            return None

    async def extract_with_steel_browser_advanced(
        self, url: str, anti_bot_level: str = "ADVANCED"
    ) -> Dict[str, Any]:
        """
        Extract events using Steel Browser with advanced anti-bot capabilities

        Args:
            url: Target URL for extraction
            anti_bot_level: STANDARD, ADVANCED, or STEALTH
        """
        try:
            logger.info(
                f"🚀 Steel Browser extraction: {url} (Anti-bot: {anti_bot_level})"
            )

            payload = {
                "urls": [url],
                "mcp_browser": True,
                "steel_browser_config": {
                    "anti_bot_level": anti_bot_level,
                    "session_persistence": True,
                    "captcha_solving": True,
                    "rate_limiting_evasion": True,
                    "ip_rotation": True,
                    "stealth_mode": True,
                    "timeout": 60000,  # 60 seconds
                    "wait_for_content": True,
                    "extract_dynamic_content": True,
                },
                "extraction_strategy": "comprehensive_event_discovery",
            }

            start_time = time.time()

            async with self.session.post(
                f"{self.steel_browser_url}/v2/extract_steel_browser",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120),  # 2 minute timeout
            ) as response:

                extraction_time = time.time() - start_time

                if response.status == 200:
                    result = await response.json()

                    # Extract key metrics
                    events_found = len(result.get("events", []))
                    cost = result.get("cost", 0.0)
                    method = result.get("extraction_method", "unknown")
                    steel_browser_used = result.get("steel_browser_used", False)

                    # Log results
                    logger.info(
                        f"✅ Steel Browser Success: {events_found} events, ${cost:.4f} cost, {extraction_time:.1f}s"
                    )
                    logger.info(
                        f"🔧 Method: {method}, Steel Browser: {steel_browser_used}"
                    )

                    # Update totals
                    self.total_events += events_found
                    self.total_costs += cost

                    return {
                        "success": True,
                        "events": result.get("events", []),
                        "events_count": events_found,
                        "cost": cost,
                        "extraction_time": extraction_time,
                        "method": method,
                        "steel_browser_used": steel_browser_used,
                        "anti_bot_level": anti_bot_level,
                    }

                else:
                    logger.error(
                        f"❌ Steel Browser extraction failed: {response.status}"
                    )
                    error_text = await response.text()
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}",
                        "extraction_time": extraction_time,
                    }

        except asyncio.TimeoutError:
            logger.error(f"⏱️ Steel Browser extraction timeout for {url}")
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            logger.error(f"❌ Steel Browser extraction error: {e}")
            return {"success": False, "error": str(e)}

    async def progressive_extraction_strategy(
        self, base_urls: List[str]
    ) -> Dict[str, Any]:
        """
        Progressive extraction strategy using Steel Browser capabilities:
        1. Start with STANDARD anti-bot level
        2. Escalate to ADVANCED if rate limited
        3. Use STEALTH mode for maximum evasion
        4. Implement intelligent retry with delays
        """
        all_events = []
        total_costs = 0.0
        extraction_stats = {
            "attempts": 0,
            "successes": 0,
            "rate_limited": 0,
            "bypassed": 0,
        }

        # Anti-bot escalation levels
        anti_bot_levels = ["STANDARD", "ADVANCED", "STEALTH"]

        for url in base_urls:
            logger.info(f"🎯 Processing URL: {url}")

            # Try each anti-bot level until successful
            for level_idx, anti_bot_level in enumerate(anti_bot_levels):
                extraction_stats["attempts"] += 1

                # Progressive delay based on previous attempts
                if level_idx > 0:
                    delay = 15 * (2**level_idx)  # Exponential backoff: 30s, 60s
                    logger.info(
                        f"⏳ Anti-bot escalation delay: {delay}s (Level: {anti_bot_level})"
                    )
                    await asyncio.sleep(delay)

                result = await self.extract_with_steel_browser_advanced(
                    url, anti_bot_level
                )

                if result["success"]:
                    events = result.get("events", [])
                    cost = result.get("cost", 0.0)

                    logger.info(
                        f"✅ Success with {anti_bot_level}: {len(events)} events, ${cost:.4f}"
                    )

                    all_events.extend(events)
                    total_costs += cost
                    extraction_stats["successes"] += 1

                    if level_idx > 0:
                        extraction_stats["bypassed"] += 1
                        logger.info(
                            f"🛡️ Rate limiting bypassed using {anti_bot_level} mode!"
                        )

                    break  # Success, move to next URL

                else:
                    error = result.get("error", "Unknown error")
                    if "429" in str(error) or "rate" in str(error).lower():
                        extraction_stats["rate_limited"] += 1
                        logger.warning(
                            f"⚠️ Rate limited with {anti_bot_level}, escalating..."
                        )
                        if level_idx < len(anti_bot_levels) - 1:
                            continue  # Try next level

                    logger.error(f"❌ Failed with {anti_bot_level}: {error}")

                    if level_idx == len(anti_bot_levels) - 1:
                        logger.error(f"💀 All anti-bot levels failed for {url}")

        return {
            "total_events": len(all_events),
            "events": all_events,
            "total_cost": total_costs,
            "stats": extraction_stats,
            "success_rate": extraction_stats["successes"]
            / max(extraction_stats["attempts"], 1)
            * 100,
        }

    async def comprehensive_extraction_campaign(self) -> Dict[str, Any]:
        """
        Comprehensive extraction campaign leveraging Steel Browser's full capabilities
        """
        logger.info("🚀 Starting Steel Browser Enhanced Extraction Campaign")

        # Check Steel Browser health first
        health = await self.check_steel_browser_health()
        if not health or health.get("status") != "healthy":
            logger.error("❌ Steel Browser service not healthy, aborting")
            return {"success": False, "error": "Steel Browser service unhealthy"}

        # Target URLs for comprehensive extraction
        target_urls = [
            "https://lu.ma/ethcc",
            "https://lu.ma/ethcc-2024",
            "https://lu.ma/ethcc/program",
            "https://lu.ma/events/eth",
            "https://lu.ma/events/ethereum",
            "https://lu.ma/events/crypto",
            "https://lu.ma/events/defi",
            "https://lu.ma/events/web3",
            "https://www.ethcc.io/program",
            "https://www.ethcc.io/schedule",
        ]

        # Execute progressive extraction strategy
        start_time = time.time()
        results = await self.progressive_extraction_strategy(target_urls)
        total_time = time.time() - start_time

        # Generate comprehensive report
        report = {
            "campaign_status": "complete",
            "total_extraction_time": f"{total_time:.1f}s",
            "events_discovered": results["total_events"],
            "total_cost": f"${results['total_cost']:.4f}",
            "extraction_stats": results["stats"],
            "success_rate": f"{results['success_rate']:.1f}%",
            "steel_browser_performance": {
                "anti_bot_escalations": results["stats"]["bypassed"],
                "rate_limiting_bypassed": results["stats"]["bypassed"] > 0,
                "stealth_mode_effectiveness": (
                    "High" if results["stats"]["bypassed"] > 0 else "Standard"
                ),
            },
            "target_achievement": {
                "target": 90,
                "achieved": results["total_events"],
                "percentage": f"{(results['total_events'] / 90) * 100:.1f}%",
                "status": (
                    "Target Achieved"
                    if results["total_events"] >= 90
                    else "Optimization Needed"
                ),
            },
        }

        # Log final results
        logger.info("🎉 STEEL BROWSER EXTRACTION CAMPAIGN COMPLETE")
        logger.info(f"📊 Events Discovered: {results['total_events']}")
        logger.info(f"💰 Total Cost: ${results['total_cost']:.4f}")
        logger.info(f"📈 Success Rate: {results['success_rate']:.1f}%")
        logger.info(f"🛡️ Rate Limiting Bypassed: {results['stats']['bypassed']} times")
        logger.info(
            f"🎯 Target Progress: {results['total_events']}/90 ({(results['total_events'] / 90) * 100:.1f}%)"
        )

        return report


async def main():
    """Main execution function"""
    logger.info("🚀 Steel Browser Enhanced Production Extraction")
    logger.info("🎯 Goal: Extract 90+ events using Steel Browser capabilities")
    logger.info("🛡️ Strategy: Progressive anti-bot escalation with rate limiting bypass")

    async with SteelBrowserOptimizedExtractor() as extractor:
        try:
            results = await extractor.comprehensive_extraction_campaign()

            # Save results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"steel_browser_extraction_report_{timestamp}.json"

            with open(filename, "w") as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"📄 Results saved to: {filename}")

            # Display summary
            print("\n" + "=" * 60)
            print("🎉 STEEL BROWSER EXTRACTION COMPLETE")
            print("=" * 60)
            print(f"📊 Events Discovered: {results['events_discovered']}")
            print(f"💰 Total Cost: {results['total_cost']}")
            print(f"📈 Success Rate: {results['success_rate']}")
            print(
                f"🛡️ Anti-bot Escalations: {results['steel_browser_performance']['anti_bot_escalations']}"
            )
            print(
                f"🎯 Target Achievement: {results['target_achievement']['percentage']}"
            )
            print(f"📄 Report: {filename}")
            print("=" * 60)

        except KeyboardInterrupt:
            logger.info("⏹️ Extraction interrupted by user")
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
