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
import logging
import time
from typing import Any, Dict, List, Optional

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
        self.session: Optional[aiohttp.ClientSession] = None
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

    async def check_steel_browser_health(self) -> Optional[Dict[str, Any]]:
        """Check Steel Browser service health and capabilities"""
        try:
            if not self.session:
                logger.error("❌ Session not initialized")
                return None

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
            if not self.session:
                logger.error("❌ Session not initialized")
                return {"success": False, "error": "Session not initialized"}

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

    async def get_target_urls(self) -> List[str]:
        """Get target URLs for Steel Browser extraction"""
        return [
            # Current crypto event calendars and platforms
            "https://www.ethcc.io/",  # EthCC main site
            "https://ethglobal.com/events",  # ETHGlobal events
            "https://coindesk.com/events/",  # CoinDesk events
            "https://blockchainevent.com/",  # Blockchain events
            "https://www.meetup.com/blockchain-developers-united/",  # Blockchain meetup
            "https://www.eventbrite.com/d/ca--san-francisco/blockchain/",  # Eventbrite blockchain events
            # Lu.ma crypto communities (these should exist)
            "https://lu.ma/ethereum",
            "https://lu.ma/crypto",
            "https://lu.ma/web3",
            "https://lu.ma/defi",
        ]

    async def validate_url(self, session: aiohttp.ClientSession, url: str) -> bool:
        """Quick validation to check if URL is accessible"""
        try:
            async with session.head(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status in [200, 201, 202, 301, 302, 307, 308]
        except Exception:
            return False

    async def get_valid_target_urls(self) -> List[str]:
        """Get target URLs and validate they're accessible"""
        all_urls = await self.get_target_urls()
        valid_urls = []

        async with aiohttp.ClientSession() as session:
            logger.info(f"🔍 Validating {len(all_urls)} target URLs...")

            validation_tasks = []
            for url in all_urls:
                validation_tasks.append(self.validate_url(session, url))

            results = await asyncio.gather(*validation_tasks, return_exceptions=True)

            for url, is_valid in zip(all_urls, results, strict=False):
                if isinstance(is_valid, bool) and is_valid:
                    valid_urls.append(url)
                    logger.info(f"✅ Valid: {url}")
                else:
                    logger.warning(f"❌ Invalid: {url}")

        logger.info(f"📊 Found {len(valid_urls)} valid URLs out of {len(all_urls)}")
        return valid_urls

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
        target_urls = await self.get_valid_target_urls()

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

    async def steel_browser_extract(
        self, session: aiohttp.ClientSession, url: str, anti_bot_level: str
    ) -> Optional[Dict[str, Any]]:
        """Extract using Steel Browser with anti-bot capabilities"""
        try:
            payload = {
                "urls": [url],
                "mcp_browser": True,
                "anti_bot_level": anti_bot_level,
                "timeout": 120000,
                "wait_for": "networkidle",
                "extract_events": True,
            }

            logger.info(
                f"🚀 Steel Browser extraction: {url} (Anti-bot: {anti_bot_level})"
            )
            logger.debug(f"🔧 Payload: {payload}")

            async with session.post(
                f"{self.steel_browser_url}/extract",  # Fixed endpoint
                json=payload,
                timeout=aiohttp.ClientTimeout(total=150),
            ) as response:
                logger.debug(f"📊 Response status: {response.status}")

                if response.status == 200:
                    result = await response.json()
                    logger.info(
                        f"✅ Success: {result.get('total_events', 0)} events extracted"
                    )
                    logger.debug(
                        f"📈 Processing time: {result.get('processing_time', 0):.2f}s"
                    )
                    logger.debug(f"💰 Cost: ${result.get('cost', 0):.4f}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(
                        f"❌ Steel Browser extraction failed: {response.status} - {error_text}"
                    )
                    return None

        except Exception as e:
            logger.error(f"💥 Steel Browser extraction error: {str(e)}")
            return None

    def calculate_event_quality_score(self, event_data: Dict[str, Any]) -> float:
        """Calculate quality score for an event to prevent storing low-quality data"""
        score = 0.0
        max_score = 10.0

        # Name quality (20%)
        if event_data.get("name"):
            if len(event_data["name"]) > 10:
                score += 2.0
            elif len(event_data["name"]) > 5:
                score += 1.0

        # Description quality (20%)
        if event_data.get("description"):
            desc_len = len(event_data["description"])
            if desc_len > 100:
                score += 2.0
            elif desc_len > 50:
                score += 1.5
            elif desc_len > 20:
                score += 1.0

        # Time information (20%)
        if event_data.get("start_time_iso"):
            score += 2.0
        elif event_data.get("date"):
            score += 1.0

        # Location information (15%)
        if event_data.get("location_name") or event_data.get("location_address"):
            score += 1.5

        # URL quality (10%)
        if event_data.get("url") or event_data.get("luma_url"):
            score += 1.0

        # Category/type information (10%)
        if event_data.get("category"):
            score += 1.0

        # Cost information (5%)
        if event_data.get("cost") or event_data.get("cost_category"):
            score += 0.5

        return min(score / max_score, 1.0)  # Return as percentage

    def create_event_hash(self, event_data: Dict[str, Any]) -> str:
        """Create hash for duplicate detection"""
        # Create a hash based on key identifying fields
        key_fields = [
            event_data.get("name", "").strip().lower(),
            event_data.get("url", ""),
            event_data.get("luma_url", ""),
            str(event_data.get("start_time_iso", "")),
            event_data.get("location_name", "").strip().lower(),
        ]

        # Remove empty fields and join
        hash_string = "|".join([f for f in key_fields if f])

        import hashlib

        return hashlib.md5(hash_string.encode()).hexdigest()

    def optimize_event_storage(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize event data for storage to reduce costs"""
        optimized = event_data.copy()

        # Truncate long descriptions (keep most important info)
        if optimized.get("description") and len(optimized["description"]) > 1000:
            optimized["description"] = optimized["description"][:997] + "..."
            logger.info("📝 Truncated long description for storage optimization")

        # Remove or compress large raw data if it exists
        if optimized.get("raw_scraped_data"):
            # Keep only essential raw data, remove redundant HTML
            raw_data = optimized["raw_scraped_data"]
            if isinstance(raw_data, dict) and len(str(raw_data)) > 5000:
                # Keep only structured data, remove large HTML content
                essential_fields = [
                    "name",
                    "description",
                    "date",
                    "time",
                    "location",
                    "url",
                    "price",
                ]
                optimized["raw_scraped_data"] = {
                    k: v
                    for k, v in raw_data.items()
                    if k in essential_fields or len(str(v)) < 500
                }
                logger.info("🗜️ Compressed raw data for storage optimization")

        # Add quality score and storage optimization flags
        optimized["completeness_score"] = self.calculate_event_quality_score(event_data)
        optimized["storage_optimized"] = True

        return optimized


async def main():
    """Run Steel Browser optimized extraction with cost optimization"""
    print("=" * 70)
    print("🚀 STEEL BROWSER OPTIMIZED EXTRACTION WITH COST OPTIMIZATION")
    print("=" * 70)

    extractor = SteelBrowserOptimizedExtractor()

    # Configuration for cost optimization
    MIN_QUALITY_SCORE = 0.4  # Only store events with >40% quality score
    seen_hashes = set()  # Track duplicates within this session

    stats = {
        "urls_processed": 0,
        "total_events_found": 0,
        "quality_filtered_events": 0,
        "duplicate_events": 0,
        "stored_events": 0,
        "storage_savings_estimated": 0,
    }

    try:
        # Get validated URLs
        target_urls = await extractor.get_valid_target_urls()
        logger.info(f"🎯 Processing {len(target_urls)} validated URLs")

        for url in target_urls:
            stats["urls_processed"] += 1
            logger.info(
                f"\n🌐 Processing URL {stats['urls_processed']}/{len(target_urls)}: {url}"
            )

            # Try different anti-bot levels if needed
            for anti_bot_level in ["STANDARD", "ADVANCED", "STEALTH"]:
                async with aiohttp.ClientSession() as session:
                    result = await extractor.steel_browser_extract(
                        session, url, anti_bot_level
                    )

                    if result and result.get("success") and result.get("events"):
                        events = result["events"]
                        stats["total_events_found"] += len(events)

                        logger.info(
                            f"✅ Found {len(events)} events with {anti_bot_level} level"
                        )

                        # Process each event with cost optimization
                        for event in events:
                            # 1. Calculate quality score
                            quality_score = extractor.calculate_event_quality_score(
                                event
                            )

                            # 2. Check quality threshold
                            if quality_score < MIN_QUALITY_SCORE:
                                stats["quality_filtered_events"] += 1
                                logger.info(
                                    f"⚠️ Skipping low-quality event (score: {quality_score:.2f}): {event.get('name', 'Unnamed')[:50]}..."
                                )
                                continue

                            # 3. Check for duplicates
                            event_hash = extractor.create_event_hash(event)
                            if event_hash in seen_hashes:
                                stats["duplicate_events"] += 1
                                logger.info(
                                    f"🔄 Skipping duplicate event: {event.get('name', 'Unnamed')[:50]}..."
                                )
                                continue

                            seen_hashes.add(event_hash)

                            # 4. Optimize for storage
                            optimized_event = extractor.optimize_event_storage(event)

                            # 5. Simulate storage (in real implementation, would save to database)
                            stats["stored_events"] += 1
                            logger.info(
                                f"💾 Stored optimized event (quality: {quality_score:.2f}): {optimized_event.get('name', 'Unnamed')[:50]}..."
                            )

                        break  # Success with this anti-bot level
                    else:
                        logger.warning(f"⚠️ No events found with {anti_bot_level} level")

                        if anti_bot_level == "STEALTH":
                            logger.error(f"❌ All anti-bot levels failed for {url}")

    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")

    # Calculate savings
    events_prevented = stats["quality_filtered_events"] + stats["duplicate_events"]
    if stats["total_events_found"] > 0:
        prevention_rate = (events_prevented / stats["total_events_found"]) * 100
        stats["storage_savings_estimated"] = int(prevention_rate)

    # Final report
    print("\n" + "=" * 70)
    print("📊 EXTRACTION & COST OPTIMIZATION REPORT")
    print("=" * 70)
    print(f"🌐 URLs Processed: {stats['urls_processed']}")
    print(f"📊 Total Events Found: {stats['total_events_found']}")
    print(f"💾 Events Stored: {stats['stored_events']}")
    print(f"⚠️ Quality Filtered: {stats['quality_filtered_events']} (prevented storage)")
    print(f"🔄 Duplicates Filtered: {stats['duplicate_events']} (prevented storage)")
    print(f"💰 Storage Prevention Rate: {stats['storage_savings_estimated']:.1f}%")

    if stats["stored_events"] > 0:
        print(
            f"✅ Success! Stored {stats['stored_events']} high-quality, unique events"
        )
        print(
            f"💡 Cost optimization prevented storing {events_prevented} low-value events"
        )
    else:
        print("⚠️ No events stored - check URLs and extraction logic")

    print("\n🎯 COST OPTIMIZATION BENEFITS:")
    print("  • Prevented storage of duplicate events")
    print("  • Filtered out low-quality events before storage")
    print("  • Optimized event data size for storage efficiency")
    print("  • Added quality scoring for future analysis")
    print("  • Maintained data quality while reducing costs")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
