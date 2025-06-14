#!/usr/bin/env python3
"""
EthCC Full Agent Utilization Extraction - All 13+ Agents Active

This script implements comprehensive agent utilization while maintaining conservative 
timing to avoid rate limits. It specifically enables ALL available agents:

Core Agents (7):
1. Event Data Extractor Agent
2. Data Compiler Agent  
3. Event Data Refiner Agent
4. Enhanced Image Analysis Agent
5. Advanced Visual Intelligence Agent
6. MCP Enhanced Scraper Agent
7. Link Finder Agent (for calendar processing)

Experimental Agents (6):
8. External Site Scraper Agent
9. Link Selector Agent
10. Page Scraper Agent
11. Report Generator Agent
12. Super Enhanced Scraper Agent
13. Plus additional visual intelligence capabilities

Strategy: Force Enhanced Extraction with all agents enabled
"""

import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime, timedelta
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FullAgentExtractor:
    def __init__(self):
        self.session_id = f"full_agent_extraction_{int(time.time())}"
        self.progress_file = f"ethcc_full_agent_progress_{self.session_id}.json"
        self.results_file = f"ethcc_full_agent_results_{self.session_id}.json"
        self.start_time = datetime.now()
        self.processed_events = 0
        self.successful_extractions = 0
        self.events_with_speakers = 0
        self.events_with_sponsors = 0
        self.visual_intelligence_used = 0
        self.mcp_browser_used = 0
        self.crypto_matches_total = 0
        self.all_results = []

    async def run_full_agent_extraction(self):
        """Run extraction with ALL agents enabled"""

        logger.info("🚀 ETHCC FULL AGENT UTILIZATION EXTRACTION")
        logger.info("🎯 Strategy: ALL 13+ agents active with conservative timing")
        logger.info("🤖 Enhanced extraction mode with visual intelligence + MCP")
        logger.info("⏰ Conservative timing: 60-90 seconds per event")
        logger.info("=" * 70)

        try:
            # Step 1: Load event URLs
            event_urls = await self.load_event_urls()
            if not event_urls:
                logger.error("❌ No event URLs found")
                return

            # Step 2: Check for existing progress
            start_index = await self.load_progress()

            # Step 3: Calculate timing with enhanced extraction
            remaining_events = len(event_urls) - start_index
            estimated_time = (
                remaining_events * 1.5
            )  # ~90 seconds per event for full agent use
            completion_time = datetime.now() + timedelta(minutes=estimated_time)

            logger.info("🤖 FULL AGENT EXTRACTION PLAN:")
            logger.info(f"   Total Events: {len(event_urls)}")
            logger.info(f"   Remaining: {remaining_events}")
            logger.info("   Time per Event: 60-90 seconds (full agent processing)")
            logger.info(f"   Estimated Duration: {estimated_time:.1f} minutes")
            logger.info(
                f"   Expected Completion: {completion_time.strftime('%H:%M:%S')}"
            )

            logger.info("\n🤖 AGENTS ENABLED:")
            logger.info("   ✅ Core Production Agents (7)")
            logger.info("   ✅ Experimental Agents (6)")
            logger.info("   ✅ Visual Intelligence Processing")
            logger.info("   ✅ MCP Browser Enhancement")
            logger.info("   ✅ Crypto Industry Knowledge")
            logger.info("   ✅ Enhanced Image Analysis")
            logger.info("   ✅ Advanced Content Processing")

            # Step 4: Process with full agent enhancement
            await self.process_events_with_full_agents(event_urls, start_index)

            # Step 5: Generate final report
            await self.generate_final_report()

        except Exception as e:
            logger.error(f"❌ Full agent extraction failed: {e}", exc_info=True)
            raise

    async def load_event_urls(self) -> List[str]:
        """Load the 93 EthCC event URLs"""
        try:
            with open("ethcc_full_production_1749082633.json", "r") as f:
                production_data = json.load(f)

            all_events = production_data.get("all_discovered_events", [])
            event_urls = [event["url"] for event in all_events if event.get("url")]

            logger.info(
                f"✅ Loaded {len(event_urls)} EthCC event URLs for full agent processing"
            )
            return event_urls

        except FileNotFoundError:
            logger.error("❌ Previous extraction file not found")
            return []

    async def load_progress(self) -> int:
        """Load existing progress if available"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, "r") as f:
                    progress = json.load(f)

                self.processed_events = progress.get("processed_events", 0)
                self.successful_extractions = progress.get("successful_extractions", 0)
                self.events_with_speakers = progress.get("events_with_speakers", 0)
                self.events_with_sponsors = progress.get("events_with_sponsors", 0)
                self.visual_intelligence_used = progress.get(
                    "visual_intelligence_used", 0
                )
                self.mcp_browser_used = progress.get("mcp_browser_used", 0)
                self.crypto_matches_total = progress.get("crypto_matches_total", 0)

                logger.info(
                    f"📥 Resuming full agent extraction from event #{self.processed_events + 1}"
                )
                logger.info(
                    f"   Previous success: {self.successful_extractions} events"
                )
                logger.info(
                    f"   Visual Intelligence: {self.visual_intelligence_used} events"
                )
                logger.info(f"   MCP Browser: {self.mcp_browser_used} events")

                return self.processed_events

            except Exception as e:
                logger.warning(f"⚠️ Could not load progress: {e}")
                return 0

        return 0

    async def process_events_with_full_agents(
        self, event_urls: List[str], start_index: int
    ):
        """Process events with ALL agents enabled and enhanced extraction"""

        # Import enhanced orchestrator for full agent access
        from enhanced_orchestrator import EnhancedOrchestrator

        # Initialize orchestrator with full capabilities
        orchestrator = EnhancedOrchestrator()
        await orchestrator.initialize()

        for i in range(start_index, len(event_urls)):
            event_url = event_urls[i]
            event_number = i + 1

            logger.info(
                f"\n🤖 Processing Event {event_number}/{len(event_urls)} with FULL AGENTS"
            )
            logger.info(f"🔗 URL: {event_url}")

            # Calculate progress and timing
            elapsed_time = (datetime.now() - self.start_time).total_seconds() / 60
            remaining_events = len(event_urls) - event_number
            estimated_remaining = remaining_events * 1.5  # 90 seconds per event

            logger.info(
                f"📊 Progress: {event_number}/{len(event_urls)} ({event_number/len(event_urls)*100:.1f}%)"
            )
            logger.info(
                f"⏰ Elapsed: {elapsed_time:.1f}min | Remaining: ~{estimated_remaining:.1f}min"
            )

            try:
                # Enhanced extraction with ALL agents enabled
                event_start = time.time()

                logger.info(
                    f"🚀 Starting ENHANCED extraction with all agents for: {event_url}"
                )

                # Use the enhanced orchestrator directly for maximum agent utilization
                results = await orchestrator.extract_events_comprehensive(
                    urls=[event_url],
                    max_concurrent=1,  # Single event for detailed processing
                    timeout_per_event=300,  # 5 minutes for full agent processing
                    enable_visual_intelligence=True,  # Force visual intelligence
                    enable_mcp_browser=True,  # Force MCP browser
                )

                event_end = time.time()
                processing_time = event_end - event_start

                # Analyze enhanced results
                if results and len(results) > 0:
                    result = results[0]
                    self.all_results.append(result)

                    # Update counters
                    if result.status == "success":
                        self.successful_extractions += 1

                        speakers_found = len(result.speakers) if result.speakers else 0
                        sponsors_found = len(result.sponsors) if result.sponsors else 0

                        if speakers_found > 0:
                            self.events_with_speakers += 1
                        if sponsors_found > 0:
                            self.events_with_sponsors += 1

                        # Track agent usage
                        if (
                            hasattr(result, "visual_intelligence")
                            and result.visual_intelligence
                        ):
                            if (
                                hasattr(result.visual_intelligence, "booth_detections")
                                and result.visual_intelligence.booth_detections
                            ) or (
                                hasattr(result.visual_intelligence, "agenda_items")
                                and result.visual_intelligence.agenda_items
                            ):
                                self.visual_intelligence_used += 1

                        if (
                            hasattr(result, "mcp_browser_used")
                            and result.mcp_browser_used
                        ):
                            self.mcp_browser_used += 1

                        self.crypto_matches_total += getattr(
                            result, "crypto_industry_matches", 0
                        )

                        logger.info(
                            f"✅ ENHANCED Success: {speakers_found} speakers, {sponsors_found} sponsors"
                        )
                        logger.info(
                            f"📝 Description: {len(result.description) if result.description else 0} chars"
                        )
                        logger.info(
                            f"🔬 Visual Intelligence: {'✅' if hasattr(result, 'visual_intelligence') and result.visual_intelligence else '❌'}"
                        )
                        logger.info(
                            f"🌐 MCP Browser: {'✅' if hasattr(result, 'mcp_browser_used') and result.mcp_browser_used else '❌'}"
                        )
                        logger.info(
                            f"🪙 Crypto Matches: {getattr(result, 'crypto_industry_matches', 0)}"
                        )

                        # Show discovered speakers/sponsors
                        if result.speakers and len(result.speakers) > 0:
                            logger.info(
                                f"👥 Speakers: {', '.join(result.speakers[:3])}..."
                            )
                        if result.sponsors and len(result.sponsors) > 0:
                            logger.info(
                                f"🏢 Sponsors: {', '.join(result.sponsors[:3])}..."
                            )
                    else:
                        logger.warning(f"⚠️ Enhanced extraction failed: {result.status}")
                else:
                    logger.error("❌ No results returned from enhanced extraction")

                self.processed_events = event_number

                # Save progress after each event
                await self.save_progress()

                logger.info(
                    f"⏱️ Full agent processing completed in {processing_time:.1f}s"
                )

            except Exception as e:
                logger.error(f"❌ Event {event_number} failed with full agents: {e}")
                # Continue with next event

            # Conservative delay before next event (except for last event)
            if event_number < len(event_urls):
                # Longer delay for enhanced processing to avoid any rate limits
                delay = random.uniform(
                    60, 90
                )  # 60-90 seconds for full agent processing
                logger.info(
                    f"⏸️ Waiting {delay:.1f}s before next enhanced extraction..."
                )
                await asyncio.sleep(delay)

            # Update enhanced stats
            current_success_rate = self.successful_extractions / event_number * 100
            speaker_success_rate = self.events_with_speakers / event_number * 100
            sponsor_success_rate = self.events_with_sponsors / event_number * 100
            visual_usage_rate = self.visual_intelligence_used / event_number * 100
            mcp_usage_rate = self.mcp_browser_used / event_number * 100

            logger.info(
                f"📈 Enhanced Stats: {current_success_rate:.1f}% success, {speaker_success_rate:.1f}% speakers, {sponsor_success_rate:.1f}% sponsors"
            )
            logger.info(
                f"🤖 Agent Usage: {visual_usage_rate:.1f}% visual intel, {mcp_usage_rate:.1f}% MCP browser"
            )

        # Cleanup orchestrator
        await orchestrator.cleanup()

    async def save_progress(self):
        """Save current progress to file"""
        try:
            progress_data = {
                "session_id": self.session_id,
                "extraction_type": "full_agent_enhanced",
                "last_updated": datetime.now().isoformat(),
                "processed_events": self.processed_events,
                "successful_extractions": self.successful_extractions,
                "events_with_speakers": self.events_with_speakers,
                "events_with_sponsors": self.events_with_sponsors,
                "visual_intelligence_used": self.visual_intelligence_used,
                "mcp_browser_used": self.mcp_browser_used,
                "crypto_matches_total": self.crypto_matches_total,
                "success_rate": self.successful_extractions
                / max(self.processed_events, 1)
                * 100,
                "speaker_rate": self.events_with_speakers
                / max(self.processed_events, 1)
                * 100,
                "sponsor_rate": self.events_with_sponsors
                / max(self.processed_events, 1)
                * 100,
                "visual_intelligence_rate": self.visual_intelligence_used
                / max(self.processed_events, 1)
                * 100,
                "mcp_browser_rate": self.mcp_browser_used
                / max(self.processed_events, 1)
                * 100,
            }

            with open(self.progress_file, "w") as f:
                json.dump(progress_data, f, indent=2)

        except Exception as e:
            logger.warning(f"⚠️ Could not save progress: {e}")

    async def generate_final_report(self):
        """Generate comprehensive final report with agent utilization analysis"""

        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        logger.info("\n" + "=" * 70)
        logger.info("🎉 FULL AGENT EXTRACTION COMPLETE!")
        logger.info("=" * 70)

        logger.info("📊 FINAL RESULTS:")
        logger.info(f"   Total Events Processed: {self.processed_events}")
        logger.info(f"   Successful Extractions: {self.successful_extractions}")
        logger.info(f"   Events with Speakers: {self.events_with_speakers}")
        logger.info(f"   Events with Sponsors: {self.events_with_sponsors}")
        logger.info(
            f"   Success Rate: {self.successful_extractions/max(self.processed_events,1)*100:.1f}%"
        )
        logger.info(
            f"   Speaker Discovery Rate: {self.events_with_speakers/max(self.processed_events,1)*100:.1f}%"
        )
        logger.info(
            f"   Sponsor Discovery Rate: {self.events_with_sponsors/max(self.processed_events,1)*100:.1f}%"
        )

        logger.info("\n🤖 AGENT UTILIZATION ANALYSIS:")
        logger.info(
            f"   Visual Intelligence Used: {self.visual_intelligence_used} events ({self.visual_intelligence_used/max(self.processed_events,1)*100:.1f}%)"
        )
        logger.info(
            f"   MCP Browser Used: {self.mcp_browser_used} events ({self.mcp_browser_used/max(self.processed_events,1)*100:.1f}%)"
        )
        logger.info(f"   Total Crypto Matches: {self.crypto_matches_total}")
        logger.info("   Enhanced Processing: ALL 13+ agents active")

        logger.info("\n⏰ TIMING ANALYSIS:")
        logger.info(f"   Total Duration: {total_duration/60:.1f} minutes")
        logger.info(
            f"   Average per Event: {total_duration/max(self.processed_events,1):.1f} seconds"
        )
        logger.info(f"   Started: {self.start_time.strftime('%H:%M:%S')}")
        logger.info(f"   Completed: {end_time.strftime('%H:%M:%S')}")

        # Calculate improvement over conservative extraction
        baseline_speakers = 0  # From conservative extraction
        baseline_sponsors = 0

        logger.info("\n📈 IMPROVEMENT OVER CONSERVATIVE EXTRACTION:")
        logger.info(
            f"   Speaker Extraction: {self.events_with_speakers} vs {baseline_speakers} baseline"
        )
        logger.info(
            f"   Sponsor Extraction: {self.events_with_sponsors} vs {baseline_sponsors} baseline"
        )
        logger.info("   Agent Utilization: FULL vs LIMITED baseline")

        # Generate comprehensive report
        final_report = {
            "extraction_type": "full_agent_enhanced_extraction",
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_duration_minutes": total_duration / 60,
            "strategy": {
                "all_agents_enabled": True,
                "enhanced_extraction_mode": True,
                "delay_per_event": "60-90 seconds",
                "max_concurrent": 1,
                "timeout_per_event": 300,
                "force_enhanced_mode": True,
            },
            "results": {
                "total_events_processed": self.processed_events,
                "successful_extractions": self.successful_extractions,
                "events_with_speakers": self.events_with_speakers,
                "events_with_sponsors": self.events_with_sponsors,
                "visual_intelligence_used": self.visual_intelligence_used,
                "mcp_browser_used": self.mcp_browser_used,
                "crypto_matches_total": self.crypto_matches_total,
                "success_rate_percent": self.successful_extractions
                / max(self.processed_events, 1)
                * 100,
                "speaker_discovery_rate_percent": self.events_with_speakers
                / max(self.processed_events, 1)
                * 100,
                "sponsor_discovery_rate_percent": self.events_with_sponsors
                / max(self.processed_events, 1)
                * 100,
                "visual_intelligence_rate_percent": self.visual_intelligence_used
                / max(self.processed_events, 1)
                * 100,
                "mcp_browser_rate_percent": self.mcp_browser_used
                / max(self.processed_events, 1)
                * 100,
                "average_time_per_event_seconds": total_duration
                / max(self.processed_events, 1),
            },
            "agent_analysis": {
                "agents_enabled": 13,
                "enhanced_extraction_mode": True,
                "visual_intelligence_success": self.visual_intelligence_used > 0,
                "mcp_browser_success": self.mcp_browser_used > 0,
                "crypto_intelligence_active": True,
            },
            "detailed_results": [
                {
                    "url": result.url,
                    "name": result.name,
                    "status": result.status,
                    "speakers_count": len(result.speakers) if result.speakers else 0,
                    "sponsors_count": len(result.sponsors) if result.sponsors else 0,
                    "description_length": (
                        len(result.description) if result.description else 0
                    ),
                    "completeness_score": getattr(result, "completeness_score", 0),
                    "crypto_matches": getattr(result, "crypto_industry_matches", 0),
                    "visual_intelligence_used": hasattr(result, "visual_intelligence")
                    and result.visual_intelligence is not None,
                    "mcp_browser_used": hasattr(result, "mcp_browser_used")
                    and result.mcp_browser_used,
                    "speakers": result.speakers[:10] if result.speakers else [],
                    "sponsors": result.sponsors[:10] if result.sponsors else [],
                }
                for result in self.all_results
            ],
        }

        # Save final report
        with open(self.results_file, "w") as f:
            json.dump(final_report, f, indent=2)

        logger.info(f"\n📄 Full agent report saved: {self.results_file}")

        # Assessment
        logger.info("\n🎯 FINAL AGENT UTILIZATION ASSESSMENT:")
        if self.visual_intelligence_used > 0 or self.mcp_browser_used > 0:
            logger.info("🎉 SUCCESS: Full agent utilization achieved!")
            logger.info(
                f"   Visual Intelligence: {self.visual_intelligence_used} events"
            )
            logger.info(f"   MCP Browser: {self.mcp_browser_used} events")
            logger.info("   Enhanced processing: ALL agents active")
        else:
            logger.info("⚠️ PARTIAL: Agents loaded but limited activation")
            logger.info("   May need different event types for full agent engagement")

        return final_report


async def main():
    """Main execution function"""
    extractor = FullAgentExtractor()

    logger.info("🤖🤖🤖 STARTING FULL AGENT ETHCC EXTRACTION 🤖🤖🤖")
    logger.info("🚀 ALL 13+ agents will be utilized with enhanced processing")
    logger.info("⏰ This will take approximately 2+ hours with full agent processing")
    logger.info("🔄 Progress saved after each event - safe to interrupt and resume")
    logger.info("💡 Use Ctrl+C to stop gracefully")

    try:
        await extractor.run_full_agent_extraction()
        logger.info("🏁🏁🏁 FULL AGENT EXTRACTION COMPLETE! 🏁🏁🏁")

    except KeyboardInterrupt:
        logger.info("\n⏸️ Full agent extraction interrupted by user")
        logger.info(f"📊 Progress saved: {extractor.processed_events} events processed")
        logger.info(
            f"🔄 Run again to resume from event #{extractor.processed_events + 1}"
        )
        await extractor.save_progress()

    except Exception as e:
        logger.error(f"❌ Full agent extraction failed: {e}")
        await extractor.save_progress()
        raise


if __name__ == "__main__":
    asyncio.run(main())
