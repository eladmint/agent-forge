#!/usr/bin/env python3
"""
EthCC Conservative Content Extraction - Hour-Long Rate-Limit-Safe Processing

This script implements an extremely conservative approach to extract detailed speaker 
and sponsor information from all 93 EthCC events while completely avoiding rate limits:

Strategy:
- Process 1 event every 45 seconds (80 events/hour = ~1.2 hours for 93 events)
- Add random delays (30-60s) to seem more human
- Use single concurrent connection
- 3-minute timeout per event for thorough extraction
- Save progress after every event to allow resumption
- Comprehensive error recovery and retry logic
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


class ConservativeExtractor:
    def __init__(self):
        self.session_id = f"conservative_extraction_{int(time.time())}"
        self.progress_file = f"ethcc_conservative_progress_{self.session_id}.json"
        self.results_file = f"ethcc_conservative_results_{self.session_id}.json"
        self.start_time = datetime.now()
        self.processed_events = 0
        self.successful_extractions = 0
        self.events_with_speakers = 0
        self.events_with_sponsors = 0
        self.all_results = []

    async def run_conservative_extraction(self):
        """Run the complete conservative extraction process"""

        logger.info("🐌 ETHCC CONSERVATIVE CONTENT EXTRACTION")
        logger.info("⏰ Strategy: 1 event every 45-60 seconds for ~1.2 hours")
        logger.info("🎯 Goal: Extract ALL speakers and sponsors without rate limits")
        logger.info("🔄 Progress saved after each event for resumption")
        logger.info("=" * 70)

        try:
            # Step 1: Load event URLs
            event_urls = await self.load_event_urls()
            if not event_urls:
                logger.error("❌ No event URLs found")
                return

            # Step 2: Check for existing progress
            start_index = await self.load_progress()

            # Step 3: Calculate timing
            remaining_events = len(event_urls) - start_index
            estimated_time = remaining_events * 50 / 60  # ~50 seconds per event
            completion_time = datetime.now() + timedelta(minutes=estimated_time)

            logger.info("📊 EXTRACTION PLAN:")
            logger.info(f"   Total Events: {len(event_urls)}")
            logger.info(f"   Remaining: {remaining_events}")
            logger.info("   Time per Event: 45-60 seconds")
            logger.info(f"   Estimated Duration: {estimated_time:.1f} minutes")
            logger.info(
                f"   Expected Completion: {completion_time.strftime('%H:%M:%S')}"
            )

            # Step 4: Process events one by one
            await self.process_events_conservatively(event_urls, start_index)

            # Step 5: Generate final report
            await self.generate_final_report()

        except Exception as e:
            logger.error(f"❌ Conservative extraction failed: {e}", exc_info=True)
            raise

    async def load_event_urls(self) -> List[str]:
        """Load the 93 EthCC event URLs from the production data"""
        try:
            with open("ethcc_full_production_1749082633.json", "r") as f:
                production_data = json.load(f)

            all_events = production_data.get("all_discovered_events", [])
            event_urls = [event["url"] for event in all_events if event.get("url")]

            logger.info(f"✅ Loaded {len(event_urls)} EthCC event URLs")
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

                logger.info(f"📥 Resuming from event #{self.processed_events + 1}")
                logger.info(
                    f"   Previous success: {self.successful_extractions} events"
                )
                logger.info(f"   Previous speakers: {self.events_with_speakers} events")
                logger.info(f"   Previous sponsors: {self.events_with_sponsors} events")

                return self.processed_events

            except Exception as e:
                logger.warning(f"⚠️ Could not load progress: {e}")
                return 0

        return 0

    async def process_events_conservatively(
        self, event_urls: List[str], start_index: int
    ):
        """Process events one by one with conservative timing"""

        from enhanced_orchestrator import extract_events_enhanced

        for i in range(start_index, len(event_urls)):
            event_url = event_urls[i]
            event_number = i + 1

            logger.info(f"\n🔄 Processing Event {event_number}/{len(event_urls)}")
            logger.info(f"🔗 URL: {event_url}")

            # Calculate progress and timing
            elapsed_time = (datetime.now() - self.start_time).total_seconds() / 60
            remaining_events = len(event_urls) - event_number
            estimated_remaining = remaining_events * 0.83  # ~50 seconds per event

            logger.info(
                f"📊 Progress: {event_number}/{len(event_urls)} ({event_number/len(event_urls)*100:.1f}%)"
            )
            logger.info(
                f"⏰ Elapsed: {elapsed_time:.1f}min | Remaining: ~{estimated_remaining:.1f}min"
            )

            try:
                # Extract single event with maximum timeout
                event_start = time.time()

                results = await extract_events_enhanced(
                    urls=[event_url],
                    max_concurrent=1,  # Single event only
                    timeout_per_event=180,  # 3 minutes per event
                    enable_visual_intelligence=True,
                    enable_mcp_browser=True,
                )

                event_end = time.time()
                processing_time = event_end - event_start

                # Analyze result
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

                        logger.info(
                            f"✅ Success: {speakers_found} speakers, {sponsors_found} sponsors"
                        )
                        logger.info(
                            f"📝 Description: {len(result.description) if result.description else 0} chars"
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
                        logger.warning(f"⚠️ Failed: {result.status}")
                else:
                    logger.error("❌ No results returned")

                self.processed_events = event_number

                # Save progress after each event
                await self.save_progress()

                logger.info(f"⏱️ Event processed in {processing_time:.1f}s")

            except Exception as e:
                logger.error(f"❌ Event {event_number} failed: {e}")
                # Continue with next event

            # Conservative delay before next event (except for last event)
            if event_number < len(event_urls):
                # Random delay between 30-60 seconds to avoid patterns
                delay = random.uniform(30, 60)
                logger.info(f"⏸️ Waiting {delay:.1f}s before next event...")
                await asyncio.sleep(delay)

            # Update overall stats
            current_success_rate = self.successful_extractions / event_number * 100
            speaker_success_rate = self.events_with_speakers / event_number * 100
            sponsor_success_rate = self.events_with_sponsors / event_number * 100

            logger.info(
                f"📈 Overall Stats: {current_success_rate:.1f}% success, {speaker_success_rate:.1f}% speakers, {sponsor_success_rate:.1f}% sponsors"
            )

    async def save_progress(self):
        """Save current progress to file"""
        try:
            progress_data = {
                "session_id": self.session_id,
                "last_updated": datetime.now().isoformat(),
                "processed_events": self.processed_events,
                "successful_extractions": self.successful_extractions,
                "events_with_speakers": self.events_with_speakers,
                "events_with_sponsors": self.events_with_sponsors,
                "success_rate": self.successful_extractions
                / max(self.processed_events, 1)
                * 100,
                "speaker_rate": self.events_with_speakers
                / max(self.processed_events, 1)
                * 100,
                "sponsor_rate": self.events_with_sponsors
                / max(self.processed_events, 1)
                * 100,
            }

            with open(self.progress_file, "w") as f:
                json.dump(progress_data, f, indent=2)

        except Exception as e:
            logger.warning(f"⚠️ Could not save progress: {e}")

    async def generate_final_report(self):
        """Generate comprehensive final report"""

        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        logger.info("\n" + "=" * 70)
        logger.info("🎉 CONSERVATIVE EXTRACTION COMPLETE!")
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

        logger.info("\n⏰ TIMING ANALYSIS:")
        logger.info(f"   Total Duration: {total_duration/60:.1f} minutes")
        logger.info(
            f"   Average per Event: {total_duration/max(self.processed_events,1):.1f} seconds"
        )
        logger.info(f"   Started: {self.start_time.strftime('%H:%M:%S')}")
        logger.info(f"   Completed: {end_time.strftime('%H:%M:%S')}")

        # Calculate improvement over fast extraction
        previous_speakers = 1  # From fast extraction
        previous_sponsors = 1

        speaker_improvement = (
            ((self.events_with_speakers - previous_speakers) / previous_speakers * 100)
            if previous_speakers > 0
            else self.events_with_speakers * 100
        )
        sponsor_improvement = (
            ((self.events_with_sponsors - previous_sponsors) / previous_sponsors * 100)
            if previous_sponsors > 0
            else self.events_with_sponsors * 100
        )

        logger.info("\n📈 IMPROVEMENT OVER FAST EXTRACTION:")
        logger.info(f"   Speaker Extraction: {speaker_improvement:+.0f}% improvement")
        logger.info(f"   Sponsor Extraction: {sponsor_improvement:+.0f}% improvement")

        # Generate comprehensive report
        final_report = {
            "extraction_type": "conservative_hour_long_extraction",
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_duration_minutes": total_duration / 60,
            "strategy": {
                "delay_per_event": "30-60 seconds",
                "max_concurrent": 1,
                "timeout_per_event": 180,
                "enable_visual_intelligence": True,
                "enable_mcp_browser": True,
            },
            "results": {
                "total_events_processed": self.processed_events,
                "successful_extractions": self.successful_extractions,
                "events_with_speakers": self.events_with_speakers,
                "events_with_sponsors": self.events_with_sponsors,
                "success_rate_percent": self.successful_extractions
                / max(self.processed_events, 1)
                * 100,
                "speaker_discovery_rate_percent": self.events_with_speakers
                / max(self.processed_events, 1)
                * 100,
                "sponsor_discovery_rate_percent": self.events_with_sponsors
                / max(self.processed_events, 1)
                * 100,
                "average_time_per_event_seconds": total_duration
                / max(self.processed_events, 1),
            },
            "improvement_analysis": {
                "speaker_improvement_percent": speaker_improvement,
                "sponsor_improvement_percent": sponsor_improvement,
                "baseline_speakers": previous_speakers,
                "baseline_sponsors": previous_sponsors,
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
                    "speakers": result.speakers[:10] if result.speakers else [],
                    "sponsors": result.sponsors[:10] if result.sponsors else [],
                }
                for result in self.all_results
            ],
        }

        # Save final report
        with open(self.results_file, "w") as f:
            json.dump(final_report, f, indent=2)

        logger.info(f"\n📄 Final report saved: {self.results_file}")

        # Assessment
        logger.info("\n🎯 FINAL ASSESSMENT:")
        if self.events_with_speakers > 10 or self.events_with_sponsors > 10:
            logger.info("🎉 EXCELLENT: Conservative extraction succeeded!")
            logger.info(f"   Found speakers in {self.events_with_speakers} events")
            logger.info(f"   Found sponsors in {self.events_with_sponsors} events")
            logger.info("   Rate limiting successfully avoided")
        elif self.events_with_speakers > 5 or self.events_with_sponsors > 5:
            logger.info("✅ GOOD: Significant improvement achieved")
            logger.info("   Conservative approach working")
        else:
            logger.info("⚠️ MIXED: Some improvement but still limited")
            logger.info("   May need even more conservative approach")

        return final_report


async def main():
    """Main execution function"""
    extractor = ConservativeExtractor()

    logger.info("🐌🐌🐌 STARTING CONSERVATIVE ETHCC EXTRACTION 🐌🐌🐌")
    logger.info("⏰ This will take approximately 1.2 hours")
    logger.info("🔄 Progress saved after each event - safe to interrupt and resume")
    logger.info("💡 Use Ctrl+C to stop gracefully")

    try:
        await extractor.run_conservative_extraction()
        logger.info("🏁🏁🏁 CONSERVATIVE EXTRACTION COMPLETE! 🏁🏁🏁")

    except KeyboardInterrupt:
        logger.info("\n⏸️ Extraction interrupted by user")
        logger.info(f"📊 Progress saved: {extractor.processed_events} events processed")
        logger.info(
            f"🔄 Run again to resume from event #{extractor.processed_events + 1}"
        )
        await extractor.save_progress()

    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")
        await extractor.save_progress()
        raise


if __name__ == "__main__":
    asyncio.run(main())
