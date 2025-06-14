"""
Enhanced event filtering for TokenHunter search functionality.
Part of Phase 2: Event Filtering

This module provides smart filtering for events based on dates, relevance,
and user preferences to improve search quality and user experience.
"""

import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple

import pytz
from dateutil import parser as date_parser
from dateutil.parser import ParserError

logger = logging.getLogger(__name__)

# Default timezone for event filtering (Token2049 Dubai)
DEFAULT_TIMEZONE = "Asia/Dubai"


class EventFilter:
    """Smart event filtering for improved search results."""

    def __init__(self, default_timezone: str = DEFAULT_TIMEZONE):
        """Initialize with default timezone."""
        self.default_timezone = pytz.timezone(default_timezone)
        self.utc = pytz.UTC

    def filter_events_by_relevance(
        self,
        events: List[Dict[str, Any]],
        include_past_events: bool = False,
        include_undated_events: bool = True,
        max_results: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Filter events based on date relevance and user preferences.

        Args:
            events: List of event dictionaries
            include_past_events: Whether to include events that have already ended
            include_undated_events: Whether to include events without dates
            max_results: Maximum number of results to return

        Returns:
            Tuple of (filtered_events, filter_stats)
        """
        logger.info(
            f"Filtering {len(events)} events (past={include_past_events}, undated={include_undated_events})"
        )

        current_time = datetime.datetime.now(self.default_timezone)

        filtered_events = []
        filter_stats = {
            "total_input": len(events),
            "past_events_filtered": 0,
            "undated_events_filtered": 0,
            "future_events": 0,
            "undated_events_kept": 0,
        }

        for event in events:
            # Analyze event date
            date_status = self._analyze_event_date(event, current_time)

            if date_status["is_past"] and not include_past_events:
                filter_stats["past_events_filtered"] += 1
                logger.debug(f"Filtered past event: {event.get('name', 'Unknown')}")
                continue

            if date_status["is_undated"] and not include_undated_events:
                filter_stats["undated_events_filtered"] += 1
                logger.debug(f"Filtered undated event: {event.get('name', 'Unknown')}")
                continue

            # Event passes filtering
            if date_status["is_past"]:
                pass  # Past event explicitly included
            elif date_status["is_undated"]:
                filter_stats["undated_events_kept"] += 1
            else:
                filter_stats["future_events"] += 1

            # Add filtering metadata to event
            event_copy = event.copy()
            event_copy["_filter_metadata"] = {
                "date_status": date_status,
                "filtered_at": current_time.isoformat(),
            }

            filtered_events.append(event_copy)

        # Apply max results limit
        if max_results and len(filtered_events) > max_results:
            filtered_events = filtered_events[:max_results]
            filter_stats["limited_to_max"] = max_results

        logger.info(
            f"Event filtering complete: {len(filtered_events)} events remain "
            f"(filtered {filter_stats['past_events_filtered']} past, "
            f"{filter_stats['undated_events_filtered']} undated)"
        )

        return filtered_events, filter_stats

    def _analyze_event_date(
        self, event: Dict[str, Any], current_time: datetime.datetime
    ) -> Dict[str, Any]:
        """
        Analyze event date to determine if it's past, future, or undated.

        Args:
            event: Event dictionary
            current_time: Current time for comparison

        Returns:
            Dictionary with date analysis results
        """
        analysis = {
            "is_past": False,
            "is_future": False,
            "is_undated": False,
            "parsed_date": None,
            "raw_date_fields": {},
            "confidence": "low",
        }

        # Extract date fields from event
        date_fields = {
            "start_time": event.get("start_time"),
            "end_time": event.get("end_time"),
            "start_time_iso": event.get("start_time_iso"),
            "end_time_iso": event.get("end_time_iso"),
            "start_date": event.get("start_date"),
            "end_date": event.get("end_date"),
        }

        analysis["raw_date_fields"] = date_fields

        # Try to parse any available date
        parsed_date = None
        date_source = None

        # Priority order for date parsing
        date_priority = [
            ("start_time_iso", date_fields.get("start_time_iso")),
            ("end_time_iso", date_fields.get("end_time_iso")),
            ("start_date", date_fields.get("start_date")),
            ("end_date", date_fields.get("end_date")),
            ("start_time", date_fields.get("start_time")),
            ("end_time", date_fields.get("end_time")),
        ]

        for field_name, field_value in date_priority:
            if field_value and field_value not in ["TBD", "N/A", "", None]:
                try:
                    if isinstance(field_value, str):
                        # Handle ISO format or other string dates
                        parsed_date = date_parser.parse(field_value)
                        if parsed_date.tzinfo is None:
                            # Assume default timezone if no timezone info
                            parsed_date = self.default_timezone.localize(parsed_date)
                        date_source = field_name
                        analysis["confidence"] = (
                            "high" if "iso" in field_name else "medium"
                        )
                        break
                    elif isinstance(field_value, datetime.datetime):
                        parsed_date = field_value
                        if parsed_date.tzinfo is None:
                            parsed_date = self.default_timezone.localize(parsed_date)
                        date_source = field_name
                        analysis["confidence"] = "high"
                        break
                except (ParserError, ValueError, TypeError) as e:
                    logger.debug(f"Could not parse {field_name}='{field_value}': {e}")
                    continue

        if parsed_date:
            analysis["parsed_date"] = parsed_date.isoformat()
            analysis["date_source"] = date_source

            # Convert current time to same timezone for comparison
            current_time_tz = current_time.astimezone(parsed_date.tzinfo)

            if parsed_date < current_time_tz:
                analysis["is_past"] = True
            else:
                analysis["is_future"] = True
        else:
            analysis["is_undated"] = True
            logger.debug(f"Event has no parseable date: {event.get('name', 'Unknown')}")

        return analysis

    def suggest_filter_preferences(
        self,
        query: str,
        past_events_available: int = 0,
        undated_events_available: int = 0,
    ) -> Dict[str, Any]:
        """
        Suggest filtering preferences based on user query context.

        Args:
            query: User search query
            past_events_available: Number of past events available
            undated_events_available: Number of undated events available

        Returns:
            Dictionary with suggested preferences and reasoning
        """
        query_lower = query.lower()

        # Default preferences (exclude past events, include undated)
        suggestions = {
            "include_past_events": False,
            "include_undated_events": True,
            "reasoning": [],
        }

        # Keywords that suggest user wants past events
        past_keywords = [
            "was",
            "were",
            "happened",
            "occurred",
            "previous",
            "last",
            "past",
            "history",
            "archive",
            "before",
            "earlier",
            "completed",
            "did",
            "had",
            "what events did",
            "what did",
            "who spoke at",
            "who was at",
        ]

        # Keywords that suggest user wants only future events
        future_keywords = [
            "upcoming",
            "future",
            "next",
            "coming",
            "will",
            "going to",
            "scheduled",
            "planned",
            "when is",
            "when will",
        ]

        # Keywords that suggest user wants all events regardless of date
        all_events_keywords = [
            "all",
            "every",
            "complete",
            "full list",
            "everything",
            "total",
        ]

        # Special case: Token2049-related queries should include past events
        # since Token2049 Dubai 2025 is a completed conference
        token2049_indicators = ["token2049", "token 2049", "dubai", "at token2049"]
        if any(indicator in query_lower for indicator in token2049_indicators):
            suggestions["include_past_events"] = True
            suggestions["reasoning"].append(
                "Query mentions Token2049 (past conference)"
            )

        # Analyze query for date preferences
        if any(keyword in query_lower for keyword in past_keywords):
            suggestions["include_past_events"] = True
            suggestions["reasoning"].append("Query suggests interest in past events")

        if any(keyword in query_lower for keyword in all_events_keywords):
            suggestions["include_past_events"] = True
            suggestions["reasoning"].append(
                "Query suggests interest in comprehensive results"
            )

        if any(keyword in query_lower for keyword in future_keywords):
            suggestions["include_past_events"] = False
            suggestions["reasoning"].append("Query specifically requests future events")

        # Adjust based on available data
        # Special case for TokenHunter: Since this is primarily a Token2049 Dubai database
        # and most events are from that conference (which is past), we should be more
        # liberal about including past events for relevant queries
        blockchain_crypto_terms = [
            "solana",
            "ethereum",
            "bitcoin",
            "defi",
            "nft",
            "crypto",
            "blockchain",
            "web3",
            "dao",
            "token",
            "coin",
            "protocol",
            "dapp",
            "smart contract",
        ]

        # If user is asking about blockchain/crypto events and most events are past,
        # they likely want to see Token2049 events (which are past)
        if (
            any(term in query_lower for term in blockchain_crypto_terms)
            and past_events_available > undated_events_available * 2
            and past_events_available >= 5
        ):  # Ensure we have meaningful past events
            if not any(
                keyword in query_lower for keyword in future_keywords
            ):  # Not asking for future
                suggestions["include_past_events"] = True
                suggestions["reasoning"].append(
                    "Crypto/blockchain query in Token2049 database context"
                )

        if undated_events_available == 0:
            suggestions["include_undated_events"] = False
            suggestions["reasoning"].append("No undated events available")

        return suggestions


def filter_events_smart(
    events: List[Dict[str, Any]],
    query: str = "",
    user_preferences: Optional[Dict[str, Any]] = None,
    max_results: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Smart event filtering that considers query context and user preferences.

    Args:
        events: List of events to filter
        query: User search query for context
        user_preferences: Optional user preferences
        max_results: Maximum number of results to return

    Returns:
        Tuple of (filtered_events, filter_info)
    """
    filter_engine = EventFilter()

    # Get smart suggestions based on query
    suggestions = filter_engine.suggest_filter_preferences(
        query,
        past_events_available=len(
            [
                e
                for e in events
                if filter_engine._analyze_event_date(
                    e, datetime.datetime.now(filter_engine.default_timezone)
                )["is_past"]
            ]
        ),
        undated_events_available=len(
            [
                e
                for e in events
                if filter_engine._analyze_event_date(
                    e, datetime.datetime.now(filter_engine.default_timezone)
                )["is_undated"]
            ]
        ),
    )

    # Apply user preferences or use smart suggestions
    preferences = user_preferences or suggestions

    # Filter events
    filtered_events, stats = filter_engine.filter_events_by_relevance(
        events,
        include_past_events=preferences.get("include_past_events", False),
        include_undated_events=preferences.get("include_undated_events", True),
        max_results=max_results,
    )

    # Combine stats and suggestions for comprehensive info
    filter_info = {
        "stats": stats,
        "suggestions_used": suggestions,
        "preferences_applied": preferences,
        "query_analyzed": query,
    }

    return filtered_events, filter_info
