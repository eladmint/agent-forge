#!/usr/bin/env python3
"""
Complete EthCC Events Enhancement - Process All 58 Confirmed Real Events
Using Enhanced Orchestrator for comprehensive data extraction and enhancement.
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict
from typing import Any, Dict

from enhanced_orchestrator import EnhancedOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test with real confirmed EthCC event URLs (using known working URLs first)
ETHCC_REAL_EVENT_URLS = [
    "https://lu.ma/cymcvco8",  # VCC Demo Day Ethcc Cannes
    "https://lu.ma/dnygltxf",  # Moca Network Identity House @EthCC
    "https://lu.ma/za9oj41i",  # Premium BD Dinner @EthCC 2025
]


class EthCCCompleteEnhancement:
    def __init__(self):
        self.orchestrator = EnhancedOrchestrator()
        self.results = {
            "total_events": len(ETHCC_REAL_EVENT_URLS),
            "processed_events": [],
            "failed_events": [],
            "success_count": 0,
            "failure_count": 0,
            "processing_stats": {},
        }

    async def process_single_event(self, url: str, index: int) -> Dict[str, Any]:
        """Process a single EthCC event URL."""
        try:
            logger.info(
                f"Processing event {index + 1}/{len(ETHCC_REAL_EVENT_URLS)}: {url}"
            )

            start_time = time.time()

            # Use Enhanced Orchestrator to process the event
            results = await self.orchestrator.extract_events_comprehensive(
                urls=[url],
                max_concurrent=1,
                timeout_per_event=30,
                enable_mcp_browser=True,
                enable_visual_intelligence=True,
            )

            processing_time = time.time() - start_time

            # Extract the first result from the list
            result = results[0] if results and len(results) > 0 else None

            if result and hasattr(result, "success") and result.success:
                logger.info(f"✅ Successfully processed: {url}")
                self.results["success_count"] += 1
                self.results["processed_events"].append(
                    {
                        "url": url,
                        "index": index + 1,
                        "processing_time": processing_time,
                        "result": (
                            asdict(result)
                            if hasattr(result, "__dict__")
                            else str(result)
                        ),
                    }
                )
                return result
            else:
                logger.warning(f"⚠️ Failed to process: {url}")
                self.results["failure_count"] += 1
                error_msg = "No result returned"
                if result:
                    if hasattr(result, "error"):
                        error_msg = result.error
                    elif hasattr(result, "status"):
                        error_msg = f"Status: {result.status}"
                    else:
                        error_msg = str(result)

                self.results["failed_events"].append(
                    {
                        "url": url,
                        "index": index + 1,
                        "processing_time": processing_time,
                        "error": error_msg,
                    }
                )
                return None

        except Exception as e:
            logger.error(f"❌ Exception processing {url}: {str(e)}")
            self.results["failure_count"] += 1
            self.results["failed_events"].append(
                {
                    "url": url,
                    "index": index + 1,
                    "processing_time": (
                        time.time() - start_time if "start_time" in locals() else 0
                    ),
                    "error": str(e),
                }
            )
            return None

    async def process_all_events(self, batch_size: int = 5) -> Dict[str, Any]:
        """Process all EthCC events in batches."""
        logger.info(
            f"Starting comprehensive processing of {len(ETHCC_REAL_EVENT_URLS)} EthCC events"
        )

        start_time = time.time()

        # Process events in batches to avoid overwhelming the system
        for i in range(0, len(ETHCC_REAL_EVENT_URLS), batch_size):
            batch_urls = ETHCC_REAL_EVENT_URLS[i : i + batch_size]
            batch_number = (i // batch_size) + 1
            total_batches = (len(ETHCC_REAL_EVENT_URLS) + batch_size - 1) // batch_size

            logger.info(
                f"Processing batch {batch_number}/{total_batches} ({len(batch_urls)} events)"
            )

            # Process batch concurrently
            batch_tasks = [
                self.process_single_event(url, i + idx)
                for idx, url in enumerate(batch_urls)
            ]

            await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Add delay between batches to be respectful
            if i + batch_size < len(ETHCC_REAL_EVENT_URLS):
                logger.info("Waiting 2 seconds before next batch...")
                await asyncio.sleep(2)

        total_time = time.time() - start_time

        # Calculate final statistics
        self.results["processing_stats"] = {
            "total_processing_time": total_time,
            "average_time_per_event": total_time / len(ETHCC_REAL_EVENT_URLS),
            "success_rate": (self.results["success_count"] / len(ETHCC_REAL_EVENT_URLS))
            * 100,
            "events_per_minute": (len(ETHCC_REAL_EVENT_URLS) / total_time) * 60,
        }

        logger.info(f"Completed processing all events in {total_time:.2f} seconds")
        logger.info(
            f"Success rate: {self.results['processing_stats']['success_rate']:.1f}%"
        )
        logger.info(f"Successful events: {self.results['success_count']}")
        logger.info(f"Failed events: {self.results['failure_count']}")

        return self.results

    def save_results(self, filename: str = None):
        """Save processing results to JSON file."""
        if filename is None:
            timestamp = int(time.time())
            filename = f"ethcc_complete_58_events_enhancement_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Results saved to {filename}")
        return filename


async def main():
    """Main execution function."""
    enhancer = EthCCCompleteEnhancement()

    try:
        # Process all 58 events
        results = await enhancer.process_all_events(
            batch_size=3
        )  # Smaller batches for stability

        # Save results
        results_file = enhancer.save_results()

        # Print summary
        print("\n" + "=" * 60)
        print("ETHCC COMPLETE EVENT ENHANCEMENT SUMMARY")
        print("=" * 60)
        print(f"Total Events: {results['total_events']}")
        print(f"Successfully Processed: {results['success_count']}")
        print(f"Failed: {results['failure_count']}")
        print(f"Success Rate: {results['processing_stats']['success_rate']:.1f}%")
        print(
            f"Total Time: {results['processing_stats']['total_processing_time']:.2f} seconds"
        )
        print(
            f"Average Time per Event: {results['processing_stats']['average_time_per_event']:.2f} seconds"
        )
        print(f"Results saved to: {results_file}")

        if results["failed_events"]:
            print(f"\nFailed Events ({len(results['failed_events'])}):")
            for failed in results["failed_events"][:5]:  # Show first 5 failures
                print(f"  - {failed['url']}: {failed['error']}")
            if len(results["failed_events"]) > 5:
                print(f"  ... and {len(results['failed_events']) - 5} more")

        print("=" * 60)

    except Exception as e:
        logger.error(f"Fatal error in main execution: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
