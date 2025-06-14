#!/usr/bin/env python3
"""
Enhanced Event Extraction Selectors for Steel Browser
Optimized selectors for JavaScript-heavy event platforms

ACHIEVEMENT: Building on Steel Browser infrastructure validation success
STATUS: Production selector optimization for Lu.ma, ETHGlobal, Meetup, Devcon
GOAL: Achieve 25%+ event discovery rate improvement through platform-specific selectors
"""

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class EventSelector:
    """Configuration for platform-specific event extraction"""

    platform: str
    primary_selectors: List[str]
    fallback_selectors: List[str]
    wait_conditions: List[str]
    javascript_triggers: List[str]
    data_attributes: List[str]


@dataclass
class ExtractionPattern:
    """Pattern for extracting specific event information"""

    field: str  # title, date, location, url, description
    selectors: List[str]
    regex_patterns: List[str]
    processing_function: Optional[str] = None


class EnhancedEventSelectorRegistry:
    """Registry of optimized selectors for major event platforms"""

    def __init__(self):
        self.platform_selectors = self._initialize_platform_selectors()
        self.extraction_patterns = self._initialize_extraction_patterns()

    def _initialize_platform_selectors(self) -> Dict[str, EventSelector]:
        """Initialize platform-specific selectors based on modern web patterns"""
        return {
            "lu.ma": EventSelector(
                platform="lu.ma",
                primary_selectors=[
                    "div[data-testid='event-card']",
                    ".event-item",
                    "article[class*='event']",
                    "[data-event-id]",
                    ".list-item[href*='/e/']",
                ],
                fallback_selectors=[
                    "a[href*='/e/']",
                    "div[class*='card'][class*='event']",
                    ".row .col a[href*='lu.ma']",
                    "[role='article']",
                ],
                wait_conditions=[
                    "div[data-testid='event-card']",
                    ".event-item",
                    "a[href*='/e/']",
                ],
                javascript_triggers=[
                    "window.scrollTo(0, document.body.scrollHeight);",
                    "document.querySelector('[data-testid=\"load-more\"]')?.click();",
                    "window.dispatchEvent(new Event('scroll'));",
                ],
                data_attributes=[
                    "data-testid",
                    "data-event-id",
                    "data-event-slug",
                    "href",
                ],
            ),
            "ethglobal.com": EventSelector(
                platform="ethglobal.com",
                primary_selectors=[
                    ".event-card",
                    "div[class*='EventCard']",
                    "article[class*='event']",
                    ".hackathon-card",
                    "a[href*='/events/']",
                ],
                fallback_selectors=[
                    ".card[href*='/events/']",
                    "div[class*='card'] a[href*='ethglobal']",
                    "[data-event]",
                    ".upcoming-event",
                ],
                wait_conditions=[
                    ".event-card",
                    "div[class*='EventCard']",
                    "a[href*='/events/']",
                ],
                javascript_triggers=[
                    "window.scrollTo(0, document.body.scrollHeight);",
                    "document.querySelector('.load-more')?.click();",
                    "window.dispatchEvent(new Event('load'));",
                ],
                data_attributes=["data-event", "data-event-id", "href", "class"],
            ),
            "meetup.com": EventSelector(
                platform="meetup.com",
                primary_selectors=[
                    "[data-testid='event-card']",
                    ".event-listing",
                    "article[data-event-id]",
                    ".ds-card[href*='/events/']",
                    "[data-automation-id='eventCard']",
                ],
                fallback_selectors=[
                    "a[href*='/events/']",
                    ".card-event",
                    "[role='article'][class*='event']",
                    ".list-item a[href*='meetup.com']",
                ],
                wait_conditions=[
                    "[data-testid='event-card']",
                    ".event-listing",
                    "a[href*='/events/']",
                ],
                javascript_triggers=[
                    "window.scrollTo(0, document.body.scrollHeight);",
                    "document.querySelector('[data-testid=\"load-more\"]')?.click();",
                    "setTimeout(() => window.scrollTo(0, document.body.scrollHeight), 2000);",
                ],
                data_attributes=[
                    "data-testid",
                    "data-event-id",
                    "data-automation-id",
                    "href",
                ],
            ),
            "devcon.org": EventSelector(
                platform="devcon.org",
                primary_selectors=[
                    ".event-item",
                    "article[class*='event']",
                    ".conference-event",
                    "[data-event]",
                    "a[href*='/event']",
                ],
                fallback_selectors=[
                    ".card a[href*='devcon']",
                    "div[class*='session']",
                    "[role='article']",
                    ".schedule-item",
                ],
                wait_conditions=[
                    ".event-item",
                    "article[class*='event']",
                    "a[href*='/event']",
                ],
                javascript_triggers=[
                    "window.scrollTo(0, document.body.scrollHeight);",
                    "document.querySelector('.load-more')?.click();",
                ],
                data_attributes=["data-event", "data-event-id", "href", "class"],
            ),
            "eventbrite.com": EventSelector(
                platform="eventbrite.com",
                primary_selectors=[
                    "[data-automation-id='event-card']",
                    ".event-card",
                    "article[data-event-id]",
                    ".discovery-event-card",
                    "a[href*='/e/']",
                ],
                fallback_selectors=[
                    ".card[href*='eventbrite.com']",
                    "[role='article'][class*='event']",
                    ".search-result a[href*='/e/']",
                ],
                wait_conditions=[
                    "[data-automation-id='event-card']",
                    ".event-card",
                    "a[href*='/e/']",
                ],
                javascript_triggers=[
                    "window.scrollTo(0, document.body.scrollHeight);",
                    "document.querySelector('[data-testid=\"load-more\"]')?.click();",
                    "setTimeout(() => window.scrollTo(0, document.body.scrollHeight), 3000);",
                ],
                data_attributes=[
                    "data-automation-id",
                    "data-event-id",
                    "href",
                    "data-testid",
                ],
            ),
        }

    def _initialize_extraction_patterns(self) -> Dict[str, List[ExtractionPattern]]:
        """Initialize field extraction patterns for each platform"""
        return {
            "lu.ma": [
                ExtractionPattern(
                    field="title",
                    selectors=[
                        "h3",
                        "h2",
                        ".title",
                        "[data-testid='event-title']",
                        "a .font-bold",
                    ],
                    regex_patterns=[r"^([^|]+)", r"(.{5,100})"],
                ),
                ExtractionPattern(
                    field="date",
                    selectors=[
                        ".date",
                        ".time",
                        "[data-testid='event-date']",
                        ".text-sm",
                        "time",
                    ],
                    regex_patterns=[
                        r"(\d{1,2}/\d{1,2}/\d{4})",
                        r"(\w+ \d{1,2}, \d{4})",
                        r"(\d{4}-\d{2}-\d{2})",
                    ],
                ),
                ExtractionPattern(
                    field="location",
                    selectors=[
                        ".location",
                        ".venue",
                        "[data-testid='event-location']",
                        ".text-gray",
                    ],
                    regex_patterns=[
                        r"(.{3,50}(?:Street|Ave|Blvd|Road|Plaza|Center))",
                        r"([^,]{3,30}, [A-Z]{2})",
                    ],
                ),
                ExtractionPattern(
                    field="url",
                    selectors=["a[href*='/e/']", "a[href*='lu.ma']"],
                    regex_patterns=[r"(https?://lu\.ma/e/[^?\s]+)", r"(/e/[^?\s]+)"],
                ),
            ],
            "ethglobal.com": [
                ExtractionPattern(
                    field="title",
                    selectors=[
                        "h2",
                        "h3",
                        ".title",
                        ".event-title",
                        "a[class*='title']",
                    ],
                    regex_patterns=[r"^([^|]+)", r"(.{5,100})"],
                ),
                ExtractionPattern(
                    field="date",
                    selectors=[".date", "time", ".event-date", "[class*='date']"],
                    regex_patterns=[
                        r"(\w+ \d{1,2}(?:st|nd|rd|th)?, \d{4})",
                        r"(\d{4}-\d{2}-\d{2})",
                    ],
                ),
                ExtractionPattern(
                    field="location",
                    selectors=[".location", ".venue", "[class*='location']"],
                    regex_patterns=[
                        r"([^,]{3,30}, [A-Z]{2,3})",
                        r"(Virtual|Online|Remote)",
                    ],
                ),
                ExtractionPattern(
                    field="url",
                    selectors=["a[href*='/events/']", "a[href*='ethglobal']"],
                    regex_patterns=[
                        r"(https?://ethglobal\.com/events/[^?\s]+)",
                        r"(/events/[^?\s]+)",
                    ],
                ),
            ],
            "meetup.com": [
                ExtractionPattern(
                    field="title",
                    selectors=[
                        "h3",
                        "h2",
                        "[data-testid='event-title']",
                        ".event-title",
                    ],
                    regex_patterns=[r"^([^|]+)", r"(.{5,100})"],
                ),
                ExtractionPattern(
                    field="date",
                    selectors=[
                        "time",
                        ".date",
                        "[data-testid='event-date']",
                        "[class*='date']",
                    ],
                    regex_patterns=[
                        r"(\w{3}, \w{3} \d{1,2})",
                        r"(\d{1,2}/\d{1,2}/\d{4})",
                    ],
                ),
                ExtractionPattern(
                    field="location",
                    selectors=[
                        ".location",
                        "[data-testid='event-location']",
                        "[class*='venue']",
                    ],
                    regex_patterns=[r"([^,]{3,30}, [A-Z]{2})", r"(Online event)"],
                ),
                ExtractionPattern(
                    field="url",
                    selectors=["a[href*='/events/']", "a[href*='meetup.com']"],
                    regex_patterns=[
                        r"(https?://www\.meetup\.com/[^/]+/events/[^?\s]+)",
                        r"(/events/[^?\s]+)",
                    ],
                ),
            ],
        }

    def get_platform_selector(self, url: str) -> Optional[EventSelector]:
        """Get platform-specific selector configuration for a URL"""
        for platform_key, selector in self.platform_selectors.items():
            if platform_key in url.lower():
                return selector
        return None

    def get_extraction_patterns(self, url: str) -> List[ExtractionPattern]:
        """Get extraction patterns for a specific platform"""
        for platform_key, patterns in self.extraction_patterns.items():
            if platform_key in url.lower():
                return patterns
        return []

    def generate_steel_browser_script(self, url: str) -> Dict[str, Any]:
        """Generate Steel Browser script configuration for enhanced extraction"""
        selector = self.get_platform_selector(url)
        patterns = self.get_extraction_patterns(url)

        if not selector:
            return self._get_generic_script()

        return {
            "platform": selector.platform,
            "extraction_strategy": {
                "wait_for_elements": selector.wait_conditions,
                "javascript_execution": selector.javascript_triggers,
                "primary_selectors": selector.primary_selectors,
                "fallback_selectors": selector.fallback_selectors,
                "data_attributes": selector.data_attributes,
            },
            "field_extraction": {
                pattern.field: {
                    "selectors": pattern.selectors,
                    "regex_patterns": pattern.regex_patterns,
                    "processing": pattern.processing_function,
                }
                for pattern in patterns
            },
            "optimization_settings": {
                "scroll_behavior": "smooth",
                "wait_timeout": 10000,
                "load_timeout": 30000,
                "retry_attempts": 3,
                "dynamic_content_detection": True,
            },
        }

    def _get_generic_script(self) -> Dict[str, Any]:
        """Generic extraction script for unknown platforms"""
        return {
            "platform": "generic",
            "extraction_strategy": {
                "wait_for_elements": ["article", ".event", ".card", "[data-event]"],
                "javascript_execution": [
                    "window.scrollTo(0, document.body.scrollHeight);"
                ],
                "primary_selectors": [
                    ".event",
                    ".event-card",
                    "article",
                    "[data-event]",
                    "a[href*='event']",
                ],
                "fallback_selectors": [".card", ".item", "[role='article']"],
                "data_attributes": ["href", "data-event", "class"],
            },
            "optimization_settings": {
                "scroll_behavior": "smooth",
                "wait_timeout": 8000,
                "load_timeout": 20000,
                "retry_attempts": 2,
                "dynamic_content_detection": True,
            },
        }


def generate_enhanced_selectors_config() -> Dict[str, Any]:
    """Generate complete enhanced selectors configuration for Steel Browser deployment"""
    registry = EnhancedEventSelectorRegistry()

    test_urls = [
        "https://lu.ma/crypto",
        "https://ethglobal.com/events",
        "https://www.meetup.com/blockchain-developers-united/",
        "https://devcon.org/en/",
        "https://www.eventbrite.com/d/ca--san-francisco/blockchain/",
    ]

    config = {
        "enhanced_selectors_version": "1.0.0",
        "generation_timestamp": datetime.now().isoformat(),
        "platform_configurations": {},
        "deployment_instructions": {
            "steel_browser_integration": "Deploy via MCP Steel Browser tools",
            "testing_urls": test_urls,
            "expected_improvement": "25%+ event discovery rate increase",
            "performance_target": "<10s per URL with enhanced selectors",
        },
    }

    for url in test_urls:
        platform_name = next(
            (key for key in registry.platform_selectors.keys() if key in url), "generic"
        )
        config["platform_configurations"][url] = registry.generate_steel_browser_script(
            url
        )

    return config


if __name__ == "__main__":
    # Generate enhanced selectors configuration
    config = generate_enhanced_selectors_config()

    # Save configuration for deployment
    with open("enhanced_selectors_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("🎯 ENHANCED EVENT SELECTORS GENERATED")
    print("=" * 50)
    print(f"Platforms configured: {len(config['platform_configurations'])}")
    print("Configuration file: enhanced_selectors_config.json")
    print("Target improvement: 25%+ event discovery rate")
    print()

    for url, platform_config in config["platform_configurations"].items():
        print(f"✅ {platform_config['platform']}: {url}")
        print(
            f"   - Primary selectors: {len(platform_config['extraction_strategy']['primary_selectors'])}"
        )
        print(
            f"   - Fallback selectors: {len(platform_config['extraction_strategy']['fallback_selectors'])}"
        )
        print(
            f"   - JS triggers: {len(platform_config['extraction_strategy']['javascript_execution'])}"
        )
        print()
