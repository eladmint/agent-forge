"""
Event data saving and processing logic.
"""

import asyncio
import logging
from typing import Any, Dict

from .client import get_supabase_client

logger = logging.getLogger(__name__)


async def save_event_data(event_data: Dict[str, Any]) -> bool:
    """
    Saves a single event data dictionary to the database using a direct insert.
    This replaces the complex relational upsert with a simple, robust insert.

    Args:
        event_data: A dictionary representing a single event from the scraper.
    """
    client = get_supabase_client()
    if not client:
        logger.error("Supabase client is not initialized. Cannot save data.")
        return False

    luma_url_for_logging = event_data.get("luma_url") or "UNKNOWN_URL"
    logger.info(f"[{luma_url_for_logging}] Starting direct database save.")
    logger.info("EXECUTING SIMPLIFIED V4 DATABASE SAVE LOGIC WITH FORCED PUSH")

    # We will only attempt to save fields that we know exist in the 'events' table.
    # This prevents errors from schema mismatches.
    # Updated to include all fields from migration 20250603000001_add_structured_event_fields.sql
    known_columns = [
        "luma_url",
        "url",
        "name",
        "description",
        "location_name",
        "ai_enhanced",
        "completeness_score",
        "crypto_industry_matches",
        # Enhanced speaker/organizer data from migration
        "speaker_names",
        "speaker_count", 
        "featured_speakers",
        # Enhanced location columns from migration
        "venue_name",
        "venue_address",
        "city",
        "country",
        "host_organization",
        # Event metadata columns from migration
        "sponsor_names",
        "partner_count",
        "extraction_method",
        "data_completeness_score",
        "extraction_sources",
        # Additional fields commonly sent by orchestrator
        "start_date",
        "category",
        "status",
        "processing_time",
        "speakers",
        "sponsors", 
        "organizers",
        "data_sources",
        "images_analyzed",
        "external_sites_scraped",
        "visual_intelligence_used",
        "mcp_browser_used",
        "data_refinement_applied"
    ]

    data_to_save = {key: event_data[key] for key in known_columns if key in event_data}

    if "luma_url" not in data_to_save:
        logger.error(f"[{luma_url_for_logging}] Missing required 'luma_url' for event insert. Aborting.")
        return False

    try:
        logger.debug(f"Attempting to insert event: {data_to_save.get('name')}")
        result = await asyncio.to_thread(
            client.table("events").insert(data_to_save).execute
        )

        # The PostgREST API wrapper returns a list in 'data' on success.
        if result.data and len(result.data) > 0:
            logger.info(f"✅ [{luma_url_for_logging}] Event '{data_to_save.get('name')}' saved successfully.")
            return True
        else:
            # This path could be taken if RLS prevents insert but doesn't raise an error,
            # or if the insert just returns no data for some reason.
            logger.error(f"❌ [{luma_url_for_logging}] Failed to save event. No data returned from insert. Result: {result}")
            return False

    except Exception as e:
        error_str = str(e)
        # Check for unique constraint violation on 'luma_url'
        if 'duplicate key value violates unique constraint "events_luma_url_key"' in error_str:
             logger.info(f"📝 [{luma_url_for_logging}] Event already exists in database.")
             return True # Treat as success, as the data is in the database.

        logger.error(f"❌ [{luma_url_for_logging}] Database save error for event '{data_to_save.get('name')}': {e}", exc_info=True)
        return False
