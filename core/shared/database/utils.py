"""
Database utilities and helper functions.
"""

import datetime
import json
import logging
import time
from typing import Any, Dict, List, Optional

import httpx
import pytz
from postgrest import APIResponse

from supabase import PostgrestAPIError

from .client import get_supabase_client

logger = logging.getLogger(__name__)


def _create_iso_timestamp(
    date_str: Optional[str],
    time_str: Optional[str],
    timezone_str: Optional[str],
    url_for_logging: str,
) -> Optional[str]:
    """
    Combines date, time, and timezone strings into a valid ISO 8601 timestamp string.
    Returns None if input is invalid or insufficient.
    """
    if not date_str or not time_str or not timezone_str:
        logger.debug(
            f"[{url_for_logging}] Insufficient date/time/timezone info to create timestamp (Date: {date_str}, Time: {time_str}, TZ: {timezone_str})."
        )
        return None

    # Clean timezone string (e.g., "GMT+4" -> "+0400", "UTC" -> "UTC")
    tz_offset_str = None
    pytz_timezone = None
    try:
        if timezone_str.upper().startswith("GMT") or timezone_str.upper().startswith(
            "UTC"
        ):
            tz_part = timezone_str[3:].strip()
            if tz_part:
                if tz_part.startswith("+") or tz_part.startswith("-"):
                    parts = tz_part.split(":")
                    hours_str = parts[0]
                    minutes_str = parts[1] if len(parts) > 1 else "0"
                    # Validate numeric parts
                    hours = int(hours_str)
                    minutes = int(minutes_str)
                    sign = hours_str[0]
                    tz_offset_str = f"{sign}{abs(hours):02d}{minutes:02d}"
                else:  # Try to parse named timezones like 'UTC'
                    pytz_timezone = pytz.timezone(timezone_str.upper())
            else:  # GMT/UTC with no offset provided, assume UTC
                pytz_timezone = pytz.utc
                tz_offset_str = "+0000"  # Indicate UTC offset

        elif timezone_str:  # Attempt to treat as Olson timezone name
            pytz_timezone = pytz.timezone(timezone_str)

    except pytz.UnknownTimeZoneError:
        logger.warning(
            f"[{url_for_logging}] Unknown timezone string: '{timezone_str}'. Cannot create timestamp."
        )
        return None
    except ValueError:
        logger.warning(
            f"[{url_for_logging}] Invalid timezone offset format: '{timezone_str}'. Cannot create timestamp."
        )
        return None
    except Exception as e:  # Catch other potential errors during TZ parsing
        logger.error(
            f"[{url_for_logging}] Error parsing timezone '{timezone_str}': {e}"
        )
        return None

    if not tz_offset_str and not pytz_timezone:
        logger.warning(
            f"[{url_for_logging}] Could not determine timezone info from string: '{timezone_str}'. Cannot create timestamp."
        )
        return None

    try:
        # Clean the time_str: Remove appended timezone info if present
        cleaned_time_str = time_str.strip()
        potential_tz_parts = cleaned_time_str.split(" ")
        if len(potential_tz_parts) > 1:  # Check if there's more than just HH:MM part
            # Check if the last part looks like a timezone (GMT, UTC, PST, EST, common offsets)
            last_part = potential_tz_parts[-1]
            # Simple check for common abbreviations or offset patterns
            if (
                last_part.upper()
                in ["GMT", "UTC", "PST", "PDT", "EST", "EDT", "CET", "CEST"]
                or (last_part.startswith(("+", "-")) and ":" in last_part)
                or (
                    last_part.startswith(("+", "-"))
                    and len(last_part) == 5
                    and last_part[1:].isdigit()
                )
                or (
                    last_part.upper().startswith("GMT")
                    and ("+" in last_part or "-" in last_part)
                )
                or (
                    last_part.upper().startswith("UTC")
                    and ("+" in last_part or "-" in last_part)
                )
            ):
                # Check if the part before the last is AM/PM
                if len(potential_tz_parts) > 2 and potential_tz_parts[-2].upper() in [
                    "AM",
                    "PM",
                ]:
                    cleaned_time_str = " ".join(
                        potential_tz_parts[:-1]
                    )  # Join time and AM/PM
                else:  # Assume it's just time like HH:MM followed by TZ
                    cleaned_time_str = potential_tz_parts[
                        0
                    ]  # Just take the first part (HH:MM)
                logger.debug(
                    f"[{url_for_logging}] Cleaned time string from '{time_str}' to '{cleaned_time_str}' for parsing."
                )
        # Else: Assume format is like 'HH:MM PM' or 'HH:MM' and needs no cleaning here

        # Combine date and cleaned time - be robust to date formats
        dt_naive = None
        # datetime_str = f"{date_str} {time_str}" # Old way

        # Common date formats Luma might use (add more if needed)
        date_formats = ["%Y-%m-%d", "%A, %B %d", "%a, %b %d", "%m/%d/%Y", "%d %b %Y"]
        time_formats = [
            "%H:%M",
            "%I:%M %p",
            "%H:%M:%S",
            "%I:%M:%S %p",
        ]  # Added formats with seconds

        parsed_date = None
        for dfmt in date_formats:
            try:
                # Attempt to parse the date string, assuming year might be missing if not YYYY-MM-DD
                # If format doesn't include year, assume current year
                date_obj_no_year = datetime.datetime.strptime(date_str, dfmt)
                current_year = datetime.datetime.now().year
                # Handle formats without year specifier (like %B %d)
                if "%Y" not in dfmt and "%y" not in dfmt:
                    parsed_date = date_obj_no_year.replace(year=current_year).date()
                else:
                    parsed_date = date_obj_no_year.date()
                break
            except ValueError:
                continue
        if parsed_date is None:
            logger.warning(
                f"[{url_for_logging}] Could not parse date string: '{date_str}'"
            )
            return None

        parsed_time = None
        # Use the potentially cleaned time string
        for tfmt in time_formats:
            try:
                parsed_time = datetime.datetime.strptime(cleaned_time_str, tfmt).time()
                break
            except ValueError:
                continue
        if parsed_time is None:
            # Log the cleaned time string that failed parsing
            logger.warning(
                f"[{url_for_logging}] Could not parse cleaned time string: '{cleaned_time_str}' (original: '{time_str}')"
            )
            return None

        dt_naive = datetime.datetime.combine(parsed_date, parsed_time)
        # >>> END MODIFICATION <<<

        # Make timezone-aware
        if pytz_timezone:
            dt_aware = pytz_timezone.localize(dt_naive)
        elif tz_offset_str:
            # Ensure tz_offset_str has sign for timedelta parsing
            sign = tz_offset_str[0]
            hours = int(tz_offset_str[1:3])
            minutes = int(tz_offset_str[3:5])
            delta = datetime.timedelta(hours=hours, minutes=minutes)
            if sign == "-":
                delta = -delta
            tzinfo = datetime.timezone(delta)
            dt_aware = dt_naive.replace(tzinfo=tzinfo)
        else:
            logger.error(
                f"[{url_for_logging}] Internal error: No timezone object or offset string available after parsing."
            )
            return None

        # Convert to ISO 8601 format with timezone offset
        return dt_aware.isoformat()

    except ValueError as e:
        logger.warning(
            f"[{url_for_logging}] Error constructing naive datetime from date='{date_str}', cleaned_time='{cleaned_time_str}': {e}"
        )
        return None
    except Exception as e:
        logger.error(
            f"[{url_for_logging}] Unexpected error creating timestamp for date='{date_str}', time='{time_str}' TZ='{timezone_str}': {e}"
        )
        return None


def _sync_upsert(client, table_name, data, conflict_column="name", source_url=None):
    """Synchronous upsert helper. Returns the ID of the upserted row."""
    if not data or not data.get(conflict_column):
        logger.warning(
            f"Upsert skipped for {table_name}: Missing data or conflict column value."
        )
        return None

    conflict_value = data[conflict_column]

    # Prepare data for upsert, removing the conflict column itself
    upsert_data = {k: v for k, v in data.items() if k != conflict_column}

    # Add source_url handling - only for tables that support it
    if source_url and table_name in ["speakers", "organizations"]:
        # Basic approach: OVERWRITE source_urls with the current source_url in an array
        # In a real scenario, you'd likely want to fetch existing and append
        # For simplicity here, we'll just store the latest source.
        upsert_data["source_urls"] = json.dumps(
            [source_url]
        )  # Store as JSON array string

    try:
        response = (
            client.table(table_name)
            .upsert(
                {conflict_column: conflict_value, **upsert_data},
                on_conflict=conflict_column,
                returning="representation",  # Request the full row back
            )
            .execute()
        )

        if response.data:
            entity_id = response.data[0]["id"]
            logger.debug(
                f"Upsert successful for {table_name} '{conflict_value}'. ID: {entity_id}"
            )
            return entity_id
        else:
            logger.warning(
                f"Upsert response for {table_name} '{conflict_value}' had no data. Response: {response}. Trying fallback select."
            )
            # Fallback: try to select the ID based on the conflict column
            select_response = (
                client.table(table_name)
                .select("id")
                .eq(conflict_column, conflict_value)
                .limit(1)
                .execute()
            )
            if select_response.data:
                entity_id = select_response.data[0]["id"]
                logger.debug(
                    f"Upsert fallback select successful for {table_name} '{conflict_value}'. ID: {entity_id}"
                )
                return entity_id
            else:
                logger.error(
                    f"Could not retrieve ID after upsert for {table_name} '{conflict_value}'."
                )
                return None
    except Exception as e:
        logger.error(
            f"Error during upsert for {table_name} '{conflict_value}': {e}",
            exc_info=True,
        )
        return None


def _sync_insert(
    data: List[Dict[str, Any]],
    table_name: str,
    max_retries: int = 3,
    delay: float = 1.0,
) -> APIResponse:
    """
    Synchronous helper function to perform insert with retries, ignoring duplicates.
    Uses standard insert, assumes ON CONFLICT rules are handled by DB policy or structure if needed.
    For linking tables, PK conflict should implicitly handle duplicates.
    """
    client = get_supabase_client()
    last_exception = None

    if not data:
        logger.debug(
            f"No data provided for insert into table '{table_name}'. Skipping."
        )
        # Return an empty successful-like response structure
        return APIResponse(data=[], count=0)

    for attempt in range(max_retries):
        try:
            logger.debug(
                f"Attempt {attempt + 1}: Inserting {len(data)} records into '{table_name}'"
            )
            # Simple insert, relies on PK constraints to avoid dupes
            insert_query = client.table(table_name).insert(data, returning="minimal")
            # For linking tables, we expect PK conflicts to just fail, which is okay
            # We might get a PostgrestAPIError (e.g., code 23505 for unique violation)
            response = insert_query.execute()
            # Check for errors even if no exception was raised
            if hasattr(response, "error") and response.error:
                raise PostgrestAPIError(response.error)
            return response
        except httpx.RemoteProtocolError as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    f"Database insert attempt {attempt + 1}/{max_retries} for table '{table_name}' failed due to RemoteProtocolError: {e}. Retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(
                    f"Database insert for table '{table_name}' failed after {max_retries} attempts due to RemoteProtocolError."
                )
        except PostgrestAPIError as e:
            # Specifically ignore unique constraint violations (duplicate PK) for linking tables
            if (
                getattr(e, "code", "") == "23505"
            ):  # Standard PostgreSQL code for unique_violation
                logger.debug(
                    f"Ignoring duplicate entry during insert into linking table '{table_name}': {e.message}"
                )
                # Return an empty successful-like response structure
                return APIResponse(data=[], count=0)
            else:
                # Log other API errors and re-raise
                error_details = {
                    "code": getattr(e, "code", "N/A"),
                    "message": getattr(e, "message", "Unknown Error"),
                    "details": getattr(e, "details", "N/A"),
                    "hint": getattr(e, "hint", "N/A"),
                }
                logger.error(
                    f"Supabase API Error during insert (Table: {table_name}): {error_details}"
                )
                raise e  # Re-raise other API errors
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during the synchronous insert (Table: {table_name}): {e}",
                exc_info=True,
            )
            raise e  # Re-raise other unexpected errors
    if last_exception:
        raise last_exception
    raise Exception(
        f"Database insert failed after all retries for table '{table_name}' without a specific exception being stored."
    )
