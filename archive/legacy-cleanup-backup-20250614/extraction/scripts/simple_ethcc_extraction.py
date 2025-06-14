#!/usr/bin/env python3
"""
Simple EthCC Event Extraction
Extract discovered EthCC events using a simplified approach
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimpleEthCCExtractor:
    """Simplified EthCC event extraction"""

    def __init__(self):
        self.results = {
            "session_id": f"simple_ethcc_{int(time.time())}",
            "started_at": datetime.now().isoformat(),
            "events_discovered": 0,
            "events_processed": 0,
            "events": [],
            "summary": {},
        }

    async def discover_ethcc_events(self) -> List[str]:
        """Discover EthCC events from main page"""

        try:
            from extraction.agents.experimental.link_finder_agent import LinkFinderAgent

            logger.info(
                "🔍 Discovering EthCC events from main page: https://lu.ma/ethcc"
            )
            link_finder = LinkFinderAgent(name="EthCCDiscovery", logger=logger)

            # Discover all event URLs from the main EthCC page
            discovery_result = await link_finder.run_async("https://lu.ma/ethcc")

            discovered_urls = []
            if discovery_result and isinstance(discovery_result, list):
                for event_data in discovery_result:
                    if isinstance(event_data, dict) and "url" in event_data:
                        discovered_urls.append(event_data["url"])
                    elif isinstance(event_data, str):
                        discovered_urls.append(event_data)

            logger.info(
                f"🎯 Discovered {len(discovered_urls)} events from main EthCC page"
            )
            self.results["events_discovered"] = len(discovered_urls)

            return discovered_urls

        except Exception as e:
            logger.error(f"❌ Failed to discover events: {e}")
            return []

    def extract_basic_event_data(self, url: str) -> Dict[str, Any]:
        """Extract basic event data from URL using simple HTTP requests"""

        event_data = {
            "url": url,
            "name": "Unknown Event",
            "description": "",
            "location": "",
            "date": "",
            "status": "failed",
            "error": None,
        }

        try:
            logger.info(f"📄 Extracting data from: {url}")

            # Simple HTTP request
            response = requests.get(
                url,
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                },
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")

                # Extract title
                title_tag = soup.find("title")
                if title_tag:
                    event_data["name"] = title_tag.get_text().strip()

                # Try to find meta description
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc:
                    event_data["description"] = meta_desc.get("content", "").strip()

                # Try to find Open Graph data
                og_title = soup.find("meta", attrs={"property": "og:title"})
                if og_title:
                    event_data["name"] = og_title.get("content", "").strip()

                og_desc = soup.find("meta", attrs={"property": "og:description"})
                if og_desc:
                    event_data["description"] = og_desc.get("content", "").strip()

                # Try to extract location from text
                text_content = soup.get_text()
                if "brussels" in text_content.lower():
                    event_data["location"] = "Brussels, Belgium"
                elif "belgium" in text_content.lower():
                    event_data["location"] = "Belgium"

                # Try to find date information
                time_tag = soup.find("time")
                if time_tag:
                    datetime_attr = time_tag.get("datetime")
                    if datetime_attr:
                        event_data["date"] = datetime_attr
                    else:
                        event_data["date"] = time_tag.get_text().strip()

                # Check if it looks like an EthCC event
                name_lower = event_data["name"].lower()
                desc_lower = event_data["description"].lower()

                if any(
                    term in name_lower or term in desc_lower
                    for term in ["ethcc", "ethereum", "eth cc"]
                ):
                    event_data["category"] = "EthCC Event"
                    event_data["status"] = "success"
                    logger.info(f"✅ Successfully extracted: {event_data['name']}")
                else:
                    event_data["status"] = "not_ethcc"
                    logger.info(f"⚠️ Not an EthCC event: {event_data['name']}")

            else:
                event_data["error"] = f"HTTP {response.status_code}"
                logger.warning(f"❌ Failed to fetch {url}: HTTP {response.status_code}")

        except Exception as e:
            event_data["error"] = str(e)
            logger.error(f"❌ Error extracting {url}: {e}")

        return event_data

    async def process_discovered_events(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Process all discovered events"""

        logger.info(f"🔄 Processing {len(urls)} discovered events...")

        events = []
        successful_extractions = 0
        ethcc_events = 0

        for i, url in enumerate(urls, 1):
            logger.info(f"📊 Processing event {i}/{len(urls)}")

            event_data = self.extract_basic_event_data(url)
            events.append(event_data)

            if event_data["status"] == "success":
                successful_extractions += 1
                ethcc_events += 1

            # Small delay to be respectful
            await asyncio.sleep(0.5)

        logger.info("✅ Processing completed:")
        logger.info(f"  📊 Total events processed: {len(events)}")
        logger.info(f"  🎯 Successful extractions: {successful_extractions}")
        logger.info(f"  🏷️ EthCC events found: {ethcc_events}")

        self.results["events_processed"] = len(events)
        self.results["events"] = events

        return events

    def generate_summary(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate extraction summary"""

        successful_events = [e for e in events if e["status"] == "success"]
        failed_events = [e for e in events if e["status"] == "failed"]
        non_ethcc_events = [e for e in events if e["status"] == "not_ethcc"]

        summary = {
            "total_urls_discovered": self.results["events_discovered"],
            "total_events_processed": len(events),
            "successful_extractions": len(successful_events),
            "failed_extractions": len(failed_events),
            "non_ethcc_events": len(non_ethcc_events),
            "success_rate": (len(successful_events) / max(1, len(events))) * 100,
            "sample_events": successful_events[:5],
            "recommendations": [],
        }

        # Generate recommendations
        if summary["success_rate"] > 80:
            summary["recommendations"].append("✅ Excellent extraction success rate")

        if len(successful_events) > 10:
            summary["recommendations"].append(
                "✅ Good number of EthCC events discovered"
            )

        if len(successful_events) > 0:
            summary["recommendations"].append(
                "🚀 Ready to enhance database with discovered EthCC events"
            )

        return summary


async def main():
    """Main execution function"""
    extractor = SimpleEthCCExtractor()

    try:
        logger.info("🎯 Starting Simple EthCC Event Extraction")
        logger.info("=" * 80)

        # Step 1: Discover events
        urls = await extractor.discover_ethcc_events()

        if not urls:
            logger.error("❌ No events discovered")
            return None

        # Step 2: Process discovered events
        events = await extractor.process_discovered_events(urls)

        # Step 3: Generate summary
        summary = extractor.generate_summary(events)
        extractor.results["summary"] = summary
        extractor.results["completed_at"] = datetime.now().isoformat()

        # Save results to file
        results_file = f"simple_ethcc_extraction_{int(time.time())}.json"
        with open(results_file, "w") as f:
            json.dump(extractor.results, f, indent=2, default=str)

        # Print summary
        print("\n" + "=" * 80)
        print("🎯 Simple EthCC Event Extraction Summary")
        print("=" * 80)
        print(f"📊 URLs Discovered: {summary['total_urls_discovered']}")
        print(f"📄 Events Processed: {summary['total_events_processed']}")
        print(f"✅ Successful Extractions: {summary['successful_extractions']}")
        print(f"❌ Failed Extractions: {summary['failed_extractions']}")
        print(f"⚠️ Non-EthCC Events: {summary['non_ethcc_events']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print()

        if summary["sample_events"]:
            print("🎯 Sample EthCC Events Found:")
            for i, event in enumerate(summary["sample_events"], 1):
                print(f"  {i}. {event['name']}")
                if event.get("location"):
                    print(f"     📍 {event['location']}")
                if event.get("date"):
                    print(f"     📅 {event['date']}")
                print(f"     🔗 {event['url']}")
                print()

        print("💡 Recommendations:")
        for rec in summary["recommendations"]:
            print(f"  {rec}")

        print(f"\n📁 Detailed results saved to: {results_file}")
        print("=" * 80)

        return extractor.results

    except Exception as e:
        logger.error(f"❌ Simple extraction failed: {e}")
        print(f"\n❌ Extraction failed: {e}")
        return None


if __name__ == "__main__":
    asyncio.run(main())
