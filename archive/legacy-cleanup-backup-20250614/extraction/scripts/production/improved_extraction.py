#!/usr/bin/env python3
"""
🎯 Improved Event Extraction - Reach 90+ Events with Rate Limiting + Database Save
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Any, Dict

import aiohttp

# Add paths for imports
sys.path.append("/Users/eladm/Projects/token/tokenhunter")
sys.path.append("/Users/eladm/Projects/token/tokenhunter/src")
sys.path.append(
    "/Users/eladm/Projects/token/tokenhunter/extraction/agents/experimental"
)

try:
    from link_finder_agent import LinkFinderAgent

    print("✅ LinkFinderAgent imported successfully")
except ImportError as e:
    print(f"❌ Failed to import LinkFinderAgent: {e}")
    sys.exit(1)


class ImprovedEventExtractor:
    """Improved event extraction with rate limiting and database save"""

    def __init__(self):
        self.session = None
        self.events_extracted = 0
        self.events_processed = 0
        self.events_data = []
        self.last_request_time = 0
        self.min_delay = 2.0  # 2 seconds between requests to avoid rate limiting

    async def initialize(self):
        """Initialize HTTP session with better headers"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=90),
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            },
        )

    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()

    async def rate_limited_request(self, url: str) -> str:
        """Make rate-limited request to avoid 429 errors"""
        # Enforce rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_delay:
            delay = self.min_delay - time_since_last
            await asyncio.sleep(delay)

        try:
            async with self.session.get(url) as response:
                self.last_request_time = time.time()

                if response.status == 200:
                    return await response.text()
                elif response.status == 429:
                    # Rate limited - wait longer and retry once
                    print("    ⏳ Rate limited, waiting 10 seconds...")
                    await asyncio.sleep(10)
                    async with self.session.get(url) as retry_response:
                        self.last_request_time = time.time()
                        if retry_response.status == 200:
                            return await retry_response.text()
                        else:
                            print(f"    ❌ Retry failed with {retry_response.status}")
                            return None
                else:
                    print(f"    ❌ HTTP {response.status}")
                    return None

        except Exception as e:
            print(f"    ❌ Error: {str(e)[:100]}")
            return None

    async def extract_single_event(self, url: str) -> Dict[str, Any]:
        """Extract a single event with improved parsing"""
        try:
            print(f"  📋 Processing: {url}")

            html_content = await self.rate_limited_request(url)
            if not html_content:
                return None

            # Parse event data
            event_data = self.parse_event_data(html_content, url)

            if event_data["name"]:  # Only count as extracted if we got a name
                self.events_extracted += 1
                self.events_data.append(event_data)
                print(f"    ✅ Extracted: {event_data['name'][:60]}...")

                # Show location and date if available
                if event_data["location"]:
                    print(f"       📍 {event_data['location'][:40]}")
                if event_data["date"]:
                    print(f"       📅 {event_data['date'][:30]}")

                return event_data
            else:
                print("    ⚠️  No event name found")
                return None

        except Exception as e:
            print(f"    ❌ Error: {str(e)[:100]}")
            return None
        finally:
            self.events_processed += 1

    def parse_event_data(self, html_content: str, url: str) -> Dict[str, Any]:
        """Enhanced event data parsing"""
        import re

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title with multiple strategies
        title = ""
        title_selectors = [
            "h1",
            '[data-testid="event-title"]',
            ".event-title",
            '[class*="title"]',
            '[class*="name"]',
            "title",
        ]

        for selector in title_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if (
                    text and len(text) > 5 and len(text) < 200
                ):  # Reasonable title length
                    title = text
                    break
            if title:
                break

        # Clean title
        if title:
            # Remove common prefixes/suffixes
            title = re.sub(r"^(Event:|Title:)\s*", "", title, flags=re.I)
            title = title.replace(" | Luma", "").strip()

        # Extract description
        description = ""
        desc_selectors = [
            '[data-testid="event-description"]',
            ".event-description",
            ".description",
            'meta[name="description"]',
            '[class*="description"]',
        ]

        for selector in desc_selectors:
            if selector.startswith("meta"):
                element = soup.select_one(selector)
                if element and element.get("content"):
                    desc = element.get("content").strip()
                    if len(desc) > 20:
                        description = desc
                        break
            else:
                element = soup.select_one(selector)
                if element:
                    desc = element.get_text(strip=True)
                    if len(desc) > 20:
                        description = desc
                        break

        # Extract location with improved detection
        location = ""
        location_patterns = [
            r"📍\s*([^📅\n]+)",  # Location emoji pattern
            r"Location:\s*([^📅\n]+)",
            r"Venue:\s*([^📅\n]+)",
            r"Where:\s*([^📅\n]+)",
        ]

        # Try pattern matching first
        full_text = soup.get_text()
        for pattern in location_patterns:
            match = re.search(pattern, full_text, re.I)
            if match:
                location = match.group(1).strip()
                break

        # If no pattern match, try selectors
        if not location:
            location_selectors = [
                '[data-testid="event-location"]',
                ".event-location",
                ".location",
                '[class*="location"]',
                '[class*="venue"]',
            ]

            for selector in location_selectors:
                element = soup.select_one(selector)
                if element:
                    loc = element.get_text(strip=True)
                    if loc and len(loc) > 3:
                        location = loc
                        break

        # Extract date with improved detection
        date_str = ""
        date_patterns = [
            r"📅\s*([^📍\n]+)",  # Date emoji pattern
            r"Date:\s*([^📍\n]+)",
            r"When:\s*([^📍\n]+)",
            r"Time:\s*([^📍\n]+)",
        ]

        # Try pattern matching
        for pattern in date_patterns:
            match = re.search(pattern, full_text, re.I)
            if match:
                date_str = match.group(1).strip()
                break

        # If no pattern match, look for date-like text
        if not date_str:
            date_regex = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}[,\s]*\d{2,4}|(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})"
            match = re.search(date_regex, full_text, re.I)
            if match:
                date_str = match.group(0)

        return {
            "name": title,
            "description": (
                description[:1000] if description else ""
            ),  # Limit description
            "location": location[:200] if location else "",  # Limit location
            "date": date_str[:100] if date_str else "",  # Limit date
            "url": url,
            "extraction_method": "improved_direct_http",
            "timestamp": datetime.now().isoformat(),
        }


async def main():
    """Main improved extraction process"""
    print("🎯 IMPROVED EXTRACTION - REACH 90+ EVENTS GOAL WITH RATE LIMITING")
    print("=" * 80)
    print()

    start_time = datetime.now()

    # Step 1: Get URLs (we know this works)
    print("📅 Step 1: Getting event URLs using LinkFinderAgent...")
    agent = LinkFinderAgent()
    event_links = await agent.run_async("https://lu.ma/ethcc")

    if not event_links:
        print("❌ No events found - stopping")
        return

    urls = [event["url"] for event in event_links if event.get("url")]
    print(f"✅ Found {len(urls)} event URLs to process")
    print()

    # Step 2: Sequential processing with rate limiting
    print("🚀 Step 2: Sequential extraction with rate limiting...")
    print("   (Processing one by one to avoid rate limits)")
    print()

    extractor = ImprovedEventExtractor()
    await extractor.initialize()

    try:
        for i, url in enumerate(urls, 1):
            print(f"📦 Processing {i}/{len(urls)}")
            await extractor.extract_single_event(url)

            # Progress update every 10 events
            if i % 10 == 0:
                print(
                    f"  📊 Progress: {extractor.events_extracted}/{i} extracted ({(extractor.events_extracted/i)*100:.1f}% success)"
                )
                print()

            # Check if we've reached our goal
            if extractor.events_extracted >= 90:
                print(
                    f"🎉 TARGET REACHED! Extracted {extractor.events_extracted} events (90+ goal achieved)"
                )
                break

    finally:
        await extractor.cleanup()

    # Final results
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 80)
    print("📊 IMPROVED EXTRACTION RESULTS")
    print("=" * 80)

    print(f"📈 Total URLs Processed: {extractor.events_processed}")
    print(f"✅ Events Successfully Extracted: {extractor.events_extracted}")
    print(
        f"📊 Success Rate: {(extractor.events_extracted/extractor.events_processed)*100:.1f}%"
    )
    print(f"⏱️  Total Processing Time: {duration:.1f} seconds")
    print(
        f"⚡ Average Time per Event: {duration/extractor.events_processed:.1f} seconds"
    )

    # Achievement check
    target_events = 90
    if extractor.events_extracted >= target_events:
        print(
            f"\n🎉 SUCCESS: Extracted {extractor.events_extracted} events (target: {target_events}+)"
        )
        print("✅ 90+ EVENTS GOAL ACHIEVED!")
        success = True
    else:
        progress = (extractor.events_extracted / target_events) * 100
        print(
            f"\n📊 PROGRESS: {extractor.events_extracted}/{target_events} events ({progress:.1f}% of target)"
        )
        success = False

    # Save results properly
    results_file = (
        f"improved_extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )

    with open(results_file, "w") as f:
        json.dump(
            {
                "metadata": {
                    "extraction_method": "improved_rate_limited",
                    "total_processed": extractor.events_processed,
                    "total_extracted": extractor.events_extracted,
                    "success_rate": (
                        extractor.events_extracted / extractor.events_processed
                    )
                    * 100,
                    "processing_time_seconds": duration,
                    "target_achieved": extractor.events_extracted >= target_events,
                    "timestamp": datetime.now().isoformat(),
                },
                "events": extractor.events_data,
            },
            indent=2,
        )

    print(f"💾 Results saved to: {results_file}")

    if extractor.events_data:
        print("\n📋 SAMPLE EXTRACTED EVENTS (first 5):")
        for i, event in enumerate(extractor.events_data[:5]):
            print(f"  {i+1}. {event['name']}")
            if event["location"]:
                print(f"     📍 {event['location']}")
            if event["date"]:
                print(f"     📅 {event['date']}")
            print()

    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🎉 MISSION ACCOMPLISHED: 90+ events extraction goal achieved!")
        else:
            print("\n🔧 GOOD PROGRESS: Moving toward 90+ events goal")
    except Exception as e:
        print(f"\n❌ Error: {e}")
