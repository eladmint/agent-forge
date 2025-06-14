#!/usr/bin/env python3
"""
EthCC Detailed Content Extraction - Slower, Batch Processing with Browser Automation

This script implements a rate-limit-friendly approach to extract detailed speaker and sponsor
information from the 93 EthCC events using:
1. Slower extraction with delays between requests
2. Batch processing to avoid overwhelming Luma's servers
3. Browser automation for human-like behavior
4. Enhanced content extraction for speakers, sponsors, and detailed descriptions
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_ethcc_detailed_extraction():
    """Run detailed content extraction with rate limiting and browser automation"""

    logger.info("🚀 ETHCC DETAILED CONTENT EXTRACTION")
    logger.info("🎯 Strategy: Slower + Batch Processing + Browser Automation")
    logger.info("📊 Goal: Extract speakers, sponsors, and detailed content")
    logger.info("=" * 60)

    start_time = datetime.now()

    try:
        # Step 1: Load the 93 event URLs from previous extraction
        logger.info("📋 Step 1: Loading EthCC event URLs...")

        try:
            with open("ethcc_full_production_1749082633.json", "r") as f:
                production_data = json.load(f)

            all_events = production_data.get("all_discovered_events", [])
            event_urls = [event["url"] for event in all_events if event.get("url")]

            logger.info(f"✅ Loaded {len(event_urls)} EthCC event URLs")

        except FileNotFoundError:
            logger.error("❌ Previous extraction file not found")
            return

        if not event_urls:
            logger.error("❌ No event URLs found to process")
            return

        # Step 2: Configure slower extraction settings
        logger.info("\n⚙️ Step 2: Configuring rate-limit-friendly settings...")

        extraction_config = {
            "batch_size": 5,  # Process 5 events at a time
            "delay_between_batches": 15,  # 15 seconds between batches
            "delay_between_events": 3,  # 3 seconds between events in batch
            "timeout_per_event": 120,  # 2 minutes per event
            "max_concurrent": 2,  # Only 2 concurrent requests
            "enable_browser_automation": True,
            "enable_visual_intelligence": True,
            "human_like_delays": True,
        }

        logger.info(f"📦 Batch size: {extraction_config['batch_size']} events")
        logger.info(
            f"⏱️ Delay between batches: {extraction_config['delay_between_batches']}s"
        )
        logger.info(
            f"⏱️ Delay between events: {extraction_config['delay_between_events']}s"
        )
        logger.info(f"🕐 Timeout per event: {extraction_config['timeout_per_event']}s")
        logger.info(f"🔄 Max concurrent: {extraction_config['max_concurrent']}")
        logger.info(
            f"🌐 Browser automation: {extraction_config['enable_browser_automation']}"
        )
        logger.info(
            f"👀 Visual intelligence: {extraction_config['enable_visual_intelligence']}"
        )

        # Step 3: Process events in batches
        logger.info(f"\n🔄 Step 3: Processing {len(event_urls)} events in batches...")

        from enhanced_orchestrator import extract_events_enhanced

        # Split URLs into batches
        batches = [
            event_urls[i : i + extraction_config["batch_size"]]
            for i in range(0, len(event_urls), extraction_config["batch_size"])
        ]

        logger.info(f"📦 Created {len(batches)} batches")

        all_results = []
        successful_extractions = 0
        events_with_speakers = 0
        events_with_sponsors = 0
        events_with_detailed_content = 0

        for batch_num, batch_urls in enumerate(batches, 1):
            logger.info(
                f"\n📦 Processing Batch {batch_num}/{len(batches)} ({len(batch_urls)} events)"
            )

            batch_start = time.time()

            # Add human-like delay before each batch (except first)
            if batch_num > 1:
                delay = extraction_config["delay_between_batches"]
                # Add some randomness to seem more human
                random_delay = delay + random.uniform(-2, 3)
                logger.info(f"⏸️ Waiting {random_delay:.1f}s between batches...")
                await asyncio.sleep(random_delay)

            try:
                # Process batch with enhanced settings (removing invalid delay_between_requests parameter)
                batch_results = await extract_events_enhanced(
                    urls=batch_urls,
                    max_concurrent=extraction_config["max_concurrent"],
                    timeout_per_event=extraction_config["timeout_per_event"],
                    enable_visual_intelligence=extraction_config[
                        "enable_visual_intelligence"
                    ],
                    enable_mcp_browser=extraction_config["enable_browser_automation"],
                )

                # Analyze batch results
                batch_successful = len(
                    [r for r in batch_results if r.status == "success"]
                )
                successful_extractions += batch_successful

                # Count content-rich events in this batch
                for result in batch_results:
                    if result.status == "success":
                        if result.speakers and len(result.speakers) > 0:
                            events_with_speakers += 1
                        if result.sponsors and len(result.sponsors) > 0:
                            events_with_sponsors += 1
                        if result.description and len(result.description) > 100:
                            events_with_detailed_content += 1

                all_results.extend(batch_results)

                batch_time = time.time() - batch_start
                logger.info(
                    f"✅ Batch {batch_num} completed: {batch_successful}/{len(batch_urls)} successful in {batch_time:.1f}s"
                )

            except Exception as e:
                logger.error(f"❌ Batch {batch_num} failed: {e}")
                # Continue with next batch
                continue

        # Step 4: Analyze comprehensive results
        processing_end = datetime.now()
        total_duration = (processing_end - start_time).total_seconds()

        logger.info("\n" + "=" * 60)
        logger.info("📊 DETAILED EXTRACTION RESULTS ANALYSIS")
        logger.info("=" * 60)

        logger.info(f"📈 Total Events Processed: {len(all_results)}")
        logger.info(f"✅ Successful Extractions: {successful_extractions}")
        logger.info(
            f"📊 Success Rate: {successful_extractions/len(event_urls)*100:.1f}%"
        )
        logger.info(f"⏱️ Total Processing Time: {total_duration/60:.1f} minutes")
        logger.info(
            f"⚡ Average Time per Event: {total_duration/len(event_urls):.1f} seconds"
        )

        logger.info("\n🎯 CONTENT EXTRACTION RESULTS:")
        logger.info(f"👥 Events with Speakers: {events_with_speakers}")
        logger.info(f"🏢 Events with Sponsors: {events_with_sponsors}")
        logger.info(f"📝 Events with Detailed Content: {events_with_detailed_content}")

        # Calculate improvement over previous extraction
        previous_speakers = 1  # From the fast extraction
        previous_sponsors = 1

        speaker_improvement = (
            ((events_with_speakers - previous_speakers) / previous_speakers * 100)
            if previous_speakers > 0
            else events_with_speakers * 100
        )
        sponsor_improvement = (
            ((events_with_sponsors - previous_sponsors) / previous_sponsors * 100)
            if previous_sponsors > 0
            else events_with_sponsors * 100
        )

        logger.info("\n📈 IMPROVEMENT OVER FAST EXTRACTION:")
        logger.info(f"👥 Speaker extraction: {speaker_improvement:+.0f}% improvement")
        logger.info(f"🏢 Sponsor extraction: {sponsor_improvement:+.0f}% improvement")

        # Step 5: Save detailed results
        detailed_report = {
            "extraction_timestamp": start_time.isoformat(),
            "extraction_strategy": "slower_batch_browser_automation",
            "total_duration_minutes": total_duration / 60,
            "total_events_processed": len(all_results),
            "successful_extractions": successful_extractions,
            "success_rate_percent": successful_extractions / len(event_urls) * 100,
            "events_with_speakers": events_with_speakers,
            "events_with_sponsors": events_with_sponsors,
            "events_with_detailed_content": events_with_detailed_content,
            "extraction_config": extraction_config,
            "speaker_improvement_percent": speaker_improvement,
            "sponsor_improvement_percent": sponsor_improvement,
            "avg_time_per_event_seconds": total_duration / len(event_urls),
            "batches_processed": len(batches),
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
                    "completeness_score": (
                        result.completeness_score
                        if hasattr(result, "completeness_score")
                        else 0
                    ),
                    "processing_time": getattr(result, "processing_time", 0),
                }
                for result in all_results
            ],
        }

        report_filename = (
            f"ethcc_detailed_extraction_{int(start_time.timestamp())}.json"
        )
        with open(report_filename, "w") as f:
            json.dump(detailed_report, f, indent=2)

        logger.info(f"\n📄 Detailed extraction report saved: {report_filename}")

        # Step 6: Save enhanced results to database (if successful)
        if successful_extractions > len(event_urls) * 0.7:  # If >70% success rate
            logger.info("\n💾 Step 6: Saving enhanced results to database...")

            try:
                from api.core.config import SUPABASE_KEY, SUPABASE_URL
                from supabase import create_client

                db_client = create_client(SUPABASE_URL, SUPABASE_KEY)

                saved_count = 0
                for result in all_results:
                    if result.status == "success" and (
                        result.speakers
                        or result.sponsors
                        or (result.description and len(result.description) > 100)
                    ):
                        try:
                            # Update existing event with enhanced data
                            update_data = {}

                            if result.description and len(result.description) > 100:
                                update_data["description"] = result.description[:1000]

                            if result.speakers:
                                # For now, store speakers as JSON in a text field
                                # Later can be normalized to separate speaker table
                                speakers_data = [
                                    {"name": speaker}
                                    for speaker in result.speakers[:10]
                                ]  # Limit to 10
                                update_data["speakers_data"] = json.dumps(speakers_data)

                            if result.sponsors:
                                # For now, store sponsors as JSON in a text field
                                sponsors_data = [
                                    {"name": sponsor}
                                    for sponsor in result.sponsors[:10]
                                ]  # Limit to 10
                                update_data["sponsors_data"] = json.dumps(sponsors_data)

                            if update_data:
                                response = (
                                    db_client.table("events")
                                    .update(update_data)
                                    .eq("luma_url", result.url)
                                    .execute()
                                )
                                if response.data:
                                    saved_count += 1

                        except Exception as e:
                            logger.warning(
                                f"⚠️ Failed to save enhanced data for {result.url}: {e}"
                            )

                logger.info(f"✅ Enhanced data saved for {saved_count} events")

            except Exception as e:
                logger.warning(f"⚠️ Database save failed: {e}")

        # Final assessment
        logger.info("\n🎯 FINAL ASSESSMENT:")
        if events_with_speakers > 10 or events_with_sponsors > 10:
            logger.info(
                "🎉 SUCCESS: Detailed extraction significantly improved content richness!"
            )
            logger.info(f"👥 Speakers extracted from {events_with_speakers} events")
            logger.info(f"🏢 Sponsors extracted from {events_with_sponsors} events")
        elif successful_extractions > len(event_urls) * 0.8:
            logger.info("✅ GOOD: High success rate but limited detailed content")
            logger.info(
                "📝 Consider additional extraction strategies for speaker/sponsor data"
            )
        else:
            logger.info("⚠️ PARTIAL: Rate limiting still impacting extraction")
            logger.info("💡 May need even slower processing or different approach")

        return detailed_report

    except Exception as e:
        logger.error(f"❌ Detailed extraction failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("🚀🚀🚀 STARTING ETHCC DETAILED CONTENT EXTRACTION 🚀🚀🚀")
    result = asyncio.run(run_ethcc_detailed_extraction())
    logger.info("🏁🏁🏁 DETAILED EXTRACTION COMPLETE! 🏁🏁🏁")
