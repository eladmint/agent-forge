#!/usr/bin/env python3
"""
Fix the Enhanced Orchestrator to extract REAL events using JSON-LD parsing
instead of creating fake events
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database utilities
try:
    from chatbot_api.core.database import get_supabase_client

    from agent_forge.core.shared.ai_helpers import generate_text_embedding

    HAS_DATABASE = True
except (ImportError, AttributeError, Exception) as e:
    print(f"Warning: Database imports not available. Running in test mode. Error: {e}")
    HAS_DATABASE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealEventExtractor:
    """Extract real events using JSON-LD parsing instead of fake generation"""

    def __init__(self):
        self.session = None
        self.supabase = None
        if HAS_DATABASE:
            try:
                self.supabase = get_supabase_client()
            except Exception as e:
                logger.warning(f"Database connection failed: {e}")
                self.supabase = None

    async def __aenter__(self):
        # No session needed for requests
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # No session to close
        pass

    async def extract_real_events_from_calendar(
        self, calendar_url: str
    ) -> List[Dict[str, Any]]:
        """Extract real events from calendar page using JSON-LD parsing"""

        logger.info(f"🎯 Extracting real events from {calendar_url}")

        try:
            # Use requests instead of aiohttp to avoid SSL issues
            response = requests.get(calendar_url, timeout=30)
            if response.status_code != 200:
                logger.error(f"Failed to fetch calendar: {response.status_code}")
                return []

            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # Find JSON-LD structured data
            json_scripts = soup.find_all("script", {"type": "application/ld+json"})

            real_events = []
            for script in json_scripts:
                try:
                    data = json.loads(script.string)

                    # Check if this contains events
                    if "events" in data and isinstance(data["events"], list):
                        logger.info(
                            f"📅 Found {len(data['events'])} real events in JSON-LD"
                        )

                        for event in data["events"]:
                            if "@id" in event and event["@id"].startswith(
                                "https://lu.ma/"
                            ):
                                real_event = {
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
                                    "offers": event.get("offers", []),
                                    "created_at": datetime.utcnow().isoformat(),
                                }
                                real_events.append(real_event)

                        logger.info(f"✅ Extracted {len(real_events)} real events")
                        return real_events

                except json.JSONDecodeError as e:
                    logger.debug(f"Skipping invalid JSON in script tag: {e}")
                    continue

            logger.warning("❌ No JSON-LD structured data with events found")
            return []

        except Exception as e:
            logger.error(f"❌ Error extracting real events: {e}")
            return []

    def _extract_location(self, location_data: Dict) -> str:
        """Extract location string from JSON-LD location object"""
        if isinstance(location_data, dict):
            if "name" in location_data:
                return location_data["name"]
            elif "address" in location_data:
                address = location_data["address"]
                if isinstance(address, dict):
                    parts = []
                    if "streetAddress" in address:
                        parts.append(address["streetAddress"])
                    if "addressLocality" in address:
                        parts.append(address["addressLocality"])
                    if "addressCountry" in address:
                        country = address["addressCountry"]
                        if isinstance(country, dict) and "name" in country:
                            parts.append(country["name"])
                        elif isinstance(country, str):
                            parts.append(country)
                    return ", ".join(parts)
        return str(location_data) if location_data else ""

    def _extract_image_url(self, image_data: List) -> str:
        """Extract image URL from JSON-LD image array"""
        if isinstance(image_data, list) and len(image_data) > 0:
            return image_data[0]
        return ""

    async def save_real_events_to_database(self, events: List[Dict[str, Any]]) -> int:
        """Save real events to database, replacing fake ones"""

        if not self.supabase:
            logger.warning("No database connection available")
            return 0

        saved_count = 0

        for event in events:
            try:
                # Check if event already exists
                existing = (
                    self.supabase.table("events")
                    .select("id")
                    .eq("luma_url", event["luma_url"])
                    .execute()
                )

                # Generate embedding for semantic search
                embedding = None
                try:
                    if HAS_DATABASE:
                        description_text = f"{event['name']} {event['description']}"
                        embedding = await generate_text_embedding(description_text)
                except Exception as e:
                    logger.warning(f"Failed to generate embedding: {e}")

                # Prepare event data for database
                event_data = {
                    "name": event["name"],
                    "description": event["description"],
                    "start_date": event["start_date"] if event["start_date"] else None,
                    "end_date": event["end_date"] if event["end_date"] else None,
                    "location": event["location"],
                    "luma_url": event["luma_url"],
                    "image_url": event["image_url"],
                    "category": "EthCC Event",  # Proper categorization
                    "metadata": {
                        "organizer": event["organizer"],
                        "offers": event["offers"],
                        "extraction_source": "real_json_ld",
                        "extraction_date": event["created_at"],
                    },
                }

                if embedding:
                    event_data["embedding"] = embedding

                if existing.data:
                    # Update existing record
                    result = (
                        self.supabase.table("events")
                        .update(event_data)
                        .eq("id", existing.data[0]["id"])
                        .execute()
                    )
                    logger.info(f"✅ Updated existing event: {event['name']}")
                else:
                    # Create new record
                    result = self.supabase.table("events").insert(event_data).execute()
                    logger.info(f"✅ Created new event: {event['name']}")

                saved_count += 1

            except Exception as e:
                logger.error(f"❌ Failed to save event {event['name']}: {e}")
                continue

        logger.info(f"💾 Saved {saved_count}/{len(events)} real events to database")
        return saved_count

    async def cleanup_fake_events(self) -> int:
        """Remove fake events that don't have real Luma URLs"""

        if not self.supabase:
            logger.warning("No database connection available")
            return 0

        try:
            # Find events with fake URLs (containing 'ethcc-' pattern but not real Luma URLs)
            fake_patterns = [
                "ethcc-validator-session",
                "ethcc-closing-party",
                "ethcc-african-initiative",
            ]

            deleted_count = 0
            for pattern in fake_patterns:
                fake_events = (
                    self.supabase.table("events")
                    .select("id, name, luma_url")
                    .ilike("luma_url", f"%{pattern}%")
                    .execute()
                )

                for event in fake_events.data:
                    logger.info(
                        f"🗑️ Removing fake event: {event['name']} ({event['luma_url']})"
                    )
                    self.supabase.table("events").delete().eq(
                        "id", event["id"]
                    ).execute()
                    deleted_count += 1

            logger.info(f"🧹 Removed {deleted_count} fake events from database")
            return deleted_count

        except Exception as e:
            logger.error(f"❌ Failed to cleanup fake events: {e}")
            return 0


async def main():
    """Main function to fix the event extraction"""

    print("🔧 Fixing Enhanced Orchestrator to Extract REAL Events")
    print("=" * 60)

    async with RealEventExtractor() as extractor:
        # Step 1: Extract real events from EthCC calendar
        real_events = await extractor.extract_real_events_from_calendar(
            "https://lu.ma/ethcc"
        )

        if not real_events:
            print("❌ No real events found. Exiting.")
            return

        print(f"\n✅ Found {len(real_events)} real events:")
        for i, event in enumerate(real_events, 1):
            print(f"  {i}. {event['name']}")
            print(f"     URL: {event['luma_url']}")
            print(f"     Date: {event['start_date']}")
            print()

        if HAS_DATABASE:
            # Step 2: Cleanup fake events
            print("\n🧹 Cleaning up fake events...")
            deleted_count = await extractor.cleanup_fake_events()

            # Step 3: Save real events to database
            print("\n💾 Saving real events to database...")
            saved_count = await extractor.save_real_events_to_database(real_events)

            print("\n🎉 Database Update Complete!")
            print(f"   Deleted: {deleted_count} fake events")
            print(f"   Saved: {saved_count} real events")
        else:
            print("\n⚠️ Running in test mode - no database updates")

        # Step 4: Verify the fix
        print("\n🔍 Verification: Testing real URL...")
        real_url = real_events[0]["luma_url"]
        try:
            response = requests.head(real_url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Real URL verified: {real_url} (200 OK)")
            else:
                print(f"⚠️ Real URL status: {real_url} ({response.status_code})")
        except Exception as e:
            print(f"❌ URL verification failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
