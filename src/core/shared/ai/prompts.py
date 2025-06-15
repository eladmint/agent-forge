"""
Prompt templates and generation functions for Agent Forge operations.

This module contains all prompt templates used for AI processing, including
event data extraction, content analysis, and other AI-driven operations.
"""

import json
import logging
from typing import Any, Dict

from .schemas import event_data_schema

logger = logging.getLogger(__name__)

# Configuration constants
MAX_PROMPT_CHARS = 30000
DEFAULT_TRUNCATION_STRATEGY = "end"  # "end", "middle", "start"


def create_gemini_prompt(
    url: str, text_content: str, max_chars: int = MAX_PROMPT_CHARS
) -> str:
    """
    Create a comprehensive prompt for Gemini AI to extract event data.

    Args:
        url: The source URL of the event page
        text_content: The extracted text content from the page
        max_chars: Maximum characters to include in prompt (default: 30000)

    Returns:
        str: The formatted prompt for AI processing
    """
    truncated_text = truncate_text_smart(text_content, max_chars)

    return f"""
Analyze the following text extracted from the event page URL '{url}'.
Extract the event details according to the schema below.

VERY IMPORTANT INSTRUCTIONS:
1.  **Speakers:** Look ONLY in sections clearly titled "Speakers", "Panelists", "Agenda" (if listing names with talks), "Presenters", "Featured Guests", or similar sections clearly listing speakers like "Speakers & Partners". 
    *   Do NOT extract names from general guest lists, attendee mentions, host sections, or presenter sections unless that section *also* clearly identifies individuals as speakers with roles/organizations.
    *   Extract the speaker's full name (`name`).
    *   Extract their associated Organization/Company (`organization`). 
    *   Extract their Title (`title`).
    *   **Handling Missing Info:** If Organization isn't found, use "N/A". If Title isn't found, use "N/A". If only an Organization is listed, use it for `organization` and "N/A" for `title`. If only a Title is listed, use it for `title` and "N/A" for `organization`.
    *   Extract any URL clearly associated *with that speaker* in that section (`url`), otherwise use null.
    *   **If no section explicitly listing speakers is found, return an empty list [] for "speakers".**
2.  **Sponsors/Partners:** Look ONLY for sections explicitly titled 'Sponsors', 'Partners', 'Supported By', 'In Association With' **for this specific event**, or distinct logo sections clearly associated with **this event**.
    *   Extract the organization's proper name (`name`). Avoid extracting surrounding descriptive phrases or generic text.
    *   Extract any URL clearly associated *with that sponsor/partner* in that section (`url`), otherwise use null.
    *   **Do NOT extract companies mentioned *only* as past partners of the organizer, past attendees, or portfolio companies unless they are also explicitly listed as a sponsor/partner of THIS event.**
    *   **If no section explicitly listing sponsors/partners for this event is found, return an empty list [] for "sponsors_partners".**
3.  **Website:** Look specifically for a link described as the "official website", "event website", "project site", "learn more here", or similar *that is different from the source URL ({url})*. Also look for phrases like "An event by [domain]" (e.g., "An event by aeternuminc.com") and extract the corresponding URL (e.g., `https://aeternuminc.com`).
    *   If a distinct official website link or a link derived from "event by [domain]" is found, extract the full, valid URL (including https://) for the `website` field.
    *   If no separate official website link is explicitly mentioned or found in the text, return `null` for the `website` field. Do NOT use the source URL ({url}) for this field unless it's explicitly stated as the official event site.
4.  **Dates & Times:** 
    *   Extract `start_date` and `end_date` **strictly** in `YYYY-MM-DD` format. If the year is missing or unclear, try to infer it, but if the full date cannot be determined in this format, return `null`.
    *   Extract `start_time` and `end_time` **strictly** in `HH:MM` (24-hour) format. If the time cannot be determined in this format, return `null`.
    *   Extract the `timezone` (e.g., `GST`, `UTC+4`, `PST`). If no timezone is clearly mentioned, return `null`. **Do not return "N/A" for timezone.**
5.  **Social Links:** Look for social media links specifically for the EVENT (not the organizer unless they are the same entity).
    *   Extract links for Twitter, LinkedIn, Facebook, Instagram, Discord, Telegram, etc.
    *   Format each as a key-value pair in the `social_links` object (e.g., `"twitter": "https://twitter.com/token2049"`)
    *   Include only complete, valid URLs (including https://)
    *   If no social media links are found for the event, return an empty object for `social_links`.
6.  **Other Fields:** Extract other event details (name, location, description, etc.) based on the schema.
7.  **Organizer:** Extract the *actual* host or organizer mentioned (e.g., "Hosted by X & Y"). **Do NOT extract the platform name (e.g., 'Luma') as the organizer.** If no specific organizer is mentioned, use `null`.
8.  **Output:** Return ONLY a single valid JSON object matching the schema. No explanations, apologies, or markdown formatting.

REMEMBER: Stick strictly to the specified sections for speakers and sponsors/partners. Adhere strictly to the requested formats for dates, times, and timezone, returning `null` if the format cannot be met. Prioritize finding a distinct official website if mentioned.

Schema:
{json.dumps(event_data_schema, indent=2)}

Extracted Text:
---
{truncated_text}
---

Return ONLY the JSON object.
"""


def create_speaker_extraction_prompt(text_content: str, event_context: str = "") -> str:
    """
    Create a focused prompt for extracting speaker information from text.

    Args:
        text_content: The text content to analyze
        event_context: Optional context about the event

    Returns:
        str: Formatted prompt for speaker extraction
    """
    return f"""
Extract speaker information from the following text. Look for sections clearly labeled as "Speakers", "Panelists", "Presenters", or "Featured Guests".

{f"Event Context: {event_context}" if event_context else ""}

For each speaker found, extract:
- Full name
- Organization/Company (use "N/A" if not found)
- Title/Role (use "N/A" if not found)  
- Associated URL (use null if not found)

Return as a JSON array of speaker objects. If no speakers are found, return an empty array.

Text to analyze:
---
{text_content[:MAX_PROMPT_CHARS]}
---

Return ONLY the JSON array.
"""


def create_event_summary_prompt(event_data: Dict[str, Any]) -> str:
    """
    Create a prompt for generating a natural language summary of event data.

    Args:
        event_data: Structured event data

    Returns:
        str: Prompt for generating event summary
    """
    return f"""
Create a concise, professional summary of the following event information. 
Focus on the key details that would be most useful to potential attendees.

Event Data:
{json.dumps(event_data, indent=2)}

Generate a 2-3 sentence summary that includes:
- Event name and type
- Date, time, and location (if available)
- Brief description of purpose/content
- Key speakers (if any)

Write in a professional, informative tone suitable for event listings.
"""


def create_content_classification_prompt(text_content: str) -> str:
    """
    Create a prompt for classifying content type and relevance.

    Args:
        text_content: Content to classify

    Returns:
        str: Classification prompt
    """
    return f"""
Analyze the following text and classify it according to these categories:

1. Content Type: (event, speaker_bio, organization_profile, news_article, other)
2. Relevance Score: (1-10, where 10 is highly relevant to blockchain/crypto events)
3. Key Topics: (list of main topics/themes found)
4. Quality Score: (1-10, based on completeness and clarity of information)

Text to analyze:
---
{text_content[:MAX_PROMPT_CHARS]}
---

Return your analysis as a JSON object with the fields: content_type, relevance_score, key_topics (array), quality_score.
"""


def truncate_text_smart(
    text: str, max_chars: int, strategy: str = DEFAULT_TRUNCATION_STRATEGY
) -> str:
    """
    Intelligently truncate text while preserving important information.

    Args:
        text: Text to truncate
        max_chars: Maximum characters to keep
        strategy: Truncation strategy ("end", "middle", "start")

    Returns:
        str: Truncated text
    """
    if len(text) <= max_chars:
        return text

    if strategy == "end":
        # Keep beginning, truncate end
        return text[:max_chars]

    elif strategy == "start":
        # Keep end, truncate beginning
        return text[-max_chars:]

    elif strategy == "middle":
        # Keep beginning and end, truncate middle
        keep_each = max_chars // 2
        start_part = text[:keep_each]
        end_part = text[-keep_each:]
        return f"{start_part}\n\n[... content truncated ...]\n\n{end_part}"

    else:
        # Default to end truncation
        return text[:max_chars]


def create_data_validation_prompt(data: Dict[str, Any], schema: Dict[str, Any]) -> str:
    """
    Create a prompt for validating extracted data against a schema.

    Args:
        data: Data to validate
        schema: Expected schema

    Returns:
        str: Validation prompt
    """
    return f"""
Validate the following extracted data against the provided schema. 
Check for:
- Missing required fields
- Incorrect data types
- Invalid formats (dates, times, URLs)
- Logical inconsistencies

Data to validate:
{json.dumps(data, indent=2)}

Expected schema:
{json.dumps(schema, indent=2)}

Return a JSON object with:
- "is_valid": boolean
- "errors": array of error descriptions
- "warnings": array of potential issues
- "suggestions": array of improvement suggestions
"""


class PromptTemplate:
    """
    A class for managing reusable prompt templates.
    """

    def __init__(self, template: str, required_params: list = None):
        """
        Initialize a prompt template.

        Args:
            template: The template string with placeholders
            required_params: List of required parameter names
        """
        self.template = template
        self.required_params = required_params or []

    def format(self, **kwargs) -> str:
        """
        Format the template with provided parameters.

        Args:
            **kwargs: Template parameters

        Returns:
            str: Formatted prompt

        Raises:
            ValueError: If required parameters are missing
        """
        # Check for required parameters
        missing_params = [
            param for param in self.required_params if param not in kwargs
        ]
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")

        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Template parameter not provided: {e}")

    def validate_params(self, **kwargs) -> list:
        """
        Validate template parameters without formatting.

        Args:
            **kwargs: Parameters to validate

        Returns:
            list: List of validation errors
        """
        errors = []

        # Check required parameters
        for param in self.required_params:
            if param not in kwargs:
                errors.append(f"Missing required parameter: {param}")

        # Check for placeholders in template
        try:
            self.template.format(**kwargs)
        except KeyError as e:
            errors.append(f"Template expects parameter: {e}")

        return errors


# Common prompt templates
EVENT_EXTRACTION_TEMPLATE = PromptTemplate(
    create_gemini_prompt("{url}", "{text_content}"),
    required_params=["url", "text_content"],
)

SPEAKER_EXTRACTION_TEMPLATE = PromptTemplate(
    create_speaker_extraction_prompt("{text_content}", "{event_context}"),
    required_params=["text_content"],
)

CONTENT_CLASSIFICATION_TEMPLATE = PromptTemplate(
    create_content_classification_prompt("{text_content}"),
    required_params=["text_content"],
)
