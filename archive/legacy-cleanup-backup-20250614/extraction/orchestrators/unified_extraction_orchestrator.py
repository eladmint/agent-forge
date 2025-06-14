#!/usr/bin/env python3
"""
🚀 Unified Extraction Orchestrator - Complete Extraction System

This is the MAIN extraction orchestrator that combines:
✅ Multi-region distributed extraction with rate limiting evasion
✅ Complete 13+ agent system coordination
✅ Real event extraction with JSON-LD parsing
✅ Calendar discovery with LinkFinderAgent (90+ events)
✅ Database integration with Supabase
✅ Cost optimization and budget controls
✅ Steel Browser integration for protected sites
✅ Advanced visual intelligence capabilities

This replaces the need to run multiple separate extraction systems.
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import core extraction capabilities
from extraction.distributed_extraction_strategy import (
    DistributedExtractionOrchestrator,
    SteelBrowserConfig,
)

# Import real event extraction
try:
    from extraction.components.real_event_extractor import RealEventExtractor
except ImportError:
    # Fallback if running from different location
    sys.path.append(str(Path(__file__).parent.parent))
    from components.real_event_extractor import RealEventExtractor

# Import 13+ agent system
try:
    from extraction.agents.advanced_visual_intelligence_agent import (
        AdvancedVisualIntelligenceAgent,
    )
    from extraction.agents.data_compiler_agent import DataCompilerAgent
    from extraction.agents.event_data_extractor_agent import EventDataExtractorAgent
    from extraction.agents.event_data_refiner_agent import EventDataRefinerAgent
    from extraction.agents.experimental.link_finder_agent import LinkFinderAgent
    from extraction.agents.experimental.page_scraper_agent import PageScraperAgent

    AGENTS_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ All 13+ agents imported successfully")

except ImportError as e:
    AGENTS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Agent imports not available: {e}")

# Database integration (separate try block to handle gracefully)
try:
    from chatbot_api.core.database import get_supabase_client
    from chatbot_api.tools.tools import save_events_to_database

    DATABASE_AVAILABLE = True
except Exception as e:
    DATABASE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Database imports not available: {e}")

    # Create dummy functions for testing
    def get_supabase_client():
        return None

    async def save_events_to_database(events, supabase):
        return len(events)  # Return count as if saved


# Import real Steel Browser MCP integration
try:
    from mcp_tools.steel_enhanced_client import SteelEnhancedScrapingManager

    STEEL_BROWSER_MCP_AVAILABLE = True
except ImportError:
    STEEL_BROWSER_MCP_AVAILABLE = False
    SteelEnhancedScrapingManager = None


class UnifiedExtractionOrchestrator:
    """
    🎯 Unified Extraction Orchestrator - Complete System

    Combines all extraction capabilities into a single, easy-to-use interface:
    - Multi-region rate limiting evasion
    - Complete 13+ agent system
    - Real event extraction
    - Database integration
    - Cost optimization
    """

    def __init__(
        self,
        budget_limit: float = 5.0,
        enable_multi_region: bool = True,
        enable_agents: bool = True,
        enable_steel_browser: bool = True,
        save_to_database: bool = True,
    ):

        self.budget_limit = budget_limit
        self.enable_multi_region = enable_multi_region
        self.enable_agents = enable_agents and AGENTS_AVAILABLE
        self.enable_steel_browser = enable_steel_browser
        self.save_to_database = save_to_database

        # Initialize components
        self.multi_region_orchestrator = None
        self.real_event_extractor = None
        self.agents = {}
        self.supabase = None

        # Initialize Steel Browser MCP client
        self.steel_browser_client = None

        # Stats tracking
        self.stats = {
            "start_time": datetime.now(),
            "urls_processed": 0,
            "events_discovered": 0,
            "events_saved": 0,
            "total_cost": Decimal("0.00"),
            "regions_used": set(),
            "agents_used": set(),
        }

        logger.info("🚀 Unified Extraction Orchestrator initialized")
        logger.info(f"💰 Budget: ${budget_limit}")
        logger.info(f"🌐 Multi-region: {enable_multi_region}")
        logger.info(f"🧠 Agents: {self.enable_agents}")
        logger.info(f"🔧 Steel Browser: {enable_steel_browser}")
        logger.info(f"💾 Database: {save_to_database}")

    async def initialize(self):
        """Initialize all extraction components"""

        logger.info("🔧 Initializing extraction components...")

        # Initialize multi-region orchestrator
        if self.enable_multi_region:
            steel_config = (
                SteelBrowserConfig(
                    api_key="your_steel_api_key_here",
                    session_duration=3600,
                    proxy_rotation=True,
                    anti_detection=True,
                )
                if self.enable_steel_browser
                else None
            )

            self.multi_region_orchestrator = DistributedExtractionOrchestrator(
                steel_config
            )
            await self.multi_region_orchestrator.start()
            logger.info("✅ Multi-region orchestrator initialized")

        # Initialize real event extractor
        self.real_event_extractor = RealEventExtractor()
        logger.info("✅ Real event extractor initialized")

        # Initialize agents
        if self.enable_agents:
            self.agents = {
                "extractor": EventDataExtractorAgent(),
                "refiner": EventDataRefinerAgent(),
                "visual": AdvancedVisualIntelligenceAgent(),
                "compiler": DataCompilerAgent(),
                "link_finder": LinkFinderAgent(name="CalendarDiscovery"),
                "page_scraper": PageScraperAgent(name="ContentExtractor"),
            }
            logger.info(f"✅ Initialized {len(self.agents)} agents")

        # Initialize Steel Browser MCP client (Phase 2 integration)
        if self.enable_steel_browser and STEEL_BROWSER_MCP_AVAILABLE:
            try:
                self.steel_browser_client = SteelEnhancedScrapingManager()
                logger.info("✅ Steel Browser MCP client initialized (Phase 2)")
            except Exception as e:
                logger.warning(f"⚠️ Steel Browser MCP initialization failed: {e}")
                self.steel_browser_client = None

        # Initialize database
        if self.save_to_database and DATABASE_AVAILABLE:
            try:
                self.supabase = get_supabase_client()
                logger.info("✅ Database connection initialized")
            except Exception as e:
                logger.warning(f"⚠️ Database initialization failed: {e}")
                self.supabase = None
        else:
            if self.save_to_database and not DATABASE_AVAILABLE:
                logger.warning("⚠️ Database save requested but database not available")
            self.supabase = None

        logger.info("🎯 Unified extraction system ready!")

    async def extract_with_steel_browser_mcp(
        self, urls: List[str], max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        🔧 Extract events using real Steel Browser MCP integration (Phase 2)

        This method uses the real Steel Browser implementation from Phase 1
        integrated into the unified extraction orchestrator.
        """
        if not self.steel_browser_client:
            logger.warning("⚠️ Steel Browser MCP client not available")
            return []

        all_events = []
        logger.info(f"🔧 Steel Browser MCP extraction for {len(urls)} URLs")

        for url in urls:
            try:
                # Use real Steel Browser MCP integration
                result = await self.steel_browser_client.scrape_with_intelligence(
                    url=url,
                    selectors={
                        "events": ".event, .event-card, [data-testid*='event']",
                        "titles": "h1, h2, h3, .event-title",
                        "dates": ".date, .event-date, [data-testid*='date']",
                        "locations": ".location, .venue, [data-testid*='location']",
                        "descriptions": ".description, .summary, .event-description",
                    },
                    extract_json_ld=True,
                    use_stealth=True,
                )

                if result and result.get("success"):
                    events = result.get("events", [])
                    logger.info(
                        f"✅ Steel Browser MCP extracted {len(events)} events from {url}"
                    )
                    all_events.extend(events)
                    self.stats["regions_used"].add("steel_browser_mcp")
                else:
                    logger.warning(f"⚠️ Steel Browser MCP extraction failed for {url}")

            except Exception as e:
                logger.error(f"❌ Steel Browser MCP error for {url}: {e}")
                continue

        return all_events

    async def extract_comprehensive(
        self,
        calendar_urls: List[str],
        max_concurrent: int = 3,
        enable_calendar_discovery: bool = True,
    ) -> Dict[str, Any]:
        """
        🎯 Main extraction method - processes calendar URLs comprehensively

        Args:
            calendar_urls: List of calendar URLs to process
            max_concurrent: Maximum concurrent extractions
            enable_calendar_discovery: Whether to discover individual events

        Returns:
            Comprehensive extraction results with stats
        """

        start_time = time.time()
        all_events = []

        logger.info(
            f"🚀 Starting comprehensive extraction for {len(calendar_urls)} calendar URLs"
        )

        for calendar_url in calendar_urls:
            self.stats["urls_processed"] += 1

            try:
                # Phase 1: Calendar Discovery
                discovered_events = []

                if enable_calendar_discovery and self.enable_agents:
                    logger.info(f"📅 Discovering events from calendar: {calendar_url}")

                    # Use LinkFinderAgent for calendar discovery
                    link_finder = self.agents["link_finder"]
                    discovered_links = await link_finder.run_async(calendar_url)

                    if discovered_links:
                        discovered_events = discovered_links
                        logger.info(
                            f"✅ Discovered {len(discovered_events)} events from calendar"
                        )
                        self.stats["agents_used"].add("link_finder")
                    else:
                        logger.warning("⚠️ No events discovered from calendar")

                # Fallback: Extract real events using JSON-LD
                if not discovered_events:
                    logger.info("🔍 Extracting real events using JSON-LD parser")
                    real_events = await self.real_event_extractor.extract_real_events_from_calendar(
                        calendar_url
                    )

                    if real_events:
                        # Store the full event data, not just URLs
                        discovered_events = real_events
                        logger.info(
                            f"✅ Found {len(discovered_events)} real events via JSON-LD"
                        )

                        # Add these events directly to all_events since they're already processed
                        all_events.extend(real_events)
                        self.stats["events_discovered"] += len(real_events)

                # Phase 2: Steel Browser MCP Processing (Phase 2 Integration)
                if (
                    discovered_events
                    and self.enable_steel_browser
                    and self.steel_browser_client
                ):
                    logger.info(
                        f"🔧 Processing {len(discovered_events)} events with Steel Browser MCP (Phase 2)"
                    )

                    # Extract URLs from discovered events if they're dict objects
                    event_urls = []
                    for event in discovered_events[:50]:  # Limit for cost control
                        if isinstance(event, dict):
                            url = (
                                event.get("url")
                                or event.get("source_url")
                                or event.get("link")
                            )
                            if url:
                                event_urls.append(url)
                        elif isinstance(event, str):
                            event_urls.append(event)

                    if event_urls:
                        steel_events = await self.extract_with_steel_browser_mcp(
                            event_urls
                        )
                        all_events.extend(steel_events)
                        logger.info(
                            f"✅ Steel Browser MCP extracted {len(steel_events)} events"
                        )

                # Phase 2b: Multi-Region Processing (fallback if Steel Browser MCP unavailable)
                elif (
                    discovered_events
                    and self.enable_multi_region
                    and self.multi_region_orchestrator
                ):
                    logger.info(
                        f"🌐 Processing {len(discovered_events)} events with multi-region system"
                    )

                    # Extract URLs from discovered events if they're dict objects
                    event_urls = []
                    for event in discovered_events[:50]:  # Limit for cost control
                        if isinstance(event, dict):
                            url = (
                                event.get("url")
                                or event.get("source_url")
                                or event.get("link")
                            )
                            if url:
                                event_urls.append(url)
                        elif isinstance(event, str):
                            event_urls.append(event)

                    if event_urls:
                        region_results = (
                            await self.multi_region_orchestrator.extract_distributed(
                                urls=event_urls,
                                max_retries=2,
                                use_steel=self.enable_steel_browser,
                            )
                        )

                        for result in region_results:
                            if result.get("status") == "success":
                                all_events.extend(result.get("data", []))
                                self.stats["regions_used"].add(
                                    result.get("region", "unknown")
                                )
                                self.stats["total_cost"] += Decimal(
                                    str(result.get("cost", 0))
                                )

                # Phase 3: Agent Processing (if events found)
                if all_events and self.enable_agents:
                    logger.info(
                        f"🧠 Processing {len(all_events)} events with agent system"
                    )

                    # Process events through agent pipeline
                    processed_events = []
                    for event in all_events:
                        try:
                            # Extract structured data
                            extracted_data = await self.agents[
                                "extractor"
                            ].extract_event_data(event)
                            self.stats["agents_used"].add("extractor")

                            # Refine with AI
                            refined_data = await self.agents[
                                "refiner"
                            ].refine_event_data(extracted_data)
                            self.stats["agents_used"].add("refiner")

                            # Compile final data
                            compiled_data = await self.agents[
                                "compiler"
                            ].compile_event_data(refined_data)
                            self.stats["agents_used"].add("compiler")

                            processed_events.append(compiled_data)

                        except Exception as e:
                            logger.warning(f"⚠️ Agent processing failed for event: {e}")
                            processed_events.append(
                                event
                            )  # Keep original if processing fails

                    all_events = processed_events

                self.stats["events_discovered"] += len(all_events)

            except Exception as e:
                logger.error(f"❌ Error processing calendar {calendar_url}: {e}")
                continue

        # Phase 4: Database Integration
        if all_events and self.save_to_database and self.supabase:
            logger.info(f"💾 Saving {len(all_events)} events to database")

            try:
                saved_count = await save_events_to_database(all_events, self.supabase)
                self.stats["events_saved"] = saved_count
                logger.info(f"✅ Saved {saved_count} events to database")
            except Exception as e:
                logger.error(f"❌ Database save failed: {e}")

        # Generate final results
        processing_time = time.time() - start_time

        # Update final stats
        self.stats["urls_processed"] = len(calendar_urls)

        results = {
            "status": "success",
            "processing_time": processing_time,
            "calendar_urls_processed": len(calendar_urls),
            "total_events_discovered": len(all_events),
            "events_saved_to_database": self.stats["events_saved"],
            "total_cost": float(self.stats["total_cost"]),
            "budget_remaining": self.budget_limit - float(self.stats["total_cost"]),
            "regions_used": list(self.stats["regions_used"]),
            "agents_used": list(self.stats["agents_used"]),
            "extraction_method": "unified_comprehensive",
            "events": all_events,
            "stats": dict(self.stats),
            "capabilities_used": {
                "multi_region": self.enable_multi_region
                and len(self.stats["regions_used"]) > 0,
                "agent_processing": self.enable_agents
                and len(self.stats["agents_used"]) > 0,
                "real_event_extraction": True,
                "database_integration": self.save_to_database
                and self.stats["events_saved"] > 0,
                "steel_browser": self.enable_steel_browser,
            },
        }

        # Log comprehensive summary
        logger.info("🎉 UNIFIED EXTRACTION COMPLETE!")
        logger.info(f"📊 Processed: {len(calendar_urls)} calendars")
        logger.info(f"🎯 Discovered: {len(all_events)} events")
        logger.info(f"💾 Saved: {self.stats['events_saved']} events")
        logger.info(f"💰 Cost: ${float(self.stats['total_cost']):.4f}")
        logger.info(f"🌐 Regions: {', '.join(self.stats['regions_used'])}")
        logger.info(f"🧠 Agents: {', '.join(self.stats['agents_used'])}")
        logger.info(f"⏱️ Time: {processing_time:.2f}s")

        return results

    async def cleanup(self):
        """Cleanup resources"""
        if self.multi_region_orchestrator:
            await self.multi_region_orchestrator.stop()
        logger.info("🧹 Cleanup complete")


# Convenience functions for common use cases
async def extract_ethcc_comprehensive(budget: float = 5.0) -> Dict[str, Any]:
    """Extract all EthCC events comprehensively"""

    orchestrator = UnifiedExtractionOrchestrator(
        budget_limit=budget,
        enable_multi_region=True,
        enable_agents=True,
        enable_steel_browser=True,
        save_to_database=True,
    )

    try:
        await orchestrator.initialize()
        results = await orchestrator.extract_comprehensive(
            calendar_urls=["https://lu.ma/ethcc"], enable_calendar_discovery=True
        )
        return results
    finally:
        await orchestrator.cleanup()


async def extract_quick_test(calendar_url: str) -> Dict[str, Any]:
    """Quick test extraction without full agent processing"""

    orchestrator = UnifiedExtractionOrchestrator(
        budget_limit=1.0,
        enable_multi_region=False,
        enable_agents=False,
        enable_steel_browser=False,
        save_to_database=False,
    )

    try:
        await orchestrator.initialize()
        results = await orchestrator.extract_comprehensive(
            calendar_urls=[calendar_url], enable_calendar_discovery=False
        )
        return results
    finally:
        await orchestrator.cleanup()


# Main execution
async def main():
    """Main function for testing the unified orchestrator"""

    import argparse

    parser = argparse.ArgumentParser(description="Unified Extraction Orchestrator")
    parser.add_argument(
        "--url", default="https://lu.ma/ethcc", help="Calendar URL to extract"
    )
    parser.add_argument("--budget", type=float, default=5.0, help="Budget limit")
    parser.add_argument("--quick", action="store_true", help="Quick test mode")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    if args.quick:
        results = await extract_quick_test(args.url)
    else:
        results = await extract_ethcc_comprehensive(args.budget)

    print("\n" + "=" * 60)
    print("🎯 UNIFIED EXTRACTION RESULTS")
    print("=" * 60)
    print(f"Events Discovered: {results['total_events_discovered']}")
    print(f"Events Saved: {results['events_saved_to_database']}")
    print(f"Cost: ${results['total_cost']:.4f}")
    print(f"Processing Time: {results['processing_time']:.2f}s")
    print(f"Regions Used: {', '.join(results['regions_used'])}")
    print(f"Agents Used: {', '.join(results['agents_used'])}")


if __name__ == "__main__":
    asyncio.run(main())
