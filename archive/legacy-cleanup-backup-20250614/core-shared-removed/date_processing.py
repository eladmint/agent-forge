"""
Enhanced date processing and parsing for TokenHunter search functionality.
Part of Phase 2: Functional Enhancements
"""

import datetime
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import pytz
from dateutil import parser as date_parser
from dateutil.parser import ParserError

logger = logging.getLogger(__name__)

# Common timezone for events (Token2049 Dubai)
DEFAULT_TIMEZONE = "Asia/Dubai"
UTC_TIMEZONE = pytz.UTC


class EnhancedDateProcessor:
    """Enhanced date processing for natural language date queries."""

    def __init__(self, default_timezone: str = DEFAULT_TIMEZONE):
        """Initialize with default timezone."""
        self.default_timezone = pytz.timezone(default_timezone)
        self.utc = UTC_TIMEZONE

        # Relative date patterns
        self.relative_patterns = {
            "today": lambda: datetime.date.today(),
            "tomorrow": lambda: datetime.date.today() + datetime.timedelta(days=1),
            "yesterday": lambda: datetime.date.today() - datetime.timedelta(days=1),
            "next week": lambda: datetime.date.today() + datetime.timedelta(days=7),
            "last week": lambda: datetime.date.today() - datetime.timedelta(days=7),
            "next monday": lambda: self._get_next_weekday(0),
            "next tuesday": lambda: self._get_next_weekday(1),
            "next wednesday": lambda: self._get_next_weekday(2),
            "next thursday": lambda: self._get_next_weekday(3),
            "next friday": lambda: self._get_next_weekday(4),
            "next saturday": lambda: self._get_next_weekday(5),
            "next sunday": lambda: self._get_next_weekday(6),
        }

    def _get_next_weekday(self, target_weekday: int) -> datetime.date:
        """Get the next occurrence of a specific weekday."""
        today = datetime.date.today()
        days_ahead = target_weekday - today.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return today + datetime.timedelta(days=days_ahead)

    def parse_date_query(self, date_str: str) -> Optional[Tuple[datetime.date, str]]:
        """
        Parse a date query string into a date object and confidence level.

        Args:
            date_str: Natural language date string

        Returns:
            Tuple of (parsed_date, confidence_level) or None if parsing fails
            Confidence levels: 'high', 'medium', 'low'
        """
        if not date_str or not isinstance(date_str, str):
            return None

        date_str_clean = date_str.strip().lower()

        # Check for relative date patterns first
        for pattern, func in self.relative_patterns.items():
            if pattern in date_str_clean:
                try:
                    result_date = func()
                    logger.info(f"Parsed relative date '{date_str}' -> {result_date}")
                    return result_date, "high"
                except Exception as e:
                    logger.warning(f"Error parsing relative date '{date_str}': {e}")
                    continue

        # Try fuzzy date parsing with dateutil
        try:
            # Add current year if not specified
            current_year = datetime.date.today().year

            # Handle ordinal numbers (1st, 2nd, 3rd, etc.)
            ordinal_pattern = r"\b(\d{1,2})(st|nd|rd|th)\b"
            date_str_clean = re.sub(ordinal_pattern, r"\1", date_str_clean)

            # Parse with fuzzy matching
            parsed_dt = date_parser.parse(date_str_clean, fuzzy=True)
            parsed_date = parsed_dt.date()

            # If year is missing, try to infer the most logical year
            if (
                parsed_dt.year == current_year
                and "year" not in date_str_clean
                and str(current_year) not in date_str
            ):
                # Check if the date already passed this year, if so, assume next year
                if parsed_date < datetime.date.today():
                    parsed_date = parsed_date.replace(year=current_year + 1)
                    confidence = "medium"
                else:
                    confidence = "high"
            else:
                confidence = "high"

            logger.info(
                f"Parsed date '{date_str}' -> {parsed_date} (confidence: {confidence})"
            )
            return parsed_date, confidence

        except ParserError as e:
            logger.warning(f"Could not parse date string '{date_str}': {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error parsing date '{date_str}': {e}")
            return None

    def get_date_range_utc(
        self, target_date: datetime.date
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        """
        Convert a date to UTC datetime range for database queries.

        Args:
            target_date: The target date

        Returns:
            Tuple of (start_datetime_utc, end_datetime_utc)
        """
        # Create datetime range in the event timezone
        start_datetime_local = datetime.datetime.combine(
            target_date, datetime.time.min, tzinfo=self.default_timezone
        )
        end_datetime_local = datetime.datetime.combine(
            target_date, datetime.time.max, tzinfo=self.default_timezone
        )

        # Convert to UTC for database queries
        start_datetime_utc = start_datetime_local.astimezone(self.utc)
        end_datetime_utc = end_datetime_local.astimezone(self.utc)

        return start_datetime_utc, end_datetime_utc

    def format_date_for_user(
        self, target_date: datetime.date, confidence: str = "high"
    ) -> str:
        """
        Format a date for user-friendly display.

        Args:
            target_date: The date to format
            confidence: Confidence level of the parsing

        Returns:
            Formatted date string
        """
        # Get day of week
        day_name = target_date.strftime("%A")

        # Format with ordinal day
        day = target_date.day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]

        formatted = f"{day_name}, {target_date.strftime('%B')} {day}{suffix}, {target_date.year}"

        if confidence != "high":
            formatted += " (interpreted)"

        return formatted

    def suggest_date_corrections(self, date_str: str) -> List[str]:
        """
        Suggest possible date corrections for unparseable strings.

        Args:
            date_str: The unparseable date string

        Returns:
            List of suggested date formats
        """
        suggestions = []

        # Common format suggestions
        suggestions.extend(
            [
                "Try formats like: 'April 25', 'Apr 25, 2025', '2025-04-25'",
                "Relative dates: 'today', 'tomorrow', 'next Monday'",
                "Date ranges: 'this weekend', 'next week'",
            ]
        )

        # If it contains numbers, suggest ISO format
        if re.search(r"\d", date_str):
            suggestions.append(
                "For specific dates, use ISO format: YYYY-MM-DD (e.g., '2025-04-25')"
            )

        return suggestions


def enhanced_get_events_by_date(
    client,
    date_str: str,
    timezone_str: str = DEFAULT_TIMEZONE,
    include_suggestions: bool = True,
) -> Dict[str, Any]:
    """
    Enhanced date-based event search with natural language processing.

    Args:
        client: Supabase client
        date_str: Natural language date string
        timezone_str: Timezone for the query
        include_suggestions: Whether to include suggestions for failed queries

    Returns:
        Dictionary with events, metadata, and suggestions
    """
    processor = EnhancedDateProcessor(timezone_str)

    # Parse the date query
    parse_result = processor.parse_date_query(date_str)

    if not parse_result:
        result = {
            "success": False,
            "message": f"Could not understand the date '{date_str}'.",
            "events": [],
            "metadata": {
                "original_query": date_str,
                "parsed_date": None,
                "confidence": None,
            },
        }

        if include_suggestions:
            suggestions = processor.suggest_date_corrections(date_str)
            result["suggestions"] = suggestions

        return result

    target_date, confidence = parse_result
    start_utc, end_utc = processor.get_date_range_utc(target_date)

    logger.info(
        f"Searching for events on {target_date} (UTC range: {start_utc} to {end_utc})"
    )

    try:
        # Query the database
        response = (
            client.table("events")
            .select("id, name, description, start_time_iso, luma_url")
            .gte("start_time_iso", start_utc.isoformat())
            .lte("start_time_iso", end_utc.isoformat())
            .order("start_time_iso", desc=False)
            .execute()
        )

        events = response.data if response.data else []

        # Format date for user display
        formatted_date = processor.format_date_for_user(target_date, confidence)

        result = {
            "success": True,
            "events": events,
            "metadata": {
                "original_query": date_str,
                "parsed_date": target_date.isoformat(),
                "formatted_date": formatted_date,
                "confidence": confidence,
                "event_count": len(events),
                "timezone": timezone_str,
            },
        }

        if events:
            result["message"] = f"Found {len(events)} event(s) for {formatted_date}"
        else:
            result["message"] = f"No events found for {formatted_date}"

            if include_suggestions and confidence != "high":
                result["suggestions"] = [
                    "Try a different date format or check nearby dates",
                    "Use 'tomorrow', 'next week', or specific dates like 'April 25'",
                ]

        logger.info(
            f"Enhanced date search: '{date_str}' -> {len(events)} events for {target_date}"
        )
        return result

    except Exception as e:
        logger.error(
            f"Database error during enhanced date search for '{date_str}': {e}",
            exc_info=True,
        )
        return {
            "success": False,
            "message": f"An error occurred while searching for events on '{date_str}'.",
            "events": [],
            "metadata": {
                "original_query": date_str,
                "parsed_date": target_date.isoformat() if target_date else None,
                "confidence": confidence if target_date else None,
                "error": str(e),
            },
        }
