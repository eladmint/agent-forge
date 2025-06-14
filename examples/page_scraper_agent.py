"""Agent responsible for scraping web page content using Playwright."""

# from swarms import Agent  # REMOVED - Framework migration complete
import asyncio
import logging
import re
from typing import Any, Dict, List, Optional  # Added Dict, Any

import playwright.async_api  # For specific Playwright exception types

# Import BeautifulSoup for image parsing
from bs4 import BeautifulSoup

# Import Playwright
from playwright.async_api import async_playwright

# Import anti-bot evasion manager
from core.shared.anti_bot_evasion_manager import (
    AntiBotEvasionManager,
    EvasionLevel,
)

# Framework-free architecture - no Pydantic configuration needed
# Utility imports
from core.shared.file_utils import ensure_directory_exists
from core.shared.url_utils import resolve_url

# Define output directory for potential debug files like screenshots
OUTPUT_DIR = "results"
# Consider making OUTPUT_DIR configurable if this agent were part of a larger, more complex system.

# Import framework BaseAgent
from core.agents.base import AsyncContextAgent


class PageScraperAgent(AsyncContextAgent):
    """Framework-free agent that uses Playwright to fetch and parse web page content.

    This agent navigates to a given URL using a headless browser (Playwright),
    retrieves the full HTML content, and can extract specific information like
    image URLs. It's designed to handle dynamic web pages that might render
    content using JavaScript.

    Enhanced with comprehensive anti-bot evasion capabilities targeting 90%+ success rate.

    Attributes:
        logger: An optional logger instance for logging agent activities.
        name: Name of the agent.
        evasion_manager: Anti-bot evasion manager for fingerprint masking.
    """

    def __init__(
        self,
        name: str = "PageScraperAgent",
        logger: Optional[logging.Logger] = None,
        evasion_level: EvasionLevel = EvasionLevel.STANDARD,
    ):
        """Initializes the PageScraperAgent.

        Args:
            name: Name of the agent.
            logger: An optional logger instance. If None, a default logger is created.
            evasion_level: Level of anti-bot evasion to apply.
        """
        self.name = name
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
        self.logger.info(
            "[%s] initialized framework-free agent with anti-bot evasion", self.name
        )

        # Initialize anti-bot evasion manager
        self.evasion_manager = AntiBotEvasionManager(
            evasion_level=evasion_level, logger=self.logger
        )

        # Ensure the main output directory exists (e.g., for screenshots if enabled).
        ensure_directory_exists(OUTPUT_DIR, custom_logger=self.logger)
        # The utility function logs its own errors/success, so no need for redundant logging here.

    # The internal `_resolve_url` method was removed and replaced by the
    # `resolve_url` utility function from `utils.url_utils`.

    def _extract_image_urls_bs4(self, html_content: str, base_url: str) -> List[str]:
        """Extracts potential image URLs from HTML content using BeautifulSoup.

        This method parses the HTML to find image URLs from various common sources:
        - Meta tags (e.g., 'og:image', 'twitter:image').
        - `<img>` tags (checking 'data-src', 'srcset', and 'src' attributes).
        - Inline style attributes containing `url(...)`.

        Args:
            html_content: The HTML content of the page as a string.
            base_url: The base URL of the page, used to resolve relative image URLs.

        Returns:
            A list of unique, absolute image URLs found in the HTML.
            Filters out common non-static image types like .gif and .svg.
        """
        if not html_content:
            self.logger.warning(
                "[%s] HTML content is empty, cannot extract images.", self.name
            )
            return []

        self.logger.debug(
            "[%s] Parsing HTML with BeautifulSoup to find image URLs (base: %s)...",
            self.name,
            base_url,
        )
        soup = BeautifulSoup(html_content, "html.parser")
        found_urls: set[str] = set()  # Use a set for automatic deduplication

        # 1. Meta tags (og:image, twitter:image)
        # These tags often provide a primary image for social media sharing.
        meta_tags_selectors = {
            "og:image": {"property": "og:image"},
            "twitter:image": {"name": "twitter:image"},
            # Add more meta tags here if needed, e.g., "msapplication-TileImage"
        }
        for name, selector_attrs in meta_tags_selectors.items():
            tag = soup.find("meta", attrs=selector_attrs)
            if tag and tag.get("content"):
                # Resolve URL found in the 'content' attribute of the meta tag.
                abs_url = resolve_url(
                    base_url, tag["content"], custom_logger=self.logger
                )
                if abs_url:
                    found_urls.add(abs_url)
                    self.logger.debug(
                        "[%s] Found meta %s: %s", self.name, name, abs_url
                    )

        # 2. Img tags (Prioritize data-src, then srcset, then src)
        # This order helps find the most relevant or highest quality image,
        # especially on pages with lazy loading or responsive images.
        for img_tag in soup.find_all("img"):
            sources_to_check: List[str] = []
            processed_img_sources = (
                False  # Flag to ensure we don't double-process if src is also in srcset
            )

            # Check 'data-src' (common for lazy-loaded images)
            data_src = img_tag.get("data-src")
            if data_src:
                sources_to_check.append(data_src)
                processed_img_sources = True

            # Check 'srcset' (for responsive images, provides multiple URLs)
            srcset = img_tag.get("srcset")
            if srcset:
                # Split srcset by comma, then take the URL part (first part before space)
                parts = srcset.split(",")
                for part in parts:
                    url_part = part.strip().split(" ")[0]
                    if url_part:
                        sources_to_check.append(url_part)
                processed_img_sources = True

            # Fallback to 'src' if no data-src or srcset processed it
            if not processed_img_sources:
                src = img_tag.get("src")
                if src:
                    sources_to_check.append(src)

            for img_url_item in sources_to_check:
                abs_url = resolve_url(base_url, img_url_item, custom_logger=self.logger)
                # Filter out common non-static or vector image types if desired.
                if abs_url and not abs_url.lower().endswith((".gif", ".svg")):
                    found_urls.add(abs_url)
                    self.logger.debug("[%s] Found img source: %s", self.name, abs_url)

        # 3. Inline background images (style attribute containing url(...))
        # This regex looks for `url(...)` patterns within style attributes.
        # It's a common way to specify background images via CSS.
        url_pattern = re.compile(r"url\([\'\"]?([^\'\"]+)[\'\"]?\)")
        for tag_with_style in soup.find_all(
            style=True
        ):  # Find all tags that have a 'style' attribute
            style_attribute = tag_with_style.get(
                "style", ""
            )  # Get the style string, default to empty
            if isinstance(
                style_attribute, list
            ):  # Handle cases where style is a list of strings (BS4 can return this)
                style_attribute = ";".join(style_attribute)

            matches = url_pattern.findall(
                style_attribute
            )  # Find all occurrences of url(...)
            for bg_url_item in matches:
                abs_url = resolve_url(base_url, bg_url_item, custom_logger=self.logger)
                if abs_url and not abs_url.lower().endswith((".gif", ".svg")):
                    found_urls.add(abs_url)
                    self.logger.debug(
                        "[%s] Found style background image: %s", self.name, abs_url
                    )

        sorted_urls = sorted(list(found_urls))  # Sort for consistent output order
        self.logger.info(
            "[%s] Extracted %d unique image URLs from %s.",
            self.name,
            len(sorted_urls),
            base_url,
        )
        return sorted_urls

    async def run_async(self, url: str) -> Dict[str, Any]:
        """Scrapes the page content asynchronously using Playwright.

        This method launches a headless browser, navigates to the specified URL,
        waits for the page to load (including network activity to settle),
        and then extracts the full HTML content. It also includes error handling
        for common Playwright issues and network timeouts.

        Args:
            url: The URL of the web page to scrape.

        Returns:
            A dictionary containing:
                - "url": The original URL scraped.
                - "html_content": The full HTML content of the page, or None if scraping failed.
                - "screenshot_path": Path to a saved screenshot (if enabled, currently commented out), else None.
                - "status": A string indicating the outcome ("Success", "Failed (ErrorType: Message)").
        """
        self.logger.info("[%s] Starting scrape for URL: %s", self.name, url)
        html_content: Optional[str] = None
        screenshot_path: Optional[str] = None  # Path for a potential screenshot
        status: str = "Pending"  # Initial status of the scraping operation

        async with async_playwright() as p:
            browser = None  # Initialize browser to None for robust error handling in 'finally'
            try:
                self.logger.debug(
                    "[%s] Launching browser with anti-bot evasion...", self.name
                )

                # Get anti-bot configuration for this URL
                evasion_config = await self.evasion_manager.get_evasion_config(url)

                # Launch browser with anti-bot settings
                browser = await p.chromium.launch(**evasion_config.browser_args)

                # Create context with enhanced anti-bot settings
                context = await browser.new_context(**evasion_config.context_args)
                page = await context.new_page()

                # Apply additional anti-bot measures
                await self.evasion_manager.apply_page_evasion(page, evasion_config)

                self.logger.debug(
                    "[%s] Navigating to %s with evasion profile: %s...",
                    self.name,
                    url,
                    evasion_config.profile_name,
                )

                # Navigate to the page. `wait_until="networkidle"` is crucial for pages
                # that load content dynamically or make many AJAX calls after initial load.
                # `timeout` is set to 60 seconds to allow ample time for slow pages.
                await page.goto(url, wait_until="networkidle", timeout=60000)

                self.logger.debug(
                    "[%s] Page loaded. Extracting HTML content...", self.name
                )
                html_content = await page.content()  # Get the full HTML of the page
                self.logger.info(
                    "[%s] Successfully scraped content from %s.", self.name, url
                )

                # --- Optional Screenshot Section (currently commented out) ---
                # If you need screenshots for debugging or archival:
                # 1. Uncomment this section.
                # 2. Ensure the 'screenshots' subdirectory within OUTPUT_DIR is handled (e.g., created).
                # try:
                #     screenshots_dir = os.path.join(OUTPUT_DIR, "screenshots")
                #     ensure_directory_exists(screenshots_dir, custom_logger=self.logger) # Create if not exists
                #
                #     # Sanitize URL to create a valid filename
                #     safe_filename_part = re.sub(r'[^a-zA-Z0-9_-]', '_', url.replace('https://', '').replace('http://', ''))
                #     screenshot_filename = f"screenshot_{safe_filename_part[:100]}.png" # Limit filename length
                #     screenshot_path = os.path.join(screenshots_dir, screenshot_filename)
                #
                #     await page.screenshot(path=screenshot_path, full_page=True) # full_page=True for entire page
                #     self.logger.debug("[%s] Screenshot saved to %s", self.name, screenshot_path)
                # except Exception as ss_err:
                #     self.logger.warning("[%s] Failed to take screenshot for %s: %s", self.name, url, ss_err, exc_info=True)
                #     screenshot_path = None # Reset path if screenshot fails
                # --- End Optional Screenshot Section ---

                status = (
                    "Success"  # Mark status as Success if all main operations complete
                )

            except playwright.async_api.TimeoutError as e:
                # Handle specific Playwright timeout errors (e.g., page.goto timeout)
                self.logger.error(
                    "[%s] Playwright TimeoutError while scraping %s: %s",
                    self.name,
                    url,
                    e,
                    exc_info=True,
                )
                status = f"Failed (Playwright TimeoutError: {str(e)})"  # Use str(e) for concise message
            except playwright.async_api.Error as e:
                # Handle other Playwright-specific errors (e.g., network errors like net::ERR_NAME_NOT_RESOLVED)
                self.logger.error(
                    "[%s] Playwright error while scraping %s: %s",
                    self.name,
                    url,
                    e,
                    exc_info=True,
                )
                status = f"Failed (Playwright Error: {str(e)})"  # Use str(e)
            except asyncio.TimeoutError:
                # Handle general asyncio timeout errors (less likely to be the primary error source here
                # if Playwright's own timeouts are configured, but good for completeness).
                self.logger.error(
                    "[%s] asyncio.TimeoutError scraping %s. Page load or operation took too long.",
                    self.name,
                    url,
                    exc_info=True,
                )
                status = "Failed (asyncio TimeoutError)"
            except Exception as e:
                # Catch any other unexpected errors during the scraping process.
                self.logger.error(
                    "[%s] Unexpected error scraping %s: %s",
                    self.name,
                    url,
                    e,
                    exc_info=True,
                )
                status = f"Failed (Unexpected Error: {str(e)})"  # Use str(e)
            finally:
                if browser:  # Ensure browser is closed if it was successfully launched
                    self.logger.debug("[%s] Closing browser...", self.name)
                    await browser.close()
                    self.logger.debug("[%s] Browser closed.", self.name)

        return {
            "url": url,
            "html_content": html_content,
            "screenshot_path": screenshot_path,
            "status": status,
        }
