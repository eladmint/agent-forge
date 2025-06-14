"""Agent for extracting structured event data from HTML content.

🎯 PART OF MAIN EXTRACTOR SYSTEM
This agent is a core component of the comprehensive 13+ agent extraction framework.
Main orchestrator: /main_extractor.py (previously enhanced_orchestrator.py)

This agent uses BeautifulSoup to parse HTML and extract specific event details
such as title, date, time, location, description, organizers, and pricing.
It leverages a configuration file for CSS selectors to make it adaptable to
changes in website structure, primarily targeting Luma.co event pages.

The main extractor coordinates this agent along with 12+ other specialized agents
for comprehensive crypto conference event extraction with database integration.
"""

import json
import logging
import re
from typing import Any, Dict, Optional  # Corrected import order and added List

from bs4 import BeautifulSoup, Tag  # Added Tag for type hints

from agent_forge.core.shared.bs_utils import extract_visible_text

# Framework-free implementation
from agent_forge.core.shared.file_utils import ensure_directory_exists
from agent_forge.core.shared.url_utils import (
    normalize_luma_url,
)  # resolve_url might be useful for other URLs
from agent_forge.core.shared.url_validation import validate_single_event

# Define the directory for saving raw HTML snippets if needed for debugging
# (Currently not saving files, but directory defined for potential future use)
RAW_HTML_DIR = "results/raw_html"

# --- Configuration Loading ---
# Attempt to load configurations from an external file.
# Fallback to default configurations if the file is not found or an import error occurs.

# Define default selectors and parameters directly in the module.
# These are used if the external config file (scraper_config.py) is not found.
DEFAULT_MANUAL_SELECTORS: Dict[str, Any] = {
    "title": "h1",  # Default selector for event title
    "initial_props_script": 'script#initial-props[type="application/json"]',  # Luma-specific
    "location_fallback": ".event-location-class",  # Generic class for location
    "description_fallback_container": ".event-description-class",  # Generic class for description
    "organizer_fallback_container": ".event-organizer-class",  # Generic class for organizer
    "price_regex": r"(\$|\€|£|Free|Ticket)",  # Regex for finding price-related text
}

DEFAULT_DIRECT_DETAIL_SELECTORS: Dict[str, Any] = {  # Highly Luma-specific selectors
    "presenter": {
        "label_text_contains": "Presented by",
        "link_href_starts_with": "/g/",  # Luma specific user/group paths
        # "link_text_contains": "Presenter Name", # This can be too specific
        "social_links_container": "div.jsx-1428039309.social-links",  # Luma specific class
        "social_link_item": "div.jsx-2703338562.social-link a",  # Luma specific class
    },
    "host": {
        "card_container": "div.jsx-4155675949.content div.jsx-3733653009.flex-column.hosts",
        "link_row": "a.host-row",
        "name_element": "div.jsx-3733653009.fw-medium.text-ellipses",
        "social_links_container": "div.jsx-1428039309.social-links",
        "social_link_item": "div.jsx-2703338562.social-link a",
    },
    "datetime": {
        "row_container": "div.jsx-1546168629.row-container",
        "icon_row": "div.jsx-2370077516.icon-row",
        "date_element": "div.jsx-2370077516.flex-1 div.jsx-2370077516.title",
        "time_element": "div.jsx-2370077516.flex-1 div.jsx-2370077516.desc",
    },
}

DEFAULT_TEXT_EXTRACTION_CONFIG: Dict[str, Any] = {
    "main_content_selectors": [
        "main",
        "article",
        'div[role="main"]',
        "body",
    ],  # Common main content selectors
    "remove_selectors": [
        "header",
        "nav",
        "footer",
        ".advertisement",
        "aside",
        ".sidebar",
        ".recommendations",
    ],  # Common noise
    "speaker_section_container_selectors": [  # Selectors for identifying speaker/partner text blocks
        'section:has(h1:contains("Speakers"))',
        'section:has(h2:contains("Speakers"))',
        'div:has(h1:contains("Speakers"))',
        'div:has(h2:contains("Speakers"))',
        "#speakers",
        ".speakers-section",  # More generic IDs/classes
    ],
}

# Global flag to indicate if external configuration was loaded successfully.
CONFIG_LOADED = False
try:
    # Attempt to import configurations from the external file.
    from config.scraper_config import (
        DIRECT_DETAIL_SELECTORS,
        MANUAL_EXTRACTION_SELECTORS,
        TEXT_EXTRACTION_CONFIG,
    )

    CONFIG_LOADED = True
    # Optional: Log successful import of config here if module-level logging is set up.
except (ImportError, FileNotFoundError):
    # Config file not found or import error, so use the defaults defined above.
    MANUAL_EXTRACTION_SELECTORS = DEFAULT_MANUAL_SELECTORS
    DIRECT_DETAIL_SELECTORS = DEFAULT_DIRECT_DETAIL_SELECTORS
    TEXT_EXTRACTION_CONFIG = DEFAULT_TEXT_EXTRACTION_CONFIG
    # Optional: Log fallback to defaults here if module-level logging is set up.

# The local Speaker Pydantic model was removed as it's not used directly by this agent
# and SpeakerDetailModel from extraction.agents.models should be used for consistency if needed.


# --- Fallback Manual Extraction Function ---
def extract_event_info_manually(
    html_content: str,
    logger: logging.Logger,
    selectors_config: Dict[
        str, Any
    ],  # Expects a config dict (e.g., MANUAL_EXTRACTION_SELECTORS)
) -> Optional[Dict[str, Any]]:
    """Extracts event information from HTML using basic BeautifulSoup selectors.

    This function serves as a fallback if more structured data extraction methods
    (like JSON-LD or initial props script parsing) fail or are incomplete.
    It tries to find common elements for title, date/time, location, description, etc.

    Args:
        html_content: The HTML content of the event page as a string.
        logger: A logger instance for logging messages.
        selectors_config: A dictionary containing CSS selectors and regex patterns
                          for various event details.

    Returns:
        A dictionary containing extracted event data (keys like "title", "date_time_raw",
        "location", "description", etc.), or None if a critical error occurs during parsing.
        Individual fields in the dictionary will be "N/A" if not found.
    """
    cfg = selectors_config  # Use the passed-in configuration for selectors

    try:
        logger.debug("Attempting manual extraction using BeautifulSoup...")
        soup = BeautifulSoup(html_content, "html.parser")
        event_data: Dict[str, Any] = {}  # Initialize dictionary for event data

        # --- Title Extraction ---
        title_selector = cfg.get("title", "h1")  # Default to 'h1' if not in config
        title_element = soup.select_one(title_selector)
        event_data["title"] = (
            title_element.get_text(strip=True) if title_element else "N/A"
        )
        logger.debug("Manually extracted title: %s", event_data["title"])

        # --- Date, Time, and Timezone from Initial Props Script (Luma-specific) ---
        initial_props_selector = cfg.get(
            "initial_props_script", 'script#initial-props[type="application/json"]'
        )
        initial_props_script_tag = soup.select_one(initial_props_selector)

        date_time_str: str = "N/A"
        start_time: Optional[str] = None
        end_time: Optional[str] = None
        timezone: Optional[str] = None
        initial_props_json: Optional[Dict[str, Any]] = None

        if initial_props_script_tag and initial_props_script_tag.string:
            try:
                initial_props_json = json.loads(initial_props_script_tag.string)
                event_details_json = (
                    initial_props_json.get("event") if initial_props_json else None
                )
                if event_details_json:  # Check if 'event' key exists
                    start_time_iso = event_details_json.get("start_at")
                    end_time_iso = event_details_json.get("end_at")
                    timezone_str_json = event_details_json.get("timezone")

                    if start_time_iso:
                        start_time = start_time_iso  # Store ISO format
                        date_time_str = f"Starts: {start_time_iso}"
                        if end_time_iso:
                            end_time = end_time_iso  # Store ISO format
                            date_time_str += f", Ends: {end_time_iso}"
                        if timezone_str_json:
                            date_time_str += f" ({timezone_str_json})"
                            timezone = timezone_str_json  # Assign to outer scope
                    logger.debug(
                        "Manually extracted time details from JSON: Start=%s, End=%s, TZ=%s",
                        start_time,
                        end_time,
                        timezone,
                    )
            except json.JSONDecodeError:
                logger.error(
                    "Failed to parse initial-props JSON for manual extraction.",
                    exc_info=True,
                )
            except Exception as e:  # Catch other errors during JSON processing
                logger.error(
                    "Error processing initial-props JSON: %s", e, exc_info=True
                )
        else:
            logger.warning(
                "Could not find or parse initial-props JSON script. Date/time extraction may be incomplete."
            )

        event_data["date_time_raw"] = date_time_str
        event_data["start_time_iso"] = start_time
        event_data["end_time_iso"] = end_time
        event_data["timezone"] = timezone

        # --- Location Extraction ---
        location_str: str = "N/A"
        # Try to get location from initial_props_json if it was successfully parsed
        if initial_props_json and initial_props_json.get("event"):
            event_details_manual_loc = initial_props_json.get(
                "event", {}
            )  # Default to empty dict
            virtual_event_flag = event_details_manual_loc.get("is_virtual", False)
            location_info = event_details_manual_loc.get("location_address")
            if location_info:  # Structured address available
                address_parts = [
                    location_info.get("address"),
                    location_info.get("locality"),
                    location_info.get("region"),
                    location_info.get("postal_code"),
                    location_info.get("country_code"),
                ]
                location_str = ", ".join(
                    filter(None, address_parts)
                )  # Join non-empty parts
                if (
                    not location_str
                ):  # If all parts were None/empty, fallback to location_name
                    location_str = event_details_manual_loc.get("location_name", "N/A")
            elif virtual_event_flag:  # Explicitly virtual event
                location_str = "Virtual"
            else:  # No structured address, not explicitly virtual
                location_str = event_details_manual_loc.get(
                    "location_name", "N/A"
                )  # Fallback to name or N/A
        else:  # Fallback to CSS selector if initial_props failed or didn't contain location
            location_fallback_selector = cfg.get(
                "location_fallback", ".event-location-class"
            )  # Default selector
            location_element = soup.select_one(location_fallback_selector)
            if location_element:
                location_str = location_element.get_text(strip=True)
            elif soup.find(
                string=re.compile(r"Online Event|Virtual Event", re.IGNORECASE)
            ):
                # Last resort: check for text cues like "Online Event" in the whole document
                location_str = "Virtual"

        event_data["location"] = (
            location_str if location_str else "N/A"
        )  # Ensure not empty string
        logger.debug("Manually extracted location: %s", event_data["location"])

        # --- Description Extraction ---
        desc_container_selector = cfg.get(
            "description_fallback_container", ".event-description-class"
        )
        description_container_tag = soup.select_one(desc_container_selector)
        if description_container_tag:
            event_data["description"] = extract_visible_text(
                description_container_tag, custom_logger=logger
            )
        else:
            event_data["description"] = "N/A"
        logger.debug(
            "Manually extracted description (first 100 chars): %s...",
            str(event_data["description"])[:100],
        )

        # --- Organizer Extraction ---
        organizer_container_selector = cfg.get(
            "organizer_fallback_container", ".event-organizer-class"
        )
        organizer_element_tag = soup.select_one(organizer_container_selector)
        if organizer_element_tag:
            event_data["organizers"] = extract_visible_text(
                organizer_element_tag, custom_logger=logger
            )
        else:
            event_data["organizers"] = "N/A"
        logger.debug("Manually extracted organizers: %s", event_data["organizers"])

        # --- Price Extraction ---
        price_str = "N/A"
        price_regex_str = cfg.get(
            "price_regex", r"(\$|\€|£|Free|Ticket)"
        )  # Get regex from config
        try:
            price_regex = re.compile(price_regex_str, re.IGNORECASE)
        except re.error as re_err:  # Handle potentially invalid regex from config file
            logger.error(
                "Invalid price regex '%s' from config: %s. Using default.",
                price_regex_str,
                re_err,
            )
            price_regex = re.compile(
                DEFAULT_MANUAL_SELECTORS["price_regex"], re.IGNORECASE
            )  # Fallback to default

        price_elements = soup.find_all(
            string=price_regex
        )  # Find text matching the regex
        if price_elements:
            # Filter out very long text blocks that might accidentally match
            potential_prices = [
                el.strip() for el in price_elements if len(el.strip()) < 50
            ]
            price_str = " | ".join(potential_prices) if potential_prices else "N/A"
        event_data["price"] = (
            price_str if price_str else "N/A"
        )  # Ensure not empty string
        logger.debug("Manually extracted price info: %s", event_data["price"])

        # --- End of Extraction Logic ---

        # Basic validation: check if critical information like title or date is missing
        if (
            event_data.get("title", "N/A") == "N/A"
            and event_data.get("date_time_raw", "N/A") == "N/A"
        ):
            logger.warning(
                "Manual extraction yielded very little data (no title or date/time)."
            )
            # Depending on requirements, one might choose to return None if critical info is missing.

        logger.info(
            "Manual extraction processing complete for potential event: %s",
            event_data.get("title", "Unknown"),
        )
        logger.debug(
            "Returning data from manual extraction (type: %s).", type(event_data)
        )
        return event_data

    except (
        Exception
    ) as e:  # Catch-all for any unexpected errors during manual extraction
        logger.error(
            "Error during manual HTML parsing/extraction: %s", e, exc_info=True
        )
        logger.debug("Returning None from manual extraction due to exception.")
        return None


# --- End Manual Fallback Function ---


class EventDataExtractorAgent:
    """Core HTML/JSON-LD extraction and structured data parsing - Framework-free implementation.

    This agent is designed to parse HTML, primarily from Luma.co event pages,
    to find and structure key event details. It uses CSS selectors defined in
    an external configuration file (`config/scraper_config.py`) to locate
    elements containing event information. If the configuration file is not
    found, it falls back to default selectors.

    The agent attempts to extract:
    - Event title, date, time, timezone.
    - Location (physical or virtual).
    - Description.
    - Organizers/hosts, including their names, profile URLs, and social media links.
    - Presenters (if applicable), with similar details to hosts.
    - General visible text content from the page.

    Attributes:
        logger: Logger instance for agent activities.
        name: Name of the agent.
        manual_selectors (Dict[str, Any]): Configuration for fallback manual extraction.
        direct_selectors (Dict[str, Any]): Configuration for Luma-specific detailed extraction.
        text_extract_config (Dict[str, Any]): Configuration for general text extraction.
    """

    def __init__(
        self,
        name: str = "EventDataExtractorAgent",
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize the framework-free Event Data Extractor Agent.

        Args:
            name: Name of the agent.
            logger: An optional logger instance. If None, a default logger is created.
        """
        self.name = name
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)

        self.logger.info(
            f"[{self.name}] Initialized framework-free Event Data Extractor Agent"
        )

        # Log whether external or default configurations are being used.
        if not CONFIG_LOADED:
            self.logger.warning(
                "[%s] Could not load configurations from config/scraper_config.py. "
                "Using default selectors and parameters. Ensure config file exists for custom settings.",
                self.name,
            )
        else:
            self.logger.info(
                "[%s] Successfully loaded configurations from config/scraper_config.py.",
                self.name,
            )

        # Store loaded (or default if load failed) configurations in the instance.
        self.manual_selectors: Dict[str, Any] = MANUAL_EXTRACTION_SELECTORS
        self.direct_selectors: Dict[str, Any] = DIRECT_DETAIL_SELECTORS
        self.text_extract_config: Dict[str, Any] = TEXT_EXTRACTION_CONFIG

        # Ensure the directory for (optional) raw HTML dumps exists.
        ensure_directory_exists(RAW_HTML_DIR, custom_logger=self.logger)

        self.logger.info("[%s] initialized. Ready for direct parsing.", self.name)

    def _extract_visible_text_bs4(self, soup: Optional[BeautifulSoup]) -> str:
        """Extract visible text from BeautifulSoup object.

        This method is required by the test suite and wraps the utility function
        from bs_utils to maintain compatibility with existing tests.

        Args:
            soup: BeautifulSoup object or None

        Returns:
            Extracted visible text or empty string if soup is None
        """
        if soup is None:
            return ""

        return extract_visible_text(
            soup,
            main_content_selectors=self.text_extract_config.get(
                "main_content_selectors", ["body"]
            ),
            remove_selectors=self.text_extract_config.get("remove_selectors", []),
        )

    def _extract_direct_details(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extracts Luma-specific details like date, time, host, and presenter.

        This method uses highly specific CSS selectors (from `self.direct_selectors`)
        tailored to the structure of Luma.co event pages.

        Args:
            soup: A BeautifulSoup object representing the parsed HTML of an event page.

        Returns:
            A dictionary containing the extracted details. Keys include
            'primary_date_str', 'primary_time_str', 'primary_host_name',
            'primary_host_url', 'primary_host_social_links', 'presenter_name',
            'presenter_url', 'presenter_social_links'. Values will be None or
            empty lists if not found.
        """
        details: Dict[str, Any] = {  # Initialize with default None/empty values
            "primary_date_str": None,
            "primary_time_str": None,
            "primary_host_name": None,
            "primary_host_url": None,
            "primary_host_social_links": [],
            "presenter_name": None,
            "presenter_url": None,
            "presenter_social_links": [],
        }

        # Fetch selector configurations for presenter, host, and datetime sections
        # Defaults to empty dict if key is missing, preventing KeyError.
        presenter_cfg = self.direct_selectors.get("presenter", {})
        host_cfg = self.direct_selectors.get("host", {})
        datetime_cfg = self.direct_selectors.get("datetime", {})

        # --- Presenter Extraction ---
        try:
            self.logger.debug(
                "[%s] Attempting direct presenter extraction...", self.name
            )
            label_text_contains = presenter_cfg.get(
                "label_text_contains", "Presented by"
            )  # Default text
            # Find the "Presented by" label using a lambda to check tag text content.
            presented_by_label = soup.find(
                lambda tag: tag.name in ["div", "span", "p"]  # Common text-hosting tags
                and label_text_contains
                in tag.get_text(strip=True)  # Check stripped text
            )
            presenter_link_element: Optional[Tag] = None
            presenter_socials_scope: Optional[Tag] = (
                None  # Scope for finding social links
            )

            if presented_by_label:
                self.logger.debug(
                    "[%s] Found '%s' label: %s",
                    self.name,
                    label_text_contains,
                    presented_by_label.name,
                )
                link_href_starts_with = presenter_cfg.get(
                    "link_href_starts_with", "/g/"
                )  # Luma specific path

                # Heuristic: Search for presenter link within the parent of the label.
                search_area = (
                    presented_by_label.parent if presented_by_label.parent else soup
                )
                potential_links = search_area.find_all(  # type: ignore # BS4 type for find_all can be broad
                    "a",
                    href=lambda href_val: href_val
                    and href_val.startswith(link_href_starts_with),
                )

                if potential_links:
                    presenter_link_element = potential_links[
                        0
                    ]  # Default to the first link found
                    self.logger.debug(
                        "[%s] Selected presenter link: %s",
                        self.name,
                        presenter_link_element.get("href"),
                    )

                    # Determine scope for social links: try link's parent first.
                    presenter_socials_scope = presenter_link_element.find_parent()  # type: ignore # presenter_link_element can be None
                else:
                    self.logger.debug(
                        "[%s] No presenter links found near '%s' label with href starting '%s'.",
                        self.name,
                        label_text_contains,
                        link_href_starts_with,
                    )
            else:
                self.logger.debug(
                    "[%s] '%s' label not found for presenter.",
                    self.name,
                    label_text_contains,
                )

            if presenter_link_element:
                details["presenter_name"] = presenter_link_element.get_text(strip=True)
                raw_presenter_url = presenter_link_element.get("href")
                details["presenter_url"] = normalize_luma_url(
                    raw_presenter_url, custom_logger=self.logger
                )
                self.logger.debug(
                    "[%s] Extracted Presenter: %s (%s)",
                    self.name,
                    details["presenter_name"],
                    details["presenter_url"],
                )

                # Extract social links if a scope was identified for them
                if presenter_socials_scope:
                    social_div_sel = presenter_cfg.get("social_links_container")
                    item_sel = presenter_cfg.get("social_link_item")

                    # The presenter_socials_scope might be the div itself or a parent.
                    actual_social_div = presenter_socials_scope.select_one(social_div_sel) if social_div_sel else presenter_socials_scope  # type: ignore

                    if actual_social_div and item_sel:
                        social_link_tags = actual_social_div.select(item_sel)
                        for link_tag in social_link_tags:
                            href = link_tag.get("href")
                            if href and href.startswith(
                                "http"
                            ):  # Basic validation for absolute URLs
                                details["presenter_social_links"].append(href)
                        self.logger.debug(
                            "[%s] Extracted Presenter Socials: %s",
                            self.name,
                            details["presenter_social_links"],
                        )
                    else:
                        self.logger.debug(
                            "[%s] Presenter social links container ('%s') or items ('%s') not found.",
                            self.name,
                            social_div_sel,
                            item_sel,
                        )
                else:
                    self.logger.debug(
                        "[%s] No defined scope for presenter social links.", self.name
                    )
            else:  # If presenter_link_element was not found
                self.logger.debug(
                    "[%s] Presenter link element not found, cannot extract full presenter details.",
                    self.name,
                )
        except Exception as pres_err:  # Catch any error during presenter extraction
            self.logger.warning(
                "[%s] Error during direct presenter parsing: %s",
                self.name,
                pres_err,
                exc_info=True,
            )

        # --- Host Extraction ---
        try:
            self.logger.debug("[%s] Attempting direct host extraction...", self.name)
            host_card_sel = host_cfg.get("card_container")
            host_card_container = (
                soup.select_one(host_card_sel) if host_card_sel else None
            )

            if host_card_container:
                host_link_sel = host_cfg.get("link_row")
                host_link_element = (
                    host_card_container.select_one(host_link_sel)
                    if host_link_sel
                    else None
                )

                if host_link_element:
                    host_name_sel = host_cfg.get("name_element")
                    host_name_element = (
                        host_link_element.select_one(host_name_sel)
                        if host_name_sel
                        else None
                    )
                    if host_name_element:
                        details["primary_host_name"] = host_name_element.get_text(
                            strip=True
                        )
                    raw_host_url = host_link_element.get("href")
                    details["primary_host_url"] = normalize_luma_url(
                        raw_host_url, custom_logger=self.logger
                    )
                    self.logger.debug(
                        "[%s] Extracted Host: %s (%s)",
                        self.name,
                        details["primary_host_name"],
                        details["primary_host_url"],
                    )
                else:
                    self.logger.debug(
                        "[%s] Host link element not found with selector: '%s'.",
                        self.name,
                        host_link_sel,
                    )

                host_social_div_sel = host_cfg.get("social_links_container")
                host_item_sel = host_cfg.get("social_link_item")
                # Assume social links are within the host_card_container
                actual_host_social_div = (
                    host_card_container.select_one(host_social_div_sel)
                    if host_social_div_sel
                    else host_card_container
                )

                if actual_host_social_div and host_item_sel:
                    social_link_tags = actual_host_social_div.select(host_item_sel)
                    for link_tag in social_link_tags:
                        href = link_tag.get("href")
                        if href and href.startswith("http"):
                            details["primary_host_social_links"].append(href)
                    self.logger.debug(
                        "[%s] Extracted Host Socials: %s",
                        self.name,
                        details["primary_host_social_links"],
                    )
                else:
                    self.logger.debug(
                        "[%s] Host social links container ('%s') or items ('%s') not found.",
                        self.name,
                        host_social_div_sel,
                        host_item_sel,
                    )
            else:
                self.logger.debug(
                    "[%s] Host card container not found with selector: '%s'.",
                    self.name,
                    host_card_sel,
                )
        except Exception as bs_err:
            self.logger.warning(
                "[%s] Error during direct host/social parsing: %s",
                self.name,
                bs_err,
                exc_info=True,
            )

        # --- Datetime Extraction ---
        try:
            self.logger.debug(
                "[%s] Attempting direct date/time extraction...", self.name
            )
            dt_container_sel = datetime_cfg.get("row_container")
            datetime_row_container = (
                soup.select_one(dt_container_sel) if dt_container_sel else None
            )

            if datetime_row_container:
                dt_icon_row_sel = datetime_cfg.get("icon_row")
                # If icon_row selector is specified, use it; otherwise, use the main container.
                datetime_row = (
                    datetime_row_container.select_one(dt_icon_row_sel)
                    if dt_icon_row_sel
                    else datetime_row_container
                )

                if datetime_row:
                    dt_date_sel = datetime_cfg.get("date_element")
                    dt_time_sel = datetime_cfg.get("time_element")

                    date_elem = (
                        datetime_row.select_one(dt_date_sel) if dt_date_sel else None
                    )
                    time_elem = (
                        datetime_row.select_one(dt_time_sel) if dt_time_sel else None
                    )

                    if date_elem:
                        details["primary_date_str"] = date_elem.get_text(strip=True)
                        self.logger.debug(
                            "[%s] Extracted Date: %s",
                            self.name,
                            details["primary_date_str"],
                        )
                    if time_elem:
                        details["primary_time_str"] = time_elem.get_text(strip=True)
                        self.logger.debug(
                            "[%s] Extracted Time: %s",
                            self.name,
                            details["primary_time_str"],
                        )
                else:
                    self.logger.debug(
                        "[%s] Datetime icon row not found with selector: '%s'.",
                        self.name,
                        dt_icon_row_sel,
                    )
            else:
                self.logger.debug(
                    "[%s] Datetime row container not found with selector: '%s'.",
                    self.name,
                    dt_container_sel,
                )
        except Exception as dt_err:
            self.logger.warning(
                "[%s] Error during direct date/time parsing: %s",
                self.name,
                dt_err,
                exc_info=True,
            )

        self.logger.info(
            "[%s] Direct parsing results: Date='%s', Time='%s', Host='%s', Presenter='%s'",
            self.name,
            details["primary_date_str"],
            details["primary_time_str"],
            details["primary_host_name"],
            details["presenter_name"],
        )
        return details

    async def run_async(
        self, event_url: str, html_content: str, event_name: str
    ) -> Dict[str, Any]:
        """Processes HTML content to extract structured event data and visible text.

        This is the main asynchronous method for the agent. It performs:
        1. Initialization of BeautifulSoup with the provided HTML content.
        2. Direct extraction of structured details (date, time, host, presenter)
           using the `_extract_direct_details` method.
        3. Extraction of general visible text from the page using the
           `extract_visible_text` utility, configured with selectors for main
           content and elements to remove.
        4. Targeted extraction of text from a potential "Speakers" or "Partners" section.
        5. Compilation of all extracted data into a result dictionary.

        Args:
            event_url: The URL of the event page (for context and inclusion in results).
            html_content: The raw HTML content of the event page.
            event_name: The name of the event (can be updated from page title).

        Returns:
            A dictionary containing the extracted data. Key fields include:
            'url', 'event_name', 'visible_text', 'extraction_status',
            and structured details like 'primary_date_str', 'primary_host_name', etc.
            In case of a major failure, 'extraction_status' will indicate the error.
        """
        self.logger.info(
            "[%s] Performing direct parsing for event: '%s' (URL: %s)",
            self.name,
            event_name,
            event_url,
        )

        direct_details: Dict[str, Any] = {}

        try:
            self.logger.debug(
                "[%s] Initializing BeautifulSoup for %s.", self.name, event_name
            )
            soup = BeautifulSoup(html_content, "html.parser")

            # --- Direct Extraction of structured details ---
            direct_details = self._extract_direct_details(soup)
            self.logger.info(
                "[%s] Completed direct detail extraction for %s.", self.name, event_name
            )

            # --- General Visible Text Extraction ---
            combined_text: str = ""
            try:
                # Fetch selectors from instance config, with defaults if keys are missing.
                main_content_selectors_list = self.text_extract_config.get(
                    "main_content_selectors", ["body"]
                )
                remove_selectors_list = self.text_extract_config.get(
                    "remove_selectors", []
                )

                combined_text = extract_visible_text(
                    soup_or_tag=soup,
                    main_content_selectors=main_content_selectors_list,
                    remove_selectors=remove_selectors_list,
                    custom_logger=self.logger,
                )
                self.logger.debug(
                    "[%s] Extracted general visible text for %s (first 500 chars): %s",
                    self.name,
                    event_name,
                    combined_text[:500],
                )
            except Exception as text_extract_err:
                self.logger.error(
                    "[%s] Error during utility text extraction for %s: %s",
                    self.name,
                    event_name,
                    text_extract_err,
                    exc_info=True,
                )
                # Fallback to an ultra-basic text extraction if the utility fails
                try:
                    self.logger.warning(
                        "[%s] Falling back to ultra-basic text extraction for %s.",
                        self.name,
                        event_name,
                    )
                    temp_soup = BeautifulSoup(str(soup), features=soup.parser.name)
                    # Remove only the most common script/style tags
                    for el_type_str in [
                        "script",
                        "style",
                        "head",
                        "meta",
                        "link",
                        "noscript",
                    ]:
                        for el_to_remove in temp_soup.find_all(el_type_str):  # type: ignore
                            el_to_remove.decompose()
                    combined_text = temp_soup.get_text(separator=" ", strip=True)
                except Exception as fallback_deep_err:
                    self.logger.error(
                        "[%s] Error during ultra-fallback text extraction for %s: %s",
                        self.name,
                        event_name,
                        fallback_deep_err,
                        exc_info=True,
                    )
                    combined_text = ""  # Ensure combined_text is an empty string on complete failure

            # --- Update Event Name from Page Title (if not already provided) ---
            current_event_name = event_name
            title_tag = soup.find("title")
            if title_tag and title_tag.string:
                page_title = title_tag.get_text(strip=True)
                if page_title and (
                    not current_event_name or current_event_name == "N/A"
                ):
                    current_event_name = page_title
                    self.logger.info(
                        "[%s] Updated event name from page title tag: %s",
                        self.name,
                        current_event_name,
                    )

            # --- Targeted Speaker/Partner Text Extraction ---
            speaker_section_text: str = ""
            try:
                speaker_section_selectors = self.text_extract_config.get(
                    "speaker_section_container_selectors", []
                )
                speaker_section_container: Optional[Tag] = None
                if speaker_section_selectors:
                    for selector in speaker_section_selectors:
                        try:
                            container_match = soup.select_one(selector)
                            if container_match:
                                speaker_section_container = container_match
                                self.logger.debug(
                                    "[%s] Found speaker section for %s with selector: %s",
                                    self.name,
                                    event_name,
                                    selector,
                                )
                                break
                        except Exception as sel_err:
                            self.logger.warning(
                                "[%s] Invalid or unsupported selector for speaker section '%s' for %s: %s",
                                self.name,
                                selector,
                                event_name,
                                sel_err,
                            )

                if speaker_section_container:
                    speaker_section_text = extract_visible_text(
                        soup_or_tag=speaker_section_container, custom_logger=self.logger
                    )
                    self.logger.debug(
                        "[%s] Extracted text from speaker/partner section for %s (first 100 chars): %s",
                        self.name,
                        event_name,
                        speaker_section_text[:100],
                    )
                else:
                    self.logger.debug(
                        "[%s] Could not find a specific speaker/partner section for %s using configured selectors: %s",
                        self.name,
                        event_name,
                        speaker_section_selectors,
                    )
            except Exception as e:
                self.logger.warning(
                    "[%s] Error trying to extract specific speaker section text for %s: %s",
                    self.name,
                    event_name,
                    e,
                    exc_info=True,
                )

            # --- Combine General and Speaker Texts ---
            if "combined_text" not in locals() or combined_text is None:
                combined_text = ""
                self.logger.warning(
                    "[%s] 'combined_text' was not initialized before speaker section for %s.",
                    self.name,
                    event_name,
                )

            if speaker_section_text.strip():
                separator = (
                    "\n\n--- Speaker/Partner Section ---\n\n"
                    if combined_text.strip()
                    else ""
                )
                combined_text += separator + speaker_section_text

            # --- Prepare Final Results ---
            results = direct_details.copy()
            results["visible_text"] = combined_text.strip()
            results["extraction_status"] = "Success (Direct Parse Only)"
            results["event_name"] = current_event_name
            results["url"] = event_url
            results["luma_url"] = event_url  # Ensure luma_url is set for validation

            # --- Validate Event Data Before Returning ---
            try:
                self.logger.debug(
                    "[%s] Validating extracted event data for '%s'",
                    self.name,
                    current_event_name,
                )
                is_valid = await validate_single_event(results)

                if not is_valid:
                    self.logger.warning(
                        "[%s] Event validation FAILED for '%s' - URL may be fake/404",
                        self.name,
                        current_event_name,
                    )
                    results["extraction_status"] = (
                        "Failed - Invalid Event (Fake/404 URL detected)"
                    )
                    results["validation_failed"] = True
                else:
                    self.logger.info(
                        "[%s] Event validation PASSED for '%s'",
                        self.name,
                        current_event_name,
                    )
                    results["validation_failed"] = False

            except Exception as validation_error:
                self.logger.warning(
                    "[%s] Event validation error for '%s': %s",
                    self.name,
                    current_event_name,
                    str(validation_error),
                )
                # Don't fail extraction due to validation errors, but mark it
                results["validation_warning"] = str(validation_error)
                results["validation_failed"] = False

            self.logger.debug(
                "[%s] Finished direct parsing for '%s'. Status: %s",
                self.name,
                results["event_name"],
                results["extraction_status"],
            )
            return results

        except Exception as e:
            self.logger.error(
                "[%s] Critical error during HTML processing for %s (URL: %s): %s",
                self.name,
                event_name,
                event_url,
                e,
                exc_info=True,
            )
            return {
                "event_name": event_name,
                "url": event_url,
                "visible_text": "",
                "extraction_status": f"Failed - Agent Error: {str(e)}",
                "primary_date_str": None,
                "primary_time_str": None,
                "primary_host_name": None,
                "primary_host_url": None,
                "primary_host_social_links": [],
                "presenter_name": None,
                "presenter_url": None,
                "presenter_social_links": [],
            }
