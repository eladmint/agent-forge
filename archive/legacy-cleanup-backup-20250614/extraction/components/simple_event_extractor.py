#!/usr/bin/env python3
"""
Extract REAL EthCC events from lu.ma/ethcc page using direct JSON-LD parsing
"""

import json
import logging

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_real_ethcc_events():
    """Extract real events from the EthCC page"""

    try:
        logger.info("🎯 Fetching real EthCC page...")
        response = requests.get("https://lu.ma/ethcc", timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Find JSON-LD structured data
        json_scripts = soup.find_all("script", {"type": "application/ld+json"})

        for script in json_scripts:
            try:
                data = json.loads(script.string)

                # Check if this contains events
                if "events" in data and isinstance(data["events"], list):
                    logger.info(
                        f"📅 Found {len(data['events'])} real events in JSON-LD"
                    )

                    real_events = []
                    for event in data["events"]:
                        if "@id" in event and event["@id"].startswith("https://lu.ma/"):
                            real_event = {
                                "name": event.get("name", "Unknown Event"),
                                "url": event["@id"],
                                "description": event.get("description", ""),
                                "start_date": event.get("startDate", ""),
                                "end_date": event.get("endDate", ""),
                                "location": event.get("location", {}).get("name", ""),
                                "organizer": event.get("organizer", []),
                            }
                            real_events.append(real_event)

                    logger.info(f"✅ Extracted {len(real_events)} real events")

                    # Print sample events
                    logger.info("📋 Sample real events:")
                    for i, event in enumerate(real_events[:5]):
                        logger.info(f"  {i+1}. {event['name']}")
                        logger.info(f"     URL: {event['url']}")
                        logger.info(f"     Date: {event['start_date']}")
                        logger.info("")

                    return real_events

            except json.JSONDecodeError as e:
                logger.debug(f"Skipping invalid JSON in script tag: {e}")
                continue

        logger.warning("❌ No JSON-LD structured data with events found")
        return []

    except Exception as e:
        logger.error(f"❌ Error extracting real events: {e}")
        return []


def verify_real_urls(events):
    """Verify that the extracted URLs are real and accessible"""
    logger.info("🔍 Verifying real URLs...")

    verified_count = 0
    for i, event in enumerate(events[:3]):  # Test first 3
        try:
            response = requests.head(event["url"], timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ {event['url']} - REAL (200 OK)")
                verified_count += 1
            else:
                logger.warning(f"⚠️ {event['url']} - Status {response.status_code}")
        except Exception as e:
            logger.error(f"❌ {event['url']} - Error: {e}")

    logger.info(f"📊 Verified {verified_count}/{min(3, len(events))} URLs as real")
    return verified_count > 0


if __name__ == "__main__":
    print("🎯 Extracting REAL EthCC Events")
    print("=" * 50)

    events = extract_real_ethcc_events()

    if events:
        print(f"\n🎉 SUCCESS: Found {len(events)} real events!")

        # Verify URLs are real
        if verify_real_urls(events):
            print("✅ Real URLs confirmed!")
        else:
            print("❌ URL verification failed")

        # Save to file for inspection
        with open("/tmp/real_ethcc_events.json", "w") as f:
            json.dump(events, f, indent=2)
        print("💾 Saved real events to /tmp/real_ethcc_events.json")
    else:
        print("❌ No real events extracted")
