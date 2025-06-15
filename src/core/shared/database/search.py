"""
Search and query functionality for database operations.
"""

import datetime
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import pytz
import requests
from dateutil import parser as date_parser
from dateutil.parser import ParserError

from supabase import Client as SupabaseClient

# Enhanced structured logging
try:
    from chatbot_api.utils.logging_utils import get_logger

    logger = get_logger(__name__)
except ImportError:
    # Fallback to basic logging if structured logging is not available
    logger = logging.getLogger(__name__)


def _sync_get_speaker_by_name(client, name: str) -> Optional[Dict[str, Any]]:
    """Synchronous helper function to retrieve a speaker by exact name match."""
    db_start_time = time.time()

    logger.info(f"Attempting direct DB lookup for speaker: '{name}'")
    try:
        # Select only the columns we actually need and intend to use
        response = (
            client.table("speakers")
            .select(
                "id, name, title, bio, linkedin_url, twitter_url, website_url, source_urls"
            )
            .ilike("name", name)
            .limit(1)
            .execute()
        )

        db_end_time = time.time()
        db_duration_ms = (db_end_time - db_start_time) * 1000

        if response.data:
            # Log successful database operation with structured logging
            logger.log_database_operation(
                operation="SELECT",
                table="speakers",
                duration_ms=db_duration_ms,
                rows_affected=len(response.data),
                success=True,
                extra={
                    "query_type": "speaker_name_lookup",
                    "search_name": name,
                    "result_found": True,
                },
            )

            logger.info(
                f"Direct lookup successful for speaker '{name}'. Found 1 record."
            )
            # Return the raw data - cleaning will happen in the API handler
            return response.data[0]
        else:
            # Log empty result with structured logging
            logger.log_database_operation(
                operation="SELECT",
                table="speakers",
                duration_ms=db_duration_ms,
                rows_affected=0,
                success=True,
                extra={
                    "query_type": "speaker_name_lookup",
                    "search_name": name,
                    "result_found": False,
                },
            )

            logger.warning(
                f"Direct lookup failed for speaker '{name}'. No records found."
            )
            return None
    except Exception as e:
        db_end_time = time.time()
        db_duration_ms = (db_end_time - db_start_time) * 1000

        # Log database error with structured logging
        logger.log_database_operation(
            operation="SELECT",
            table="speakers",
            duration_ms=db_duration_ms,
            rows_affected=None,
            success=False,
            error_type=type(e).__name__,
            extra={
                "query_type": "speaker_name_lookup",
                "search_name": name,
                "error_details": str(e),
            },
        )

        logger.error(
            f"Error during direct speaker lookup for '{name}': {e}", exc_info=True
        )
        return None


def _sync_get_events_by_date(
    client: SupabaseClient, date_str: str, timezone_str: str = "Asia/Dubai"
) -> List[Dict[str, Any]]:
    """
    Enhanced synchronous helper to fetch events occurring on a specific date.
    Now uses enhanced date processing for better natural language support.
    """
    logger.info(f"Enhanced date lookup for events on date string: '{date_str}'")

    try:
        # Import here to avoid circular imports
        from ..ai.date_processing import enhanced_get_events_by_date

        # Use enhanced date processing
        result = enhanced_get_events_by_date(
            client, date_str, timezone_str, include_suggestions=False
        )

        if result["success"]:
            events = result["events"]
            logger.info(
                f"Enhanced date lookup found {len(events)} events for '{date_str}'"
            )
            return events
        else:
            logger.warning(
                f"Enhanced date lookup failed for '{date_str}': {result.get('message', 'Unknown error')}"
            )
            return []

    except ImportError:
        # Fallback to original implementation if enhanced processing is not available
        logger.warning(
            "Enhanced date processing not available, falling back to basic parsing"
        )
        return _sync_get_events_by_date_basic(client, date_str, timezone_str)
    except Exception as e:
        logger.error(
            f"Error in enhanced date lookup for '{date_str}': {e}", exc_info=True
        )
        return []


def _sync_get_events_by_date_basic(
    client: SupabaseClient, date_str: str, timezone_str: str = "Asia/Dubai"
) -> List[Dict[str, Any]]:
    """Basic date parsing implementation (fallback)."""
    logger.info(f"Basic date lookup for events on date string: '{date_str}'")
    try:
        # Attempt to parse the date string, assuming current year if not specified
        # Use fuzzy parsing to handle variations like "28th", "April 28"
        target_date = date_parser.parse(date_str, fuzzy=True).date()
        logger.debug(f"Parsed target date: {target_date}")

        # Define the date range for the query (using the provided timezone)
        tz = pytz.timezone(timezone_str)
        start_datetime_local = datetime.datetime.combine(
            target_date, datetime.time.min, tzinfo=tz
        )
        end_datetime_local = datetime.datetime.combine(
            target_date, datetime.time.max, tzinfo=tz
        )

        # Convert to UTC for Supabase query (timestamptz is stored in UTC)
        start_datetime_utc = start_datetime_local.astimezone(pytz.utc)
        end_datetime_utc = end_datetime_local.astimezone(pytz.utc)

        logger.debug(
            f"Querying events between UTC: {start_datetime_utc.isoformat()} and {end_datetime_utc.isoformat()}"
        )

        response = (
            client.table("events")
            .select("id, name, description, start_time_iso, luma_url")
            .gte("start_time_iso", start_datetime_utc.isoformat())
            .lte("start_time_iso", end_datetime_utc.isoformat())
            .order("start_time_iso", desc=False)
            .execute()
        )

        if response.data:
            logger.info(
                f"Basic date lookup found {len(response.data)} events for '{date_str}' ({target_date})."
            )
            # Return raw data - cleaning happens in API handler
            return response.data
        else:
            logger.info(
                f"Basic date lookup did not find any events for '{date_str}' ({target_date})."
            )
            return []

    except ParserError:
        logger.error(f"Could not parse date string: '{date_str}'")
        return []
    except pytz.UnknownTimeZoneError:
        logger.error(f"Unknown timezone provided for date query: '{timezone_str}'")
        return []  # Or default to UTC?
    except Exception as e:
        logger.error(
            f"Error during basic event lookup by date for '{date_str}': {e}",
            exc_info=True,
        )
        return []


def _sync_keyword_search_events(
    client: SupabaseClient, query: str, limit: int = 10
) -> List[Dict[str, Any]]:
    """Performs a keyword search using the keyword_search_events RPC via direct HTTP POST."""
    # Ensure we have the necessary config - read directly as client object might not be fully initialized
    # if client initialization is lazy and this is called before the client is used elsewhere.
    # If client is guaranteed to be initialized, client.supabase_url/key could be used.
    supabase_url_local = os.getenv("SUPABASE_URL")
    supabase_key_local = os.getenv("SUPABASE_KEY")

    if not supabase_url_local or not supabase_key_local:
        logger.error("Supabase URL or Key not configured for direct RPC call.")
        return []

    rpc_url = f"{supabase_url_local.rstrip('/')}/rest/v1/rpc/keyword_search_events"
    headers = {
        "apikey": supabase_key_local,
        "Authorization": f"Bearer {supabase_key_local}",
        "Content-Type": "application/json",
        "Content-Profile": "public",  # Added: Specify schema for RPC
        "Prefer": "params=single-object",  # To send params as a single JSON object
    }
    payload = {"keyword": query, "result_limit": limit}

    logger.info(
        f"Performing keyword search via direct POST to RPC endpoint for query: '{query}'"
    )
    logger.debug(f"Calling RPC URL: {rpc_url}")
    logger.debug(
        f"Using headers (key redacted): {{'apikey': '...', 'Authorization': 'Bearer ...', 'Content-Type': '{headers.get('Content-Type')}', 'Content-Profile': '{headers.get('Content-Profile')}', 'Prefer': '{headers.get('Prefer')}'}}"
    )
    logger.debug(f"Using payload: {payload}")

    try:
        # Make the POST request with explicit UTF-8 encoding
        response = requests.post(
            rpc_url,
            headers=headers,
            data=json.dumps(payload).encode("utf-8"),  # Encode payload explicitly
            timeout=15,
        )
        # Ensure Content-Type reflects the encoded data if needed (requests usually handles this)
        # If issues persist, might need to set 'Content-Type': 'application/json; charset=utf-8' explicitly

        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        response_data = response.json()

        # Check if response contains data (PostgREST returns JSON array)
        if isinstance(response_data, list):
            logger.info(
                f"Keyword search direct RPC POST returned {len(response_data)} events."
            )
            return response_data
        else:
            # Log unexpected response format
            logger.warning(
                f"Keyword search direct RPC POST for query '{query}' returned unexpected format. Response: {response_data}"
            )
            return []

    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error calling keyword search RPC: {e}", exc_info=True)
        # Consider the type of error - e.g., timeout vs. connection error vs. HTTP error code
        # Log details from response if available (e.g., e.response.text)
        if e.response is not None:
            logger.error(f"RPC Response Status: {e.response.status_code}")
            logger.error(f"RPC Response Body: {e.response.text}")
        return []
    except Exception as e:
        logger.error(
            f"Unexpected error calling keyword search RPC via POST: {e}", exc_info=True
        )
        return []


def sanitize_search_query(query: str) -> str:
    """
    Sanitize search query to prevent SQL injection and other attacks.

    Args:
        query: Raw search query from user input

    Returns:
        str: Sanitized query safe for database operations
    """
    if not query:
        return ""

    # Remove dangerous SQL keywords and patterns
    dangerous_patterns = [
        r";.*?--",  # SQL comments
        r";\s*(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|TRUNCATE)",  # Dangerous SQL commands
        r"(UNION|union).*?(SELECT|select)",  # UNION injection
        r"(OR|or)\s+\d+\s*=\s*\d+",  # OR 1=1 patterns
        r"<script.*?>.*?</script>",  # Script tags
        r"javascript:",  # JavaScript URLs
        r"vbscript:",  # VBScript URLs
    ]

    import re

    sanitized = query

    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

    # Remove SQL comment markers
    sanitized = sanitized.replace("--", "").replace("/*", "").replace("*/", "")

    # Limit length to prevent memory exhaustion
    max_length = 1000
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Basic cleanup
    sanitized = sanitized.strip()

    return sanitized
