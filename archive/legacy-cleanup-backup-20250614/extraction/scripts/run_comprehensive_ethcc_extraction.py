#!/usr/bin/env python3
"""
Comprehensive EthCC Event Extraction - 1-2 Hour Full Extraction
Extract all 90+ EthCC events with complete details
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup


class ComprehensiveEthCCExtractor:
    """
    Comprehensive EthCC event extractor for 90+ events with full details
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )
        self.extracted_events = []
        self.processed_urls = set()

    def extract_all_ethcc_events_from_calendar(
        self, calendar_url: str = "https://lu.ma/ethcc"
    ) -> List[Dict[str, Any]]:
        """
        Extract ALL EthCC events from the Luma calendar page using comprehensive methods
        """
        print(f"🎯 Starting comprehensive extraction from {calendar_url}")

        try:
            # Get the main calendar page
            response = self.session.get(calendar_url, timeout=30)
            response.raise_for_status()

            print(f"✅ Successfully fetched calendar page ({len(response.text)} chars)")

            soup = BeautifulSoup(response.text, "html.parser")
            all_events = []

            # Method 1: Extract JSON-LD structured data (most reliable)
            print("🔍 Method 1: Extracting JSON-LD structured data...")
            json_ld_events = self._extract_json_ld_events(soup)
            all_events.extend(json_ld_events)
            print(f"   Found {len(json_ld_events)} events via JSON-LD")

            # Method 2: Extract from JavaScript data
            print("🔍 Method 2: Extracting from JavaScript data...")
            js_events = self._extract_javascript_events(response.text)
            all_events.extend(js_events)
            print(f"   Found {len(js_events)} events via JavaScript")

            # Method 3: Extract from HTML elements
            print("🔍 Method 3: Extracting from HTML elements...")
            html_events = self._extract_html_events(soup)
            all_events.extend(html_events)
            print(f"   Found {len(html_events)} events via HTML parsing")

            # Method 4: Extract from data attributes
            print("🔍 Method 4: Extracting from data attributes...")
            try:
                data_events = self._extract_data_attributes(soup)
                all_events.extend(data_events)
                print(f"   Found {len(data_events)} events via data attributes")
            except Exception as e:
                print(f"   ⚠️  Data attributes extraction failed: {e}")
                data_events = []

            # Deduplicate events by URL
            unique_events = {}
            for event in all_events:
                if "luma_url" in event and event["luma_url"]:
                    unique_events[event["luma_url"]] = event

            final_events = list(unique_events.values())
            print(f"🎉 Total unique events discovered: {len(final_events)}")

            # Method 5: Discover additional events by following links
            if len(final_events) < 20:  # If we don't have many events, try to find more
                print("🔍 Method 5: Discovering additional events via links...")
                additional_events = self._discover_additional_events(soup, calendar_url)
                for event in additional_events:
                    if event["luma_url"] not in unique_events:
                        unique_events[event["luma_url"]] = event
                        final_events.append(event)
                print(f"   Found {len(additional_events)} additional events via links")

            print(f"🎉 Total unique events discovered: {len(final_events)}")
            return final_events

        except Exception as e:
            print(f"❌ Error extracting events: {e}")
            return []

    def _extract_json_ld_events(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract events from JSON-LD structured data"""
        events = []
        json_scripts = soup.find_all("script", {"type": "application/ld+json"})

        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and "events" in data:
                    for event in data["events"]:
                        if "@id" in event and event["@id"].startswith("https://lu.ma/"):
                            parsed_event = {
                                "name": event.get("name", "Unknown Event"),
                                "luma_url": event["@id"],
                                "description": event.get("description", ""),
                                "start_date": event.get("startDate", ""),
                                "end_date": event.get("endDate", ""),
                                "location": self._extract_location(
                                    event.get("location", {})
                                ),
                                "organizer": event.get("organizer", []),
                                "image_url": self._extract_image_url(
                                    event.get("image", [])
                                ),
                                "extraction_method": "json_ld",
                                "created_at": datetime.utcnow().isoformat(),
                            }
                            events.append(parsed_event)
            except json.JSONDecodeError:
                continue

        return events

    def _extract_javascript_events(self, html_text: str) -> List[Dict[str, Any]]:
        """Extract events from JavaScript variables and API calls"""
        events = []

        # Look for common JavaScript patterns that contain event data
        patterns = [
            r"window\.__INITIAL_STATE__\s*=\s*({.*?});",
            r"window\.__DATA__\s*=\s*({.*?});",
            r"const\s+events\s*=\s*(\[.*?\]);",
            r"var\s+events\s*=\s*(\[.*?\]);",
            r'"events":\s*(\[.*?\])',
        ]

        import re

        for pattern in patterns:
            matches = re.findall(pattern, html_text, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, list):
                        # Direct array of events
                        for item in data:
                            if isinstance(item, dict) and "url" in item:
                                event = self._normalize_event_data(item, "javascript")
                                if event:
                                    events.append(event)
                    elif isinstance(data, dict):
                        # Look for events in nested structure
                        self._extract_nested_events(data, events, "javascript")
                except (json.JSONDecodeError, TypeError):
                    continue

        return events

    def _extract_html_events(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract events from HTML elements with class names and patterns"""
        events = []

        # Common selectors for event listings
        event_selectors = [
            ".event-card",
            ".event-item",
            ".event-listing",
            "[data-event]",
            "[data-event-id]",
            "[data-event-url]",
            ".card",
            ".item",
            ".listing",
            "article",
            ".post",
            ".entry",
        ]

        for selector in event_selectors:
            elements = soup.select(selector)
            for element in elements:
                event = self._extract_event_from_element(element)
                if event:
                    events.append(event)

        return events

    def _extract_data_attributes(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract events from data attributes in HTML elements"""
        events = []

        # Look for elements with data attributes containing event info
        elements_with_data = soup.find_all(
            attrs=lambda x: x and any(key.startswith("data-") for key in x.keys())
        )

        for element in elements_with_data:
            attrs = element.attrs
            event_data = {}

            # Extract event information from data attributes
            for attr, value in attrs.items():
                if attr.startswith("data-event"):
                    key = attr.replace("data-event-", "").replace("data-", "")
                    event_data[key] = value

            if event_data and ("url" in event_data or "id" in event_data):
                event = self._normalize_event_data(event_data, "data_attributes")
                if event:
                    events.append(event)

        return events

    def _extract_location(self, location_data):
        """Extract location from various formats"""
        if isinstance(location_data, str):
            return location_data
        elif isinstance(location_data, dict):
            return location_data.get("name", location_data.get("address", ""))
        elif isinstance(location_data, list) and location_data:
            return (
                location_data[0].get("name", "")
                if isinstance(location_data[0], dict)
                else str(location_data[0])
            )
        return "TBD"

    def _extract_image_url(self, image_data):
        """Extract image URL from various formats"""
        if isinstance(image_data, str):
            return image_data
        elif isinstance(image_data, list) and image_data:
            return (
                image_data[0].get("url", "")
                if isinstance(image_data[0], dict)
                else str(image_data[0])
            )
        elif isinstance(image_data, dict):
            return image_data.get("url", "")
        return ""

    def _normalize_event_data(self, raw_data: Dict, method: str) -> Dict[str, Any]:
        """Normalize event data from different sources into consistent format"""
        if not isinstance(raw_data, dict):
            return None

        # Try to find URL in various fields
        url = (
            raw_data.get("url")
            or raw_data.get("link")
            or raw_data.get("href")
            or raw_data.get("event_url")
        )

        if not url or not url.startswith("https://lu.ma/"):
            return None

        name = (
            raw_data.get("name")
            or raw_data.get("title")
            or raw_data.get("event_name")
            or "Unknown Event"
        )

        return {
            "name": name,
            "luma_url": url,
            "description": raw_data.get("description", ""),
            "start_date": raw_data.get("start_date", raw_data.get("date", "")),
            "end_date": raw_data.get("end_date", ""),
            "location": raw_data.get("location", "TBD"),
            "extraction_method": method,
            "created_at": datetime.utcnow().isoformat(),
        }

    def _extract_nested_events(self, data: Dict, events: List, method: str):
        """Recursively extract events from nested data structures"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "events" and isinstance(value, list):
                    for item in value:
                        event = self._normalize_event_data(item, method)
                        if event:
                            events.append(event)
                elif isinstance(value, (dict, list)):
                    self._extract_nested_events(value, events, method)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._extract_nested_events(item, events, method)

    def _extract_event_from_element(self, element) -> Dict[str, Any]:
        """Extract event data from HTML element"""
        # Look for links to lu.ma
        links = element.find_all("a", href=True)
        luma_links = [link for link in links if "lu.ma/" in link["href"]]

        if not luma_links:
            return None

        url = luma_links[0]["href"]
        if not url.startswith("https://"):
            url = "https://lu.ma/" + url.split("lu.ma/")[-1]

        # Extract name from text content
        name = element.get_text(strip=True)
        if len(name) > 200:  # Truncate very long text
            name = name[:200] + "..."

        return {
            "name": name or "Unknown Event",
            "luma_url": url,
            "description": "",
            "start_date": "",
            "location": "TBD",
            "extraction_method": "html_element",
            "created_at": datetime.utcnow().isoformat(),
        }

    def verify_event_urls(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verify that event URLs are accessible"""
        print(f"🔍 Verifying {len(events)} event URLs...")
        verified_events = []

        for i, event in enumerate(events):
            url = event["luma_url"]
            try:
                response = self.session.head(url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    event["status"] = "verified"
                    event["verified_at"] = datetime.utcnow().isoformat()
                    verified_events.append(event)
                    print(f"   ✅ {i+1}/{len(events)}: {url[:50]}...")
                else:
                    print(
                        f"   ❌ {i+1}/{len(events)}: {url[:50]}... (HTTP {response.status_code})"
                    )
            except Exception as e:
                print(f"   ❌ {i+1}/{len(events)}: {url[:50]}... (Error: {e})")

            # Rate limiting
            time.sleep(0.5)

        print(f"✅ Verified {len(verified_events)} working event URLs")
        return verified_events


async def run_comprehensive_extraction():
    """
    Run comprehensive EthCC extraction to get all 90+ events
    """
    print("🚀 STARTING COMPREHENSIVE ETHCC EXTRACTION")
    print("=" * 80)
    print("🎯 Target: Extract ALL EthCC events (90+ expected)")
    print("⏱️  Expected Duration: 1-2 hours for complete extraction")
    print("🔧 Methods: JSON-LD, JavaScript, HTML parsing, Data attributes")
    print()

    extractor = ComprehensiveEthCCExtractor()

    start_time = time.time()

    # Phase 1: Extract all events from main calendar
    print("📋 PHASE 1: Extracting events from main EthCC calendar...")
    all_events = extractor.extract_all_ethcc_events_from_calendar()

    if not all_events:
        print("❌ No events found! Check network connectivity and calendar URL")
        return

    print(f"✅ Phase 1 complete: Found {len(all_events)} total events")
    print()

    # Phase 2: Verify event URLs are working
    print("📋 PHASE 2: Verifying event URLs...")
    verified_events = extractor.verify_event_urls(all_events)
    print(f"✅ Phase 2 complete: {len(verified_events)} verified working events")
    print()

    # Phase 3: Save results
    print("📋 PHASE 3: Saving extraction results...")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"comprehensive_ethcc_extraction_{timestamp}.json"

    extraction_report = {
        "extraction_summary": {
            "started_at": datetime.fromtimestamp(start_time).isoformat(),
            "completed_at": datetime.now().isoformat(),
            "total_duration_seconds": time.time() - start_time,
            "total_events_discovered": len(all_events),
            "verified_working_events": len(verified_events),
            "verification_rate": (
                len(verified_events) / len(all_events) if all_events else 0
            ),
        },
        "extraction_methods": {
            "json_ld": len(
                [e for e in all_events if e.get("extraction_method") == "json_ld"]
            ),
            "javascript": len(
                [e for e in all_events if e.get("extraction_method") == "javascript"]
            ),
            "html_element": len(
                [e for e in all_events if e.get("extraction_method") == "html_element"]
            ),
            "data_attributes": len(
                [
                    e
                    for e in all_events
                    if e.get("extraction_method") == "data_attributes"
                ]
            ),
        },
        "verified_events": verified_events,
        "all_discovered_events": all_events,
    }

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(extraction_report, f, indent=2, ensure_ascii=False)

    print(f"✅ Results saved to: {results_file}")
    print()

    # Final summary
    print("🎉 COMPREHENSIVE ETHCC EXTRACTION COMPLETE!")
    print("=" * 80)
    print("📊 FINAL SUMMARY:")
    print(f"   • Total Events Discovered: {len(all_events)}")
    print(f"   • Verified Working Events: {len(verified_events)}")
    print(f"   • Success Rate: {(len(verified_events)/len(all_events)*100):.1f}%")
    print(f"   • Total Duration: {(time.time() - start_time):.1f} seconds")
    print()

    if verified_events:
        print("🎯 SAMPLE VERIFIED EVENTS:")
        for i, event in enumerate(verified_events[:5]):
            print(f"   {i+1}. {event['name'][:60]}...")
            print(f"      URL: {event['luma_url']}")
            print(f"      Method: {event['extraction_method']}")
            print()

    print("✅ All events are now ready for database population!")
    print("🔧 Next step: Populate database with verified events")

    return extraction_report


if __name__ == "__main__":
    asyncio.run(run_comprehensive_extraction())
