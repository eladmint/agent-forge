"""BeautifulSoup utility functions for HTML parsing and text extraction."""

import logging
from typing import List, Optional, Union  # Union for type hint

from bs4 import BeautifulSoup, Tag  # Tag for type hint

# Standard logger for the module
logger = logging.getLogger(__name__)


def extract_visible_text(
    soup_or_tag: Union[BeautifulSoup, Tag],
    main_content_selectors: Optional[List[str]] = None,
    remove_selectors: Optional[List[str]] = None,
    separator: str = " ",
    custom_logger: Optional[logging.Logger] = None,
) -> str:
    """Extracts visible text from a BeautifulSoup object or a specific Tag.

    This function aims to retrieve human-readable text by:
    1. Optionally focusing on a main content area specified by selectors.
    2. Removing common non-visible elements (scripts, styles, head, etc.).
    3. Optionally removing other user-specified elements (e.g., nav, footer).
    4. Using BeautifulSoup's `get_text()` for final extraction.

    Args:
        soup_or_tag: The BeautifulSoup object (representing the whole document)
                     or a specific bs4.element.Tag to extract text from.
        main_content_selectors: An optional list of CSS selectors. The function
                                will try these in order to find a primary content
                                container. The first one found is used as the basis
                                for text extraction. If None or if no selector matches,
                                the entire `soup_or_tag` is used.
        remove_selectors: An optional list of CSS selectors for elements that should
                          be removed from the soup/tag before text extraction
                          (e.g., '.ads', 'nav', 'footer').
        separator: The separator string to use between text blocks when calling
                   `get_text()`. Defaults to a single space.
        custom_logger: An optional custom logger instance. If not provided,
                       the module-level logger is used.

    Returns:
        str: A string containing the extracted visible text. Returns an empty
             string if the input is invalid or an error occurs during processing.

    Side Effects:
        - Modifies a copy of the input BeautifulSoup/Tag object by decomposing elements.
          The original object passed by the caller is not altered.
        - Logs debug or error messages.
    """
    log = custom_logger or logger

    if not soup_or_tag:
        log.warning("Cannot extract text from None input for soup_or_tag.")
        return ""

    try:
        # Work on a copy to avoid modifying the original soup/tag passed by the caller.
        # str(soup_or_tag) re-parses, ensuring a deep copy for BeautifulSoup objects.
        # .copy() is for Tag objects, but might not be deep enough for all cases if children are complex.
        # Re-parsing from string is safer for ensuring complete detachment if soup_or_tag is a Tag.
        if isinstance(soup_or_tag, BeautifulSoup):
            # If it's already a full soup, re-parse its string representation
            # Use 'html.parser' as fallback if parser is not available
            parser_name = (
                getattr(soup_or_tag.parser, "name", "html.parser")
                if soup_or_tag.parser
                else "html.parser"
            )
            current_scope = BeautifulSoup(str(soup_or_tag), features=parser_name)
        elif isinstance(soup_or_tag, Tag):
            # If it's a Tag, convert to string and re-parse to ensure it's a new soup structure
            # Tag objects don't have parser attribute, so use 'html.parser' as fallback
            current_scope = BeautifulSoup(str(soup_or_tag), "html.parser")
        else:
            log.error(
                "Invalid input type for text extraction: %s. Expected BeautifulSoup or Tag.",
                type(soup_or_tag),
            )
            return ""

        # current_scope is now always a BeautifulSoup object, representing the element to work on.
        target_element: Union[BeautifulSoup, Tag] = current_scope

        # 1. Try to narrow down to main content area if selectors are provided
        if main_content_selectors:
            found_main_content = False
            for selector in main_content_selectors:
                try:
                    selected_area = target_element.select_one(selector)
                    if selected_area:
                        target_element = (
                            selected_area  # Update target_element to the selected area
                        )
                        log.debug(
                            "Focused on main content area selected by: '%s'", selector
                        )
                        found_main_content = True
                        break  # Use the first matching main content selector
                except Exception as e_sel:  # Catch errors from invalid selectors
                    log.warning(
                        "Error applying main_content_selector '%s': %s", selector, e_sel
                    )
            if not found_main_content:
                log.debug(
                    "No specific main content area found by selectors; using the initial scope."
                )

        # 2. Remove common non-visible or irrelevant elements from the target_element
        # These are typically script, style, head, meta, link, noscript.
        elements_to_always_remove = [
            "script",
            "style",
            "head",
            "meta",
            "link",
            "noscript",
            "button",
            "input",
            "select",
            "textarea",
            "form",
            "iframe",
        ]
        for element_type in elements_to_always_remove:
            # Decompose works directly on the elements found within target_element
            for el in target_element.find_all(element_type):
                el.decompose()

        # 3. Remove user-specified elements by selectors from the target_element
        if remove_selectors:
            for selector in remove_selectors:
                try:
                    for el in target_element.select(selector):
                        el.decompose()
                    log.debug(
                        "Decomposed element(s) matching user selector: '%s'", selector
                    )
                except Exception as e_rem_sel:
                    log.warning(
                        "Error applying remove_selector '%s': %s", selector, e_rem_sel
                    )

        # 4. Extract text from the cleaned target_element
        # `get_text()` is called on the potentially narrowed and cleaned `target_element`.
        text = target_element.get_text(separator=separator, strip=True)
        return text

    except Exception as e:
        log.error("Error during visible text extraction: %s", e, exc_info=True)
        return ""


def sanitize_html_content(html_content: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.

    Args:
        html_content: Raw HTML content to sanitize

    Returns:
        str: Sanitized HTML content safe for display
    """
    if not html_content:
        return ""

    # Remove dangerous tags and attributes
    dangerous_tags = ["script", "style", "iframe", "object", "embed", "applet", "meta"]
    dangerous_attrs = [
        "onclick",
        "onload",
        "onerror",
        "onmouseover",
        "onfocus",
        "onblur",
    ]

    soup = BeautifulSoup(html_content, "html.parser")

    # Remove dangerous tags
    for tag_name in dangerous_tags:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    # Remove dangerous attributes from all tags
    for tag in soup.find_all():
        for attr in dangerous_attrs:
            if attr in tag.attrs:
                del tag.attrs[attr]

        # Remove javascript: and data: URLs
        if "href" in tag.attrs:
            href = tag.attrs["href"]
            if href.startswith(("javascript:", "data:", "vbscript:")):
                del tag.attrs["href"]

        if "src" in tag.attrs:
            src = tag.attrs["src"]
            if src.startswith(("javascript:", "data:", "vbscript:")):
                del tag.attrs["src"]

    return str(soup)


def extract_text_from_element(element: Union[BeautifulSoup, Tag]) -> str:
    """
    Extract clean text from a BeautifulSoup element.

    Args:
        element: BeautifulSoup object or Tag to extract text from

    Returns:
        str: Extracted text content
    """
    if not element:
        return ""

    try:
        # Use the existing extract_visible_text function for consistency
        return extract_visible_text(element)
    except Exception as e:
        logger.error("Error extracting text from element: %s", e)
        return ""
