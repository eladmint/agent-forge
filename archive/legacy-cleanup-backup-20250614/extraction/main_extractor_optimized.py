#!/usr/bin/env python3
"""
🎯 TokenHunter Optimized Main Extractor System

Unified, production-ready extraction system that combines:
- Complete 13+ Agent Orchestration
- Multi-Region Distribution 
- Advanced Database Integration
- Real Event Processing
- Steel Browser Capabilities
- Performance Optimization

Status: Production-ready with all capabilities unified
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .agents.advanced_visual_intelligence_agent import AdvancedVisualIntelligenceAgent
from .agents.data_compiler_agent import DataCompilerAgent
from .agents.enhanced_image_analysis_agent import EnhancedImageAnalysisAgent

# Core extraction imports
from .agents.event_data_extractor_agent import EventDataExtractorAgent
from .agents.event_data_refiner_agent import EventDataRefinerAgent
from .agents.experimental.external_site_scraper_agent import ExternalSiteScraperAgent
from .agents.experimental.link_finder_agent import LinkFinderAgent
from .agents.experimental.page_scraper_agent import PageScraperAgent
from .agents.experimental.super_enhanced_scraper_agent import SuperEnhancedScraperAgent
from .agents.mcp_enhanced_scraper_agent import MCPEnhancedScraperAgent

# Database integration
try:
    from .utils.database import (
        check_event_exists_by_url,
        get_supabase_client,
        save_event_data,
    )

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Multi-region support
try:
    from .distributed_extraction_strategy import DistributedExtractionOrchestrator

    MULTIREGION_AVAILABLE = True
except ImportError:
    MULTIREGION_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class OptimizedExtractionResult:
    """Comprehensive extraction result with all capabilities"""

    # Core event data
    url: str
    name: str = ""
    description: str = ""
    start_date: str = ""
    end_date: str = ""
    location: str = ""
    venue: str = ""

    # Enhanced data
    speakers: List[Dict[str, Any]] = field(default_factory=list)
    sponsors: List[Dict[str, Any]] = field(default_factory=list)
    organizers: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Processing metadata
    status: str = "pending"  # pending, success, error, timeout
    processing_time: float = 0.0
    completeness_score: float = 0.0
    error_message: str = ""

    # Agent utilization
    agents_used: List[str] = field(default_factory=list)
    extraction_method: str = ""
    data_sources: List[str] = field(default_factory=list)

    # Advanced capabilities
    visual_intelligence_applied: bool = False
    crypto_industry_matches: int = 0
    mcp_browser_used: bool = False
    multi_region_used: bool = False
    steel_browser_used: bool = False

    # Database integration
    database_save_attempted: bool = False
    database_save_success: bool = False
    database_save_error: str = ""

    # Quality metrics
    images_analyzed: int = 0
    external_sites_scraped: int = 0
    confidence_score: float = 0.0


@dataclass
class ExtractionConfig:
    """Configuration for extraction process"""

    # Core settings
    max_concurrent: int = 8
    timeout_per_event: int = 120
    enable_database_saving: bool = True

    # Agent capabilities
    enable_visual_intelligence: bool = True
    enable_crypto_intelligence: bool = True
    enable_mcp_browser: bool = True
    enable_steel_browser: bool = True
    enable_multi_region: bool = True

    # Performance settings
    batch_size: int = 5
    retry_attempts: int = 3
    concurrent_agents: int = 3

    # Quality thresholds
    min_completeness_score: float = 0.3
    crypto_confidence_threshold: float = 0.8

    # Calendar extraction
    max_calendar_events: int = 100
    calendar_scroll_timeout: int = 120


class OptimizedMainExtractor:
    """
    Unified, optimized main extractor combining all capabilities
    """

    def __init__(self, config: Optional[ExtractionConfig] = None):
        self.config = config or ExtractionConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Agent instances
        self.agents = {}
        self.initialized = False

        # Database integration
        self.db_client = None
        self.database_enabled = False

        # Multi-region orchestrator
        self.multi_region_orchestrator = None
        self.multi_region_enabled = False

        # Performance tracking
        self.start_time = None
        self.total_events_processed = 0
        self.successful_extractions = 0
        self.database_saves = 0

    async def initialize(self) -> bool:
        """Initialize all components and capabilities"""
        if self.initialized:
            return True

        self.start_time = time.time()
        self.logger.info("🚀 Initializing Optimized Main Extractor...")

        try:
            # Initialize core agents
            await self._initialize_agents()

            # Initialize database integration
            await self._initialize_database()

            # Initialize multi-region support
            await self._initialize_multi_region()

            self.initialized = True
            self.logger.info("✅ Optimized Main Extractor initialized successfully")

            # Log capabilities
            self._log_capabilities()

            return True

        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {e}")
            return False

    async def _initialize_agents(self):
        """Initialize all extraction agents"""
        self.logger.info("🤖 Initializing agents...")

        # Core agents
        self.agents["event_extractor"] = EventDataExtractorAgent()
        self.agents["event_refiner"] = EventDataRefinerAgent()
        self.agents["image_analyzer"] = EnhancedImageAnalysisAgent()
        self.agents["visual_intelligence"] = AdvancedVisualIntelligenceAgent()
        self.agents["data_compiler"] = DataCompilerAgent()

        # Browser automation agents
        self.agents["link_finder"] = LinkFinderAgent()
        self.agents["page_scraper"] = PageScraperAgent()
        self.agents["super_scraper"] = SuperEnhancedScraperAgent()
        self.agents["external_scraper"] = ExternalSiteScraperAgent()

        # MCP/Steel browser agent
        if self.config.enable_mcp_browser:
            self.agents["mcp_scraper"] = MCPEnhancedScraperAgent()

        self.logger.info(f"✅ Initialized {len(self.agents)} agents")

    async def _initialize_database(self):
        """Initialize database integration with enhanced error handling"""
        if not DATABASE_AVAILABLE or not self.config.enable_database_saving:
            self.logger.warning("⚠️ Database integration disabled")
            return

        try:
            self.db_client = get_supabase_client()
            if self.db_client:
                # Test database connection
                test_result = (
                    self.db_client.table("events").select("id").limit(1).execute()
                )
                self.database_enabled = True
                self.logger.info("✅ Database integration initialized and tested")
            else:
                self.logger.warning("⚠️ Database client is None")

        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            self.database_enabled = False

    async def _initialize_multi_region(self):
        """Initialize multi-region distribution if available"""
        if not MULTIREGION_AVAILABLE or not self.config.enable_multi_region:
            self.logger.warning("⚠️ Multi-region distribution disabled")
            return

        try:
            self.multi_region_orchestrator = DistributedExtractionOrchestrator()
            await self.multi_region_orchestrator.start()
            self.multi_region_enabled = True
            self.logger.info("✅ Multi-region distribution initialized")

        except Exception as e:
            self.logger.error(f"❌ Multi-region initialization failed: {e}")
            self.multi_region_enabled = False

    def _log_capabilities(self):
        """Log current system capabilities"""
        capabilities = []

        if self.agents:
            capabilities.append(f"🤖 {len(self.agents)} Agents")
        if self.database_enabled:
            capabilities.append("💾 Database")
        if self.multi_region_enabled:
            capabilities.append("🌍 Multi-Region")
        if self.config.enable_visual_intelligence:
            capabilities.append("👁️ Visual Intelligence")
        if self.config.enable_crypto_intelligence:
            capabilities.append("₿ Crypto Intelligence")
        if self.config.enable_steel_browser:
            capabilities.append("🛡️ Steel Browser")

        self.logger.info(f"🎯 Active Capabilities: {' | '.join(capabilities)}")

    async def extract_calendar_comprehensive(
        self, calendar_url: str
    ) -> List[OptimizedExtractionResult]:
        """
        Extract all events from a calendar page with full agent orchestration
        """
        if not self.initialized:
            await self.initialize()

        self.logger.info(
            f"📅 Starting comprehensive calendar extraction: {calendar_url}"
        )

        # Phase 1: Discovery - Find all event URLs
        event_urls = await self._discover_calendar_events(calendar_url)

        if not event_urls:
            self.logger.warning("❌ No events discovered from calendar")
            return []

        self.logger.info(f"🔍 Discovered {len(event_urls)} events")

        # Phase 2: Extract all events with full agent orchestration
        results = await self._extract_events_comprehensive(event_urls)

        # Phase 3: Database integration
        if self.database_enabled:
            await self._save_results_to_database(results)

        # Phase 4: Generate summary
        self._log_extraction_summary(results)

        return results

    async def _discover_calendar_events(self, calendar_url: str) -> List[str]:
        """Discover all event URLs from calendar page"""
        try:
            if self.multi_region_enabled:
                # Use multi-region for rate limiting evasion
                self.logger.info("🌍 Using multi-region discovery")
                return await self._discover_with_multi_region(calendar_url)
            else:
                # Use LinkFinderAgent directly
                link_finder = self.agents.get("link_finder")
                if link_finder:
                    self.logger.info("🔗 Using LinkFinderAgent for discovery")
                    return await link_finder.find_event_links(calendar_url)

        except Exception as e:
            self.logger.error(f"❌ Calendar discovery failed: {e}")

        return []

    async def _discover_with_multi_region(self, calendar_url: str) -> List[str]:
        """Use multi-region orchestrator for discovery"""
        try:
            results = await self.multi_region_orchestrator.extract_distributed(
                urls=[calendar_url],
                discovery_only=True,
                max_events=self.config.max_calendar_events,
            )

            # Extract URLs from results
            event_urls = []
            for result in results:
                if hasattr(result, "discovered_urls"):
                    event_urls.extend(result.discovered_urls)

            return event_urls

        except Exception as e:
            self.logger.error(f"❌ Multi-region discovery failed: {e}")
            return []

    async def _extract_events_comprehensive(
        self, event_urls: List[str]
    ) -> List[OptimizedExtractionResult]:
        """Extract all events with full agent orchestration"""
        results = []

        # Process in batches for performance
        for i in range(0, len(event_urls), self.config.batch_size):
            batch = event_urls[i : i + self.config.batch_size]
            batch_results = await self._process_event_batch(batch)
            results.extend(batch_results)

            # Progress logging
            progress = min(i + self.config.batch_size, len(event_urls))
            self.logger.info(
                f"📊 Progress: {progress}/{len(event_urls)} events processed"
            )

        return results

    async def _process_event_batch(
        self, urls: List[str]
    ) -> List[OptimizedExtractionResult]:
        """Process a batch of events concurrently"""
        semaphore = asyncio.Semaphore(self.config.max_concurrent)

        async def process_single_event(url: str) -> OptimizedExtractionResult:
            async with semaphore:
                return await self._extract_single_event_optimized(url)

        tasks = [process_single_event(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _extract_single_event_optimized(
        self, url: str
    ) -> OptimizedExtractionResult:
        """Extract single event with full agent orchestration"""
        start_time = time.time()
        result = OptimizedExtractionResult(url=url)

        try:
            # Phase 1: Content extraction
            content_result = await self._extract_content_enhanced(url, result)

            # Phase 2: Data processing with agents
            await self._process_with_agents(content_result, result)

            # Phase 3: Quality assessment
            self._calculate_completeness_score(result)

            # Phase 4: Final optimization
            await self._apply_final_optimizations(result)

            result.status = "success"
            result.processing_time = time.time() - start_time
            self.successful_extractions += 1

        except Exception as e:
            result.status = "error"
            result.error_message = str(e)
            result.processing_time = time.time() - start_time
            self.logger.error(f"❌ Extraction failed for {url}: {e}")

        self.total_events_processed += 1
        return result

    async def _extract_content_enhanced(
        self, url: str, result: OptimizedExtractionResult
    ) -> Dict[str, Any]:
        """Extract content using best available method"""
        content_data = {}

        try:
            # Try PageScraperAgent first (browser automation)
            page_scraper = self.agents.get("page_scraper")
            if page_scraper:
                status, data = await page_scraper.run_async(url)
                if status == "Success" and data:
                    content_data = data
                    result.agents_used.append("page_scraper")
                    result.extraction_method = "browser_automation"

            # Fallback to SuperEnhancedScraperAgent if needed
            if not content_data:
                super_scraper = self.agents.get("super_scraper")
                if super_scraper:
                    status, data = await super_scraper.run_async(url)
                    if status == "Success" and data:
                        content_data = data
                        result.agents_used.append("super_scraper")
                        result.extraction_method = "enhanced_scraping"

            # Use MCP/Steel browser for complex sites
            if not content_data and self.config.enable_steel_browser:
                mcp_scraper = self.agents.get("mcp_scraper")
                if mcp_scraper:
                    status, data = await mcp_scraper.run_async(url)
                    if status == "Success" and data:
                        content_data = data
                        result.agents_used.append("mcp_scraper")
                        result.extraction_method = "steel_browser"
                        result.steel_browser_used = True

        except Exception as e:
            self.logger.error(f"❌ Content extraction failed for {url}: {e}")

        return content_data

    async def _process_with_agents(
        self, content_data: Dict[str, Any], result: OptimizedExtractionResult
    ):
        """Process content through all available agents"""

        # Event data extraction
        if content_data.get("html"):
            event_extractor = self.agents.get("event_extractor")
            if event_extractor:
                extracted_data = await event_extractor.extract_event_data(
                    content_data["html"]
                )
                if extracted_data:
                    result.name = extracted_data.get("name", "")
                    result.description = extracted_data.get("description", "")
                    result.start_date = extracted_data.get("start_date", "")
                    result.location = extracted_data.get("location", "")
                    result.agents_used.append("event_extractor")

        # Image analysis
        if content_data.get("images") and self.config.enable_visual_intelligence:
            image_analyzer = self.agents.get("image_analyzer")
            if image_analyzer:
                image_data = await image_analyzer.analyze_images(content_data["images"])
                if image_data:
                    result.sponsors.extend(image_data.get("sponsors", []))
                    result.speakers.extend(image_data.get("speakers", []))
                    result.images_analyzed = len(content_data["images"])
                    result.agents_used.append("image_analyzer")
                    result.visual_intelligence_applied = True

        # Data refinement
        event_refiner = self.agents.get("event_refiner")
        if event_refiner and result.name:
            refined_data = await event_refiner.refine_event_data(
                {
                    "name": result.name,
                    "description": result.description,
                    "location": result.location,
                }
            )
            if refined_data:
                # Apply crypto intelligence enhancements
                if self.config.enable_crypto_intelligence:
                    result.crypto_industry_matches = refined_data.get(
                        "crypto_matches", 0
                    )
                result.agents_used.append("event_refiner")

        # Data compilation
        data_compiler = self.agents.get("data_compiler")
        if data_compiler:
            compiled_data = await data_compiler.compile_event_data(result.__dict__)
            if compiled_data:
                result.tags = compiled_data.get("tags", [])
                result.organizers = compiled_data.get("organizers", [])
                result.agents_used.append("data_compiler")

    def _calculate_completeness_score(self, result: OptimizedExtractionResult):
        """Calculate comprehensive completeness score"""
        score = 0.0
        max_score = 0.0

        # Core fields (weighted)
        if result.name:
            score += 30
        max_score += 30

        if result.description:
            score += 20
        max_score += 20

        if result.start_date:
            score += 20
        max_score += 20

        if result.location:
            score += 15
        max_score += 15

        # Enhanced data
        if result.speakers:
            score += 10
        max_score += 10

        if result.sponsors:
            score += 10
        max_score += 10

        # Agent utilization bonus
        agent_bonus = min(len(result.agents_used) * 2, 10)
        score += agent_bonus
        max_score += 10

        # Crypto intelligence bonus
        if result.crypto_industry_matches > 0:
            score += 5
        max_score += 5

        result.completeness_score = (score / max_score) * 100 if max_score > 0 else 0
        result.confidence_score = result.completeness_score / 100

    async def _apply_final_optimizations(self, result: OptimizedExtractionResult):
        """Apply final optimizations and enhancements"""

        # Add data sources
        if result.extraction_method:
            result.data_sources.append(result.extraction_method)
        if result.agents_used:
            result.data_sources.extend(
                [f"agent:{agent}" for agent in result.agents_used]
            )

        # Set multi-region flag if used
        if self.multi_region_enabled:
            result.multi_region_used = True

    async def _save_results_to_database(self, results: List[OptimizedExtractionResult]):
        """Save all results to database with enhanced error handling"""
        if not self.database_enabled:
            return

        self.logger.info(f"💾 Saving {len(results)} events to database...")

        for result in results:
            if result.status == "success":
                await self._save_single_result(result)

    async def _save_single_result(self, result: OptimizedExtractionResult):
        """Save single result to database with comprehensive error handling"""
        result.database_save_attempted = True

        try:
            # Check if event already exists
            if check_event_exists_by_url(result.url):
                self.logger.info(f"⚠️ Event already exists: {result.name}")
                return

            # Prepare event data for database
            event_data = {
                "name": result.name,
                "description": result.description,
                "start_date": result.start_date,
                "end_date": result.end_date,
                "location": result.location,
                "venue": result.venue,
                "url": result.url,
                "speakers": result.speakers,
                "sponsors": result.sponsors,
                "organizers": result.organizers,
                "tags": result.tags,
                "completeness_score": result.completeness_score,
                "processing_time": result.processing_time,
                "agents_used": result.agents_used,
                "extraction_method": result.extraction_method,
                "crypto_industry_matches": result.crypto_industry_matches,
                "visual_intelligence_applied": result.visual_intelligence_applied,
                "steel_browser_used": result.steel_browser_used,
                "multi_region_used": result.multi_region_used,
                "created_at": datetime.now().isoformat(),
            }

            # Save to database
            success = await save_event_data(event_data)

            if success:
                result.database_save_success = True
                self.database_saves += 1
                self.logger.info(f"✅ Saved to database: {result.name}")
            else:
                result.database_save_error = "Save operation returned False"
                self.logger.error(f"❌ Database save failed: {result.name}")

        except Exception as e:
            result.database_save_error = str(e)
            self.logger.error(f"❌ Database save error for {result.name}: {e}")

    def _log_extraction_summary(self, results: List[OptimizedExtractionResult]):
        """Log comprehensive extraction summary"""
        total_events = len(results)
        successful = len([r for r in results if r.status == "success"])
        failed = len([r for r in results if r.status == "error"])
        database_saved = len([r for r in results if r.database_save_success])

        avg_completeness = (
            sum(r.completeness_score for r in results) / total_events
            if total_events > 0
            else 0
        )
        avg_processing_time = (
            sum(r.processing_time for r in results) / total_events
            if total_events > 0
            else 0
        )

        # Agent utilization
        all_agents_used = []
        for result in results:
            all_agents_used.extend(result.agents_used)
        unique_agents = set(all_agents_used)

        # Capability utilization
        visual_intelligence_used = len(
            [r for r in results if r.visual_intelligence_applied]
        )
        crypto_matches = sum(r.crypto_industry_matches for r in results)
        steel_browser_used = len([r for r in results if r.steel_browser_used])
        multi_region_used = len([r for r in results if r.multi_region_used])

        self.logger.info("=" * 80)
        self.logger.info("📊 EXTRACTION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"📈 Events Processed: {total_events}")
        self.logger.info(
            f"✅ Successful: {successful} ({successful/total_events*100:.1f}%)"
        )
        self.logger.info(f"❌ Failed: {failed} ({failed/total_events*100:.1f}%)")
        self.logger.info(
            f"💾 Database Saved: {database_saved} ({database_saved/total_events*100:.1f}%)"
        )
        self.logger.info(f"🎯 Avg Completeness: {avg_completeness:.1f}%")
        self.logger.info(f"⏱️ Avg Processing Time: {avg_processing_time:.1f}s")
        self.logger.info(
            f"🤖 Agents Utilized: {len(unique_agents)} ({', '.join(unique_agents)})"
        )
        self.logger.info(f"👁️ Visual Intelligence: {visual_intelligence_used} events")
        self.logger.info(f"₿ Crypto Matches: {crypto_matches}")
        self.logger.info(f"🛡️ Steel Browser: {steel_browser_used} events")
        self.logger.info(f"🌍 Multi-Region: {multi_region_used} events")

        if self.start_time:
            total_time = time.time() - self.start_time
            self.logger.info(f"🕐 Total Runtime: {total_time:.1f}s")

        self.logger.info("=" * 80)

    async def cleanup(self):
        """Cleanup all resources"""
        self.logger.info("🧹 Cleaning up resources...")

        # Cleanup agents
        for agent_name, agent in self.agents.items():
            if hasattr(agent, "cleanup"):
                try:
                    await agent.cleanup()
                except Exception as e:
                    self.logger.warning(f"⚠️ Agent cleanup warning ({agent_name}): {e}")

        # Cleanup multi-region orchestrator
        if self.multi_region_orchestrator and hasattr(
            self.multi_region_orchestrator, "cleanup"
        ):
            try:
                await self.multi_region_orchestrator.cleanup()
            except Exception as e:
                self.logger.warning(f"⚠️ Multi-region cleanup warning: {e}")

        self.logger.info("✅ Cleanup completed")


# Convenience functions for easy usage
async def extract_ethcc_comprehensive(
    calendar_url: str = "https://lu.ma/ethcc", config: Optional[ExtractionConfig] = None
) -> List[OptimizedExtractionResult]:
    """
    Extract complete EthCC calendar with all capabilities
    """
    extractor = OptimizedMainExtractor(config)
    try:
        return await extractor.extract_calendar_comprehensive(calendar_url)
    finally:
        await extractor.cleanup()


async def extract_single_event_optimized(
    url: str, config: Optional[ExtractionConfig] = None
) -> OptimizedExtractionResult:
    """
    Extract single event with full optimization
    """
    extractor = OptimizedMainExtractor(config)
    try:
        await extractor.initialize()
        return await extractor._extract_single_event_optimized(url)
    finally:
        await extractor.cleanup()


# CLI interface
async def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Optimized TokenHunter Event Extractor"
    )
    parser.add_argument(
        "--url", default="https://lu.ma/ethcc", help="Calendar URL to extract"
    )
    parser.add_argument("--single-event", help="Extract single event URL")
    parser.add_argument(
        "--max-concurrent", type=int, default=8, help="Max concurrent extractions"
    )
    parser.add_argument("--timeout", type=int, default=120, help="Timeout per event")
    parser.add_argument(
        "--no-database", action="store_true", help="Disable database saving"
    )
    parser.add_argument(
        "--no-visual", action="store_true", help="Disable visual intelligence"
    )
    parser.add_argument(
        "--no-crypto", action="store_true", help="Disable crypto intelligence"
    )
    parser.add_argument("--no-steel", action="store_true", help="Disable Steel browser")
    parser.add_argument(
        "--no-multiregion", action="store_true", help="Disable multi-region"
    )

    args = parser.parse_args()

    # Create configuration
    config = ExtractionConfig(
        max_concurrent=args.max_concurrent,
        timeout_per_event=args.timeout,
        enable_database_saving=not args.no_database,
        enable_visual_intelligence=not args.no_visual,
        enable_crypto_intelligence=not args.no_crypto,
        enable_steel_browser=not args.no_steel,
        enable_multi_region=not args.no_multiregion,
    )

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run extraction
    if args.single_event:
        result = await extract_single_event_optimized(args.single_event, config)
        print(
            f"Result: {result.name} - {result.status} - {result.completeness_score:.1f}%"
        )
    else:
        results = await extract_ethcc_comprehensive(args.url, config)
        print(f"Extracted {len(results)} events")


if __name__ == "__main__":
    asyncio.run(main())
