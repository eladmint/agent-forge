#!/usr/bin/env python3
"""
Efficient batch processing of EthCC events - Extract calendar first, then process events in batches
"""

import asyncio
import json
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_ethcc_batch_processing():
    """Run EthCC extraction in efficient batches"""

    ethcc_url = "https://lu.ma/ethcc"

    logger.info("🚀 STARTING ETHCC BATCH PROCESSING")
    logger.info(f"🎯 Target: {ethcc_url}")
    logger.info("📋 Strategy: Extract calendar first, then process individual events")
    logger.info("=" * 60)

    start_time = datetime.now()

    # Step 1: Extract calendar to get individual event URLs
    logger.info("📅 Step 1: Extracting calendar to discover individual events...")

    try:
        # Use the Link Finder Agent directly for faster calendar extraction
        sys.path.append("/Users/eladm/Projects/token/tokenhunter/agents/experimental")
        from link_finder_agent import LinkFinderAgent

        agent = LinkFinderAgent()
        event_links = await agent.run_async(ethcc_url)

        calendar_time = datetime.now()
        calendar_duration = (calendar_time - start_time).total_seconds()

        logger.info(
            f"✅ Calendar extraction complete: {len(event_links)} events found in {calendar_duration:.1f}s"
        )

        if not event_links:
            logger.error("❌ No events found in calendar")
            return

        # Show sample of discovered events
        logger.info("📋 Sample of discovered events:")
        for i, event in enumerate(event_links[:5]):
            logger.info(
                f"   {i+1}. {event.get('name', 'Unknown')} - {event.get('url', 'No URL')}"
            )

        if len(event_links) > 5:
            logger.info(f"   ... and {len(event_links) - 5} more events")

        # Step 2: Process first batch of events (5 events) to test the pipeline
        logger.info(
            f"\n🔄 Step 2: Processing first batch of events (5/{len(event_links)})..."
        )

        from enhanced_orchestrator import extract_events_enhanced

        # Take first 5 event URLs for testing
        test_urls = [event["url"] for event in event_links[:5] if event.get("url")]

        logger.info(f"🎯 Processing {len(test_urls)} events:")
        for i, url in enumerate(test_urls):
            logger.info(f"   {i+1}. {url}")

        # Process the batch
        batch_start = datetime.now()
        results = await extract_events_enhanced(
            urls=test_urls,
            max_concurrent=2,  # Process 2 events at a time
            timeout_per_event=60,  # 1 minute per event
            enable_visual_intelligence=True,
            enable_mcp_browser=True,
        )

        batch_end = datetime.now()
        batch_duration = (batch_end - batch_start).total_seconds()

        logger.info(
            f"✅ Batch processing complete: {len(results)} events processed in {batch_duration:.1f}s"
        )

        # Analyze batch results
        successful_results = [r for r in results if r.status == "success"]
        failed_results = [r for r in results if r.status != "success"]

        logger.info(f"✅ Successful: {len(successful_results)}")
        logger.info(f"❌ Failed: {len(failed_results)}")

        # Show detailed results for the batch
        logger.info("\n📊 BATCH RESULTS ANALYSIS:")
        for i, result in enumerate(results):
            status_icon = "✅" if result.status == "success" else "❌"
            completeness = getattr(result, "completeness_score", 0)
            speakers_count = len(result.speakers) if result.speakers else 0
            sponsors_count = len(result.sponsors) if result.sponsors else 0

            logger.info(f"   {i+1}. {status_icon} {result.name}")
            logger.info(f"       Completeness: {completeness:.2f}")
            logger.info(
                f"       Speakers: {speakers_count}, Sponsors: {sponsors_count}"
            )
            logger.info(
                f"       Processing time: {getattr(result, 'processing_time', 0):.1f}s"
            )

        # Calculate extrapolated performance
        total_events = len(event_links)
        avg_time_per_event = batch_duration / len(test_urls) if test_urls else 0
        estimated_total_time = avg_time_per_event * total_events

        logger.info("\n📈 PERFORMANCE PROJECTION:")
        logger.info(f"   Events discovered: {total_events}")
        logger.info(f"   Batch size tested: {len(test_urls)}")
        logger.info(f"   Average time per event: {avg_time_per_event:.1f}s")
        logger.info(f"   Estimated total time: {estimated_total_time/60:.1f} minutes")
        logger.info(f"   Success rate: {len(successful_results)/len(results)*100:.1f}%")

        # Save batch report
        batch_report = {
            "test_timestamp": start_time.isoformat(),
            "calendar_extraction_time": calendar_duration,
            "batch_processing_time": batch_duration,
            "total_events_discovered": total_events,
            "batch_size_tested": len(test_urls),
            "successful_extractions": len(successful_results),
            "failed_extractions": len(failed_results),
            "success_rate": (
                len(successful_results) / len(results) * 100 if results else 0
            ),
            "avg_time_per_event": avg_time_per_event,
            "estimated_total_time_minutes": estimated_total_time / 60,
            "discovered_events": event_links,
            "batch_results": [
                {
                    "name": r.name,
                    "url": r.url,
                    "status": r.status,
                    "completeness_score": getattr(r, "completeness_score", 0),
                    "speakers_count": len(r.speakers) if r.speakers else 0,
                    "sponsors_count": len(r.sponsors) if r.sponsors else 0,
                    "processing_time": getattr(r, "processing_time", 0),
                }
                for r in results
            ],
        }

        report_filename = f"ethcc_batch_test_{int(start_time.timestamp())}.json"
        with open(report_filename, "w") as f:
            json.dump(batch_report, f, indent=2)

        logger.info(f"📄 Batch report saved: {report_filename}")

        # Final assessment
        total_time = (datetime.now() - start_time).total_seconds()
        logger.info("\n🎯 FINAL ASSESSMENT:")
        logger.info(f"✅ Calendar extraction: {total_events} events discovered")
        logger.info(
            f"✅ Batch processing: {len(successful_results)}/{len(test_urls)} events successful"
        )
        logger.info(f"⏱️  Total test time: {total_time:.1f}s")
        logger.info("🚀 Ready for full production run!")

        return batch_report

    except Exception as e:
        logger.error(f"❌ Batch processing failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("🔥 Starting EthCC Batch Processing Test")
    report = asyncio.run(run_ethcc_batch_processing())
    logger.info("🏁 Batch processing test complete!")
