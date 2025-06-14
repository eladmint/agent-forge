"""Pydantic models for structuring event-related data.

This module defines the core data structures used by various agents for
representing organizations, speakers, and comprehensive event details.
These models ensure data consistency, provide type hinting, and enable
data validation throughout the event processing pipeline.

Framework Status: ✅ Framework-free compatible
- Used by Enhanced Orchestrator (production agents)
- Used by experimental agents in agents/experimental/
- Supports both production and specialized use cases
- All 13/13 agents now framework-free (migrated June 3, 2025)

Usage:
- Production: Enhanced Orchestrator coordinates agents using these models
- Experimental: Specialized agents use these models for custom workflows
"""

from typing import Any, List, Optional
from urllib.parse import urlparse  # For basic URL validation

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Helper function for validating non-empty strings
def check_not_empty(field_name: str):
    """Returns a validator that checks if a string field is not empty or just whitespace."""

    def validator(value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError(
                f"{field_name} must not be empty or consist only of whitespace."
            )
        return value

    return validator


# Helper function for validating lists of strings (e.g., URLs or tags)
def check_list_item_not_empty(field_name: str):
    """Returns a validator that checks if all string items in a list are non-empty."""

    def validator(values: List[str]) -> List[str]:
        for v in values:
            if not isinstance(v, str) or not v.strip():
                raise ValueError(
                    f"All items in {field_name} must be non-empty strings."
                )
        return values

    return validator


# Helper function for basic URL string validation (more flexible than HttpUrl)
def check_string_url(field_name: str):
    """Returns a validator that checks if a string is a plausible URL."""

    def validator(value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if (
            not value.strip()
        ):  # Allow empty string if Optional, but if provided, should be valid
            # Or raise ValueError here if empty string is not allowed even for Optional fields
            # For now, allowing empty string to be None later if needed, or caught by non-empty validator if chained
            return value
        try:
            parsed = urlparse(value)
            # Basic check: scheme (http/https) and netloc (domain) must be present for absolute URLs.
            # Relative URLs (no scheme, no netloc, but path exists) could also be considered valid here
            # depending on use case. For now, we are more lenient.
            if not (
                (parsed.scheme and parsed.netloc)
                or (not parsed.scheme and not parsed.netloc and parsed.path)
            ):
                if not (
                    value.startswith("/")
                    or value.startswith("./")
                    or value.startswith("../")
                ):  # Allow relative paths
                    # Heuristic: if it doesn't look like a common relative path, and lacks scheme/netloc, it's suspicious.
                    # This won't catch all invalid URLs but is a basic sanity check for string fields.
                    # For stricter validation, Pydantic's HttpUrl type should be used.
                    pass  # Relaxing this for now, as many internal/partial URLs are used.
                    # raise ValueError(f"{field_name} ('{value}') does not appear to be a valid absolute or relative URL structure.")
        except (
            ValueError
        ):  # Catches errors from urlparse itself on truly malformed strings
            raise ValueError(f"{field_name} ('{value}') is not a valid URL structure.")
        return value

    return validator


class OrganizationModel(BaseModel):
    """Represents an organization involved in an event (e.g., organizer, sponsor).

    Attributes:
        name: The official name of the organization.
        url: An optional URL to the organization's official website.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(description="The official name of the organization.")
    url: Optional[str] = Field(
        default=None,
        description="An optional URL to the organization's official website.",
    )

    _validate_name_not_empty = field_validator("name")(
        check_not_empty("Organization name")
    )
    _validate_url_format = field_validator("url")(check_string_url("Organization URL"))


class SpeakerDetailModel(BaseModel):
    """Represents a speaker or presenter at an event.

    Attributes:
        name: The full name of the speaker.
        title: An optional job title or role of the speaker (e.g., "CEO", "Software Engineer").
        organization: An optional organization the speaker is affiliated with.
        url: An optional URL to the speaker's profile, personal website, or company page.
             This is a string to accommodate various URL types (e.g., Luma internal paths).
        social_links: A list of URLs to the speaker's social media profiles (e.g., LinkedIn, Twitter).
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(description="The full name of the speaker.")
    title: Optional[str] = Field(
        default=None, description="The job title or role of the speaker."
    )
    organization: Optional[str] = Field(
        default=None, description="The organization the speaker is affiliated with."
    )
    url: Optional[str] = Field(
        default=None, description="A URL to the speaker's profile or website."
    )
    social_links: List[str] = Field(
        default_factory=list, description="A list of URLs to social media profiles."
    )

    _validate_name_not_empty = field_validator("name")(check_not_empty("Speaker name"))
    _validate_url_format = field_validator("url")(check_string_url("Speaker URL"))

    @field_validator("social_links")
    @classmethod
    def validate_social_links(cls, value: List[str]) -> List[str]:
        if value is None:  # Should not happen with default_factory=list
            return []
        for link in value:
            if not link or not link.strip():
                raise ValueError("Social media links must not be empty strings.")
            # Apply basic string URL check to each social link
            check_string_url("Social media link")(link)  # Reuse the helper
        return value

    @field_validator("title", "organization")
    @classmethod
    def validate_optional_strings_are_none_if_empty(
        cls, value: Optional[str], info: Any
    ) -> Optional[str]:
        """Ensure that if an optional string is provided but is empty/whitespace, it becomes None."""
        if value is not None and not value.strip():
            return None
        return value


class RefinedEventData(BaseModel):
    """A detailed model representing structured information about an event.

    This model consolidates data extracted and processed from various sources,
    aiming to provide a comprehensive overview of an event.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    event_name: str = Field(description="The official name or title of the event.")
    source_url: str = Field(
        description="The original URL from which the event data was extracted."
    )

    start_date: Optional[str] = Field(
        default=None, description="The start date of the event (e.g., YYYY-MM-DD)."
    )
    start_time: Optional[str] = Field(
        default=None,
        description="The start time of the event (e.g., HH:MM or HH:MM AM/PM).",
    )
    end_date: Optional[str] = Field(
        default=None,
        description="The end date of the event (e.g., YYYY-MM-DD), if different from start_date.",
    )
    end_time: Optional[str] = Field(
        default=None,
        description="The end time of the event (e.g., HH:MM or HH:MM AM/PM).",
    )
    timezone: Optional[str] = Field(
        default=None,
        description="The timezone of the event (e.g., PST, UTC+4, Europe/London).",
    )

    location_name: Optional[str] = Field(
        default=None, description="The name of the venue or 'Virtual' if online."
    )
    location_address: Optional[str] = Field(
        default=None, description="The full street address of the event location."
    )
    location_city: Optional[str] = Field(
        default=None, description="The city where the event is held."
    )
    location_country: Optional[str] = Field(
        default=None, description="The country where the event is held."
    )

    description_summary: Optional[str] = Field(
        default=None, description="A concise summary of the event's description."
    )
    full_description: Optional[str] = Field(
        default=None, description="The full description of the event."
    )

    cost_usd: Optional[float] = Field(
        default=None,
        description="The cost of the event in USD. None if free or not specified.",
    )
    cost_details: Optional[str] = Field(
        default=None,
        description="Additional details about cost or ticket types (e.g., 'Free', 'Starts from $99').",
    )

    website: Optional[str] = Field(
        default=None,
        description="The official website for the event, if different from source_url.",
    )

    tags: List[str] = Field(
        default_factory=list, description="Relevant tags or keywords for the event."
    )
    categories: List[str] = Field(
        default_factory=list, description="Categories the event falls into."
    )
    event_social_media_links: List[str] = Field(
        default_factory=list,
        description="Social media links specifically for the event itself.",
    )

    organizers: List[OrganizationModel] = Field(
        default_factory=list,
        description="Organizations responsible for organizing the event.",
    )
    speakers: List[SpeakerDetailModel] = Field(
        default_factory=list, description="Speakers presenting at the event."
    )
    sponsors_partners: List[OrganizationModel] = Field(
        default_factory=list,
        description="Organizations sponsoring or partnering with the event.",
    )

    raw_visible_text_snippet: Optional[str] = Field(
        default=None,
        description="A snippet of the raw text extracted, for context or fallback.",
    )
    extractor_status: Optional[str] = Field(
        default=None,
        description="Status from the initial EventDataExtractorAgent, if applicable.",
    )

    # Validators
    _validate_event_name_not_empty = field_validator("event_name")(
        check_not_empty("Event name")
    )
    _validate_source_url_format = field_validator("source_url")(
        check_string_url("Source URL")
    )
    _validate_website_format = field_validator("website")(
        check_string_url("Event website URL")
    )

    @field_validator("cost_usd")
    @classmethod
    def validate_cost_non_negative(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and value < 0:
            raise ValueError("cost_usd must be non-negative.")
        return value

    # Date/Time string format validation (example - can be made more specific)
    # For now, these are illustrative and can be expanded with regex if needed.
    # A more robust solution might involve using datetime objects internally and serializing/deserializing.
    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, value: Optional[str], info: Any) -> Optional[str]:
        if value is None:
            return value
        # Example: Basic check for YYYY-MM-DD like structure.
        # import re # Would need re import
        # if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
        #     raise ValueError(f"{info.field_name} ('{value}') is not in YYYY-MM-DD format.")
        # For now, keeping it simple as formats might vary from sources.
        if not value.strip():
            return None  # Convert empty string to None
        return value

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, value: Optional[str], info: Any) -> Optional[str]:
        if value is None:
            return value
        # Example: Basic check for HH:MM like structure.
        # import re
        # if not re.match(r"^\d{1,2}:\d{2}(?:\s*(?:AM|PM))?$", value, re.IGNORECASE):
        #     raise ValueError(f"{info.field_name} ('{value}') is not in HH:MM or HH:MM AM/PM format.")
        if not value.strip():
            return None
        return value

    _validate_tags_items = field_validator("tags")(
        check_list_item_not_empty("Tags list")
    )
    _validate_categories_items = field_validator("categories")(
        check_list_item_not_empty("Categories list")
    )

    @field_validator("event_social_media_links")
    @classmethod
    def validate_event_social_links(cls, value: List[str]) -> List[str]:
        if value is None:
            return []  # Should be handled by default_factory
        for link in value:
            if not link or not link.strip():
                raise ValueError("Event social media links must not be empty strings.")
            check_string_url("Event social media link")(link)  # Reuse basic URL check
        return value

    # Ensure optional text fields become None if they are empty strings after stripping
    @field_validator(
        "start_date",
        "start_time",
        "end_date",
        "end_time",
        "timezone",
        "location_name",
        "location_address",
        "location_city",
        "location_country",
        "description_summary",
        "full_description",
        "cost_details",
        "website",
        "raw_visible_text_snippet",
        "extractor_status",
        mode="before",
    )
    @classmethod
    def validate_optional_strings_allow_none(
        cls, value: Optional[str]
    ) -> Optional[str]:
        """Allow None values for optional fields, convert empty strings to None."""
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None  # Convert empty strings to None
        return value

    # For RefinedEventData, ensure that if end_date is provided, start_date is also provided.
    @field_validator("end_date")
    @classmethod
    def validate_end_date_requires_start_date(
        cls, value: Optional[str], values: Any
    ) -> Optional[str]:
        # Pydantic V2: `values` is a `ValidationInfo` object, data is in `values.data`
        if value is not None and (values.data.get("start_date") is None):
            raise ValueError("end_date cannot be set if start_date is not provided.")
        # Add more complex date logic if needed (e.g., end_date >= start_date)
        # This would require parsing string dates to date objects.
        return value

    # Pydantic V2 uses model_validator for model-level validation
    # from pydantic import model_validator
    # @model_validator(mode='after')
    # def check_end_date_after_start_date(self) -> 'RefinedEventData':
    #     if self.start_date and self.end_date:
    #         # This would require parsing string dates to actual date objects for comparison
    #         # For example, using datetime.strptime.
    #         # If not valid, raise ValueError("end_date must be after or the same as start_date.")
    #         pass # Placeholder for more complex date logic
    #     return self


# Enhanced data structures for crypto intelligence and visual analysis
# These are defined in individual agent files but documented here for reference


class EnhancedSponsorDetection(BaseModel):
    """Enhanced sponsor detection with crypto industry knowledge.

    Used by EnhancedImageAnalysisAgent for crypto company recognition.
    Framework-free compatible - used in Enhanced Orchestrator.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    company_name: str = Field(description="Detected company name")
    tier: str = Field(
        description="Sponsor tier: Title/Gold/Silver/Bronze/Partner/Media"
    )
    confidence_score: float = Field(description="Detection confidence (0.0-1.0)")
    crypto_industry_match: bool = Field(
        description="Whether company is in crypto knowledge base"
    )
    detection_source: str = Field(description="Source of detection (image, text, etc.)")


class VisualIntelligenceResult(BaseModel):
    """Visual intelligence analysis results from AdvancedVisualIntelligenceAgent.

    Framework-free compatible - used in Enhanced Orchestrator Phase 3.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    floor_plan_data: Optional[dict] = Field(
        default=None, description="Floor plan analysis data"
    )
    booth_mappings: List[dict] = Field(
        default_factory=list, description="Booth location mappings"
    )
    crowd_analytics: Optional[dict] = Field(
        default=None, description="Crowd flow and density analysis"
    )
    agenda_extracted: List[dict] = Field(
        default_factory=list, description="Visual agenda extraction"
    )


class ScrapingTierResult(BaseModel):
    """Multi-tier scraping result from SuperEnhancedScraperAgent.

    Framework-free experimental agent - available for specialized use cases.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    status: str = Field(description="Result status: Success/Failed/Partial")
    tier_used: int = Field(
        description="Tier used: 1 (Playwright), 2 (Steel Browser), 3 (Premium)"
    )
    tier_name: str = Field(description="Human-readable tier name")
    response_time: float = Field(description="Processing time in seconds")
    data: Optional[dict] = Field(default=None, description="Extracted data")
    error: Optional[str] = Field(default=None, description="Error message if failed")


# Framework migration notes:
# - All models compatible with both Enhanced Orchestrator and experimental agents
# - No framework dependencies in model definitions
# - Supports both production workflows and specialized use cases
# - Enhanced models provide crypto industry intelligence and visual analysis capabilities
