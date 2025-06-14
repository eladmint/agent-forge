"""
Link Finder Agent - Event Discovery Component

🎯 PART OF MAIN EXTRACTOR SYSTEM
This agent is a specialized component of the comprehensive 13+ agent extraction framework.
Main orchestrator: /main_extractor.py (previously enhanced_orchestrator.py)

This agent discovers event URLs from calendar pages using intelligent scrolling and dynamic content loading.
It works as part of the main extraction workflow to find all events before detailed processing.

The main extractor coordinates this agent along with 12+ other specialized agents
for comprehensive crypto conference event extraction with database integration.
"""

# from swarms import Agent  # REMOVED - Framework migration complete
import logging
import os
from logging import Logger
from typing import Dict, List, Optional
from urllib.parse import urljoin

# Import Playwright
from playwright.async_api import async_playwright

# Import anti-bot evasion manager
from extraction.utils.anti_bot_evasion_manager import (
    AntiBotEvasionManager,
    EvasionLevel,
)

# Define output dir for potential debug files
OUTPUT_DIR = "results"


class LinkFinderAgent:
    """Framework-free agent that finds all relevant event links from a main listing page using Playwright.

    Enhanced with comprehensive anti-bot evasion capabilities targeting 90%+ success rate.
    Critical for calendar discovery - handles Cloudflare challenges and anti-bot detection.
    """

    def __init__(
        self,
        name: str = "LinkFinderAgent",
        logger: Optional[Logger] = None,
        evasion_level: EvasionLevel = EvasionLevel.ADVANCED,  # Use advanced level for calendar pages
    ):
        """Initialize the LinkFinderAgent.

        Args:
            name: Name of the agent.
            logger: Optional logger instance. If None, a default logger is created.
            evasion_level: Level of anti-bot evasion to apply (defaults to ADVANCED for calendar pages).
        """
        self.name = name
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
        self.logger.info(
            "[%s] initialized framework-free agent with anti-bot evasion", self.name
        )

        # Initialize anti-bot evasion manager with advanced settings for calendar pages
        self.evasion_manager = AntiBotEvasionManager(
            evasion_level=evasion_level, logger=self.logger
        )

        # Ensure results directory exists for potential debug output
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    async def run_async(self, main_list_url: str) -> List[Dict[str, str]]:
        """
        Uses Playwright to dynamically load and extract event links from a listing page.

        Args:
            main_list_url (str): The URL of the main event listing page.

        Returns:
            list: A list of dictionaries, each containing 'name' and 'url' of an event.
                  Returns an empty list if scraping fails.
        """
        self.logger.info(
            f"[{self.name}] Attempting to fetch event list from {main_list_url} with Playwright..."
        )  # Use self.logger
        event_list = []
        processed_urls = set()  # Keep track of processed URLs
        browser = None
        page = None
        # Reverted selector back to original based on direct inspection
        event_link_selector = "a.event-link.content-link"

        # --- Nested helper function from original code ---
        async def extract_links_from_page(current_page):
            nonlocal event_list, processed_urls  # Allow modification of outer scope vars
            new_events_found_this_pass = 0
            link_elements = await current_page.query_selector_all(event_link_selector)
            for i, link_element in enumerate(link_elements):
                event_name = ""
                event_url = ""
                relative_url = ""
                try:
                    relative_url = await link_element.get_attribute("href")
                    # Handle relative paths (like /b5jaizb6) correctly
                    if (
                        relative_url
                        and not relative_url.startswith("http")
                        and relative_url.startswith("/")
                    ):
                        temp_url = (
                            urljoin(main_list_url, relative_url)
                            .split("?")[0]
                            .split("#")[0]
                        )
                        # Validate it's a Luma URL and not the base URL itself
                        if (
                            temp_url.startswith("https://lu.ma/")
                            and temp_url != main_list_url
                        ):
                            event_url = temp_url
                        else:
                            self.logger.debug(
                                f"Skipping joined URL (not lu.ma or is base URL): {temp_url}"
                            )  # Use self.logger
                            continue
                    else:
                        self.logger.debug(
                            f"Skipping URL (not a valid relative path starting with '/'): {relative_url}"
                        )  # Use self.logger
                        continue

                    # Enhanced event name extraction with multiple fallbacks
                    event_name = None

                    # Method A: Get event name from aria-label (most reliable for Luma)
                    event_name_raw = await link_element.get_attribute("aria-label")
                    if event_name_raw and event_name_raw.strip():
                        event_name = event_name_raw.strip()

                        # Clean up cover image labels
                        if (
                            "Cover Image for" in event_name
                            and len(event_name.split()) > 4
                        ):
                            event_name = event_name.replace(
                                "Cover Image for", ""
                            ).strip()

                    # Method B: Get text content if aria-label is generic or missing
                    if (
                        not event_name
                        or event_name.startswith("Unknown")
                        or len(event_name) < 5
                    ):
                        text_content = await link_element.text_content()
                        if (
                            text_content
                            and text_content.strip()
                            and len(text_content.strip()) > 5
                        ):
                            event_name = text_content.strip()

                    # Method C: Try title attribute
                    if (
                        not event_name
                        or event_name.startswith("Unknown")
                        or len(event_name) < 5
                    ):
                        title_attr = await link_element.get_attribute("title")
                        if title_attr and title_attr.strip():
                            event_name = title_attr.strip()

                    # Method D: Look for nearby text elements (headings, labels)
                    if (
                        not event_name
                        or event_name.startswith("Unknown")
                        or len(event_name) < 5
                    ):
                        try:
                            # Look for heading elements near the link
                            parent = await link_element.query_selector("..")
                            if parent:
                                heading = await parent.query_selector(
                                    "h1, h2, h3, h4, h5, h6"
                                )
                                if heading:
                                    heading_text = await heading.text_content()
                                    if heading_text and len(heading_text.strip()) > 5:
                                        event_name = heading_text.strip()
                        except:
                            pass  # Ignore errors in complex DOM navigation

                    # Final fallback with context-aware naming
                    if (
                        not event_name
                        or event_name.startswith("Unknown")
                        or len(event_name) < 5
                    ):
                        path_id = event_url.split("/")[-1]
                        if "ethcc" in main_list_url.lower():
                            event_name = f"EthCC Event {path_id}"
                        elif "devcon" in main_list_url.lower():
                            event_name = f"Devcon Event {path_id}"
                        elif "consensus" in main_list_url.lower():
                            event_name = f"Consensus Event {path_id}"
                        elif "token" in main_list_url.lower():
                            event_name = f"Token Event {path_id}"
                        else:
                            event_name = f"Crypto Event {path_id}"

                    if event_url and event_name and event_url not in processed_urls:
                        self.logger.debug(
                            f"Found event: Name='{event_name}', URL='{event_url}'"
                        )  # Use self.logger
                        event_list.append({"name": event_name, "url": event_url})
                        processed_urls.add(event_url)
                        new_events_found_this_pass += 1
                    elif not event_url:
                        self.logger.debug(
                            f"Skipping due to invalid/empty event URL derived from relative path: {relative_url}"
                        )  # Use self.logger
                    elif not event_name:
                        self.logger.debug(
                            f"Skipping due to invalid/empty event name for URL: {event_url}"
                        )  # Use self.logger

                except Exception as e:
                    # Log the specific URL being processed if available
                    url_in_error = (
                        event_url
                        if event_url
                        else (relative_url if relative_url else "unknown_href")
                    )
                    self.logger.error(
                        f"    [{self.name}] Error processing a link element (href: {url_in_error}): {e}"
                    )  # Use self.logger
            return new_events_found_this_pass

        # --- End nested helper function ---

        try:
            async with async_playwright() as p:
                self.logger.debug(
                    f"[{self.name}] Launching browser with anti-bot evasion..."
                )

                # Get anti-bot configuration for calendar page
                evasion_config = await self.evasion_manager.get_evasion_config(
                    main_list_url
                )

                # Launch browser with anti-bot settings
                browser = await p.chromium.launch(**evasion_config.browser_args)

                # Create context with enhanced anti-bot settings
                context = await browser.new_context(**evasion_config.context_args)
                page = await context.new_page()

                # Apply additional anti-bot measures for calendar discovery
                await self.evasion_manager.apply_page_evasion(page, evasion_config)

                self.logger.debug(
                    f"[{self.name}] Navigating to {main_list_url} with evasion profile: {evasion_config.profile_name}..."
                )  # Use self.logger

                # Navigate and check for rate limiting
                response = await page.goto(
                    main_list_url, wait_until="domcontentloaded", timeout=90000
                )

                # Check for rate limiting (HTTP 429 or Cloudflare blocks)
                if response and response.status == 429:
                    self.logger.error(
                        f"[{self.name}] ❌ RATE LIMITED: Luma returned HTTP 429 (Too Many Requests)"
                    )
                    self.logger.error(
                        f"[{self.name}] 🚫 EXTRACTION STOPPED: Rate limiting detected. Wait before retrying."
                    )
                    await browser.close()
                    return []

                # Check for Cloudflare challenge or blocking pages
                page_content = await page.content()
                if (
                    "challenge" in page_content.lower()
                    or "cloudflare" in page_content.lower()
                ):
                    if (
                        "ray id" in page_content.lower()
                        or "checking your browser" in page_content.lower()
                    ):
                        self.logger.error(
                            f"[{self.name}] ❌ CLOUDFLARE CHALLENGE: Bot detection triggered"
                        )
                        self.logger.error(
                            f"[{self.name}] 🚫 EXTRACTION STOPPED: Cloudflare blocking requests. Need different approach."
                        )
                        await browser.close()
                        return []

                self.logger.debug(
                    f"[{self.name}] Performing initial link extraction..."
                )  # Use self.logger
                initial_found = await extract_links_from_page(page)
                self.logger.info(
                    f"[{self.name}] Found {initial_found} events initially."
                )  # Use self.logger

                self.logger.debug(
                    f"[{self.name}] Starting iterative scrolling and extraction..."
                )  # Use self.logger
                scroll_attempts = 35
                scroll_delay_ms = 1000
                no_change_threshold = 5
                no_change_count = 0

                for i in range(scroll_attempts):
                    current_height = await page.evaluate("document.body.scrollHeight")
                    await page.evaluate(
                        "window.scrollTo(0, document.body.scrollHeight)"
                    )
                    await page.wait_for_timeout(scroll_delay_ms)
                    new_height = await page.evaluate("document.body.scrollHeight")

                    found_this_scroll = await extract_links_from_page(page)
                    if found_this_scroll > 0:
                        self.logger.info(
                            f"[{self.name}] Scroll attempt {i + 1}/{scroll_attempts}: Found {found_this_scroll} new events. Total: {len(event_list)}"
                        )  # Use self.logger

                    if new_height == current_height:
                        no_change_count += 1
                        self.logger.debug(
                            f"[{self.name}] Height unchanged ({no_change_count}/{no_change_threshold})"
                        )  # Use self.logger
                        if no_change_count >= no_change_threshold:
                            self.logger.info(
                                f"[{self.name}] Stopping scroll: Page height stable after {no_change_count} checks."
                            )  # Use self.logger
                            break
                    else:
                        no_change_count = 0

                self.logger.debug(
                    f"[{self.name}] Finished scrolling. Performing final extraction pass..."
                )  # Use self.logger
                await page.wait_for_timeout(3000)
                final_found = await extract_links_from_page(page)
                if final_found > 0:
                    self.logger.info(
                        f"[{self.name}] Found {final_found} additional events in final pass. Total: {len(event_list)}"
                    )  # Use self.logger

                self.logger.info(
                    f"[{self.name}] Successfully extracted {len(event_list)} unique event links."
                )  # Use self.logger
                await browser.close()
                browser = None

        except Exception as e:
            self.logger.error(
                f"[{self.name}] Error during Playwright event list fetching: {e}",
                exc_info=True,
            )  # Use self.logger
            # Optionally save page source on error for debugging
            if page:
                try:
                    debug_path = os.path.join(
                        "results", "debug_playwright_linkfinder_source.html"
                    )
                    os.makedirs(os.path.dirname(debug_path), exist_ok=True)
                    with open(debug_path, "w", encoding="utf-8") as f:
                        f.write(await page.content())
                    self.logger.info(
                        f"[{self.name}] Saved page source to {debug_path}"
                    )  # Use self.logger
                except Exception as save_err:
                    self.logger.error(
                        f"[{self.name}] Could not save page source: {save_err}"
                    )  # Use self.logger

        finally:
            if browser:
                self.logger.debug(
                    f"[{self.name}] Ensuring browser is closed in finally block."
                )  # Use self.logger
                try:
                    await browser.close()
                except Exception as close_err:
                    self.logger.error(
                        f"[{self.name}] Error closing browser: {close_err}"
                    )  # Use self.logger

        return event_list  # Return the actual list
