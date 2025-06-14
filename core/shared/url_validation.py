#!/usr/bin/env python3
"""
Real-time URL Validation System
Prevent fake/404 events from being added to the database by validating URLs before insertion.
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import aiohttp

logger = logging.getLogger(__name__)


class URLValidator:
    """Real-time URL validation to prevent fake events from entering the database."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.fake_patterns = [
            r"^Page Not Found",
            r"^404",
            r"^Error",
            r"^Page Not Found · Luma$",  # Only exact "Page Not Found · Luma"
            r"^Not Found",
            r"^Access Denied",
            r"^Permission Denied",
        ]

        # Known fake URL patterns that should never be saved (based on cleanup results)
        # Be very conservative - only block patterns we're certain are fake
        self.fake_url_patterns = [
            r"https://lu\.ma/w/events/.*",  # Generic event pages
            r"https://lu\.ma/test-.*",  # Test URLs
            r"https://lu\.ma/demo-.*",  # Demo URLs
            r"https://lu\.ma/fake-.*",  # Obviously fake URLs
            r"https://lu\.ma/ethcc-(hackathon|developer-day|after-party|opening|closing)$",  # Known fake patterns from cleanup
            r"https://lu\.ma/ethcc-[a-z\-]+(workshop|event|session|meetup)$",  # Only specific fake suffixes
            # Remove the 8-char pattern as it catches legitimate URLs like cymcvco8
        ]

        # Cache for recent validations (avoid re-checking same URLs)
        self.validation_cache: Dict[str, Tuple[bool, datetime]] = {}
        self.cache_ttl = timedelta(hours=1)

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def is_fake_url_pattern(self, url: str) -> bool:
        """Check if URL matches known fake patterns."""
        for pattern in self.fake_url_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                logger.warning(f"🚫 URL matches fake pattern: {url}")
                return True
        return False

    def is_fake_title_pattern(self, title: str) -> bool:
        """Check if title matches fake/error patterns."""
        if not title:
            return False

        for pattern in self.fake_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                logger.warning(f"🚫 Title matches fake pattern: {title}")
                return True
        return False

    async def validate_url_exists(
        self, url: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate that URL exists and returns valid content.

        Returns:
            (is_valid, title, error_message)
        """
        if not url:
            return False, None, "Empty URL"

        # Check cache first
        if url in self.validation_cache:
            cached_result, cached_time = self.validation_cache[url]
            if datetime.now() - cached_time < self.cache_ttl:
                logger.debug(f"Using cached validation for {url}: {cached_result}")
                return (
                    cached_result,
                    None,
                    None if cached_result else "Cached as invalid",
                )

        # Check fake URL patterns
        if self.is_fake_url_pattern(url):
            self.validation_cache[url] = (False, datetime.now())
            return False, None, "Matches fake URL pattern"

        if not self.session:
            return False, None, "No HTTP session available"

        try:
            logger.info(f"🔍 Validating URL: {url}")

            async with self.session.get(url, allow_redirects=True) as response:
                status = response.status

                if status == 404:
                    logger.warning(f"🚫 URL returns 404: {url}")
                    self.validation_cache[url] = (False, datetime.now())
                    return False, None, f"HTTP {status} Not Found"

                if status >= 400:
                    logger.warning(f"🚫 URL returns error {status}: {url}")
                    self.validation_cache[url] = (False, datetime.now())
                    return False, None, f"HTTP {status} Error"

                # Get page content to check title
                try:
                    content = await response.text()
                    title = self.extract_title(content)

                    # Check if title indicates fake/error page
                    if self.is_fake_title_pattern(title):
                        logger.warning(f"🚫 URL has fake title: {url} -> {title}")
                        self.validation_cache[url] = (False, datetime.now())
                        return False, title, "Title indicates error page"

                    logger.info(f"✅ URL is valid: {url} -> {title}")
                    self.validation_cache[url] = (True, datetime.now())
                    return True, title, None

                except Exception as e:
                    logger.warning(f"⚠️ Could not read content from {url}: {str(e)}")
                    # Still consider it valid if HTTP status is OK
                    self.validation_cache[url] = (True, datetime.now())
                    return True, None, None

        except asyncio.TimeoutError:
            logger.warning(f"⏰ Timeout validating URL: {url}")
            self.validation_cache[url] = (False, datetime.now())
            return False, None, "Request timeout"

        except Exception as e:
            logger.warning(f"❌ Error validating URL {url}: {str(e)}")
            self.validation_cache[url] = (False, datetime.now())
            return False, None, f"Validation error: {str(e)}"

    def extract_title(self, html_content: str) -> Optional[str]:
        """Extract title from HTML content."""
        try:
            # Simple regex to extract title
            title_match = re.search(
                r"<title[^>]*>([^<]+)</title>", html_content, re.IGNORECASE
            )
            if title_match:
                title = title_match.group(1).strip()
                # Clean up common HTML entities
                title = (
                    title.replace("&amp;", "&")
                    .replace("&lt;", "<")
                    .replace("&gt;", ">")
                )
                return title
        except Exception as e:
            logger.debug(f"Could not extract title: {str(e)}")

        return None

    async def validate_event_data(
        self, event_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate complete event data before database insertion.

        Returns:
            (is_valid, list_of_issues)
        """
        issues = []

        # Check required fields
        url = event_data.get("luma_url") or event_data.get("url")
        name = event_data.get("name")

        if not url:
            issues.append("Missing event URL")
            return False, issues

        if not name:
            issues.append("Missing event name")

        # Validate URL
        is_valid_url, title, error = await self.validate_url_exists(url)
        if not is_valid_url:
            issues.append(f"Invalid URL: {error}")
            return False, issues

        # Check if extracted title matches fake patterns
        if title and self.is_fake_title_pattern(title):
            issues.append(f"Title indicates fake event: {title}")
            return False, issues

        # Check if event name matches fake patterns
        if name and self.is_fake_title_pattern(name):
            issues.append(f"Event name indicates fake event: {name}")
            return False, issues

        # Additional validation rules
        if name and len(name.strip()) < 3:
            issues.append("Event name too short")

        if url and not urlparse(url).netloc:
            issues.append("Malformed URL")

        return len(issues) == 0, issues


class EventValidator:
    """High-level event validation orchestrator."""

    def __init__(self):
        self.url_validator = URLValidator()

    async def validate_before_save(
        self, event_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Validate event data before saving to database.

        This is the main entry point for validation.
        """
        async with self.url_validator:
            return await self.url_validator.validate_event_data(event_data)

    async def validate_bulk_events(
        self, events_data: List[Dict[str, Any]]
    ) -> List[Tuple[bool, List[str]]]:
        """Validate multiple events efficiently."""
        async with self.url_validator:
            results = []
            for event_data in events_data:
                result = await self.url_validator.validate_event_data(event_data)
                results.append(result)
            return results


# Decorator for automatic validation
def validate_event_data(func):
    """Decorator to automatically validate event data before database operations."""

    async def wrapper(*args, **kwargs):
        # Extract event data from arguments
        event_data = None
        if args and isinstance(args[0], dict):
            event_data = args[0]
        elif "event_data" in kwargs:
            event_data = kwargs["event_data"]

        if event_data:
            validator = EventValidator()
            is_valid, issues = await validator.validate_before_save(event_data)

            if not is_valid:
                logger.warning(f"🚫 Event validation failed: {issues}")
                raise ValueError(f"Event validation failed: {', '.join(issues)}")

        return await func(*args, **kwargs)

    return wrapper


# Utility functions for easy integration
async def validate_single_event(event_data: Dict[str, Any]) -> bool:
    """
    Quick validation for a single event.
    
    Includes smart bypass logic for calendar-extracted events from trusted sources.
    """
    # Check if this event was extracted from a trusted calendar source
    extraction_source = event_data.get('extraction_source') or event_data.get('source_url')
    extraction_method = event_data.get('extraction_method', '')
    description = event_data.get('description', '')
    
    # Also check metadata fields (added for EnhancedExtractionResult objects)
    metadata = event_data.get('metadata') or {}
    if not extraction_source:
        extraction_source = metadata.get('extraction_source')
    if not extraction_method:
        extraction_method = metadata.get('extraction_method', '')
    
    # Check for calendar extraction flag in metadata
    is_calendar_extraction = metadata.get('calendar_extraction', False)
    
    # Trusted calendar sources that don't need individual URL validation
    trusted_calendar_sources = [
        'https://lu.ma/ethcc',
        'https://lu.ma/web3festival', 
        'https://ethcc.io',
        'https://lu.ma/discover',
        'https://lu.ma/events'
    ]
    
    # Check if extracted from trusted calendar source
    is_from_trusted_calendar = (
        extraction_source in trusted_calendar_sources or
        # Check description field for calendar extraction markers
        'Event from calendar' in description or
        'extracted via enhanced_fallback' in description or
        'extracted via ai_enhanced_fallback' in description or
        # Check extraction method
        'enhanced_fallback' in extraction_method or
        'calendar_extraction' in extraction_method or
        # Check metadata flag
        is_calendar_extraction
    )
    
    if is_from_trusted_calendar:
        # Still do basic validation (required fields, reasonable content)
        name = event_data.get("name", "")
        if not name or len(str(name).strip()) < 3:
            logger.warning(f"Calendar-extracted event has invalid name: '{name}'")
            return False
            
        # Check for obviously fake event names
        fake_name_patterns = [
            r"^Page Not Found",
            r"^404",
            r"^Error",
            r"^Test Event$",
            r"^Demo Event$"
        ]
        
        name_str = str(name)
        for pattern in fake_name_patterns:
            if re.search(pattern, name_str, re.IGNORECASE):
                logger.warning(f"Calendar-extracted event has fake name pattern: '{name_str}'")
                return False
        
        logger.info(f"✅ Calendar-extracted event bypassed URL validation: '{name_str}' from {extraction_source}")
        return True
    
    # For non-calendar events, use standard validation
    validator = EventValidator()
    is_valid, issues = await validator.validate_before_save(event_data)
    if not is_valid:
        logger.warning(f"Event validation failed: {issues}")
    return is_valid


async def validate_url_quick(url: str) -> bool:
    """Quick URL validation."""
    async with URLValidator() as validator:
        is_valid, _, _ = await validator.validate_url_exists(url)
        return is_valid


# Example usage
if __name__ == "__main__":

    async def test_validation():
        """Test the validation system."""

        test_events = [
            {
                "name": "EthCC Demo Day",
                "luma_url": "https://lu.ma/cymcvco8",
                "description": "Real event",
            },
            {
                "name": "Page Not Found · Luma",
                "luma_url": "https://lu.ma/fake-event-123",
                "description": "Fake event",
            },
            {
                "name": "Test Event",
                "luma_url": "https://lu.ma/ethcc-fake-event",
                "description": "Pattern-based fake",
            },
        ]

        validator = EventValidator()

        for i, event in enumerate(test_events, 1):
            print(f"\n--- Testing Event {i} ---")
            print(f"Name: {event['name']}")
            print(f"URL: {event['luma_url']}")

            is_valid, issues = await validator.validate_before_save(event)

            if is_valid:
                print("✅ Event is VALID")
            else:
                print("🚫 Event is INVALID:")
                for issue in issues:
                    print(f"  - {issue}")

    # Run test
    asyncio.run(test_validation())
