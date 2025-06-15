import asyncio
import json
import logging
import re
from typing import Any, Dict, Optional, Tuple

import google.generativeai as genai
from bs4 import BeautifulSoup
from playwright.async_api import (
    Error as PlaywrightError,
)
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
)
from playwright.async_api import (
    async_playwright,
)

# from swarms import Agent  # REMOVED - Framework migration complete

MAX_EXTERNAL_PROMPT_CHARS = 30000  # Define max chars for external site prompt

# Import framework BaseAgent
from core.agents.base import AsyncContextAgent


class ExternalSiteScraperAgent(AsyncContextAgent):
    """Framework-free agent responsible for scraping external event websites
    (provided via Luma data) to augment the initially extracted information.

    Currently focuses on fetching basic page content. Detailed extraction is deferred.
    """

    def __init__(
        self,
        name: str = "ExternalSiteScraperAgent",
        logger: Optional[logging.Logger] = None,
        timeout_ms: int = 30000,  # 30 seconds page load timeout
        gemini_model: Optional[genai.GenerativeModel] = None,
        gemini_config: Optional[genai.types.GenerationConfig] = None,
        event_data_schema: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the ExternalSiteScraperAgent.

        Args:
            name: Name of the agent.
            logger: Optional logger instance. If None, a default logger is created.
            timeout_ms: Page load timeout in milliseconds.
            gemini_model: Optional Gemini AI model for content extraction.
            gemini_config: Optional Gemini configuration.
            event_data_schema: Optional event data schema for AI extraction.
        """
        self.name = name
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
        self.timeout_ms = timeout_ms
        self.gemini_model = gemini_model
        self.gemini_config = gemini_config
        self.event_data_schema = event_data_schema

        self.logger.info(
            "[%s] initialized framework-free agent with timeout %dms",
            self.name,
            self.timeout_ms,
        )
        self.logger.debug(
            "[%s] Gemini model: %s, config: %s",
            self.name,
            "set" if gemini_model else "None",
            "set" if gemini_config else "None",
        )

    def _create_external_site_prompt(
        self, url, text_content, existing_event_data: Optional[Dict[str, Any]] = None
    ):
        """Creates the prompt for extracting data from an external site, using Luma context."""
        if not self.event_data_schema:
            self.logger.error("Event data schema is missing, cannot create prompt.")
            return None

        truncated_text = text_content[:MAX_EXTERNAL_PROMPT_CHARS]

        # Build context string from existing Luma data
        context_str = "No prior context provided."
        if existing_event_data:
            context_parts = [
                f"Original Event Name: {existing_event_data.get('event_name')}",
                f"Original URL: {existing_event_data.get('source_url')}",
                f"Original Date: {existing_event_data.get('primary_date_str')}",
                f"Original Host: {existing_event_data.get('primary_host_name')}",
            ]
            if existing_event_data.get("speakers"):
                context_parts.append(
                    f"Known Speakers (from original source): {', '.join([s.get('name', '') for s in existing_event_data['speakers']])}"
                )
            if existing_event_data.get("sponsors_partners"):
                context_parts.append(
                    f"Known Partners (from original source): {', '.join([s.get('name', '') for s in existing_event_data['sponsors_partners']])}"
                )
            context_str = "\n".join(filter(None, context_parts))

        return f"""
Analyze the text extracted from the external website '{url}'.
This website was linked from a Luma event page with the following details:
--- CONTEXT FROM ORIGINAL LUMA EVENT PAGE ---
{context_str}
---

Your Goal: Extract information relevant to the original event context, according to the schema below. 

VERY IMPORTANT INSTRUCTIONS:
1.  **Relevance Check:** First, determine if this external page ('{url}') is directly about the **Original Event** (check name, date, host context). 
    *   If YES (it's the specific event page): Extract all details for that event according to the schema.
    *   If MAYBE (it seems to be the website for the **Original Host** or a related entity, but NOT the specific event page): Extract information that **augments** the original context. Prioritize:
        *   Finding **additional details** about the **Known Speakers** (e.g., missing titles, organizations, URLs).
        *   Identifying **additional speakers** associated with the **Original Host** or relevant topics.
        *   Identifying **general partners/sponsors** of the **Original Host/Organization**.
        *   Finding a better **description** of the **Original Host/Organization**.
        *   Extract other schema fields ONLY IF they clearly relate to the original host/organization.
    *   If NO (the page seems completely unrelated to the Original Event or Host): Return an empty JSON object {{}}.
2.  **Extraction Rules (Apply IF page is relevant - specific event or host site):**
    *   **Speakers:** Look for sections explicitly listing speakers/panelists. Extract full name, organization, title, and URL. Use "N/A" or null if details are missing. Give preference to speakers mentioned in the original context if found.
    *   **Sponsors/Partners:** Look for explicit sponsor/partner sections or logo walls. Extract name and URL. Give preference to partners mentioned in the original context if found.
    *   **Dates/Times/Location/Cost:** Extract ONLY IF the page confirms details for the *Original Event*. If the page is just the host's general site, set these fields to null.
    *   **Description:** If the page is about the specific event, summarize it. If it's the host's site, summarize the *host/organization's* primary purpose or mission.
    *   **Website/Socials:** Extract links IF they appear to be the official ones for the *Original Host/Organization*. 
3.  **Output:** Return ONLY a single valid JSON object matching the schema. If the page is deemed irrelevant (Instruction 1, NO case), return {{}}. No explanations or markdown.

Schema:
{json.dumps(self.event_data_schema, indent=2)}

Extracted Text:
---
{truncated_text}
---

Return ONLY the JSON object.
"""

    def _extract_visible_text_bs4(self, html_content: str) -> str:
        """Extracts visible text from HTML using BeautifulSoup, attempting to filter noise."""
        if not html_content:
            return ""
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script, style, head, nav, footer tags
            for element in soup(
                ["script", "style", "head", "nav", "footer", "header", "aside", "form"]
            ):
                element.decompose()

            # Get text from remaining elements, joining with spaces
            text = soup.get_text(separator="\n", strip=True)

            # Clean up excessive newlines/whitespace
            text = re.sub(r"\n{3,}", "\n\n", text)
            text = re.sub(r"[ \t]{2,}", " ", text)

            return text
        except Exception as e:
            self.logger.error(f"Error extracting text with BeautifulSoup: {e}")
            return ""  # Return empty string on error

    async def run_async(
        self, website_url: str, existing_event_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Scrapes the provided external website URL and attempts to extract event data using Gemini.

        Args:
            website_url (str): The URL of the external event website.
            existing_event_data (Optional[Dict[str, Any]]): Existing Luma data (unused currently, for potential future merging logic).

        Returns:
            Tuple[str, Optional[Dict[str, Any]]]]: A tuple containing:
                - status (str): "Success", "Scrape Failed", "Navigation Error", "Timeout", "Invalid URL", "Unsupported URL", "Extraction Failed", "AI Error", "Unknown Error"
                - extracted_data (Optional[Dict[str, Any]]): The extracted data dictionary, or None on failure.
        """
        # --- ADDED DEBUG LOG ---
        self.logger.debug(
            f"Entering run_async for {website_url}: self.gemini_model is {'set' if self.gemini_model else 'None'}, self.gemini_config is {'set' if self.gemini_config else 'None'}"
        )
        # --- END DEBUG LOG ---
        self.logger.info(f"[{website_url}] Attempting to scrape external site.")

        if not website_url or not website_url.startswith(("http://", "https://")):
            self.logger.warning(f"[{website_url}] Invalid or missing URL provided.")
            return "Invalid URL", None

        # Basic check for common non-event platforms we likely can't scrape well yet
        # Can be expanded later
        unsupported_domains = [
            "t.me",
            "telegram.me",
            "twitter.com",
            "x.com",
            "linkedin.com",
            "discord.gg",
        ]
        try:
            domain = website_url.split("/")[2].replace("www.", "")
            if any(unsupported in domain for unsupported in unsupported_domains):
                self.logger.warning(
                    f"[{website_url}] URL domain ({domain}) is likely unsupported for detailed scraping. Skipping."
                )
                return "Unsupported URL", None
        except IndexError:
            self.logger.warning(f"[{website_url}] Could not parse domain. Skipping.")
            return "Invalid URL", None

        html_content = None
        status = "Unknown Error"  # Default status
        extracted_data = None  # Initialize extracted_data

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()

                try:
                    self.logger.debug(
                        f"[{website_url}] Navigating with timeout {self.timeout_ms}ms..."
                    )
                    await page.goto(
                        website_url,
                        timeout=self.timeout_ms,
                        wait_until="domcontentloaded",
                    )

                    # Optional: Add a small delay or wait for a common element if needed for dynamic content
                    # await asyncio.sleep(2) # Example delay

                    self.logger.debug(
                        f"[{website_url}] Navigation successful, getting content..."
                    )
                    html_content = await page.content()
                    status = "Success"  # Restore status update on successful scrape
                    self.logger.info(
                        f"[{website_url}] Successfully scraped external site HTML content."
                    )

                except PlaywrightTimeoutError:
                    status = "Timeout"
                    self.logger.error(
                        f"[{website_url}] Timeout error during navigation or loading."
                    )
                except PlaywrightError as pe:
                    if "net::ERR_" in str(pe):
                        status = f"Navigation Error ({str(pe).splitlines()[0]})"  # Extract specific net error
                        self.logger.error(
                            f"[{website_url}] Network error during navigation: {status}"
                        )
                    else:
                        status = "Scrape Failed"
                        self.logger.error(
                            f"[{website_url}] Playwright error during scraping: {pe}"
                        )
                except Exception as e:
                    # Catch other potential errors during goto/content
                    status = f"Scrape Failed ({type(e).__name__})"
                    self.logger.error(
                        f"[{website_url}] Unexpected error during scraping: {e}"
                    )
                finally:
                    await browser.close()

        except PlaywrightError as pe:
            # Errors during playwright startup/shutdown
            status = "Playwright Initialization Error"
            self.logger.critical(
                f"[{website_url}] Playwright initialization/shutdown error: {pe}"
            )
        except Exception as e:
            # Catch-all for truly unexpected errors
            status = f"Unknown Error ({type(e).__name__})"
            self.logger.critical(
                f"[{website_url}] An unexpected error occurred during Playwright phase: {e}"
            )
            return status, None  # Return early if Playwright failed critically

        # --- AI Data Extraction ---
        extracted_data = None  # Initialize extracted_data here
        if html_content and self.gemini_model and self.gemini_config:
            if status == "Success":  # Only proceed if scrape was successful
                self.logger.info(
                    f"[{website_url}] Attempting AI extraction from external site content."
                )
                try:
                    # Extract visible text using BeautifulSoup
                    visible_text = self._extract_visible_text_bs4(html_content)

                    prompt_text = ""  # Initialize variable for prompt content

                    if not visible_text:
                        self.logger.warning(
                            f"[{website_url}] Could not extract visible text using BeautifulSoup. Falling back to raw HTML for AI prompt."
                        )
                        prompt_text = html_content  # Use raw HTML as fallback
                    else:
                        prompt_text = visible_text  # Use cleaned text

                    # Check if prompt_text is non-empty before proceeding
                    if not prompt_text:
                        self.logger.error(
                            f"[{website_url}] Both visible text extraction and raw HTML were empty. Cannot proceed with AI extraction."
                        )
                        status = (
                            "Extraction Failed (Empty Content)"  # More specific status
                        )
                    else:
                        # Create the prompt with context using the determined prompt_text
                        prompt = self._create_external_site_prompt(
                            website_url, prompt_text, existing_event_data
                        )
                        if not prompt:
                            raise ValueError(
                                "Failed to create Gemini prompt for external site."
                            )

                        # --- ADDED LOGGING ---
                        self.logger.debug(
                            f"[{website_url}] Sending external site prompt to Gemini (first 1000 chars):\n{prompt[:1000]}"
                        )
                        # --- END LOGGING ---

                        # Call Gemini (synchronous, wrapped in thread)
                        response = await asyncio.to_thread(
                            self.gemini_model.generate_content,
                            prompt,
                            generation_config=self.gemini_config,
                        )

                        if response is None or not response.parts:
                            raise ValueError(
                                "Gemini response missing or has no parts for external site."
                            )

                        json_text = response.text
                        # **Fix**: Strip Markdown fences and whitespace before parsing
                        if json_text.strip().startswith("```json"):
                            json_text = json_text.strip()[7:]
                        if json_text.strip().endswith("```"):
                            json_text = json_text.strip()[:-3]
                        json_text = json_text.strip()

                        # --- ADDED LOGGING ---
                        self.logger.debug(
                            f"[{website_url}] Raw Gemini response text (External Site):\n{json_text}"
                        )
                        # --- END ADDED LOGGING ---

                        # Check for empty JSON object response, indicating irrelevance
                        if json_text == "{}":
                            self.logger.info(
                                f"[{website_url}] Gemini indicated external site was irrelevant based on context. No data extracted."
                            )
                            extracted_data = {}  # Represent irrelevance as empty dict
                            # Status remains "Success" because the process worked, but yielded no relevant data
                        else:
                            extracted_data = json.loads(json_text)
                            self.logger.info(
                                f"[{website_url}] Successfully extracted data from external site via AI."
                            )
                            # Status is already "Success" from scraping stage

                except json.JSONDecodeError as json_err:
                    status = "Extraction Failed (JSON Decode)"
                    self.logger.error(
                        f"[{website_url}] Failed to decode Gemini JSON response: {json_err}. Response text was:\n{json_text}",
                        exc_info=True,
                    )
                    extracted_data = None  # Ensure data is None on error
                except Exception as ai_err:
                    status = f"AI Error ({type(ai_err).__name__})"
                    self.logger.error(
                        f"[{website_url}] Error during AI extraction: {ai_err}",
                        exc_info=True,
                    )
                    extracted_data = None  # Ensure data is None on error
            else:
                # If scraping failed initially, don't attempt AI extraction
                self.logger.warning(
                    f"[{website_url}] Skipping AI extraction because initial scraping status was: {status}"
                )

        elif status == "Success":
            # If scrape was successful but AI part was skipped (no model/config or no html)
            self.logger.warning(
                f"[{website_url}] External site scraped, but AI extraction was skipped (missing HTML, model, or config)."
            )
            status = "Extraction Skipped"  # More specific status

        # Final return based on status and extracted_data
        return status, extracted_data


# Example usage (for testing)
async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    )
    logger = logging.getLogger("TestExternalScraper")
    agent = ExternalSiteScraperAgent(
        logger=logger,
        # Need to pass model/config/schema here for test if we want to test AI extraction
        # gemini_model=... ,
        # gemini_config=...,
        # event_data_schema=...
    )

    test_urls = [
        "https://example.com",  # Should succeed
        "https://httpbin.org/delay/5",  # Should likely succeed (adjust agent timeout if needed)
        "https://thissitedoesnotexistandneverwill.xyz",  # Should fail (Navigation Error)
        "https://lu.ma/token2049",  # Realistic test
        "wss://invalid.protocol.xyz",  # Invalid URL
        "https://twitter.com/some_event",  # Unsupported URL
    ]

    for url in test_urls:
        print(f"--- Testing URL: {url} ---")
        status, data = await agent.run_async(website_url=url)
        print(f"Status: {status}")
        if data:
            print(f"Extracted Data Keys: {list(data.keys())}")
            # print(json.dumps(data, indent=2)) # Optional: print full extracted data
        else:
            print("Extracted Data: None")
        # print(f"Content Length: {len(content) if content else 'N/A'}")
        print("-" * 20)


if __name__ == "__main__":
    # asyncio.run(main())
    pass  # Keep example usage commented out for production script
