#!/usr/bin/env python3
"""
Calendar Synchronization Service
Part of Phase 20: Real-time Event Monitoring
Handles calendar integration, ICS generation, and sync management
"""

import asyncio
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import pytz
from icalendar import Calendar, Event, vText

# Database and utilities
from .database.client import get_supabase_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CalendarSyncType(Enum):
    """Types of calendar synchronization"""

    FULL_CALENDAR = "full_calendar"  # Complete event calendar
    SUBSCRIBED_EVENTS = "subscribed_events"  # Only subscribed events
    REGISTERED_EVENTS = "registered_events"  # Only registered events
    CUSTOM_FILTER = "custom_filter"  # Custom filtered events


class SyncStatus(Enum):
    """Calendar sync status"""

    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    EXPIRED = "expired"


@dataclass
class CalendarSubscription:
    """Calendar subscription configuration"""

    id: str
    user_id: str
    sync_type: CalendarSyncType
    calendar_name: str
    sync_url: str
    filter_criteria: Dict[str, Any]
    auto_sync: bool
    sync_interval_hours: int
    status: SyncStatus
    last_sync: Optional[datetime]
    next_sync: Optional[datetime]
    sync_count: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


@dataclass
class CalendarEvent:
    """Represents a calendar event for synchronization"""

    id: str
    event_id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: str
    url: str
    organizer: Optional[str]
    speakers: List[str]
    tags: List[str]
    registration_required: bool
    registration_url: Optional[str]
    last_modified: datetime


class CalendarSyncService:
    """Manages calendar synchronization and ICS generation"""

    def __init__(self):
        self.supabase = get_supabase_client()
        self.running = False
        self.sync_check_interval = 3600  # Check every hour

    async def initialize(self):
        """Initialize the calendar sync service"""
        logger.info("🗓️ Initializing Calendar Sync Service")

        # Create necessary database tables
        await self._create_calendar_tables()

        logger.info("✅ Calendar Sync Service initialized")

    async def _create_calendar_tables(self):
        """Create database tables for calendar synchronization"""
        try:
            # Calendar subscriptions table
            subscriptions_table = """
            CREATE TABLE IF NOT EXISTS calendar_subscriptions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id TEXT NOT NULL,
                sync_type TEXT NOT NULL,
                calendar_name TEXT NOT NULL,
                sync_url TEXT NOT NULL UNIQUE,
                filter_criteria JSONB DEFAULT '{}',
                auto_sync BOOLEAN DEFAULT true,
                sync_interval_hours INTEGER DEFAULT 24,
                status TEXT DEFAULT 'active',
                last_sync TIMESTAMP WITH TIME ZONE,
                next_sync TIMESTAMP WITH TIME ZONE,
                sync_count INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                metadata JSONB DEFAULT '{}'
            );
            """

            # Calendar sync history table
            sync_history_table = """
            CREATE TABLE IF NOT EXISTS calendar_sync_history (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                subscription_id UUID REFERENCES calendar_subscriptions(id),
                sync_started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                sync_completed_at TIMESTAMP WITH TIME ZONE,
                events_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'in_progress',
                error_message TEXT,
                sync_duration_seconds REAL,
                metadata JSONB DEFAULT '{}'
            );
            """

            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_calendar_subscriptions_user_id ON calendar_subscriptions(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_calendar_subscriptions_status ON calendar_subscriptions(status);",
                "CREATE INDEX IF NOT EXISTS idx_calendar_subscriptions_next_sync ON calendar_subscriptions(next_sync);",
                "CREATE INDEX IF NOT EXISTS idx_calendar_sync_history_subscription_id ON calendar_sync_history(subscription_id);",
            ]

            # Execute table creation
            self.supabase.query("query", default="").eq(
                "query", subscriptions_table
            ).execute()
            self.supabase.query("query", default="").eq(
                "query", sync_history_table
            ).execute()

            # Execute index creation
            for index in indexes:
                self.supabase.query("query", default="").eq("query", index).execute()

            logger.info("✅ Calendar tables created successfully")

        except Exception as e:
            logger.error(f"❌ Failed to create calendar tables: {e}")

    async def create_calendar_subscription(
        self, user_id: str, config: Dict[str, Any]
    ) -> str:
        """Create a new calendar subscription"""
        try:
            subscription_id = str(uuid.uuid4())
            sync_url = f"/api/calendar/{subscription_id}/events.ics"

            subscription = CalendarSubscription(
                id=subscription_id,
                user_id=user_id,
                sync_type=CalendarSyncType(config["sync_type"]),
                calendar_name=config["calendar_name"],
                sync_url=sync_url,
                filter_criteria=config.get("filter_criteria", {}),
                auto_sync=config.get("auto_sync", True),
                sync_interval_hours=config.get("sync_interval_hours", 24),
                status=SyncStatus.ACTIVE,
                last_sync=None,
                next_sync=datetime.now()
                + timedelta(hours=config.get("sync_interval_hours", 24)),
                sync_count=0,
                error_message=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata=config.get("metadata", {}),
            )

            # Save to database
            subscription_data = asdict(subscription)
            subscription_data["sync_type"] = subscription.sync_type.value
            subscription_data["status"] = subscription.status.value
            subscription_data["created_at"] = subscription.created_at.isoformat()
            subscription_data["updated_at"] = subscription.updated_at.isoformat()
            if subscription_data["last_sync"]:
                subscription_data["last_sync"] = subscription.last_sync.isoformat()
            if subscription_data["next_sync"]:
                subscription_data["next_sync"] = subscription.next_sync.isoformat()

            self.supabase.table("calendar_subscriptions").insert(
                subscription_data
            ).execute()

            logger.info(
                f"✅ Created calendar subscription {subscription_id} for user {user_id}"
            )
            return subscription_id

        except Exception as e:
            logger.error(f"❌ Failed to create calendar subscription: {e}")
            raise

    async def generate_ics_calendar(self, subscription_id: str) -> str:
        """Generate ICS calendar data for a subscription"""
        try:
            # Get subscription details
            subscription_response = (
                self.supabase.table("calendar_subscriptions")
                .select("*")
                .eq("id", subscription_id)
                .execute()
            )

            if not subscription_response.data:
                raise ValueError(f"Calendar subscription {subscription_id} not found")

            subscription_data = subscription_response.data[0]

            # Get events based on subscription type and filters
            events = await self._get_filtered_events(subscription_data)

            # Create ICS calendar
            cal = Calendar()
            cal.add("prodid", "-//TokenHunter//Event Calendar//EN")
            cal.add("version", "2.0")
            cal.add("calscale", "GREGORIAN")
            cal.add("method", "PUBLISH")
            cal.add("x-wr-calname", vText(subscription_data["calendar_name"]))
            cal.add(
                "x-wr-caldesc",
                vText(f"TokenHunter Events - {subscription_data['sync_type']}"),
            )
            cal.add("x-wr-timezone", vText("UTC"))

            # Add events to calendar
            for event_data in events:
                cal_event = self._create_ics_event(event_data)
                cal.add_component(cal_event)

            # Update sync statistics
            await self._update_sync_statistics(subscription_id, len(events))

            logger.info(
                f"📅 Generated ICS calendar with {len(events)} events for subscription {subscription_id}"
            )
            return cal.to_ical().decode("utf-8")

        except Exception as e:
            logger.error(f"❌ Failed to generate ICS calendar: {e}")
            await self._mark_subscription_error(subscription_id, str(e))
            raise

    async def _get_filtered_events(self, subscription_data: Dict) -> List[Dict]:
        """Get events based on subscription filters"""
        try:
            user_id = subscription_data["user_id"]
            sync_type = subscription_data["sync_type"]
            filter_criteria = subscription_data.get("filter_criteria", {})

            # Base query
            query = self.supabase.table("events").select("*")

            # Apply sync type filters
            if sync_type == "subscribed_events":
                # Get user's subscribed events
                subscriptions_response = (
                    self.supabase.table("event_subscriptions")
                    .select("event_ids")
                    .eq("user_id", user_id)
                    .eq("is_active", True)
                    .execute()
                )

                subscribed_event_ids = []
                for sub in subscriptions_response.data:
                    subscribed_event_ids.extend(sub.get("event_ids", []))

                if subscribed_event_ids:
                    query = query.in_("id", subscribed_event_ids)
                else:
                    return []  # No subscribed events

            elif sync_type == "registered_events":
                # Get user's registered events
                registrations_response = (
                    self.supabase.table("event_registrations")
                    .select("event_id")
                    .eq("user_id", user_id)
                    .execute()
                )

                registered_event_ids = [
                    reg["event_id"] for reg in registrations_response.data
                ]

                if registered_event_ids:
                    query = query.in_("id", registered_event_ids)
                else:
                    return []  # No registered events

            # Apply additional filters
            if filter_criteria:
                # Date range filter
                if "start_date" in filter_criteria:
                    query = query.gte("date", filter_criteria["start_date"])
                if "end_date" in filter_criteria:
                    query = query.lte("date", filter_criteria["end_date"])

                # Location filter
                if "locations" in filter_criteria:
                    location_filter = "|".join(filter_criteria["locations"])
                    query = query.ilike("venue", f"%{location_filter}%")

                # Category filter
                if "categories" in filter_criteria:
                    categories_filter = filter_criteria["categories"]
                    if categories_filter:
                        query = query.in_("category", categories_filter)

                # Organization filter
                if "organizations" in filter_criteria:
                    org_ids = filter_criteria["organizations"]
                    if org_ids:
                        query = query.in_("organization_id", org_ids)

            # Execute query
            response = query.execute()

            # Convert to CalendarEvent objects
            calendar_events = []
            for event_data in response.data:
                cal_event = self._convert_to_calendar_event(event_data)
                if cal_event:
                    calendar_events.append(cal_event)

            return calendar_events

        except Exception as e:
            logger.error(f"❌ Failed to get filtered events: {e}")
            return []

    def _convert_to_calendar_event(self, event_data: Dict) -> Optional[Dict]:
        """Convert database event to calendar event format"""
        try:
            # Parse datetime
            start_time = (
                datetime.fromisoformat(event_data["date"])
                if event_data.get("date")
                else datetime.now()
            )

            # Estimate duration (default 2 hours if not specified)
            duration_hours = 2
            if "duration" in event_data and event_data["duration"]:
                try:
                    duration_hours = float(event_data["duration"])
                except:
                    duration_hours = 2

            end_time = start_time + timedelta(hours=duration_hours)

            # Extract speakers
            speakers = []
            if "speakers" in event_data and event_data["speakers"]:
                if isinstance(event_data["speakers"], list):
                    speakers = event_data["speakers"]
                elif isinstance(event_data["speakers"], str):
                    speakers = [event_data["speakers"]]

            # Extract tags
            tags = []
            if "tags" in event_data and event_data["tags"]:
                if isinstance(event_data["tags"], list):
                    tags = event_data["tags"]
                elif isinstance(event_data["tags"], str):
                    tags = event_data["tags"].split(",")

            return {
                "id": event_data["id"],
                "event_id": event_data["id"],
                "title": event_data.get("name", "Untitled Event"),
                "description": event_data.get("description", ""),
                "start_time": start_time,
                "end_time": end_time,
                "location": event_data.get("venue", ""),
                "url": event_data.get("url", ""),
                "organizer": event_data.get("organizer", ""),
                "speakers": speakers,
                "tags": tags,
                "registration_required": bool(event_data.get("registration_url")),
                "registration_url": event_data.get("registration_url"),
                "last_modified": datetime.now(),
            }

        except Exception as e:
            logger.error(f"❌ Failed to convert event {event_data.get('id')}: {e}")
            return None

    def _create_ics_event(self, event_data: Dict) -> Event:
        """Create an ICS event from event data"""
        event = Event()

        # Basic event information
        event.add("uid", f"tokenhunter-{event_data['event_id']}@tokenhunter.app")
        event.add("summary", vText(event_data["title"]))
        event.add("description", vText(event_data["description"]))

        # Date and time (convert to UTC)
        utc = pytz.UTC
        start_time = event_data["start_time"].replace(tzinfo=utc)
        end_time = event_data["end_time"].replace(tzinfo=utc)

        event.add("dtstart", start_time)
        event.add("dtend", end_time)
        event.add("dtstamp", datetime.now(utc))
        event.add("last-modified", event_data["last_modified"].replace(tzinfo=utc))

        # Location
        if event_data["location"]:
            event.add("location", vText(event_data["location"]))

        # URL
        if event_data["url"]:
            event.add("url", vText(event_data["url"]))

        # Organizer
        if event_data["organizer"]:
            event.add("organizer", vText(event_data["organizer"]))

        # Categories (tags)
        if event_data["tags"]:
            event.add("categories", event_data["tags"])

        # Custom properties
        if event_data["speakers"]:
            speakers_text = ", ".join(event_data["speakers"])
            event.add("X-SPEAKERS", vText(speakers_text))

        if event_data["registration_required"] and event_data["registration_url"]:
            event.add("X-REGISTRATION-URL", vText(event_data["registration_url"]))

        # Status
        event.add("status", vText("CONFIRMED"))
        event.add("class", vText("PUBLIC"))

        return event

    async def _update_sync_statistics(self, subscription_id: str, events_count: int):
        """Update sync statistics for a subscription"""
        try:
            now = datetime.now()

            # Get current subscription data
            subscription_response = (
                self.supabase.table("calendar_subscriptions")
                .select("sync_count, sync_interval_hours")
                .eq("id", subscription_id)
                .execute()
            )

            if subscription_response.data:
                current_sync_count = subscription_response.data[0].get("sync_count", 0)
                sync_interval_hours = subscription_response.data[0].get(
                    "sync_interval_hours", 24
                )

                # Update subscription
                self.supabase.table("calendar_subscriptions").update(
                    {
                        "last_sync": now.isoformat(),
                        "next_sync": (
                            now + timedelta(hours=sync_interval_hours)
                        ).isoformat(),
                        "sync_count": current_sync_count + 1,
                        "status": "active",
                        "error_message": None,
                        "updated_at": now.isoformat(),
                    }
                ).eq("id", subscription_id).execute()

                # Record sync history
                self.supabase.table("calendar_sync_history").insert(
                    {
                        "subscription_id": subscription_id,
                        "sync_started_at": now.isoformat(),
                        "sync_completed_at": now.isoformat(),
                        "events_count": events_count,
                        "status": "completed",
                        "sync_duration_seconds": 1.0,  # Approximate
                        "metadata": {"events_generated": events_count},
                    }
                ).execute()

        except Exception as e:
            logger.error(f"❌ Failed to update sync statistics: {e}")

    async def _mark_subscription_error(self, subscription_id: str, error_message: str):
        """Mark a subscription as having an error"""
        try:
            self.supabase.table("calendar_subscriptions").update(
                {
                    "status": "error",
                    "error_message": error_message,
                    "updated_at": datetime.now().isoformat(),
                }
            ).eq("id", subscription_id).execute()

        except Exception as e:
            logger.error(f"❌ Failed to mark subscription error: {e}")

    async def get_user_calendar_subscriptions(self, user_id: str) -> List[Dict]:
        """Get all calendar subscriptions for a user"""
        try:
            response = (
                self.supabase.table("calendar_subscriptions")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"❌ Failed to get user calendar subscriptions: {e}")
            return []

    async def update_subscription(self, subscription_id: str, updates: Dict) -> bool:
        """Update a calendar subscription"""
        try:
            updates["updated_at"] = datetime.now().isoformat()

            self.supabase.table("calendar_subscriptions").update(updates).eq(
                "id", subscription_id
            ).execute()

            logger.info(f"✅ Updated calendar subscription {subscription_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update calendar subscription: {e}")
            return False

    async def delete_subscription(self, subscription_id: str) -> bool:
        """Delete a calendar subscription"""
        try:
            # Delete subscription
            self.supabase.table("calendar_subscriptions").delete().eq(
                "id", subscription_id
            ).execute()

            # Delete sync history
            self.supabase.table("calendar_sync_history").delete().eq(
                "subscription_id", subscription_id
            ).execute()

            logger.info(f"✅ Deleted calendar subscription {subscription_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete calendar subscription: {e}")
            return False

    async def start_auto_sync_monitor(self):
        """Start the automatic sync monitoring service"""
        logger.info("🔄 Starting calendar auto-sync monitor")
        self.running = True

        while self.running:
            try:
                await self._check_scheduled_syncs()
                await asyncio.sleep(self.sync_check_interval)
            except Exception as e:
                logger.error(f"❌ Error in auto-sync monitor: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _check_scheduled_syncs(self):
        """Check for subscriptions that need syncing"""
        try:
            now = datetime.now()

            # Get subscriptions due for sync
            response = (
                self.supabase.table("calendar_subscriptions")
                .select("*")
                .eq("auto_sync", True)
                .eq("status", "active")
                .lte("next_sync", now.isoformat())
                .execute()
            )

            for subscription in response.data:
                try:
                    logger.info(f"🔄 Auto-syncing calendar {subscription['id']}")
                    await self.generate_ics_calendar(subscription["id"])
                except Exception as e:
                    logger.error(
                        f"❌ Failed to auto-sync calendar {subscription['id']}: {e}"
                    )
                    await self._mark_subscription_error(subscription["id"], str(e))

        except Exception as e:
            logger.error(f"❌ Error checking scheduled syncs: {e}")

    def stop_auto_sync_monitor(self):
        """Stop the automatic sync monitoring service"""
        logger.info("🛑 Stopping calendar auto-sync monitor")
        self.running = False


# Global calendar service instance
calendar_service = CalendarSyncService()


async def initialize_calendar_service():
    """Initialize the global calendar service"""
    await calendar_service.initialize()
    return calendar_service


if __name__ == "__main__":

    async def main():
        service = await initialize_calendar_service()
        await service.start_auto_sync_monitor()

    asyncio.run(main())
