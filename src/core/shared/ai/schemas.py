"""
Data schemas and validation models for Agent Forge AI operations.

This module contains structured data schemas used by AI processing functions,
particularly for event data extraction and validation.
"""

from typing import Any, Dict, List

# Event data extraction schema for AI processing
event_data_schema = {
    "event_name": "Name of the event",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD (if different from start_date, otherwise same)",
    "start_time": "HH:MM (24-hour format, e.g., 14:30)",
    "end_time": "HH:MM (24-hour format)",
    "timezone": "Timezone abbreviation or offset (e.g., GST, UTC+4)",
    "location_name": "Name of the venue or 'Online'",
    "location_address": "Full street address (or N/A if online/not specified)",
    "organizer_name": "Name of the primary organizer/host",
    "event_category": "Relevant category (e.g., Networking, Workshop, Party, Conference, Demo Day, Pitch)",
    "description_summary": "A brief 1-2 sentence summary of the event's purpose.",
    "cost_usd": "Ticket price in USD (numeric value, 0 if free, -1 if unknown/not specified)",
    "website": "Official event website or registration link (if different from the source URL)",
    "social_links": {
        "twitter": "Twitter URL for the event (e.g., https://twitter.com/token2049)",
        "linkedin": "LinkedIn URL for the event",
        "facebook": "Facebook URL for the event",
        "instagram": "Instagram URL for the event",
        "discord": "Discord URL for the event",
        "telegram": "Telegram URL for the event",
    },
    "speakers": [
        {
            "name": "Speaker's Full Name",
            "organization": "Speaker's Affiliated Organization (or N/A)",
            "title": "Speaker's Title (or N/A)",
            "url": "URL associated with speaker (e.g., profile, company) or null",
        }
    ],
    "sponsors_partners": [
        {
            "name": "Organization/Company Name (exact name, no surrounding text)",
            "url": "URL associated with the sponsor/partner or null",
        }
    ],
}


# Speaker schema for validation
speaker_schema = {
    "name": "str",
    "organization": "str",
    "title": "str",
    "url": "str or null",
}


# Social links schema
social_links_schema = {
    "twitter": "str or null",
    "linkedin": "str or null",
    "facebook": "str or null",
    "instagram": "str or null",
    "discord": "str or null",
    "telegram": "str or null",
}


# Sponsor/Partner schema
sponsor_schema = {
    "name": "str",
    "url": "str or null",
}


def validate_event_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate event data against the expected schema.

    Args:
        data: Event data dictionary to validate

    Returns:
        List[str]: List of validation errors, empty if valid
    """
    errors = []

    # Required fields
    required_fields = ["event_name"]
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")

    # Date format validation
    date_fields = ["start_date", "end_date"]
    for field in date_fields:
        if field in data and data[field] and data[field] != "null":
            date_str = data[field]
            if not _validate_date_format(date_str):
                errors.append(
                    f"Invalid date format for {field}: {date_str} (expected YYYY-MM-DD)"
                )

    # Time format validation
    time_fields = ["start_time", "end_time"]
    for field in time_fields:
        if field in data and data[field] and data[field] != "null":
            time_str = data[field]
            if not _validate_time_format(time_str):
                errors.append(
                    f"Invalid time format for {field}: {time_str} (expected HH:MM)"
                )

    # Speakers validation
    if "speakers" in data and isinstance(data["speakers"], list):
        for i, speaker in enumerate(data["speakers"]):
            speaker_errors = _validate_speaker(speaker, i)
            errors.extend(speaker_errors)

    # Social links validation
    if "social_links" in data and isinstance(data["social_links"], dict):
        social_errors = _validate_social_links(data["social_links"])
        errors.extend(social_errors)

    return errors


def _validate_date_format(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD."""
    try:
        parts = date_str.split("-")
        if len(parts) != 3:
            return False
        year, month, day = parts
        return (
            len(year) == 4
            and year.isdigit()
            and len(month) == 2
            and month.isdigit()
            and 1 <= int(month) <= 12
            and len(day) == 2
            and day.isdigit()
            and 1 <= int(day) <= 31
        )
    except:
        return False


def _validate_time_format(time_str: str) -> bool:
    """Validate time format HH:MM."""
    try:
        parts = time_str.split(":")
        if len(parts) != 2:
            return False
        hour, minute = parts
        return (
            len(hour) == 2
            and hour.isdigit()
            and 0 <= int(hour) <= 23
            and len(minute) == 2
            and minute.isdigit()
            and 0 <= int(minute) <= 59
        )
    except:
        return False


def _validate_speaker(speaker: Dict[str, Any], index: int) -> List[str]:
    """Validate individual speaker data."""
    errors = []

    if not isinstance(speaker, dict):
        errors.append(f"Speaker {index}: must be a dictionary")
        return errors

    # Name is required
    if "name" not in speaker or not speaker["name"]:
        errors.append(f"Speaker {index}: missing required field 'name'")

    # Optional fields should be strings or null
    optional_fields = ["organization", "title", "url"]
    for field in optional_fields:
        if field in speaker and speaker[field] is not None:
            if not isinstance(speaker[field], str):
                errors.append(f"Speaker {index}: {field} must be string or null")

    return errors


def _validate_social_links(social_links: Dict[str, Any]) -> List[str]:
    """Validate social links data."""
    errors = []

    valid_platforms = [
        "twitter",
        "linkedin",
        "facebook",
        "instagram",
        "discord",
        "telegram",
    ]

    for platform, url in social_links.items():
        if platform not in valid_platforms:
            errors.append(f"Unknown social platform: {platform}")

        if url is not None and not isinstance(url, str):
            errors.append(f"Social link {platform}: must be string or null")

        if isinstance(url, str) and not url.startswith("http"):
            errors.append(
                f"Social link {platform}: must be valid URL starting with http"
            )

    return errors


def get_empty_event_data() -> Dict[str, Any]:
    """
    Get an empty event data structure with default values.

    Returns:
        Dict[str, Any]: Empty event data with proper structure
    """
    return {
        "event_name": None,
        "start_date": None,
        "end_date": None,
        "start_time": None,
        "end_time": None,
        "timezone": None,
        "location_name": None,
        "location_address": None,
        "organizer_name": None,
        "event_category": None,
        "description_summary": None,
        "cost_usd": -1,
        "website": None,
        "social_links": {},
        "speakers": [],
        "sponsors_partners": [],
    }


def normalize_event_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize event data by ensuring proper types and handling special values.

    Args:
        data: Raw event data

    Returns:
        Dict[str, Any]: Normalized event data
    """
    normalized = get_empty_event_data()

    # Update with provided data
    for key, value in data.items():
        if key in normalized:
            # Handle string "null" values
            if value == "null" or value == "N/A":
                normalized[key] = None
            else:
                normalized[key] = value

    # Ensure speakers and sponsors_partners are lists
    if not isinstance(normalized["speakers"], list):
        normalized["speakers"] = []

    if not isinstance(normalized["sponsors_partners"], list):
        normalized["sponsors_partners"] = []

    if not isinstance(normalized["social_links"], dict):
        normalized["social_links"] = {}

    return normalized
