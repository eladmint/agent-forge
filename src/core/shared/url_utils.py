"""URL utility functions for resolving and normalizing web addresses."""

import logging
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import requests

# Standard logger for the module
logger = logging.getLogger(__name__)


def resolve_url(
    base_url: Optional[str], url: str, custom_logger: Optional[logging.Logger] = None
) -> Optional[str]:
    """Resolves a given URL against a base URL to form an absolute URL.

    This function handles various common cases, including protocol-relative URLs,
    URLs that are already absolute, and ensures the output is a valid HTTP/HTTPS URL.

    Args:
        base_url: The base URL to resolve against. Can be None or empty.
                  If `base_url` itself is relative, the behavior of `urljoin` might be unexpected.
                  It's best to provide an absolute `base_url`.
        url: The URL to resolve (can be relative or absolute).
        custom_logger: An optional custom logger instance. If not provided,
                       the module-level logger is used.

    Returns:
        Optional[str]: The absolute HTTP/HTTPS URL if resolvable and valid,
                       otherwise None. Returns None for non-HTTP/HTTPS schemes
                       (e.g., 'ftp', 'mailto', 'javascript', 'data').

    Side Effects:
        Logs debug or warning messages based on the resolution process.
    """
    log = custom_logger or logger

    if not url:
        log.debug("URL is None or empty, cannot resolve")
        return None

    url_stripped = url.strip()

    # Reject clearly invalid or non-HTTP URLs early
    if not url_stripped or url_stripped.startswith(
        ("data:", "javascript:", "mailto:", "tel:")
    ):
        log.debug(
            "Skipping URL resolution for non-HTTP/data/javascript/mailto/tel URI: %s",
            url_stripped[:50],
        )
        return None

    # If base_url is provided, ensure it has a scheme for robust joining, especially with protocol-relative 'url'.
    # urljoin can be tricky if base_url has no scheme.
    parsed_base = None
    if base_url:
        parsed_base = urlparse(base_url.strip())
        if not parsed_base.scheme:  # If base_url is like "www.example.com/path"
            # Prepend a default scheme (https) if base_url is schemeless but looks like a domain.
            # This helps urljoin behave more predictably.
            if parsed_base.netloc or (
                not parsed_base.path.startswith("/")
                and "." in parsed_base.path.split("/")[0]
            ):
                base_url = "https://" + base_url.strip()
                log.debug("Prepended https:// to schemeless base_url: %s", base_url)

    # Attempt to join the base URL and the relative URL.
    # `urljoin` handles cases where `url` is already an absolute URL correctly.
    try:
        abs_url = urljoin(base_url or "", url_stripped)
    except ValueError as ve:  # Should be rare with string inputs
        log.warning(
            "urljoin raised ValueError for base_url='%s', url='%s': %s",
            base_url,
            url_stripped,
            ve,
        )
        return None

    log.debug(
        "Resolved URL: '%s' with base '%s' -> '%s'", url_stripped, base_url, abs_url
    )

    # Handle protocol-relative URLs that weren't resolved with a scheme
    if abs_url.startswith("//"):
        abs_url = "https:" + abs_url
        log.debug("Added https scheme to protocol-relative URL: %s", abs_url)

    # Final validation: ensure the scheme is http or https.
    parsed_abs_url = urlparse(abs_url)
    if parsed_abs_url.scheme in ["http", "https"]:
        return abs_url

    log.debug(
        "URL resolution resulted in a non-HTTP(S) scheme ('%s'): %s",
        parsed_abs_url.scheme,
        abs_url,
    )
    return None


def normalize_luma_url(
    url: Optional[str], custom_logger: Optional[logging.Logger] = None
) -> Optional[str]:
    """Normalizes a Luma.lu event, user, or group URL.

    Specifically, this function prefixes common Luma relative paths (like '/user/',
    '/g/', '/event/') with 'https://lu.ma'. If the URL is already absolute and
    appears to be a Luma URL, it's returned as is. Other types of URLs might be
    returned as is or as None depending on strictness (currently returns them).

    Args:
        url: The Luma URL (relative or absolute) to normalize.
        custom_logger: An optional custom logger instance.

    Returns:
        Optional[str]: The normalized absolute Luma URL if it's a recognized Luma
                       path or an existing valid Luma URL. Returns None if the input
                       URL is empty or if it's an unrecognized format (and strict
                       mode was implied, though current implementation is lenient).
    """
    log = custom_logger or logger

    if not url:
        log.debug("Cannot normalize an empty URL.")
        return None

    url_stripped = url.strip()
    luma_base = "https://lu.ma"

    # Check for common Luma relative paths
    if url_stripped.startswith(("/user/", "/g/", "/event/")):
        abs_url = urljoin(luma_base, url_stripped)
        log.debug("Normalized Luma relative URL: '%s' -> '%s'", url_stripped, abs_url)
        return abs_url
    elif url_stripped.startswith("http://") or url_stripped.startswith("https://"):
        # URL is already absolute. Check if it's a Luma URL (optional but good for sanity).
        parsed_url = urlparse(url_stripped)
        if "lu.ma" in parsed_url.netloc:
            log.debug("URL is already absolute and is a Luma URL: '%s'", url_stripped)
            return url_stripped
        else:
            # It's an absolute URL but not a Luma one (e.g., an external link found on a Luma page).
            # Depending on the desired strictness for a "Luma URL normalizer":
            # - Lenient: return the URL as is.
            # - Strict: return None if it's not a lu.ma domain.
            log.debug(
                "URL is absolute but not identified as Luma domain: '%s'. Returning as is.",
                url_stripped,
            )
            return url_stripped  # Current behavior: lenient
    else:
        # Unrecognized format (e.g., a relative path not matching common Luma patterns, or a malformed URL fragment)
        log.warning(
            "Unrecognized URL format for Luma normalization: '%s'. Consider using generic resolve_url.",
            url_stripped,
        )
        # Could return `urljoin(luma_base, url_stripped)` if we want to be more aggressive,
        # or None if we want to be strict. For now, returning None for unhandled relative paths.
        return None  # Or resolve_url(luma_base, url_stripped, custom_logger=log) for broader coverage.


class URLNormalizer:
    """Enhanced URL normalization and redirect handling"""

    def __init__(self, max_redirects: int = 10, timeout: int = 10):
        self.max_redirects = max_redirects
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (compatible; EventCrawler/1.0)"}
        )

        # Cache for resolved URLs to avoid redundant requests
        self.redirect_cache: Dict[str, str] = {}

    def normalize_url(self, url: str) -> str:
        """
        Normalize URL by removing tracking parameters and standardizing format
        """
        if not url or not isinstance(url, str):
            return ""

        try:
            # Parse the URL
            parsed = urlparse(url.strip())

            # Normalize scheme
            scheme = parsed.scheme.lower() if parsed.scheme else "https"

            # Normalize netloc (domain)
            netloc = parsed.netloc.lower()

            # Remove common tracking parameters
            tracking_params = {
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "utm_term",
                "utm_content",
                "fbclid",
                "gclid",
                "ref",
                "source",
                "medium",
                "campaign",
                "_ga",
                "_gl",
                "mc_cid",
                "mc_eid",
                "hsCtaTracking",
            }

            # Parse and filter query parameters
            query_params = parse_qs(parsed.query, keep_blank_values=False)
            filtered_params = {
                k: v
                for k, v in query_params.items()
                if k.lower() not in tracking_params
            }

            # Rebuild query string
            query = urlencode(filtered_params, doseq=True) if filtered_params else ""

            # Normalize path (remove trailing slash unless it's root)
            path = parsed.path
            if path != "/" and path.endswith("/"):
                path = path.rstrip("/")

            # Remove fragment (hash)
            fragment = ""

            # Rebuild URL
            normalized = urlunparse(
                (scheme, netloc, path, parsed.params, query, fragment)
            )

            return normalized

        except Exception as e:
            logger.warning(f"Failed to normalize URL {url}: {e}")
            return url

    def follow_redirects(self, url: str) -> Tuple[str, List[str]]:
        """
        Follow redirect chain and return final URL with redirect chain
        Returns: (final_url, redirect_chain)
        """
        if url in self.redirect_cache:
            return self.redirect_cache[url], []

        normalized_url = self.normalize_url(url)
        redirect_chain = []
        current_url = normalized_url

        try:
            for redirect_count in range(self.max_redirects):
                try:
                    # Make HEAD request to check for redirects
                    response = self.session.head(
                        current_url, allow_redirects=False, timeout=self.timeout
                    )

                    # Check if this is a redirect
                    if response.status_code in (301, 302, 303, 307, 308):
                        redirect_url = response.headers.get("location")
                        if redirect_url:
                            # Handle relative redirects
                            redirect_url = urljoin(current_url, redirect_url)
                            redirect_url = self.normalize_url(redirect_url)

                            # Avoid infinite loops
                            if (
                                redirect_url in redirect_chain
                                or redirect_url == current_url
                            ):
                                logger.warning(f"Redirect loop detected for {url}")
                                break

                            redirect_chain.append(current_url)
                            current_url = redirect_url
                            continue

                    # Not a redirect, we're done
                    break

                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request failed for {current_url}: {e}")
                    break

            # Cache the result
            self.redirect_cache[url] = current_url

            return current_url, redirect_chain

        except Exception as e:
            logger.warning(f"Failed to follow redirects for {url}: {e}")
            return normalized_url, []

    def get_canonical_url(self, url: str) -> str:
        """
        Get the canonical URL by normalizing and following redirects
        """
        final_url, _ = self.follow_redirects(url)
        return final_url

    def are_urls_equivalent(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs are equivalent after normalization and redirect following
        """
        canonical1 = self.get_canonical_url(url1)
        canonical2 = self.get_canonical_url(url2)
        return canonical1 == canonical2

    def extract_luma_id(self, url: str) -> Optional[str]:
        """
        Extract Luma event ID from various URL formats
        Examples:
        - https://lu.ma/event-id -> event-id
        - https://lu.ma/event/evt-123 -> evt-123
        - https://luma.com/event-id -> event-id
        """
        try:
            canonical_url = self.get_canonical_url(url)
            parsed = urlparse(canonical_url)

            # Handle different Luma URL patterns
            if "lu.ma" in parsed.netloc or "luma.com" in parsed.netloc:
                path = parsed.path.strip("/")

                # Pattern: /event/evt-123
                if path.startswith("event/"):
                    return path.split("/", 1)[1]

                # Pattern: /event-id (direct)
                elif path and "/" not in path:
                    return path

                # Pattern: /e/event-id
                elif path.startswith("e/"):
                    return path.split("/", 1)[1]

            return None

        except Exception as e:
            logger.warning(f"Failed to extract Luma ID from {url}: {e}")
            return None


class URLDeduplicator:
    """Detect and handle duplicate URLs across different formats"""

    def __init__(self):
        self.normalizer = URLNormalizer()
        self.url_mappings: Dict[str, Set[str]] = {}  # canonical -> {variants}
        self.canonical_urls: Dict[str, str] = {}  # variant -> canonical

    def add_url(self, url: str) -> str:
        """
        Add URL to the deduplicator and return its canonical form
        """
        canonical = self.normalizer.get_canonical_url(url)

        # Add to mappings
        if canonical not in self.url_mappings:
            self.url_mappings[canonical] = set()

        self.url_mappings[canonical].add(url)
        self.canonical_urls[url] = canonical

        return canonical

    def get_canonical_url(self, url: str) -> str:
        """Get the canonical URL for a given variant"""
        return self.canonical_urls.get(url, self.normalizer.get_canonical_url(url))

    def get_url_variants(self, url: str) -> Set[str]:
        """Get all known variants of a URL"""
        canonical = self.get_canonical_url(url)
        return self.url_mappings.get(canonical, {url})

    def is_duplicate(self, url1: str, url2: str) -> bool:
        """Check if two URLs are duplicates"""
        return self.get_canonical_url(url1) == self.get_canonical_url(url2)


# Global instances for easy access
url_normalizer = URLNormalizer()
url_deduplicator = URLDeduplicator()


def normalize_url_enhanced(url: str) -> str:
    """Enhanced URL normalization with tracking parameter removal"""
    return url_normalizer.normalize_url(url)


def follow_redirects_enhanced(url: str) -> Tuple[str, List[str]]:
    """Follow redirect chain and return final URL with redirect chain"""
    return url_normalizer.follow_redirects(url)


def get_canonical_url(url: str) -> str:
    """Get canonical URL by normalizing and following redirects"""
    return url_normalizer.get_canonical_url(url)


def are_urls_equivalent(url1: str, url2: str) -> bool:
    """Check if two URLs are equivalent after normalization and redirect following"""
    return url_normalizer.are_urls_equivalent(url1, url2)


def extract_luma_id(url: str) -> Optional[str]:
    """Extract Luma event ID from various URL formats"""
    return url_normalizer.extract_luma_id(url)


# For backward compatibility with existing code
def is_valid_url(url):
    """Check if URL is valid and reachable"""
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc and parsed.scheme)
    except:
        return False


def clean_url(url):
    """Clean and normalize URL (backward compatibility)"""
    return normalize_url_enhanced(url)
