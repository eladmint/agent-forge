"""
Social media link extraction and processing functionality.
"""

import json
import logging
import re
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Regular expressions for social media URLs
SOCIAL_MEDIA_PATTERNS = {
    "twitter": re.compile(r"https?://(?:www\.)?(?:twitter\.com|x\.com)/[\w\d_-]+"),
    "facebook": re.compile(r"https?://(?:www\.)?facebook\.com/[\w\d./_-]+"),
    "linkedin": re.compile(
        r"https?://(?:www\.)?linkedin\.com/(?:company|in|profile)/[\w\d\-_%/]+"
    ),
    "instagram": re.compile(r"https?://(?:www\.)?instagram\.com/[\w\d._-]+"),
    "discord": re.compile(r"https?://(?:www\.)?discord(?:\.gg|app\.com)/[\w\d/]+"),
    "telegram": re.compile(r"https?://(?:www\.)?t\.me/[\w\d/]+"),
    "youtube": re.compile(
        r"https?://(?:www\.)?youtube\.com/(?:user|channel|c)/[\w\d-]+"
    ),
    "github": re.compile(r"https?://(?:www\.)?github\.com/[\w\d-]+"),
}

# Simplified patterns to catch domains without full URLs
DOMAIN_PATTERNS = {
    "facebook": re.compile(r"facebook\.com/[\w\d./_-]+"),
    "linkedin": re.compile(r"linkedin\.com/(?:company|in|profile)/[\w\d\-_%/]+"),
    "twitter": re.compile(r"(?:twitter\.com|x\.com)/[\w\d_-]+"),
    "instagram": re.compile(r"instagram\.com/[\w\d._-]+"),
    "discord": re.compile(r"discord(?:\.gg|app\.com)/[\w\d/]+"),
    "telegram": re.compile(r"t\.me/[\w\d/]+"),
}


def extract_social_links(event_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract social media links from event data.

    Prioritizes links in this order:
    1. Links in raw_scraped_data.social_links object (highest priority)
    2. Links in specific URL fields (e.g., twitter_url)
    3. Links found in text fields like description (lowest priority)

    Args:
        event_data: Dictionary containing event data

    Returns:
        Dictionary mapping social media platforms to their URLs
    """
    result = {}

    # Extract links from text fields (lowest priority)
    text_fields = ["description", "about", "details", "summary"]
    for field in text_fields:
        if field in event_data and event_data[field]:
            text = str(event_data[field])
            for platform, pattern in SOCIAL_MEDIA_PATTERNS.items():
                if platform not in result:  # Only add if not already found
                    match = pattern.search(text)
                    if match:
                        result[platform] = match.group(0)

    # Extract links from specific URL fields (medium priority)
    if "twitter_url" in event_data and event_data["twitter_url"]:
        result["twitter"] = event_data["twitter_url"]

    if "facebook_url" in event_data and event_data["facebook_url"]:
        result["facebook"] = event_data["facebook_url"]

    if "linkedin_url" in event_data and event_data["linkedin_url"]:
        result["linkedin"] = event_data["linkedin_url"]

    if "instagram_url" in event_data and event_data["instagram_url"]:
        result["instagram"] = event_data["instagram_url"]

    # Extract links from raw_scraped_data.social_links (highest priority)
    if "raw_scraped_data" in event_data and event_data["raw_scraped_data"]:
        try:
            raw_data = event_data["raw_scraped_data"]
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data)

            if isinstance(raw_data, dict) and "social_links" in raw_data:
                social_links = raw_data["social_links"]
                if isinstance(social_links, dict):
                    # Update with the highest priority links
                    result.update(social_links)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error parsing raw_scraped_data for social links: {e}")

    return result
