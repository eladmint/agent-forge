import logging
import re
import traceback
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

# from swarms import Agent  # REMOVED - Framework migration complete


# --- Constants for Filtering/Scoring ---

# Domains to explicitly ignore
BLOCKLIST_DOMAINS = {
    "lu.ma",
    "google.com",  # Maps, search results, etc.
    "maps.google.com",
    "calendar.google.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "instagram.com",
    "t.me",
    "telegram.me",
    "discord.gg",
    "wa.me",  # WhatsApp
    "youtube.com",
    "youtu.be",
    "vimeo.com",
    "zoom.us",
    "webex.com",
    "teams.microsoft.com",
    # Add more common platforms if needed
}

# Keywords that strongly suggest an official event website link text
POSITIVE_LINK_TEXT_KEYWORDS = [
    "official website",
    "event website",
    "project site",
    "homepage",
    "main site",
    "register here",
    "registration",
    "tickets",
    "get tickets",
    "learn more",
    "more info",
    "details",
    "event page",
    # Consider adding conference/summit specific terms if needed
]

# Keywords that might indicate an external link but are less specific
NEUTRAL_LINK_TEXT_KEYWORDS = [
    "website",
    "site",
    "link",
    "url",
    "click here",
]

# Patterns in URLs that might indicate an official site (e.g., subdomain)
# Less reliable, use with caution
# POSITIVE_URL_PATTERNS = [r'event[s]?\.', r'conference\.', r'summit\.', r'token\d*\.', r'web3\.', r'blockchain\.', r'crypto\.']


class LinkSelectorAgent:
    """Framework-free agent that analyzes HTML content to identify and select
    the most likely external official event website URL, filtering out social
    media, platform links, etc.
    """

    def __init__(
        self,
        name: str = "LinkSelectorAgent",
        logger: Optional[logging.Logger] = None,
        score_threshold: float = 0.40,  # Minimum score to select a link
    ):
        """Initialize the LinkSelectorAgent.

        Args:
            name: Name of the agent.
            logger: Optional logger instance. If None, a default logger is created.
            score_threshold: Minimum score threshold to select a link.
        """
        self.name = name
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
        self.score_threshold = score_threshold

        self.logger.info(
            "[%s] initialized framework-free agent with score threshold: %s",
            self.name,
            self.score_threshold,
        )

    def _is_valid_external_link(self, url: str, base_domain: str) -> bool:
        """Checks if a URL is a valid, external, non-blocked HTTP/HTTPS link."""
        if not url:
            return False
        try:
            parsed = urlparse(url)
            # 1. Check scheme (allow only http/https)
            if parsed.scheme not in ("http", "https"):
                # self.logger.debug(f"Filtering invalid scheme: {parsed.scheme} for {url}")
                return False
            # 2. Check domain
            domain = parsed.netloc.replace("www.", "")
            if not domain:
                # self.logger.debug(f"Filtering missing domain: {url}")
                return False
            # 3. Check against blocklist
            if domain in BLOCKLIST_DOMAINS:
                # self.logger.debug(f"Filtering blocklisted domain: {url}")
                return False
            # 4. Check if it's the same base domain or a subdomain of it (e.g., help.lu.ma)
            # base_domain is expected to be like 'lu.ma'
            if domain == base_domain or domain.endswith("." + base_domain):
                # self.logger.debug(f"Filtering internal domain/subdomain: {url}")
                return False
            # 5. Basic check for common file extensions (can be expanded)
            if re.search(
                r"\.(pdf|jpg|jpeg|png|gif|zip|mp4|mov|avi|svg|webp)$",
                parsed.path.lower(),
            ):
                # self.logger.debug(f"Filtering direct file link: {url}")
                return False

            return True
        except ValueError:
            # Handle potential parsing errors for malformed URLs
            self.logger.warning(f"Could not parse URL: {url}")
            return False

    def _score_link(
        self,
        link_tag: Tag,
        url: str,
        host_name: Optional[str] = None,
        presenter_name: Optional[str] = None,
    ) -> float:
        """Assigns a score to a link based on heuristics, including surrounding text context and host/presenter names."""
        score = 0.0
        link_text = link_tag.get_text(strip=True).lower() if link_tag else ""

        # Return early if no link text and not just domain
        parsed_url = urlparse(url)
        if not link_text and parsed_url.path and parsed_url.path != "/":
            return 0.0

        # --- 1. Score based on Link Text ---
        link_text_score = 0.0
        positive_keyword_in_link = False
        neutral_keyword_in_link = False
        for keyword in POSITIVE_LINK_TEXT_KEYWORDS:
            if keyword in link_text:
                link_text_score = 1.0
                positive_keyword_in_link = True
                self.logger.debug(
                    f"Positive keyword ('{keyword}') in LINK TEXT '{link_text[:50]}...' for {url}"
                )
                break  # Only add score once per category
        if not positive_keyword_in_link:
            for keyword in NEUTRAL_LINK_TEXT_KEYWORDS:
                if keyword in link_text:
                    link_text_score = 0.3
                    neutral_keyword_in_link = True
                    self.logger.debug(
                        f"Neutral keyword ('{keyword}') in LINK TEXT '{link_text[:50]}...' for {url}"
                    )
                    break
        score += link_text_score

        # --- 2. Score based on Surrounding Context (Parent Element Text) ---
        context_score = 0.0
        parent_text = ""
        if link_tag and link_tag.parent:
            # Get text of parent, excluding the link's own text to avoid double count
            parent_text = link_tag.parent.get_text(separator=" ", strip=True).lower()
            # Simple way to remove link text: replace first occurrence. Might not be perfect for complex HTML.
            parent_text_without_link = parent_text.replace(link_text, "", 1).strip()

            # Only search context if keywords weren't already found in link text
            if not positive_keyword_in_link:
                for keyword in POSITIVE_LINK_TEXT_KEYWORDS:
                    if keyword in parent_text_without_link:
                        context_score = 0.5  # Lower score for context match
                        self.logger.debug(
                            f"Positive keyword ('{keyword}') in PARENT CONTEXT for {url}. Adding {context_score:.2f}"
                        )
                        break
            if (
                not positive_keyword_in_link
                and not neutral_keyword_in_link
                and context_score == 0.0
            ):  # Check neutral only if no positive found in link or context
                for keyword in NEUTRAL_LINK_TEXT_KEYWORDS:
                    if keyword in parent_text_without_link:
                        context_score = 0.15  # Lower score for context match
                        self.logger.debug(
                            f"Neutral keyword ('{keyword}') in PARENT CONTEXT for {url}. Adding {context_score:.2f}"
                        )
                        break
        score += context_score

        # --- 3. Penalize very long link text ---
        if len(link_text) > 80:
            score -= 0.2

        # --- 4. Bonus if link text matches or contains domain name ---
        domain_text = parsed_url.netloc.replace("www.", "")
        domain_match_bonus = 0.0
        if domain_text:  # Ensure domain_text is not empty
            if link_text == domain_text:
                domain_match_bonus = 0.4  # Keep existing bonus for exact match
                self.logger.debug(
                    f"Link text exactly matches domain for {url}. Adding {domain_match_bonus:.2f}"
                )
            elif domain_text in link_text:
                domain_match_bonus = 0.2
                self.logger.debug(
                    f"Link text contains domain for {url}. Adding {domain_match_bonus:.2f}"
                )
        score += domain_match_bonus

        # --- 5. Very basic TLD check ---
        tld_bonus = 0.0
        if domain_text:
            tld = domain_text.split(".")[-1] if "." in domain_text else ""
            common_tlds = {
                "com",
                "org",
                "io",
                "xyz",
                "net",
                "co",
                "ai",
                "dev",
                "app",
                "events",
                "info",
                "tech",
                "network",
                "life",
            }
            if tld in common_tlds:
                tld_bonus = 0.1
                score += tld_bonus
                # self.logger.debug(f"Common TLD ('{tld}') bonus {tld_bonus:.2f} for {url}")

        # --- 6. Penalize if it looks like a directory listing ---
        if (
            parsed_url.path
            and parsed_url.path.endswith("/")
            and len(parsed_url.path) > 1
        ):
            score -= 0.1

        # --- 7. Bonus for linking to the root path ---
        root_path_bonus = 0.0
        if not parsed_url.path or parsed_url.path == "/":
            root_path_bonus = 0.15
            score += root_path_bonus
            # self.logger.debug(f"Link points to root path for {url}. Adding {root_path_bonus:.2f}")

        # --- 8. Bonus if domain relates to host/presenter name ---
        host_presenter_match_bonus = 0.0
        names_to_check = [
            name for name in [host_name, presenter_name] if name
        ]  # Filter out None
        # --- ADDED LOGGING ---
        self.logger.debug(
            f"_score_link received host_name='{host_name}', presenter_name='{presenter_name}'"
        )
        self.logger.debug(f"Checking against names: {names_to_check}")
        # --- END ADDED LOGGING ---
        if domain_text and names_to_check:
            domain_root = domain_text.split(".")[
                0
            ]  # Simple root domain extraction (e.g., 'circolo' from 'circolo.life')
            normalized_domain_root = re.sub(
                r"[^a-z0-9]", "", domain_root.lower()
            )  # Keep only letters/numbers
            # --- ADDED LOGGING ---
            self.logger.debug(
                f"Normalized domain root for {url}: '{normalized_domain_root}'"
            )
            # --- END ADDED LOGGING ---

            for name in names_to_check:
                # Normalize name: lowercase, remove common suffixes and spaces
                normalized_name = name.lower()
                for suffix in [
                    " life",
                    " inc",
                    " llc",
                    " ltd",
                    " gmbh",
                    " group",
                    " labs",
                    " studio",
                ]:  # Extend as needed
                    normalized_name = normalized_name.replace(suffix, "")
                normalized_name = re.sub(
                    r"[^a-z0-9]", "", normalized_name
                )  # Keep only letters/numbers
                # --- ADDED LOGGING ---
                self.logger.debug(
                    f"Normalized name '{normalized_name}' from original '{name}'"
                )
                # --- END ADDED LOGGING ---

                if (
                    normalized_domain_root
                    and normalized_name
                    and (
                        normalized_domain_root in normalized_name
                        or normalized_name in normalized_domain_root
                    )
                ):
                    host_presenter_match_bonus = 0.25  # Assign bonus
                    self.logger.debug(
                        f"Domain root '{normalized_domain_root}' matches normalized name '{normalized_name}' from '{name}' for {url}. Adding {host_presenter_match_bonus:.2f}"
                    )
                    break  # Apply bonus only once

        score += host_presenter_match_bonus

        self.logger.debug(
            f"Final score breakdown for {url}: LinkText={link_text_score:.2f}, Context={context_score:.2f}, DomainMatch={domain_match_bonus:.2f}, TLD={tld_bonus:.2f}, RootPath={root_path_bonus:.2f}, HostPresenterMatch={host_presenter_match_bonus:.2f} -> Total={max(0, score):.2f}"
        )
        return max(0, score)  # Ensure score doesn't go below 0

    async def run_async(
        self,
        html_content: str,
        base_url: str,
        host_name: Optional[str] = None,
        presenter_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Parses HTML, finds potential external links, scores them, and returns the best candidate.

        Args:
            html_content: The HTML content of the source page (e.g., Luma event page).
            base_url: The URL of the source page (used for resolving relative links and filtering).
            host_name: The name of the host or presenter of the event.
            presenter_name: The name of the presenter of the event.

        Returns:
            The selected external URL string, or None if no suitable link is found.
        """
        self.logger.debug(f"LinkSelectorAgent running for base URL: {base_url}")
        if not html_content:
            self.logger.warning("Received empty HTML content.")
            return None

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            base_domain = urlparse(base_url).netloc.replace("www.", "")

            candidate_links: Dict[str, float] = {}  # Store URL -> score

            # Find potential domains mentioned in text like "event by [domain]"
            # Make regex more robust to handle potential spaces or http(s):// prefix
            mentioned_domains = set(
                re.findall(
                    r"event by\\s+(?:https?://)?(?:www\\.)?([a-zA-Z0-9.-]+\\.[a-zA-Z]{2,})",
                    html_content,
                    re.IGNORECASE,
                )
            )
            self.logger.debug(f"Found mentioned domains in text: {mentioned_domains}")

            links = soup.find_all("a", href=True)
            self.logger.debug(f"Found {len(links)} total links in HTML.")

            valid_external_links_found = 0  # Counter for valid external links

            for link in links:
                raw_href = link["href"].strip()
                if (
                    not raw_href
                    or raw_href.startswith("#")
                    or raw_href.lower().startswith("javascript:")
                ):
                    continue  # Skip empty, fragment, or javascript links

                # Attempt to resolve relative URLs
                try:
                    abs_url = urljoin(base_url, raw_href)
                except ValueError:
                    self.logger.debug(f"Skipping malformed href: {raw_href}")
                    continue

                # Filter out invalid/internal/blocked links
                if not self._is_valid_external_link(abs_url, base_domain):
                    continue

                # --- Added Logging ---
                valid_external_links_found += 1
                self.logger.debug(f"Found valid external link candidate: {abs_url}")
                # --- End Added Logging ---

                # Score the valid external link, passing host/presenter names
                score = self._score_link(link, abs_url, host_name, presenter_name)

                # --- Added Logging ---
                self.logger.debug(
                    f"Calculated score {score:.2f} for link: {abs_url} (Text: '{link.get_text(strip=True)[:50]}...')"
                )
                # --- End Added Logging ---

                # Bonus if the link's domain was mentioned in "event by [domain]"
                link_domain = urlparse(abs_url).netloc.replace("www.", "")
                if link_domain in mentioned_domains:
                    boost = 0.7  # Define boost amount
                    score += boost
                    self.logger.debug(
                        f"Boosting score by {boost:.2f} for mentioned domain '{link_domain}' in {abs_url}. New score: {score:.2f}"
                    )

                # Store link and highest score if above zero
                if score > 0:
                    # Only update if the new score is higher for this URL
                    candidate_links[abs_url] = max(
                        score, candidate_links.get(abs_url, 0.0)
                    )

            # --- Added Logging ---
            self.logger.debug(
                f"Finished iterating links. Found {valid_external_links_found} valid external link(s)."
            )
            self.logger.debug(
                f"Candidate links before threshold filtering (Top 10 by score): {dict(sorted(candidate_links.items(), key=lambda item: item[1], reverse=True)[:10])}"
            )
            # --- End Added Logging ---

            # Find the best candidate above the threshold
            if not candidate_links:
                self.logger.info(
                    f"No valid external candidate links found scoring > 0 for {base_url}."
                )
                return None

            # Sort by score descending, then by URL length ascending (prefer shorter URLs at same score)
            sorted_candidates = sorted(
                candidate_links.items(), key=lambda item: (-item[1], len(item[0]))
            )

            best_url, best_score = sorted_candidates[0]

            self.logger.debug(
                f"Top candidates scoring > 0: {[(url, f'{score:.2f}') for url, score in sorted_candidates if score > 0]}"
            )

            if best_score >= self.score_threshold:
                self.logger.info(
                    f"Selected external link: {best_url} with score {best_score:.2f} (Threshold: {self.score_threshold})"
                )
                return best_url
            else:
                # --- Added Logging ---
                self.logger.info(
                    f"No candidate link met threshold {self.score_threshold} (best was {best_url} with score {best_score:.2f})."
                )
                # --- End Added Logging ---
                return None

        except Exception as e:
            self.logger.error(
                f"Error during link selection for {base_url}: {e}\\n{traceback.format_exc()}",
                exc_info=True,
            )  # Add traceback
            return None


# Example usage (keep commented out)
# async def main():
#     logging.basicConfig(level=logging.DEBUG)
#     logger = logging.getLogger("TestLinkSelector")
#     # Sample HTML content would go here
#     sample_html = """
#     <html><body>
#         <p>Welcome to the event! More info at <a href='https://official-event.com/details'>our official website</a>.</p>
#         <p>Also check <a href='https://www.socialsite.com/event'>socials</a>.</p>
#         <p>This is an event by coolcompany.io.</p>
#         <a href='/internal-page'>Internal</a>
#         <a href='https://coolcompany.io'>CoolCompany.io</a>
#         <a href='mailto:test@example.com'>Email us</a>
#         <a href='https://lu.ma/someother'>Another Luma Event</a>
#         <a href='https://subdomain.coolcompany.io/specific'>Specific Subdomain</a>
#     </body></html>
#     """
#     base_url = "https://lu.ma/myevent"
#     agent = LinkSelectorAgent(logger=logger, score_threshold=0.5)
#     selected = await agent.run_async(sample_html, base_url)
#     print(f"Selected URL: {selected}") # Expecting https://coolcompany.io

# if __name__ == "__main__":
#     asyncio.run(main())
