#!/usr/bin/env python3
"""
Advanced Event Extractor - Integrating Advanced Agent Capabilities
Framework-free extractor enhanced with visual intelligence, MCP browser control, 
and crypto industry knowledge for maximum extraction quality.
"""

import asyncio
import json
import logging
import re
import ssl
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

# Import browser automation
try:
    from browser_automation_orchestrator import (
        BrowserExtractionResult,
        HybridOrchestrator,
        RobustBrowserAutomation,
    )

    BROWSER_AUTOMATION_AVAILABLE = True
except ImportError:
    BROWSER_AUTOMATION_AVAILABLE = False

    # Define dummy classes for development environments
    class RobustBrowserAutomation:
        def __init__(self, *args, **kwargs):
            pass

        async def initialize(self):
            return False

        async def cleanup(self):
            pass

        # Add missing attributes that are referenced
        _orchestrator_ai_method = None
        _orchestrator_save_method = None

    class HybridOrchestrator:
        def __init__(self, *args, **kwargs):
            pass

        async def initialize(self):
            pass

        async def cleanup(self):
            pass

        async def extract_page_intelligent(self, *args, **kwargs):
            return None

    class BrowserExtractionResult:
        def __init__(self, *args, **kwargs):
            pass


# Direct imports without Swarms
import os
import sys

sys.path.insert(0, os.getcwd())

# Import Vertex AI directly with error handling
import vertexai

try:
    from vertexai.generative_models import GenerativeModel, Part
except ImportError:
    try:
        # Fallback for older versions
        from vertexai.preview.generative_models import GenerativeModel, Part
    except ImportError:
        # Ultimate fallback - define dummy classes for deployment
        class GenerativeModel:
            def __init__(self, *args, **kwargs):
                pass

            def generate_content(self, *args, **kwargs):
                return type(
                    "Response", (), {"text": '{"error": "AI model not available"}'}
                )()

        class Part:
            @staticmethod
            def from_data(*args, **kwargs):
                return None

            @staticmethod
            def from_uri(*args, **kwargs):
                return None


from api.core.config import VERTEX_LOCATION, VERTEX_PROJECT_ID, get_secret

# Import database functionality
try:
    from agent_forge.core.shared.database.client import (
        create_client as create_supabase_client,
    )
    from agent_forge.core.shared.database.client import (
        get_supabase_client,
    )
    from agent_forge.core.shared.database.event_data import save_event_data

    DATABASE_IMPORTS_AVAILABLE = True

    # Try to import check_event_exists_by_url, but continue if it doesn't exist
    try:
        from agent_forge.core.shared.database.search import check_event_exists_by_url
    except ImportError:

        def check_event_exists_by_url(url: str) -> bool:
            return False

except ImportError as e:
    print(f"Database imports not available: {e}")
    import traceback

    print(f"Full traceback: {traceback.format_exc()}")
    DATABASE_IMPORTS_AVAILABLE = False

    # Define dummy functions for environments without database
    async def save_event_data(data):
        return True

    def create_supabase_client():
        return None

    def check_event_exists_by_url(url: str) -> bool:
        return False

    def get_supabase_client():
        return None

    async def check_event_exists_by_url(url):
        return None


# Import existing monitoring functionality
try:
    from agent_forge.core.shared.logging.logging_utils import get_logger
    from agent_forge.core.shared.monitoring.monitoring import (
        start_orchestrator_timer,
        stop_orchestrator_timer,
        track_orchestrator_error,
        track_orchestrator_event_completion,
        track_orchestrator_session,
        track_orchestrator_session_completion,
    )

    MONITORING_IMPORTS_AVAILABLE = True
except ImportError as e:
    # Use basic logging since logger may not be defined yet
    logging.warning(f"Monitoring imports not available: {e}")
    MONITORING_IMPORTS_AVAILABLE = False

    # Define dummy functions for environments without monitoring
    def track_orchestrator_session(*args, **kwargs):
        pass

    def track_orchestrator_event_completion(*args, **kwargs):
        pass

    def track_orchestrator_session_completion(*args, **kwargs):
        pass

    def track_orchestrator_error(*args, **kwargs):
        pass

    def start_orchestrator_timer(*args, **kwargs):
        return None

    def stop_orchestrator_timer(*args, **kwargs):
        pass

    def get_logger(name):
        return logging.getLogger(name)


logger = logging.getLogger(__name__)


# Enhanced data structures
class SponsorTier(Enum):
    """Sponsor tier classification"""

    TITLE = "title"
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    PARTNER = "partner"
    MEDIA = "media"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Confidence level for detection"""

    HIGH = "high"  # 0.8+
    MEDIUM = "medium"  # 0.5-0.8
    LOW = "low"  # 0.3-0.5
    VERY_LOW = "very_low"  # <0.3


class BoothSize(Enum):
    """Booth size classification"""

    LARGE = "large"  # Major sponsors, prominent placement
    MEDIUM = "medium"  # Standard sponsors
    SMALL = "small"  # Community sponsors
    KIOSK = "kiosk"  # Small info stands
    UNKNOWN = "unknown"


@dataclass
class EnhancedSponsorDetection:
    """Enhanced sponsor detection with tier and confidence"""

    name: str
    tier: SponsorTier
    confidence: float
    confidence_level: ConfidenceLevel
    context: str
    detection_source: str  # 'logo', 'text', 'booth_analysis'
    booth_info: Optional[Dict] = None


@dataclass
class EnhancedSpeakerDetection:
    """Enhanced speaker detection with crypto industry context"""

    name: str
    title: Optional[str]
    company: Optional[str]
    bio: Optional[str]
    confidence: float
    confidence_level: ConfidenceLevel
    industry_match: bool  # True if matched against crypto industry knowledge
    session_info: Optional[Dict] = None


@dataclass
class VisualIntelligenceResult:
    """Results from visual intelligence analysis"""

    booth_detections: Optional[List[Dict]] = None
    agenda_items: Optional[List[Dict]] = None
    crowd_analysis: Optional[Dict] = None
    floor_plan_analysis: Optional[Dict] = None

    def __post_init__(self):
        if self.booth_detections is None:
            self.booth_detections = []
        if self.agenda_items is None:
            self.agenda_items = []


@dataclass
class CalendarExtractionReport:
    """Comprehensive calendar extraction report for database integration"""

    extraction_id: str
    timestamp: str
    source_url: str
    total_events_found: int
    events_already_in_db: int
    events_added_to_db: int
    events_rejected: int
    rejection_reasons: List[Dict[str, Any]]
    processing_details: Dict[str, Any]
    success: bool


@dataclass
class EnhancedExtractionResult:
    """Enhanced result from orchestration extraction with advanced capabilities"""

    url: str
    status: str  # success, error, timeout
    processing_time: float
    completeness_score: float = 0.0

    # Event data
    name: str = ""
    description: str = ""
    start_date: str = ""
    end_date: str = ""
    location: str = ""
    speakers: Optional[List[EnhancedSpeakerDetection]] = None
    sponsors: Optional[List[EnhancedSponsorDetection]] = None
    organizers: Optional[List[Dict]] = None
    tags: Optional[List[str]] = None

    # Enhanced analysis data
    images_analyzed: int = 0
    external_sites_scraped: int = 0
    data_sources: Optional[List[str]] = None
    error_message: str = ""

    # New advanced capabilities
    visual_intelligence: Optional[VisualIntelligenceResult] = None
    mcp_browser_used: bool = False
    crypto_industry_matches: int = 0
    data_refinement_applied: bool = False

    # Missing attributes for tier processing
    storage_tier: str = "standard"
    quality_metadata: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    # Calendar extraction integration
    calendar_extraction_report: Optional[CalendarExtractionReport] = None
    database_integrated: bool = False

    # Additional fields that may be referenced
    success: bool = True

    def __post_init__(self):
        if self.speakers is None:
            self.speakers = []
        if self.sponsors is None:
            self.sponsors = []
        if self.organizers is None:
            self.organizers = []
        if self.data_sources is None:
            self.data_sources = []
        if self.tags is None:
            self.tags = []
        if self.visual_intelligence is None:
            self.visual_intelligence = VisualIntelligenceResult()
        # Set success based on status
        self.success = self.status == "success"


# URL Resolution Enhancement for 90% Success Strategy
@dataclass
class URLResolutionResult:
    """Result from comprehensive URL resolution"""

    original_url: str
    final_url: str
    redirect_chain: List[str]
    resolution_successful: bool
    final_status: int
    resolution_time: float = 0.0
    error_message: str = ""


class TooManyRedirectsError(Exception):
    """Raised when URL resolution exceeds maximum redirects"""

    pass


class EnhancedURLResolver:
    """Comprehensive URL resolution before Enhanced Orchestrator processing"""

    def __init__(self, session: aiohttp.ClientSession, max_redirects: int = 10):
        self.session = session
        self.max_redirects = max_redirects
        self.logger = logging.getLogger(f"{__name__}.URLResolver")

    async def resolve_event_url_chain(self, url: str) -> URLResolutionResult:
        """Follow complete redirect chain to final destination"""
        start_time = time.time()
        redirect_chain = []
        current_url = url

        try:
            for redirect_count in range(self.max_redirects):
                # Use session with custom headers to avoid bot detection
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }

                async with self.session.get(
                    current_url,
                    allow_redirects=False,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as response:
                    # Check for redirect status codes
                    if response.status in [301, 302, 303, 307, 308]:
                        # Safely get Location header
                        next_url = (
                            response.headers.get("Location")
                            if response.headers
                            else None
                        )
                        if next_url:
                            # Handle relative URLs
                            next_url = urljoin(current_url, next_url)
                            redirect_chain.append(current_url)
                            current_url = next_url
                            self.logger.debug(
                                f"🔄 Redirect {redirect_count + 1}: {current_url}"
                            )
                            continue

                    # Final destination reached or non-redirect response
                    resolution_time = time.time() - start_time

                    return URLResolutionResult(
                        original_url=url,
                        final_url=current_url,
                        redirect_chain=redirect_chain,
                        resolution_successful=True,
                        final_status=response.status,
                        resolution_time=resolution_time,
                    )

            # Too many redirects
            raise TooManyRedirectsError(
                f"Exceeded {self.max_redirects} redirects for {url}"
            )

        except asyncio.TimeoutError:
            resolution_time = time.time() - start_time
            return URLResolutionResult(
                original_url=url,
                final_url=current_url,
                redirect_chain=redirect_chain,
                resolution_successful=False,
                final_status=0,
                resolution_time=resolution_time,
                error_message="Timeout during URL resolution",
            )
        except Exception as e:
            resolution_time = time.time() - start_time
            return URLResolutionResult(
                original_url=url,
                final_url=current_url,
                redirect_chain=redirect_chain,
                resolution_successful=False,
                final_status=0,
                resolution_time=resolution_time,
                error_message=str(e),
            )

    async def batch_resolve_urls(
        self, urls: List[str]
    ) -> Dict[str, URLResolutionResult]:
        """Batch resolve all URLs before processing with detailed results"""
        self.logger.info(f"🔗 Starting batch URL resolution for {len(urls)} URLs")
        resolved_results = {}

        # Use semaphore to limit concurrent URL resolutions
        semaphore = asyncio.Semaphore(5)  # Conservative limit

        async def resolve_single_url(url: str) -> Tuple[str, URLResolutionResult]:
            async with semaphore:
                try:
                    result = await self.resolve_event_url_chain(url)
                    if result.resolution_successful:
                        self.logger.debug(f"✅ Resolved {url} → {result.final_url}")
                    else:
                        self.logger.warning(
                            f"⚠️ Resolution failed for {url}: {result.error_message}"
                        )
                    return url, result
                except Exception as e:
                    self.logger.error(f"❌ URL resolution error for {url}: {e}")
                    return url, URLResolutionResult(
                        original_url=url,
                        final_url=url,  # Fallback to original
                        redirect_chain=[],
                        resolution_successful=False,
                        final_status=0,
                        error_message=str(e),
                    )

        # Execute batch resolution
        tasks = [resolve_single_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        successful_resolutions = 0
        unique_final_urls = set()

        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"❌ Batch resolution exception: {result}")
                continue

            url, resolution_result = result
            resolved_results[url] = resolution_result

            if resolution_result.resolution_successful:
                successful_resolutions += 1
                unique_final_urls.add(resolution_result.final_url)

        # Log resolution statistics
        resolution_rate = successful_resolutions / len(urls) if urls else 0
        duplicate_eliminations = len(urls) - len(unique_final_urls)

        self.logger.info("📊 URL Resolution Statistics:")
        self.logger.info(f"   Original URLs: {len(urls)}")
        self.logger.info(
            f"   Successful Resolutions: {successful_resolutions} ({resolution_rate:.1%})"
        )
        self.logger.info(f"   Unique Final URLs: {len(unique_final_urls)}")
        self.logger.info(f"   Duplicate Eliminations: {duplicate_eliminations}")

        return resolved_results


# Platform Classification for Week 2 Expansion
class PlatformRouter:
    """Intelligent platform routing for multi-platform event support"""

    def __init__(self):
        self.platform_patterns = {
            "luma": ["lu.ma", "luma.com"],
            "eventbrite": ["eventbrite.com", "eventbrite.co.uk"],
            "meetup": ["meetup.com"],
            "facebook": ["facebook.com/events", "fb.me"],
            "external": ["conference", "summit", "event", "expo"],
            "complex": ["medium.com", "github.com", "linkedin.com"],
        }
        self.logger = logging.getLogger(f"{__name__}.PlatformRouter")

    def classify_url(self, url: str) -> Dict[str, Any]:
        """Classify URL and determine optimal processing strategy"""
        url_lower = url.lower()

        # Check for known platforms
        for platform, patterns in self.platform_patterns.items():
            for pattern in patterns:
                if pattern in url_lower:
                    complexity_score = self._calculate_complexity(url, platform)
                    return {
                        "platform": platform,
                        "complexity": complexity_score,
                        "recommended_strategy": self._get_strategy(
                            platform, complexity_score
                        ),
                        "tier": self._get_processing_tier(platform, complexity_score),
                    }

        # Default classification for unknown URLs
        return {
            "platform": "unknown",
            "complexity": 0.5,
            "recommended_strategy": "standard_with_fallback",
            "tier": 1,
        }

    def _calculate_complexity(self, url: str, platform: str) -> float:
        """Calculate URL complexity score for processing strategy selection"""
        complexity_factors = {
            "has_query_params": "?" in url,
            "has_hash_fragments": "#" in url,
            "long_path": len(url.split("/")) > 5,
            "dynamic_content": platform in ["facebook", "linkedin", "twitter"],
            "anti_bot_likely": platform in ["medium", "github", "linkedin"],
            "external_platform": platform not in ["luma", "eventbrite", "meetup"],
        }

        return sum(complexity_factors.values()) / len(complexity_factors)

    def _get_strategy(self, platform: str, complexity: float) -> str:
        """Determine optimal processing strategy"""
        if platform == "luma":
            return "standard" if complexity < 0.3 else "enhanced"
        elif platform in ["eventbrite", "meetup"]:
            return "enhanced"
        elif complexity > 0.6:
            return "steel_browser"
        else:
            return "playwright"

    def _get_processing_tier(self, platform: str, complexity: float) -> int:
        """Determine processing tier (1=standard, 2=enhanced, 3=steel_browser)"""
        if platform == "luma" and complexity < 0.3:
            return 1
        elif complexity > 0.7:
            return 3
        else:
            return 2


@dataclass
class ContentProcessingResult:
    """Result of content processing with tier information"""

    success: bool
    content: str = ""
    processing_tier: str = ""
    completeness_target: float = 0.0
    reason: str = ""
    processing_time: float = 0.0


@dataclass
class AIExtractionResult:
    """Result of AI extraction with retry information"""

    success: bool
    data: Dict[str, Any] = None
    attempt_count: int = 0
    processing_method: str = ""
    content_size: int = 0
    error_message: str = ""


class ProgressiveContentProcessor:
    """Implement tiered content processing thresholds for Week 3 optimization"""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.content_tiers = {
            "premium": {"min_chars": 2000, "completeness_target": 0.85},
            "standard": {"min_chars": 1000, "completeness_target": 0.70},
            "basic": {"min_chars": 500, "completeness_target": 0.50},
            "preliminary": {"min_chars": 200, "completeness_target": 0.30},
        }

    def determine_processing_tier(self, content: str, url: str) -> str:
        """Determine appropriate processing tier based on content analysis"""
        content_length = len(content)

        # Check for structured data indicators
        has_json_ld = "application/ld+json" in content
        has_meta_tags = "og:title" in content or "twitter:title" in content
        is_luma_event = "lu.ma" in url
        has_event_schema = "schema.org/Event" in content

        # Enhanced tier determination with multiple factors
        if content_length >= 2000 and (
            has_json_ld or is_luma_event or has_event_schema
        ):
            return "premium"
        elif content_length >= 1000 and (has_meta_tags or is_luma_event):
            return "standard"
        elif content_length >= 500:
            return "basic"
        else:
            return "preliminary"

    async def process_with_tier(
        self, content: str, tier: str, url: str
    ) -> ContentProcessingResult:
        """Process content according to tier requirements"""
        start_time = time.time()
        tier_config = self.content_tiers[tier]

        if len(content) < tier_config["min_chars"]:
            return ContentProcessingResult(
                success=False,
                reason=f"Content below {tier} tier minimum ({len(content)} < {tier_config['min_chars']} chars)",
                processing_tier=tier,
                processing_time=time.time() - start_time,
            )

        # Content meets tier requirements
        self.logger.info(
            f"🎯 Processing content with {tier} tier (target: {tier_config['completeness_target']:.1%})"
        )

        return ContentProcessingResult(
            success=True,
            content=content,
            processing_tier=tier,
            completeness_target=tier_config["completeness_target"],
            processing_time=time.time() - start_time,
        )


class RobustAIProcessor:
    """AI processing with comprehensive retry and fallback strategies for Week 3 optimization"""

    def __init__(
        self, model, crypto_companies=None, crypto_personalities=None, logger=None
    ):
        self.model = model
        self.crypto_companies = crypto_companies or set()
        self.crypto_personalities = crypto_personalities or set()
        self.logger = logger or logging.getLogger(__name__)
        self.max_retries = 3

    async def extract_with_retry(self, content: str, url: str) -> AIExtractionResult:
        """AI extraction with intelligent retry logic and progressive content chunking"""

        for attempt in range(self.max_retries):
            try:
                self.logger.info(
                    f"🤖 AI extraction attempt {attempt + 1}/{self.max_retries}"
                )

                # Progressive content chunking strategy
                if attempt == 0:
                    # Full content first (up to 12000 chars)
                    processed_content = content[:12000]
                    method = "full_content"
                elif attempt == 1:
                    # Intelligent content chunking - extract key sections
                    processed_content = self._extract_key_sections(content)
                    method = "key_sections"
                else:
                    # Minimal essential content
                    processed_content = self._extract_minimal_content(content)
                    method = "minimal_content"

                self.logger.debug(
                    f"📝 Processing {len(processed_content)} chars with {method} method"
                )

                # Execute AI extraction with timeout
                result = await asyncio.wait_for(
                    self._ai_extract_with_crypto_knowledge(processed_content, url),
                    timeout=30.0,
                )

                if result and result.get("success", True):
                    return AIExtractionResult(
                        success=True,
                        data=result,
                        attempt_count=attempt + 1,
                        processing_method=method,
                        content_size=len(processed_content),
                    )

            except asyncio.TimeoutError:
                self.logger.warning(f"⏱️ AI processing timeout on attempt {attempt + 1}")
                continue
            except Exception as e:
                self.logger.warning(f"⚠️ AI processing error attempt {attempt + 1}: {e}")
                continue

        # All retries failed - use rule-based fallback
        self.logger.info(
            "🔄 All AI retries failed, falling back to rule-based extraction"
        )
        fallback_result = await self._rule_based_extraction_fallback(content, url)

        return AIExtractionResult(
            success=bool(fallback_result),
            data=fallback_result,
            attempt_count=self.max_retries,
            processing_method="rule_based_fallback",
            content_size=len(content),
        )

    def _extract_key_sections(self, content: str) -> str:
        """Extract key sections for AI processing (attempt 2)"""
        try:
            soup = BeautifulSoup(content, "html.parser")
            key_sections = []

            # Title and meta information
            if soup.find("title"):
                title_tag = soup.find("title")
                if title_tag:
                    key_sections.append(f"TITLE: {title_tag.get_text()}")

            # Meta descriptions
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                content = (
                    meta_desc.get("content") if hasattr(meta_desc, "get") else None
                )
                if content:
                    key_sections.append(f"DESCRIPTION: {content}")

            # Event-specific content selectors
            event_selectors = [
                "[data-event]",
                ".event-details",
                ".event-info",
                ".event-content",
                ".speaker-list",
                ".speakers",
                ".agenda",
                ".schedule",
                ".sponsors",
                ".partners",
                ".organizers",
            ]

            for selector in event_selectors:
                elements = soup.select(selector)
                for elem in elements[:3]:  # Limit to avoid too much content
                    text = elem.get_text(strip=True)[:500]
                    if text:
                        key_sections.append(f"{selector.upper()}: {text}")

            # JSON-LD structured data (highest priority)
            json_ld_scripts = soup.find_all("script", type="application/ld+json")
            for script in json_ld_scripts[:2]:  # Max 2 JSON-LD blocks
                key_sections.append(f"JSON-LD: {script.get_text()}")

            # Main content areas
            main_areas = soup.find_all(
                ["main", "article", ".main-content", ".event-main"]
            )
            for area in main_areas[:1]:  # Just the first main area
                text = area.get_text(strip=True)[:1000]
                if text:
                    key_sections.append(f"MAIN: {text}")

            result = " | ".join(key_sections)[:8000]  # Limit total size
            self.logger.debug(
                f"📋 Extracted {len(key_sections)} key sections, {len(result)} chars"
            )
            return result

        except Exception as e:
            self.logger.warning(
                f"⚠️ Key section extraction failed: {e}, using truncated content"
            )
            return content[:6000]

    def _extract_minimal_content(self, content: str) -> str:
        """Extract minimal essential content (attempt 3)"""
        try:
            soup = BeautifulSoup(content, "html.parser")
            minimal_sections = []

            # Essential elements only
            if soup.find("title"):
                title_tag = soup.find("title")
                if title_tag:
                    minimal_sections.append(title_tag.get_text())

            # Primary headings
            for tag in ["h1", "h2"]:
                headings = soup.find_all(tag)
                for h in headings[:3]:
                    minimal_sections.append(h.get_text(strip=True))

            # Meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                minimal_sections.append(meta_desc.get("content"))

            # First JSON-LD only
            json_ld = soup.find("script", type="application/ld+json")
            if json_ld:
                minimal_sections.append(json_ld.get_text())

            result = " | ".join(minimal_sections)[:4000]  # Very limited size
            self.logger.debug(
                f"🎯 Minimal extraction: {len(minimal_sections)} elements, {len(result)} chars"
            )
            return result

        except Exception as e:
            self.logger.warning(f"⚠️ Minimal extraction failed: {e}, using title only")
            # Final fallback - just the title
            try:
                soup = BeautifulSoup(content, "html.parser")
                title = soup.find("title")
                return title.get_text() if title else content[:500]
            except:
                return content[:500]

    async def _rule_based_extraction_fallback(
        self, content: str, url: str
    ) -> Dict[str, Any]:
        """Rule-based extraction as final fallback when AI fails"""
        try:
            self.logger.info("🔧 Executing rule-based extraction fallback")
            soup = BeautifulSoup(content, "html.parser")

            # Rule-based speaker extraction
            speakers = []
            speaker_patterns = [
                r"speaker[:\s]*([A-Z][a-z]+ [A-Z][a-z]+)",
                r"presented by[:\s]*([A-Z][a-z]+ [A-Z][a-z]+)",
                r"with[:\s]*([A-Z][a-z]+ [A-Z][a-z]+)",
                r"([A-Z][a-z]+ [A-Z][a-z]+)[,\s]*CEO|CTO|founder|co-founder",
            ]

            text_content = soup.get_text()
            for pattern in speaker_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                for match in matches[:3]:  # Limit to avoid noise
                    if len(match) > 2 and match not in [
                        s.get("name") for s in speakers
                    ]:
                        speakers.append(
                            {
                                "name": match,
                                "title": "Speaker",
                                "company": "",
                                "bio": "",
                                "confidence": 0.3,  # Low confidence for rule-based
                                "industry_match": False,
                            }
                        )

            # Rule-based sponsor extraction
            sponsors = []
            sponsor_selectors = [
                ".sponsors",
                ".partners",
                '[class*="sponsor"]',
                '[class*="partner"]',
            ]
            for selector in sponsor_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    # Look for company names (simple pattern)
                    company_links = elem.find_all("a")
                    for link in company_links[:5]:
                        company_name = link.get_text(strip=True)
                        if len(company_name) > 2 and company_name not in [
                            s.get("name") for s in sponsors
                        ]:
                            sponsors.append(
                                {
                                    "name": company_name,
                                    "tier": "partner",
                                    "confidence": 0.4,
                                    "crypto_company": company_name.lower()
                                    in [c.lower() for c in self.crypto_companies],
                                }
                            )

            # Basic event details
            title = soup.find("title")
            title_text = title.get_text() if title else ""

            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc.get("content") if meta_desc else ""

            return {
                "speakers": speakers,
                "sponsors": sponsors,
                "organizers": [],
                "crypto_matches": sum(1 for s in sponsors if s.get("crypto_company")),
                "enhanced_description": description or title_text,
                "topics": [],
                "target_audience": "",
                "success": True,
            }

        except Exception as e:
            self.logger.error(f"❌ Rule-based extraction failed: {e}")
            return {
                "speakers": [],
                "sponsors": [],
                "organizers": [],
                "crypto_matches": 0,
                "enhanced_description": "",
                "topics": [],
                "target_audience": "",
                "success": False,
            }

    async def _ai_extract_with_crypto_knowledge(
        self, html_content: str, url: str
    ) -> Dict[str, Any]:
        """AI extraction method - calls the orchestrator's method with proper error handling"""
        # This is a proxy method that will be set by the orchestrator
        if hasattr(self, "_orchestrator_ai_method"):
            return await self._orchestrator_ai_method(html_content, url)
        else:
            raise NotImplementedError("AI extraction method not properly configured")


class TieredEventStorage:
    """Implement tiered storage for different event quality levels - Week 4 Enhancement"""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.quality_thresholds = {
            "premium": 0.80,  # High quality: Full storage with all metadata
            "standard": 0.60,  # Standard quality: Full storage (current threshold)
            "basic": 0.40,  # Basic quality: Preliminary storage with enhancement flag
            "reject": 0.30,  # Too low quality: Log for analysis but don't store
        }

    def determine_storage_tier(
        self, completeness_score: float, data_sources: List[str]
    ) -> str:
        """Determine storage tier based on completeness score and data sources"""

        # Bonus points for high-quality data sources
        quality_bonus = 0.0
        high_quality_sources = [
            "ai_enhanced_full_content",
            "progressive_content_premium",
            "steel_browser_extraction",
            "visual_intelligence",
        ]

        for source in data_sources:
            if any(hq_source in source for hq_source in high_quality_sources):
                quality_bonus += 0.05

        # Cap bonus at 0.15 (15%)
        quality_bonus = min(quality_bonus, 0.15)
        adjusted_score = completeness_score + quality_bonus

        if adjusted_score >= self.quality_thresholds["premium"]:
            return "premium"
        elif adjusted_score >= self.quality_thresholds["standard"]:
            return "standard"
        elif adjusted_score >= self.quality_thresholds["basic"]:
            return "basic"
        else:
            return "reject"

    async def save_event_with_tier(self, result: "EnhancedExtractionResult") -> bool:
        """Save event based on quality tier with appropriate metadata"""

        storage_tier = self.determine_storage_tier(
            result.completeness_score, result.data_sources
        )

        self.logger.info(
            f"📊 Storage tier determined: {storage_tier} (score: {result.completeness_score:.1%})"
        )

        # Track storage tier metrics
        await self._track_storage_metrics(
            storage_tier, result.completeness_score, result.data_sources
        )

        if storage_tier == "reject":
            # Too low quality: Log for analysis but don't store
            self.logger.info(
                f"⚠️ Event quality too low for storage: {result.completeness_score:.1%} - {result.url}"
            )
            await self._log_rejected_event(result)
            return False

        # Add storage tier metadata
        result.storage_tier = storage_tier
        result.quality_metadata = {
            "storage_tier": storage_tier,
            "original_completeness": result.completeness_score,
            "enhancement_needed": storage_tier == "basic",
            "storage_timestamp": time.time(),
            "quality_bonus_applied": storage_tier in ["premium", "standard"],
        }

        # Store based on tier
        if storage_tier == "premium":
            return await self._save_premium_event(result)
        elif storage_tier == "standard":
            return await self._save_standard_event(result)
        elif storage_tier == "basic":
            return await self._save_preliminary_event(result)
        else:
            # Fallback case
            return False

    async def _save_premium_event(self, result: "EnhancedExtractionResult") -> bool:
        """Save premium quality event with full metadata and priority indexing"""
        try:
            self.logger.info(f"💎 Saving premium quality event: {result.name}")

            # Enhanced event data for premium tier
            enhanced_metadata = {
                "quality_tier": "premium",
                "enhancement_needed": False,
                "priority_indexing": True,
                "full_metadata_stored": True,
                "discovery_timestamp": time.time(),
                "retention_priority": "high",
            }

            # Add enhanced metadata to result
            if hasattr(result, "metadata") and result.metadata is not None:
                result.metadata.update(enhanced_metadata)
            else:
                result.metadata = enhanced_metadata

            # Save with standard method (already handles all metadata)
            return await self._save_to_database(result)

        except Exception as e:
            self.logger.error(f"❌ Premium event save failed: {e}")
            return False

    async def _save_standard_event(self, result: "EnhancedExtractionResult") -> bool:
        """Save standard quality event with full storage (current default behavior)"""
        try:
            self.logger.info(f"📄 Saving standard quality event: {result.name}")

            # Standard metadata
            standard_metadata = {
                "quality_tier": "standard",
                "enhancement_needed": False,
                "priority_indexing": False,
                "full_metadata_stored": True,
                "discovery_timestamp": time.time(),
                "retention_priority": "normal",
            }

            if hasattr(result, "metadata") and result.metadata is not None:
                result.metadata.update(standard_metadata)
            else:
                result.metadata = standard_metadata

            return await self._save_to_database(result)

        except Exception as e:
            self.logger.error(f"❌ Standard event save failed: {e}")
            return False

    async def _save_preliminary_event(self, result: "EnhancedExtractionResult") -> bool:
        """Save preliminary event for future enhancement"""
        try:
            self.logger.info(
                f"🔄 Saving preliminary event for enhancement: {result.name}"
            )

            # Mark for future enhancement
            preliminary_metadata = {
                "quality_tier": "preliminary",
                "enhancement_needed": True,
                "priority_indexing": False,
                "full_metadata_stored": False,
                "discovery_timestamp": time.time(),
                "retention_priority": "low",
                "enhancement_candidates": True,
                "reprocessing_recommended": True,
            }

            if hasattr(result, "metadata") and result.metadata is not None:
                result.metadata.update(preliminary_metadata)
            else:
                result.metadata = preliminary_metadata

            # Save with enhancement flag
            return await self._save_to_database(result)

        except Exception as e:
            self.logger.error(f"❌ Preliminary event save failed: {e}")
            return False

    async def _log_rejected_event(self, result: "EnhancedExtractionResult"):
        """Log rejected event for analysis without storing in main database"""
        try:
            rejection_log = {
                "url": result.url,
                "name": result.name or "Unknown Event",
                "completeness_score": result.completeness_score,
                "data_sources": result.data_sources,
                "rejection_reason": "quality_below_threshold",
                "rejection_timestamp": time.time(),
                "speakers_found": len(result.speakers),
                "sponsors_found": len(result.sponsors),
            }

            self.logger.info(f"📝 Logged rejected event: {rejection_log}")
            # Could save to separate analytics table for improvement analysis

        except Exception as e:
            self.logger.warning(f"⚠️ Failed to log rejected event: {e}")

    async def _track_storage_metrics(
        self, storage_tier: str, completeness_score: float, data_sources: List[str]
    ):
        """Track storage tier metrics for monitoring and optimization"""
        try:
            metrics = {
                "storage_tier": storage_tier,
                "completeness_score": completeness_score,
                "data_sources_count": len(data_sources),
                "high_quality_sources": sum(
                    1
                    for source in data_sources
                    if any(
                        hq in source
                        for hq in ["premium", "steel_browser", "visual_intelligence"]
                    )
                ),
                "timestamp": time.time(),
            }

            # Log metrics for monitoring systems
            self.logger.info(f"📊 Storage metrics: {metrics}")

            # Could integrate with monitoring system here
            # await track_storage_tier_metrics(metrics)

        except Exception as e:
            self.logger.warning(f"⚠️ Storage metrics tracking failed: {e}")

    async def _save_to_database(self, result: "EnhancedExtractionResult") -> bool:
        """Save to database using the orchestrator's save method"""
        # This will be set by the orchestrator during initialization
        if hasattr(self, "_orchestrator_save_method"):
            return await self._orchestrator_save_method(result)
        else:
            raise NotImplementedError("Database save method not properly configured")


class EventExtractor:
    """
    Enhanced orchestrator with integrated agent capabilities
    Framework-free with advanced visual intelligence, MCP browser control, and crypto knowledge
    """

    def __init__(self):
        self.model = None
        self.project_id = None
        self.location = None
        self.session = None
        self.logger = logging.getLogger(__name__)

        # Crypto industry knowledge base (subset for demonstration)
        self.crypto_companies = {
            "polygon",
            "ethereum",
            "solana",
            "chainlink",
            "binance",
            "coinbase",
            "metamask",
            "uniswap",
            "aave",
            "compound",
            "opensea",
            "alchemy",
            "infura",
            "consensys",
            "stellar",
            "ripple",
            "cardano",
            "polkadot",
            "avalanche",
            "algorand",
            "tezos",
            "near",
            "cosmos",
            "terra",
            "fantom",
            "arbitrum",
            "optimism",
            "immutablex",
            "loopring",
        }

        self.crypto_personalities = {
            "vitalik buterin",
            "gavin wood",
            "charles hoskinson",
            "silvio micali",
            "anatoly yakovenko",
            "sergey nazarov",
            "hayden adams",
            "stani kulechov",
            "andre cronje",
            "sandeep nailwal",
            "mihailo bjelic",
            "ryan sean adams",
            "laura shin",
            "anthony pompliano",
            "naval ravikant",
            "balaji srinivasan",
        }

        self.mcp_available = False
        self._check_mcp_availability()

        # Platform routing for Week 2 expansion
        self.platform_router = PlatformRouter()

        # Week 3 Content Processing Optimization
        self.content_processor = None
        self.ai_processor = None

        # Week 4 Tiered Storage Strategy
        self.tiered_storage = None

        # Browser automation capabilities
        self.browser_automation_available = BROWSER_AUTOMATION_AVAILABLE
        self.hybrid_orchestrator = None

        # Database integration capabilities
        self.db_client = None
        self.database_integration_enabled = False
        self.comprehensive_reporting_enabled = False

        # JavaScript-heavy site patterns for browser automation
        self.js_heavy_patterns = [
            "lu.ma",
            "luma.com",
            "eventbrite.com",
            "eventbrite.co.uk",
            "meetup.com",
            "facebook.com/events",
            "ticket",
            "event",
        ]

    def _check_mcp_availability(self):
        """Check if MCP tools are available"""
        try:
            mcp_path = os.path.join(os.getcwd(), "mcp_tools")
            if os.path.exists(mcp_path):
                self.mcp_available = True
                logger.info("✅ MCP tools detected - enhanced scraping available")
            else:
                logger.info("ℹ️  MCP tools not found - using standard scraping")
        except Exception as e:
            logger.warning(f"MCP availability check failed: {e}")

    async def initialize(self) -> bool:
        """Initialize Enhanced Orchestrator"""
        try:
            logger.info(
                "🚀 Initializing Enhanced Orchestrator with Agent Capabilities..."
            )

            # Setup Vertex AI
            model_name = get_secret(
                "VERTEX_MODEL_NAME", "VERTEX_MODEL_NAME", "gemini-2.0-flash-001"
            )
            self.project_id = VERTEX_PROJECT_ID or "your-project-id"
            self.location = VERTEX_LOCATION or "us-central1"

            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel(model_name)

            # Create HTTP session with SSL configuration for Cloud Run
            ssl_context = ssl.create_default_context()
            # In Cloud Run environments, we may need to handle SSL more permissively
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=100,
                limit_per_host=30,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )

            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; Nuru-AI-Bot/2.0; +https://nuru.ai)"
                },
            )

            # Initialize Week 3 Content Processing Optimization
            self.content_processor = ProgressiveContentProcessor(logger=logger)
            self.ai_processor = RobustAIProcessor(
                model=self.model,
                crypto_companies=self.crypto_companies,
                crypto_personalities=self.crypto_personalities,
                logger=logger,
            )

            # Set up AI method reference for the processor
            self.ai_processor._orchestrator_ai_method = (
                self._ai_extract_with_crypto_knowledge
            )

            # Initialize Week 4 Tiered Storage Strategy
            self.tiered_storage = TieredEventStorage(logger=logger)

            # Set up storage method reference for the tiered storage
            self.tiered_storage._orchestrator_save_method = (
                self._save_enhanced_to_database
            )

            # Initialize browser automation
            if self.browser_automation_available:
                try:
                    logger.info("🌐 Initializing browser automation...")
                    self.hybrid_orchestrator = HybridOrchestrator(
                        http_session=self.session,
                        enable_browser_fallback=True,
                        browser_automation=RobustBrowserAutomation(
                            page_timeout=180000,  # 3 minutes per page
                            navigation_timeout=120000,  # 2 minutes for navigation
                            element_timeout=60000,  # 1 minute for elements
                            scroll_delay=3000,  # 3 seconds between scrolls
                            max_scroll_attempts=10,
                            headless=True,
                            enable_screenshots=False,  # Disable to save space
                        ),
                    )

                    browser_init_success = await self.hybrid_orchestrator.initialize()
                    if browser_init_success:
                        logger.info("✅ Browser automation initialized successfully")
                    else:
                        logger.warning("⚠️  Browser automation initialization failed")
                        self.hybrid_orchestrator = None

                except Exception as e:
                    logger.error(f"❌ Browser automation setup failed: {e}")
                    self.hybrid_orchestrator = None

            capabilities = [
                "✅ Advanced Visual Intelligence",
                "✅ Crypto Industry Knowledge Base",
                "✅ Enhanced Image Analysis",
                "✅ Week 3: Progressive Content Processing & AI Retry Logic",
                "✅ Week 4: Tiered Storage Strategy with Quality-Based Persistence",
                "✅ Optimized Completeness Scoring",
                "✅ Database Integration",
                "✅ Comprehensive Monitoring",
            ]

            if self.mcp_available:
                capabilities.append("✅ MCP Browser Control")
            else:
                capabilities.append("⚠️  MCP Browser Control (not available)")

            if self.hybrid_orchestrator:
                capabilities.append("✅ Browser Automation (Playwright)")
            elif self.browser_automation_available:
                capabilities.append("⚠️  Browser Automation (Playwright - init failed)")
            else:
                capabilities.append("❌ Browser Automation (Playwright not available)")

            # Initialize database integration
            self._initialize_database_integration()

            logger.info("✅ Enhanced Orchestrator ready with capabilities:")
            for capability in capabilities:
                logger.info(f"   {capability}")

            return True

        except Exception as e:
            logger.error(f"❌ Enhanced Orchestrator initialization failed: {e}")
            return False

    def _initialize_database_integration(self):
        """Initialize database integration capabilities"""
        try:
            if DATABASE_IMPORTS_AVAILABLE:
                # Import configuration
                from chatbot_api.core.config import SUPABASE_KEY, SUPABASE_URL

                if SUPABASE_URL and SUPABASE_KEY:
                    self.db_client = create_supabase_client(SUPABASE_URL, SUPABASE_KEY)
                    if self.db_client:
                        self.database_integration_enabled = True
                        self.comprehensive_reporting_enabled = True
                        logger.info("✅ Database integration initialized")
                    else:
                        logger.warning("⚠️ Database client is None")
                        self.database_integration_enabled = False
                        self.comprehensive_reporting_enabled = False
                else:
                    logger.warning("⚠️ Database credentials not available")
                    self.database_integration_enabled = False
                    self.comprehensive_reporting_enabled = False
            else:
                logger.warning("⚠️ Database imports not available")
                self.database_integration_enabled = False
                self.comprehensive_reporting_enabled = False
        except Exception as e:
            logger.warning(f"⚠️ Database integration initialization failed: {e}")
            self.database_integration_enabled = False
            self.comprehensive_reporting_enabled = False

    def enable_database_integration(self, enable: bool = True):
        """Enable or disable database integration"""
        self.database_integration_enabled = enable
        if enable:
            self._initialize_database_integration()
        logger.info(f"🗄️ Database integration {'enabled' if enable else 'disabled'}")

    def enable_comprehensive_reporting(self, enable: bool = True):
        """Enable or disable comprehensive reporting"""
        self.comprehensive_reporting_enabled = enable
        logger.info(f"📊 Comprehensive reporting {'enabled' if enable else 'disabled'}")

    async def _process_database_integration_for_calendar(
        self, events: List[EnhancedExtractionResult], calendar_url: str
    ) -> CalendarExtractionReport:
        """Process database integration with comprehensive reporting for calendar extraction"""
        from datetime import datetime, timezone
        from uuid import uuid4

        extraction_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Initialize report
        report = CalendarExtractionReport(
            extraction_id=extraction_id,
            timestamp=timestamp,
            source_url=calendar_url,
            total_events_found=len(events),
            events_already_in_db=0,
            events_added_to_db=0,
            events_rejected=0,
            rejection_reasons=[],
            processing_details={},
            success=False,
        )

        if not self.db_client or not self.database_integration_enabled:
            report.rejection_reasons.append(
                {"reason": "Database integration not available", "count": len(events)}
            )
            report.events_rejected = len(events)
            return report

        try:
            logger.info(f"🗄️ Processing {len(events)} events for database integration")

            for event in events:
                event_url = event.url
                event_name = event.name

                if not event_url:
                    report.events_rejected += 1
                    report.rejection_reasons.append(
                        {"reason": "Missing URL", "event_name": event_name, "count": 1}
                    )
                    continue

                # Check if event already exists
                try:
                    existing_event = await check_event_exists_by_url(event_url)
                    if existing_event:
                        report.events_already_in_db += 1
                        logger.debug(f"📋 Event already in database: {event_name}")
                        continue
                except Exception as e:
                    logger.warning(f"⚠️ Error checking existing event: {e}")

                # Prepare event data for database
                event_data = {
                    "luma_url": calendar_url,  # Fixed: Use calendar_url (source) not event_url (individual event)
                    "name": event_name,  # Fixed: changed from event_name to name to match database schema
                    "description": event.description,
                    "location_name": event.location,
                    "url": event_url,  # Add url field as it exists in schema - individual event URL
                    "ai_enhanced": True,  # Boolean field that exists
                    "crypto_industry_matches": {"source": "enhanced_orchestrator_calendar"},  # JSONB field
                    "completeness_score": event.completeness_score,  # Numeric field that exists
                    # Note: Removed fields that don't exist in database schema:
                    # - speakers, sponsors (no such columns)
                    # - source, source_url (no such columns)  
                    # - extraction_id, created_at, updated_at (no such columns)
                    # - start_date (field doesn't exist, database has start_time_iso instead)
                }

                # Save to database
                try:
                    save_result = await save_event_data(event_data)
                    if save_result:
                        report.events_added_to_db += 1
                        event.database_integrated = True
                        logger.info(f"💾 Saved to database: {event_name}")
                    else:
                        report.events_rejected += 1
                        report.rejection_reasons.append(
                            {
                                "reason": "Database save failed",
                                "event_name": event_name,
                                "count": 1,
                            }
                        )
                except Exception as e:
                    report.events_rejected += 1
                    report.rejection_reasons.append(
                        {
                            "reason": f"Database error: {str(e)}",
                            "event_name": event_name,
                            "count": 1,
                        }
                    )
                    logger.error(f"❌ Database save error for {event_name}: {e}")

            report.success = (
                report.events_added_to_db > 0 or report.events_already_in_db > 0
            )
            report.processing_details = {
                "database_integration_enabled": True,
                "enhanced_processing_enabled": True,
                "extraction_method": "enhanced_orchestrator_calendar",
            }

            logger.info(
                f"📊 Database integration complete - Added: {report.events_added_to_db}, "
                f"Already existed: {report.events_already_in_db}, Rejected: {report.events_rejected}"
            )

        except Exception as e:
            logger.error(f"❌ Database integration error: {e}", exc_info=True)
            report.rejection_reasons.append(
                {"reason": f"Integration error: {str(e)}", "count": len(events)}
            )
            report.events_rejected = len(events)

        return report

    async def extract_events_comprehensive(
        self,
        urls: List[str],
        max_concurrent: int = 8,
        timeout_per_event: int = 120,
        enable_visual_intelligence: bool = True,
        enable_mcp_browser: bool = True,
    ) -> List[EnhancedExtractionResult]:
        """
        Extract comprehensive data with enhanced agent capabilities
        """
        # Start monitoring session
        session_id = f"enhanced_extraction_{int(time.time())}"
        track_orchestrator_session(session_id, len(urls))

        logger.info(f"🎯 Starting ENHANCED extraction of {len(urls)} events")
        logger.info(f"⚡ Max concurrent: {max_concurrent}")
        logger.info(f"📊 Monitoring session: {session_id}")
        logger.info(
            f"🔬 Visual Intelligence: {'Enabled' if enable_visual_intelligence else 'Disabled'}"
        )
        logger.info(
            f"🌐 MCP Browser: {'Enabled' if enable_mcp_browser and self.mcp_available else 'Disabled/Unavailable'}"
        )

        # STEP 0: Comprehensive URL Resolution (90% Success Strategy - Week 1)
        logger.info(f"🔗 Step 0: Batch URL Resolution for {len(urls)} URLs...")
        url_resolver = EnhancedURLResolver(session=self.session)
        url_resolutions = await url_resolver.batch_resolve_urls(urls)

        # Extract unique successfully resolved URLs for processing
        successful_resolutions = {
            original_url: resolution
            for original_url, resolution in url_resolutions.items()
            if resolution.resolution_successful
        }

        # Create mapping of final URLs to original URLs (for result tracking)
        final_to_original_mapping = {}
        unique_final_urls = []

        for original_url, resolution in successful_resolutions.items():
            final_url = resolution.final_url
            if final_url not in final_to_original_mapping:
                final_to_original_mapping[final_url] = []
                unique_final_urls.append(final_url)
            final_to_original_mapping[final_url].append(original_url)

        # Log URL resolution impact
        resolution_rate = len(successful_resolutions) / len(urls) if urls else 0
        duplicate_eliminations = len(urls) - len(unique_final_urls)

        logger.info("📊 URL Resolution Results:")
        logger.info(f"   Original URLs: {len(urls)}")
        logger.info(
            f"   Successful Resolutions: {len(successful_resolutions)} ({resolution_rate:.1%})"
        )
        logger.info(f"   Unique Final URLs: {len(unique_final_urls)}")
        logger.info(f"   Duplicate Eliminations: {duplicate_eliminations}")

        # STEP 0.7: Calendar Detection and Event Discovery
        logger.info("📅 Step 0.7: Calendar Detection and Individual Event Discovery...")
        calendar_results, non_calendar_urls = await self._process_calendar_urls(
            unique_final_urls
        )

        # Use non-calendar URLs for normal processing + add calendar results
        processing_urls = non_calendar_urls
        logger.info(
            f"🎯 Processing {len(processing_urls)} non-calendar URLs + {len(calendar_results)} calendar events (targeting 90% success rate)"
        )

        # STEP 0.5: Platform-Specific URL Classification (90% Success Strategy - Week 2)
        logger.info("🌐 Step 0.5: Platform Classification and Route Planning...")
        platform_routing = self._analyze_platform_routing(processing_urls)

        logger.info("📊 Platform Routing Analysis:")
        logger.info(
            f"   Luma URLs: {platform_routing['luma_urls']} (standard processing)"
        )
        logger.info(
            f"   External URLs: {platform_routing['external_urls']} (enhanced scraping)"
        )
        logger.info(
            f"   Complex URLs: {platform_routing['complex_urls']} (Steel Browser routing)"
        )

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_single_event(
            url: str, index: int
        ) -> EnhancedExtractionResult:
            async with semaphore:
                return await self._extract_single_event_enhanced(
                    url,
                    index,
                    timeout_per_event,
                    enable_visual_intelligence,
                    enable_mcp_browser,
                )

        # Create tasks for resolved URLs
        tasks = [process_single_event(url, i) for i, url in enumerate(processing_urls)]

        # Execute with progress tracking and monitoring
        results = []
        completed = 0

        # Add calendar results first
        results.extend(calendar_results)
        completed += len(calendar_results)

        # Log calendar results
        for result in calendar_results:
            status_icon = "✅" if result.status == "success" else "❌"
            logger.info(
                f"{status_icon} [Calendar] {result.name} - "
                f"Score: {result.completeness_score:.2f}, Source: Calendar extraction"
            )

        for task in asyncio.as_completed(tasks):
            result = await task
            results.append(result)
            completed += 1

            status_icon = "✅" if result.status == "success" else "❌"
            enhancements = []
            if result.visual_intelligence and (
                result.visual_intelligence.booth_detections
                or result.visual_intelligence.agenda_items
            ):
                enhancements.append("🔬 VI")
            if result.mcp_browser_used:
                enhancements.append("🌐 MCP")
            if result.crypto_industry_matches > 0:
                enhancements.append(f"🪙 {result.crypto_industry_matches}")

            enhancement_str = f" [{', '.join(enhancements)}]" if enhancements else ""

            logger.info(
                f"{status_icon} [{completed}/{len(urls)}] {result.url} - "
                f"Score: {result.completeness_score:.2f}, Time: {result.processing_time:.1f}s{enhancement_str}"
            )

            # Track individual event completion
            track_orchestrator_event_completion(
                session_id=session_id,
                success=result.status == "success",
                completeness_score=result.completeness_score,
                processing_time=result.processing_time,
                speakers_count=len(result.speakers),
                sponsors_count=len(result.sponsors),
                images_analyzed=result.images_analyzed,
            )

            # Log errors to monitoring
            if result.status != "success" and result.error_message:
                track_orchestrator_error(session_id, result.error_message, result.url)

        # Add results for URLs that failed resolution
        failed_resolution_urls = [
            url
            for url, resolution in url_resolutions.items()
            if not resolution.resolution_successful
        ]

        for failed_url in failed_resolution_urls:
            resolution = url_resolutions[failed_url]
            failed_result = EnhancedExtractionResult(
                url=failed_url,
                status="url_resolution_failed",
                processing_time=resolution.resolution_time,
                completeness_score=0.0,
                error_message=f"URL resolution failed: {resolution.error_message}",
            )
            results.append(failed_result)
            track_orchestrator_error(
                session_id, failed_result.error_message, failed_url
            )

        # Map results back to original URLs for duplicates
        expanded_results = []
        for result in results:
            if result.url in final_to_original_mapping:
                # This final URL maps to multiple original URLs
                original_urls = final_to_original_mapping[result.url]
                for i, original_url in enumerate(original_urls):
                    if i == 0:
                        # First occurrence keeps the actual result
                        result.url = original_url  # Update URL to original
                        expanded_results.append(result)
                    else:
                        # Additional occurrences get duplicate results
                        duplicate_result = EnhancedExtractionResult(
                            url=original_url,
                            status="duplicate_resolved",
                            processing_time=0.0,
                            completeness_score=result.completeness_score,
                            name=result.name,
                            description=result.description,
                            start_date=result.start_date,
                            location=result.location,
                            speakers=result.speakers.copy(),
                            sponsors=result.sponsors.copy(),
                            organizers=(
                                result.organizers.copy() if result.organizers else []
                            ),
                            error_message=f"Duplicate of resolved URL: {result.url}",
                        )
                        expanded_results.append(duplicate_result)
            else:
                expanded_results.append(result)

        results = expanded_results

        # Calculate final summary
        successful = [r for r in results if r.status == "success"]
        failed = [r for r in results if r.status != "success"]
        avg_completeness = (
            sum(r.completeness_score for r in successful) / len(successful)
            if successful
            else 0
        )
        avg_time = (
            sum(r.processing_time for r in successful) / len(successful)
            if successful
            else 0
        )
        total_speakers = sum(len(r.speakers) for r in successful)
        total_sponsors = sum(len(r.sponsors) for r in successful)
        total_crypto_matches = sum(r.crypto_industry_matches for r in successful)
        visual_intelligence_used = sum(
            1
            for r in successful
            if r.visual_intelligence
            and (
                r.visual_intelligence.booth_detections
                or r.visual_intelligence.agenda_items
            )
        )
        mcp_browser_used = sum(1 for r in successful if r.mcp_browser_used)

        logger.info(
            f"📊 ENHANCED SUMMARY: {len(successful)}/{len(urls)} successful, "
            f"avg completeness: {avg_completeness:.2f}"
        )
        logger.info(
            f"🔬 Visual Intelligence: {visual_intelligence_used} events enhanced"
        )
        logger.info(f"🌐 MCP Browser: {mcp_browser_used} events used MCP")
        logger.info(f"🪙 Crypto Matches: {total_crypto_matches} industry matches found")

        # Complete monitoring session
        track_orchestrator_session_completion(
            session_id=session_id,
            total_events=len(urls),
            successful_events=len(successful),
            failed_events=len(failed),
            avg_completeness=avg_completeness * 100,  # Convert to percentage
            avg_processing_time=avg_time,
            total_speakers=total_speakers,
            total_sponsors=total_sponsors,
        )

        return results

    def _analyze_platform_routing(self, urls: List[str]) -> Dict[str, int]:
        """Analyze URLs and provide platform routing statistics for Week 2 expansion"""
        routing_stats = {
            "luma_urls": 0,
            "external_urls": 0,
            "complex_urls": 0,
            "standard_tier": 0,
            "enhanced_tier": 0,
            "steel_tier": 0,
        }

        for url in urls:
            classification = self.platform_router.classify_url(url)
            platform = classification["platform"]
            tier = classification["tier"]

            # Count by platform
            if platform == "luma":
                routing_stats["luma_urls"] += 1
            elif platform in ["eventbrite", "meetup", "facebook", "external"]:
                routing_stats["external_urls"] += 1
            else:
                routing_stats["complex_urls"] += 1

            # Count by tier
            if tier == 1:
                routing_stats["standard_tier"] += 1
            elif tier == 2:
                routing_stats["enhanced_tier"] += 1
            else:
                routing_stats["steel_tier"] += 1

        return routing_stats

    async def _extract_single_event_enhanced(
        self,
        url: str,
        index: int,
        timeout: int,
        enable_visual_intelligence: bool,
        enable_mcp_browser: bool,
    ) -> EnhancedExtractionResult:
        """Extract comprehensive data for a single event with enhancements"""
        start_time = time.time()

        try:
            # STEP 1: Platform Classification (90% Success Strategy - Week 2)
            platform_classification = self.platform_router.classify_url(url)
            logger.info(
                f"🌐 Platform: {platform_classification['platform']}, "
                f"Tier: {platform_classification['tier']}, "
                f"Strategy: {platform_classification['recommended_strategy']}"
            )

            # Apply timeout
            result = await asyncio.wait_for(
                self._enhanced_extraction_workflow_with_routing(
                    url,
                    platform_classification,
                    enable_visual_intelligence,
                    enable_mcp_browser,
                ),
                timeout=timeout,
            )

            result.processing_time = time.time() - start_time
            result.status = "success"

            return result

        except asyncio.TimeoutError:
            logger.warning(f"⏰ Timeout for {url} after {timeout}s")
            return EnhancedExtractionResult(
                url=url,
                status="timeout",
                processing_time=timeout,
                error_message=f"Processing exceeded {timeout} seconds",
            )

        except Exception as e:
            logger.error(f"❌ Error processing {url}: {e}")
            return EnhancedExtractionResult(
                url=url,
                status="error",
                processing_time=time.time() - start_time,
                error_message=str(e),
            )

    async def _enhanced_extraction_workflow_with_routing(
        self,
        url: str,
        platform_classification: Dict[str, Any],
        enable_visual_intelligence: bool,
        enable_mcp_browser: bool,
    ) -> EnhancedExtractionResult:
        """Enhanced extraction workflow with intelligent platform routing (Week 2)"""

        result = EnhancedExtractionResult(
            url=url, status="processing", processing_time=0.0
        )
        platform = platform_classification["platform"]
        tier = platform_classification["tier"]
        strategy = platform_classification["recommended_strategy"]

        # Add platform metadata to result
        result.data_sources.append(f"platform_{platform}_tier_{tier}")

        # STEP 1: Platform-specific content extraction
        if strategy == "steel_browser" and self.mcp_available:
            # Tier 3: Steel Browser for complex sites
            logger.info(f"🔧 Using Steel Browser strategy for {url}")
            html_content, basic_data = await self._extract_with_steel_browser(url)
            result.data_sources.append("steel_browser_extraction")
        elif strategy == "enhanced" or tier >= 2:
            # Tier 2: Enhanced Playwright with fallbacks
            logger.info(f"🎭 Using Enhanced Playwright strategy for {url}")
            html_content, basic_data = await self._extract_with_enhanced_playwright(
                url, enable_mcp_browser
            )
            result.data_sources.append("enhanced_playwright_extraction")
        else:
            # Tier 1: Standard extraction
            logger.info(f"📄 Using Standard extraction strategy for {url}")
            html_content, basic_data = await self._extract_page_content_enhanced(
                url, enable_mcp_browser
            )
            result.data_sources.append("standard_enhanced_extraction")

        # Continue with existing enhanced workflow
        return await self._continue_enhanced_workflow(
            result,
            url,
            html_content,
            basic_data,
            enable_visual_intelligence,
            enable_mcp_browser,
        )

    async def _enhanced_extraction_workflow(
        self, url: str, enable_visual_intelligence: bool, enable_mcp_browser: bool
    ) -> EnhancedExtractionResult:
        """Enhanced extraction workflow with agent capabilities integrated"""

        result = EnhancedExtractionResult(
            url=url, status="processing", processing_time=0.0
        )

        # STEP 1: Basic page extraction (enhanced with MCP fallback)
        html_content, basic_data = await self._extract_page_content_enhanced(
            url, enable_mcp_browser
        )
        result.data_sources.append("enhanced_page_extraction")

        # Update basic fields with null safety
        if basic_data and isinstance(basic_data, dict):
            result.name = basic_data.get("title", "")
            result.description = basic_data.get("description", "")
            result.start_date = basic_data.get("start_date", "")
            result.location = basic_data.get("location", "")
        else:
            logger.warning(f"Basic data extraction failed for {url}, using defaults")
            result.name = ""
            result.description = ""
            result.start_date = ""
            result.location = ""

        # STEP 2: Enhanced AI extraction with crypto industry knowledge
        if html_content and self.model:
            enhanced_data = await self._ai_extract_with_crypto_knowledge(
                html_content, url
            )
            result.data_sources.append("crypto_enhanced_ai")

            # Merge enhanced AI data with null safety
            if enhanced_data and isinstance(enhanced_data, dict):
                result.speakers.extend(enhanced_data.get("speakers", []))
                result.sponsors.extend(enhanced_data.get("sponsors", []))
                result.organizers.extend(enhanced_data.get("organizers", []))
                result.crypto_industry_matches = enhanced_data.get("crypto_matches", 0)
            else:
                logger.warning(f"Enhanced AI extraction failed for {url}")
                result.crypto_industry_matches = 0

        # STEP 3: Advanced image discovery and visual intelligence
        image_urls = await self._discover_images(html_content, url)
        if image_urls:
            if enable_visual_intelligence:
                visual_data = await self._advanced_visual_intelligence_analysis(
                    image_urls, url
                )
                result.visual_intelligence = visual_data
                result.data_sources.append("visual_intelligence")

                # Merge visual intelligence data
                # Note: visual_data is a VisualIntelligenceResult object, not a dict
                # For now, just store it; will enhance extraction in next iteration
            else:
                # Standard image analysis
                image_data = await self._analyze_images_for_entities(image_urls)
                result.data_sources.append("standard_image_analysis")

                # Convert to enhanced format
                for sponsor in image_data.get("sponsors", []):
                    enhanced_sponsor = EnhancedSponsorDetection(
                        name=sponsor.get("name", ""),
                        tier=SponsorTier.UNKNOWN,
                        confidence=0.6,
                        confidence_level=ConfidenceLevel.MEDIUM,
                        context="standard_image_analysis",
                        detection_source="image",
                    )
                    result.sponsors.append(enhanced_sponsor)

            result.images_analyzed = len(image_urls)

        # STEP 4: External site discovery with MCP enhancement
        external_urls = await self._find_external_sites(html_content, url)
        if external_urls:
            external_data = await self._scrape_external_sites_enhanced(
                external_urls[:3], enable_mcp_browser
            )
            result.external_sites_scraped = len(external_data)
            result.data_sources.append("enhanced_external_sites")

            # Merge external data
            for ext_data in external_data:
                result.speakers.extend(ext_data.get("speakers", []))
                result.sponsors.extend(ext_data.get("sponsors", []))

        # STEP 5: Data refinement and deduplication
        await self._apply_data_refinement(result)
        result.data_refinement_applied = True

        # STEP 6: Calculate enhanced completeness
        result.completeness_score = self._calculate_enhanced_completeness(result)

        # STEP 7: Save to database with Week 4 tiered storage strategy
        try:
            save_success = await self.tiered_storage.save_event_with_tier(result)
            if save_success:
                tier = getattr(result, "storage_tier", "unknown")
                logger.info(
                    f"💾 Saved enhanced {result.name} to database (tier: {tier})"
                )
            else:
                logger.warning(
                    f"⚠️ Event not saved due to quality threshold: {result.name}"
                )
        except Exception as e:
            logger.error(f"❌ Enhanced tiered storage failed for {result.name}: {e}")

        return result

    async def _continue_enhanced_workflow(
        self,
        result: EnhancedExtractionResult,
        url: str,
        html_content: str,
        basic_data: Dict[str, Any],
        enable_visual_intelligence: bool,
        enable_mcp_browser: bool,
    ) -> EnhancedExtractionResult:
        """Continue with standard enhanced workflow after platform-specific extraction"""

        # Update basic fields with null safety
        if basic_data and isinstance(basic_data, dict):
            result.name = basic_data.get("title", "")
            result.description = basic_data.get("description", "")
            result.start_date = basic_data.get("start_date", "")
            result.location = basic_data.get("location", "")
        else:
            logger.warning(f"Basic data extraction failed for {url}, using defaults")

        # Continue with Week 3 optimized workflow steps 2-7
        if (
            html_content and len(html_content) > 200
        ):  # Lower threshold for preliminary processing
            # STEP 2A: Progressive Content Processing (Week 3 Enhancement)
            content_tier = self.content_processor.determine_processing_tier(
                html_content, url
            )
            content_result = await self.content_processor.process_with_tier(
                html_content, content_tier, url
            )

            logger.info(
                f"📊 Content processing tier: {content_tier} (target: {content_result.completeness_target:.1%})"
            )
            result.data_sources.append(f"progressive_content_{content_tier}")

            if content_result.success:
                # STEP 2B: Enhanced AI extraction with retry logic (Week 3 Enhancement)
                ai_result = await self.ai_processor.extract_with_retry(
                    content_result.content, url
                )

                if ai_result.success and ai_result.data:
                    logger.info(
                        f"🤖 AI extraction successful: {ai_result.processing_method} (attempt {ai_result.attempt_count})"
                    )
                    enhanced_data = ai_result.data

                    # Update result with enhanced data
                    if enhanced_data.get("speakers"):
                        result.speakers.extend(enhanced_data["speakers"])
                    if enhanced_data.get("sponsors"):
                        result.sponsors.extend(enhanced_data["sponsors"])
                    if enhanced_data.get("organizers"):
                        result.organizers.extend(enhanced_data["organizers"])
                    if enhanced_data.get("crypto_matches"):
                        result.crypto_industry_matches = enhanced_data["crypto_matches"]

                    result.data_sources.append(
                        f"ai_enhanced_{ai_result.processing_method}"
                    )
                else:
                    logger.warning(
                        f"⚠️ AI extraction failed after {ai_result.attempt_count} attempts"
                    )
                    result.data_sources.append("ai_extraction_failed")
            else:
                logger.warning(f"⚠️ Content processing failed: {content_result.reason}")
                result.data_sources.append("content_processing_failed")

            # STEP 3: Visual intelligence and image analysis (combined)
            if enable_visual_intelligence:
                # Extract and analyze images
                image_urls = self._extract_image_urls(html_content, url)
                if image_urls:
                    visual_data = await self._advanced_visual_intelligence_analysis(
                        image_urls, url
                    )
                    result.visual_intelligence = visual_data
                    result.data_sources.append("visual_intelligence")
                    result.images_analyzed = len(image_urls)
                else:
                    # Standard image analysis without visual intelligence
                    result.images_analyzed = len(
                        self._extract_image_urls(html_content, url)
                    )
                    result.data_sources.append("standard_image_analysis")

            # STEP 5: Data refinement and deduplication
            await self._apply_data_refinement(result)
            result.data_refinement_applied = True

            # STEP 6: Calculate enhanced completeness
            result.completeness_score = self._calculate_enhanced_completeness(result)

            # STEP 7: Save to database with Week 4 tiered storage strategy
            try:
                save_success = await self.tiered_storage.save_event_with_tier(result)
                if save_success:
                    tier = getattr(result, "storage_tier", "unknown")
                    logger.info(
                        f"💾 Saved enhanced {result.name} to database (tier: {tier})"
                    )
                else:
                    logger.warning(
                        f"⚠️ Event not saved due to quality threshold: {result.name}"
                    )
            except Exception as e:
                logger.error(
                    f"❌ Enhanced tiered storage failed for {result.name}: {e}"
                )

        return result

    async def _extract_with_steel_browser(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """Extract content using Steel Browser for complex sites (Tier 3)"""
        try:
            # Import SuperEnhancedScraperAgent for Steel Browser capabilities
            from extraction.agents.experimental.super_enhanced_scraper_agent import (
                SuperEnhancedScraperAgent,
            )

            scraper = SuperEnhancedScraperAgent(
                name="PlatformRouter_Steel", logger=logger
            )

            # Use tier 3 (Steel Browser) strategy
            # Check if the method exists, fallback to basic scrape if not
            if hasattr(scraper, "scrape_with_tier"):
                result = await scraper.scrape_with_tier(url, tier=3, timeout=30)
            elif hasattr(scraper, "scrape"):
                result = await scraper.scrape(url, timeout=30)
            else:
                # Fallback for missing method
                logger.warning("SuperEnhancedScraperAgent missing expected methods")
                return "", {}

            if result.success and result.content:
                # Parse basic metadata from Steel Browser result
                basic_data = {
                    "title": self._extract_title_from_content(result.content),
                    "description": self._extract_description_from_content(
                        result.content
                    ),
                    "start_date": self._extract_start_date_from_content(result.content),
                    "location": self._extract_location_from_content(result.content),
                }
                logger.info(
                    f"✅ Steel Browser extraction successful for {url} ({len(result.content)} chars)"
                )
                return result.content, basic_data
            else:
                raise Exception(f"Steel Browser extraction failed: {result.error}")

        except Exception as e:
            logger.warning(
                f"⚠️ Steel Browser extraction failed for {url}: {e}, falling back to standard"
            )
            return await self._extract_page_content_enhanced(url, True)

    async def _extract_with_enhanced_playwright(
        self, url: str, enable_mcp_fallback: bool
    ) -> Tuple[str, Dict[str, Any]]:
        """Extract content using Enhanced Playwright strategy (Tier 2)"""
        try:
            # Import PageScraperAgent for enhanced Playwright capabilities
            from extraction.agents.experimental.page_scraper_agent import (
                PageScraperAgent,
            )

            scraper = PageScraperAgent(name="PlatformRouter_Enhanced", logger=logger)

            # Use enhanced Playwright with longer timeout for external sites
            result = await asyncio.wait_for(scraper.run_async(url), timeout=45.0)

            if result and result.get("status") == "Success":
                content = result.get("html_content", "")
                if len(content) > 1000:
                    # Parse basic metadata from enhanced result
                    basic_data = {
                        "title": self._extract_title_from_content(content),
                        "description": self._extract_description_from_content(content),
                        "start_date": self._extract_start_date_from_content(content),
                        "location": self._extract_location_from_content(content),
                    }
                    logger.info(
                        f"✅ Enhanced Playwright extraction successful for {url} ({len(content)} chars)"
                    )
                    return content, basic_data

            raise Exception("Enhanced Playwright extraction insufficient content")

        except Exception as e:
            logger.warning(
                f"⚠️ Enhanced Playwright extraction failed for {url}: {e}, falling back to standard"
            )
            return await self._extract_page_content_enhanced(url, enable_mcp_fallback)

    def _extract_title_from_content(self, content: str) -> str:
        """Extract title from HTML content"""
        try:
            soup = BeautifulSoup(content, "html.parser")
            title_tag = soup.find("title")
            return title_tag.get_text().strip() if title_tag else ""
        except:
            return ""

    def _extract_description_from_content(self, content: str) -> str:
        """Extract description from HTML content"""
        try:
            soup = BeautifulSoup(content, "html.parser")
            # Try meta description first
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc and meta_desc.get("content"):
                return meta_desc.get("content").strip()
            # Try Open Graph description
            og_desc = soup.find("meta", attrs={"property": "og:description"})
            if og_desc and og_desc.get("content"):
                return og_desc.get("content").strip()
            return ""
        except:
            return ""

    def _extract_start_date_from_content(self, content: str) -> str:
        """Extract start date from HTML content"""
        try:
            soup = BeautifulSoup(content, "html.parser")
            # Look for structured data or common date patterns
            # This is a simplified implementation
            return ""
        except:
            return ""

    def _extract_location_from_content(self, content: str) -> str:
        """Extract location from HTML content"""
        try:
            soup = BeautifulSoup(content, "html.parser")
            # Look for location in structured data or common patterns
            # This is a simplified implementation
            return ""
        except:
            return ""

    def _extract_start_date_from_text(self, html_content: str) -> str:
        """Extract start date from HTML content (for browser automation results)"""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            return self._extract_start_date(soup)
        except:
            return ""

    def _extract_location_from_text(self, html_content: str) -> str:
        """Extract location from HTML content (for browser automation results)"""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            return self._extract_location(soup)
        except:
            return ""

    def _requires_browser_automation(self, url: str) -> bool:
        """Determine if URL requires browser automation based on patterns"""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.js_heavy_patterns)

    async def _extract_page_content_enhanced(
        self, url: str, enable_mcp: bool
    ) -> tuple[str, Dict[str, Any]]:
        """Enhanced page extraction with browser automation for JavaScript-heavy sites"""
        try:
            # Check if this URL requires browser automation
            needs_browser = self._requires_browser_automation(url)

            # If browser automation is available and needed, use hybrid orchestrator
            if needs_browser and self.hybrid_orchestrator:
                logger.info(
                    f"🌐 Using browser automation for JavaScript-heavy site: {url}"
                )

                try:
                    # Use hybrid orchestrator for intelligent extraction
                    browser_result = (
                        await self.hybrid_orchestrator.extract_page_intelligent(
                            url, force_browser=True
                        )
                    )

                    if (
                        browser_result.success
                        and len(browser_result.html_content) > 1000
                    ):
                        logger.info(
                            f"✅ Browser automation successful for {url} ({len(browser_result.html_content)} chars)"
                        )
                        logger.info(
                            f"   URLs discovered: {len(browser_result.extracted_urls)}"
                        )
                        logger.info(
                            f"   Processing time: {browser_result.processing_time:.2f}s"
                        )

                        basic_data = {
                            "title": browser_result.page_title,
                            "description": browser_result.meta_description,
                            "start_date": self._extract_start_date_from_text(
                                browser_result.html_content
                            ),
                            "location": self._extract_location_from_text(
                                browser_result.html_content
                            ),
                            "discovered_urls": browser_result.extracted_urls,  # Additional URLs found
                            "extraction_method": "browser_automation",
                        }

                        return browser_result.html_content, basic_data
                    else:
                        logger.warning(
                            f"⚠️  Browser automation failed for {url}: {browser_result.error_message}"
                        )

                except Exception as e:
                    logger.error(f"❌ Browser automation error for {url}: {e}")

            # Fallback to standard HTTP extraction
            logger.info(f"📡 Using standard HTTP extraction for: {url}")
            async with self.session.get(url) as response:
                html_content = await response.text()

            soup = BeautifulSoup(html_content, "html.parser")

            # Check if standard extraction got good content
            if len(html_content) > 1000 and soup.find("title"):
                # Standard extraction successful
                basic_data = {
                    "title": (
                        soup.find("title").get_text().strip()
                        if soup.find("title")
                        else ""
                    ),
                    "description": self._extract_meta_description(soup),
                    "start_date": self._extract_start_date(soup),
                    "location": self._extract_location(soup),
                    "extraction_method": "http",
                }

                logger.info(
                    f"✅ Standard extraction successful for {url} ({len(html_content)} chars)"
                )
                return html_content, basic_data

            # If content looks like it needs JavaScript, warn user
            if needs_browser and not self.hybrid_orchestrator:
                logger.warning(
                    f"⚠️  {url} appears to need browser automation but it's not available"
                )
                logger.warning("   Content may be incomplete or empty")

            # Final fallback to PageScraperAgent if available
            if enable_mcp and self.mcp_available:
                try:
                    logger.info(
                        f"🌐 Standard extraction insufficient, trying PageScraperAgent for {url}"
                    )
                    from extraction.agents.experimental.page_scraper_agent import (
                        PageScraperAgent,
                    )

                    page_scraper = PageScraperAgent(
                        name="OrchestrationScraper", logger=logger
                    )

                    # Add timeout for PageScraperAgent
                    scraper_result = await asyncio.wait_for(
                        page_scraper.run_async(url), timeout=30.0
                    )

                    if scraper_result and scraper_result.get("status") == "Success":
                        html_content = scraper_result.get("html_content", "")
                        logger.info(
                            f"✅ PageScraperAgent successful for {url} ({len(html_content)} chars)"
                        )

                        # Parse the content for metadata
                        soup = BeautifulSoup(html_content, "html.parser")
                        basic_data = {
                            "title": (
                                soup.find("title").get_text().strip()
                                if soup.find("title")
                                else ""
                            ),
                            "description": self._extract_meta_description(soup),
                            "start_date": self._extract_start_date(soup),
                            "location": self._extract_location(soup),
                            "extraction_method": "mcp_page_scraper",
                        }

                        return html_content, basic_data

                except (Exception, asyncio.TimeoutError) as scraper_error:
                    logger.warning(
                        f"PageScraperAgent failed/timeout for {url}: {scraper_error}, using standard content"
                    )

            # Use standard content even if it's minimal
            basic_data = {
                "title": (
                    soup.find("title").get_text().strip() if soup.find("title") else ""
                ),
                "description": self._extract_meta_description(soup),
                "start_date": self._extract_start_date(soup),
                "location": self._extract_location(soup),
            }

            return html_content, basic_data

        except Exception as e:
            logger.error(f"Enhanced page content extraction failed: {e}")
            return "", {}

    async def cleanup(self):
        """Clean up orchestrator resources"""
        try:
            # Clean up HTTP session
            if self.session:
                await self.session.close()
                self.session = None

            # Clean up browser automation
            if self.hybrid_orchestrator:
                await self.hybrid_orchestrator.cleanup()
                self.hybrid_orchestrator = None

            logger.info("✅ Enhanced Orchestrator cleanup completed")

        except Exception as e:
            logger.error(f"❌ Orchestrator cleanup failed: {e}")

    async def _ai_extract_with_crypto_knowledge(
        self, html_content: str, url: str
    ) -> Dict[str, Any]:
        """AI extraction enhanced with crypto industry knowledge"""
        try:
            # Enhanced prompt with crypto industry context
            prompt = f"""
            Extract comprehensive event data from this crypto/blockchain event page HTML.
            
            URL: {url}
            
            Use your knowledge of the crypto/blockchain industry to identify speakers, sponsors, and organizations.
            Pay special attention to known crypto companies like: {', '.join(list(self.crypto_companies)[:10])}
            And known crypto personalities like: {', '.join(list(self.crypto_personalities)[:5])}
            
            Return JSON with enhanced detection confidence:
            {{
                "speakers": [
                    {{
                        "name": "Speaker Name", 
                        "title": "Job Title", 
                        "company": "Company", 
                        "bio": "Brief bio",
                        "industry_match": true/false,
                        "confidence": 0.0-1.0
                    }}
                ],
                "sponsors": [
                    {{
                        "name": "Company Name", 
                        "tier": "title/gold/silver/bronze/partner", 
                        "confidence": 0.0-1.0,
                        "crypto_company": true/false
                    }}
                ],
                "organizers": [
                    {{
                        "name": "Organizer Name", 
                        "company": "Company", 
                        "role": "Role"
                    }}
                ],
                "crypto_matches": 0,
                "enhanced_description": "Detailed event description",
                "topics": ["topic1", "topic2"],
                "target_audience": "Description of target audience"
            }}
            
            Focus on accuracy and confidence scoring. Mark crypto_company/industry_match as true
            if you recognize the entity from the crypto/blockchain space.
            
            HTML Content:
            {html_content[:12000]}...
            """

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Try to extract JSON from response
            if "{" in response_text and "}" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_str = response_text[start:end]

                extracted_data = json.loads(json_str)

                # Convert to enhanced format
                enhanced_speakers = []
                for speaker in extracted_data.get("speakers", []):
                    enhanced_speaker = EnhancedSpeakerDetection(
                        name=speaker.get("name", ""),
                        title=speaker.get("title"),
                        company=speaker.get("company"),
                        bio=speaker.get("bio"),
                        confidence=speaker.get("confidence", 0.6),
                        confidence_level=self._get_confidence_level(
                            speaker.get("confidence", 0.6)
                        ),
                        industry_match=speaker.get("industry_match", False),
                    )
                    enhanced_speakers.append(enhanced_speaker)

                enhanced_sponsors = []
                for sponsor in extracted_data.get("sponsors", []):
                    tier_str = sponsor.get("tier", "unknown").lower()
                    tier = SponsorTier.UNKNOWN
                    try:
                        tier = SponsorTier(tier_str)
                    except ValueError:
                        pass

                    enhanced_sponsor = EnhancedSponsorDetection(
                        name=sponsor.get("name", ""),
                        tier=tier,
                        confidence=sponsor.get("confidence", 0.6),
                        confidence_level=self._get_confidence_level(
                            sponsor.get("confidence", 0.6)
                        ),
                        context="crypto_enhanced_ai",
                        detection_source="ai_analysis",
                    )
                    enhanced_sponsors.append(enhanced_sponsor)

                return {
                    "speakers": enhanced_speakers,
                    "sponsors": enhanced_sponsors,
                    "organizers": extracted_data.get("organizers", []),
                    "crypto_matches": extracted_data.get("crypto_matches", 0),
                }

            return {}

        except Exception as e:
            logger.error(f"Crypto-enhanced AI extraction failed: {e}")
            return {}

    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert confidence score to confidence level"""
        if confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    async def _advanced_visual_intelligence_analysis(
        self, image_urls: List[str], base_url: str
    ) -> VisualIntelligenceResult:
        """Advanced visual intelligence analysis with booth mapping and agenda extraction"""
        try:
            if not self.model or not image_urls:
                return VisualIntelligenceResult()

            # Enhanced multimodal analysis prompt
            prompt_parts = [
                """Analyze these event images with advanced visual intelligence capabilities.
                
                For each image, identify:
                1. AGENDA SCHEDULES: Session times, speaker names, session titles
                2. SPONSOR LOGOS: Company logos and tier classification (only from visible logos/text)
                3. SPEAKER IDENTIFICATION: Speaker names from photos, nameplates, or agenda text
                
                Return comprehensive JSON:
                {
                    "agenda_items": [
                        {
                            "title": "Session Title",
                            "speaker_names": ["Speaker 1", "Speaker 2"],
                            "time_start": "10:00",
                            "time_end": "11:00",
                            "session_type": "keynote/panel/workshop"
                        }
                    ],
                    "sponsors_detected": [
                        {
                            "name": "Company Name",
                            "tier": "gold/silver/bronze",
                            "confidence": 0.0-1.0,
                            "detection_source": "logo/banner/text"
                        }
                    ],
                    "speakers_detected": [
                        {
                            "name": "Speaker Name",
                            "confidence": 0.0-1.0,
                            "context": "photo/agenda/nameplate"
                        }
                    ]
                }
                
                Focus on extracting maximum value from visual information."""
            ]

            # Add images (limit to avoid timeout)
            for url in image_urls[:5]:
                try:
                    prompt_parts.append(Part.from_uri(url, mime_type="image/*"))
                except:
                    continue  # Skip problematic images

            if len(prompt_parts) == 1:  # No images added
                return VisualIntelligenceResult()

            response = self.model.generate_content(prompt_parts)
            response_text = response.text.strip()

            # Extract JSON
            if "{" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_str = response_text[start:end]
                visual_data = json.loads(json_str)

                # Convert sponsors to enhanced format
                enhanced_sponsors = []
                for sponsor in visual_data.get("sponsors_detected", []):
                    tier_str = sponsor.get("tier", "unknown").lower()
                    tier = SponsorTier.UNKNOWN
                    try:
                        tier = SponsorTier(tier_str)
                    except ValueError:
                        pass

                    enhanced_sponsor = EnhancedSponsorDetection(
                        name=sponsor.get("name", ""),
                        tier=tier,
                        confidence=sponsor.get("confidence", 0.7),
                        confidence_level=self._get_confidence_level(
                            sponsor.get("confidence", 0.7)
                        ),
                        context="visual_intelligence",
                        detection_source=sponsor.get("detection_source", "visual"),
                        booth_info=sponsor.get("booth_info"),
                    )
                    enhanced_sponsors.append(enhanced_sponsor)

                # Convert speakers to enhanced format
                enhanced_speakers = []
                for speaker in visual_data.get("speakers_detected", []):
                    enhanced_speaker = EnhancedSpeakerDetection(
                        name=speaker.get("name", ""),
                        title=None,
                        company=None,
                        bio=None,
                        confidence=speaker.get("confidence", 0.7),
                        confidence_level=self._get_confidence_level(
                            speaker.get("confidence", 0.7)
                        ),
                        industry_match=False,  # Would need to check against crypto knowledge
                        session_info=speaker.get("session_info"),
                    )
                    enhanced_speakers.append(enhanced_speaker)

                return VisualIntelligenceResult(
                    booth_detections=[],  # FIXED: Removed inaccurate booth detection
                    agenda_items=visual_data.get("agenda_items", []),
                    crowd_analysis=None,  # FIXED: Removed inaccurate crowd analysis
                    floor_plan_analysis=None,  # FIXED: Removed inaccurate floor plan analysis
                )

            return VisualIntelligenceResult()

        except Exception as e:
            logger.error(f"Advanced visual intelligence analysis failed: {e}")
            return VisualIntelligenceResult()

    async def _scrape_external_sites_enhanced(
        self, urls: List[str], enable_mcp: bool
    ) -> List[Dict[str, Any]]:
        """Enhanced external site scraping with MCP fallback"""
        results = []

        for url in urls:
            try:
                # Try standard scraping first
                async with self.session.get(url, timeout=15) as response:
                    content = await response.text()

                # Check if scraping was successful
                if len(content) < 500:  # Likely blocked or minimal content
                    if enable_mcp and self.mcp_available:
                        logger.info(
                            f"🌐 Standard scraping failed, would use MCP for {url}"
                        )
                        # In actual implementation, would use MCP client here

                soup = BeautifulSoup(content, "html.parser")

                # Enhanced extraction with crypto knowledge
                speakers = self._extract_team_info_enhanced(soup)
                sponsors = self._extract_partner_info_enhanced(soup)

                results.append(
                    {
                        "url": url,
                        "speakers": speakers,
                        "sponsors": sponsors,
                        "mcp_used": False,  # Would be True if MCP was actually used
                    }
                )

            except Exception as e:
                logger.warning(f"Enhanced external site scraping failed for {url}: {e}")
                continue

        return results

    def _extract_team_info_enhanced(self, soup) -> List[EnhancedSpeakerDetection]:
        """Enhanced team extraction with crypto industry matching"""
        speakers = []

        # Look for team sections
        team_sections = soup.find_all(
            ["div", "section"], class_=lambda x: x and "team" in x.lower()
        )

        for section in team_sections:
            names = section.find_all(["h3", "h4", "p"])
            for name_elem in names:
                name = name_elem.get_text().strip()
                if len(name) > 3 and len(name) < 50:  # Reasonable name length
                    # Check if it's a known crypto personality
                    industry_match = name.lower() in self.crypto_personalities

                    enhanced_speaker = EnhancedSpeakerDetection(
                        name=name,
                        title=None,
                        company=None,
                        bio=None,
                        confidence=0.6 if not industry_match else 0.9,
                        confidence_level=(
                            ConfidenceLevel.MEDIUM
                            if not industry_match
                            else ConfidenceLevel.HIGH
                        ),
                        industry_match=industry_match,
                    )
                    speakers.append(enhanced_speaker)

        return speakers[:5]  # Limit to 5

    def _extract_partner_info_enhanced(self, soup) -> List[EnhancedSponsorDetection]:
        """Enhanced partner extraction with crypto industry matching"""
        sponsors = []

        # Look for partner sections
        partner_sections = soup.find_all(
            ["div", "section"],
            class_=lambda x: x
            and any(term in x.lower() for term in ["partner", "sponsor", "client"]),
        )

        for section in partner_sections:
            # Look for company names
            company_elems = section.find_all(["img", "h3", "h4"])
            for elem in company_elems:
                company_name = ""

                if elem.name == "img":
                    company_name = elem.get("alt", "")
                else:
                    company_name = elem.get_text().strip()

                if company_name and len(company_name) > 2 and len(company_name) < 50:
                    # Check if it's a known crypto company
                    is_crypto = company_name.lower() in self.crypto_companies

                    enhanced_sponsor = EnhancedSponsorDetection(
                        name=company_name,
                        tier=SponsorTier.PARTNER,
                        confidence=0.6 if not is_crypto else 0.9,
                        confidence_level=(
                            ConfidenceLevel.MEDIUM
                            if not is_crypto
                            else ConfidenceLevel.HIGH
                        ),
                        context="external_site_enhanced",
                        detection_source=(
                            "external_text" if elem.name != "img" else "external_logo"
                        ),
                    )
                    sponsors.append(enhanced_sponsor)

        return sponsors[:5]  # Limit to 5

    async def _apply_data_refinement(self, result: EnhancedExtractionResult):
        """Apply data refinement and deduplication"""
        try:
            # Deduplicate sponsors by name (case insensitive)
            seen_sponsors = set()
            unique_sponsors = []
            for sponsor in result.sponsors:
                name_key = sponsor.name.lower().strip()
                if name_key not in seen_sponsors and name_key:
                    seen_sponsors.add(name_key)
                    unique_sponsors.append(sponsor)
            result.sponsors = unique_sponsors

            # Deduplicate speakers by name
            seen_speakers = set()
            unique_speakers = []
            for speaker in result.speakers:
                name_key = speaker.name.lower().strip()
                if name_key not in seen_speakers and name_key:
                    seen_speakers.add(name_key)
                    unique_speakers.append(speaker)
            result.speakers = unique_speakers

            # Count crypto industry matches
            crypto_matches = 0
            for speaker in result.speakers:
                if speaker.industry_match:
                    crypto_matches += 1
            for sponsor in result.sponsors:
                if sponsor.name.lower() in self.crypto_companies:
                    crypto_matches += 1

            result.crypto_industry_matches = crypto_matches

        except Exception as e:
            logger.error(f"Data refinement failed: {e}")

    def _calculate_enhanced_completeness(
        self, result: EnhancedExtractionResult
    ) -> float:
        """Enhanced completeness calculation with visual intelligence and crypto matches"""
        total_weight = 0
        achieved_weight = 0

        # Core fields - same as before but with bonuses
        core_fields = [
            ("name", 3),
            ("description", 2),
            ("start_date", 1),
            ("location", 1),
        ]

        for field, weight in core_fields:
            total_weight += weight
            value = getattr(result, field, "")
            if value and len(value.strip()) > 10:
                achieved_weight += weight
            elif value and len(value.strip()) > 0:
                achieved_weight += weight * 0.5

        # Enhanced entity scoring
        sponsors_count = len(result.sponsors)
        speakers_count = len(result.speakers)

        # Sponsors with tier weighting
        sponsor_weight = 2.5  # Increased weight
        total_weight += sponsor_weight
        if sponsors_count >= 3:
            achieved_weight += sponsor_weight
        elif sponsors_count >= 1:
            achieved_weight += sponsor_weight * 0.7

        # Speakers with crypto industry bonus
        speaker_weight = 2.0  # Increased weight
        total_weight += speaker_weight
        if speakers_count >= 5:
            achieved_weight += speaker_weight
        elif speakers_count >= 1:
            achieved_weight += speaker_weight * 0.6

        # Visual intelligence bonus
        if result.visual_intelligence:
            vi_weight = 1.0
            total_weight += vi_weight
            vi_score = 0
            if result.visual_intelligence.booth_detections:
                vi_score += 0.4
            if result.visual_intelligence.agenda_items:
                vi_score += 0.4
            if result.visual_intelligence.crowd_analysis:
                vi_score += 0.2
            achieved_weight += vi_weight * vi_score

        # Crypto industry knowledge bonus
        if result.crypto_industry_matches > 0:
            crypto_weight = 0.5
            total_weight += crypto_weight
            # Scale bonus with matches (max at 5 matches)
            crypto_bonus = min(result.crypto_industry_matches / 5.0, 1.0)
            achieved_weight += crypto_weight * crypto_bonus

        # Data refinement bonus
        if result.data_refinement_applied:
            achieved_weight += 0.3
            total_weight += 0.3

        # Multi-source extraction bonus (enhanced)
        source_count = len(result.data_sources)
        if source_count >= 5:
            achieved_weight += 1.2
            total_weight += 1.2
        elif source_count >= 4:
            achieved_weight += 1.0
            total_weight += 1.2
        elif source_count >= 3:
            achieved_weight += 0.8
            total_weight += 1.2
        else:
            total_weight += 1.2

        # MCP browser bonus
        if result.mcp_browser_used:
            achieved_weight += 0.2
            total_weight += 0.2

        final_score = achieved_weight / total_weight if total_weight > 0 else 0.0
        return min(max(final_score, 0.0), 1.0)

    async def _save_enhanced_to_database(
        self, result: EnhancedExtractionResult
    ) -> bool:
        """Save enhanced extraction result to database"""
        try:
            # Convert enhanced data to database format
            event_data = {
                "url": result.url,
                "luma_url": result.url,
                "event_name": result.name,
                "name": result.name,
                "description": result.description,
                "start_date": result.start_date,
                "location_name": result.location,
                "category": "Enhanced Event Extraction",
                "extraction_method": "enhanced_orchestrator",
                "status": result.status,
                "processing_time": result.processing_time,
                "completeness_score": result.completeness_score,
                # Convert enhanced speakers to simple format for database
                "speakers": (
                    [speaker.name for speaker in result.speakers]
                    if result.speakers
                    else []
                ),
                "sponsors": (
                    [sponsor.name for sponsor in result.sponsors]
                    if result.sponsors
                    else []
                ),
                "organizers": (
                    [org.get("name", str(org)) for org in result.organizers]
                    if result.organizers
                    else []
                ),
                # Enhanced metadata
                "data_sources": result.data_sources,
                "images_analyzed": result.images_analyzed,
                "external_sites_scraped": result.external_sites_scraped,
                "crypto_industry_matches": result.crypto_industry_matches,
                "visual_intelligence_used": bool(
                    result.visual_intelligence
                    and (
                        result.visual_intelligence.booth_detections
                        or result.visual_intelligence.agenda_items
                    )
                ),
                "mcp_browser_used": result.mcp_browser_used,
                "data_refinement_applied": result.data_refinement_applied,
            }

            await save_event_data(event_data)
            return True

        except Exception as e:
            logger.error(f"Enhanced database save error: {e}")
            return False

    # Utility methods from original orchestrator
    async def _discover_images(self, html_content: str, base_url: str) -> List[str]:
        """Discover relevant images from the page"""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            image_urls = []

            for img in soup.find_all("img"):
                src = img.get("src") or img.get("data-src")
                if src:
                    full_url = urljoin(base_url, src)
                    if self._is_relevant_image(src, img):
                        image_urls.append(full_url)

            return image_urls[:10]

        except Exception as e:
            logger.error(f"Image discovery failed: {e}")
            return []

    def _is_relevant_image(self, url: str, img_element) -> bool:
        """Check if image is relevant for analysis"""
        url_lower = url.lower()

        relevant_keywords = [
            "speaker",
            "sponsor",
            "partner",
            "logo",
            "banner",
            "avatar",
            "profile",
            "booth",
            "floor",
            "agenda",
        ]
        if any(keyword in url_lower for keyword in relevant_keywords):
            return True

        attrs_text = " ".join(str(v) for v in img_element.attrs.values()).lower()
        if any(keyword in attrs_text for keyword in relevant_keywords):
            return True

        skip_keywords = ["icon", "favicon", "pixel", "tracking"]
        if any(keyword in url_lower for keyword in skip_keywords):
            return False

        return False

    async def _analyze_images_for_entities(
        self, image_urls: List[str]
    ) -> Dict[str, Any]:
        """Standard image analysis (fallback method)"""
        try:
            if not self.model or not image_urls:
                return {}

            prompt_parts = [
                "Analyze these event images and extract sponsor companies and speaker names. "
                "Look for logos, company names, and people photos with names. "
                'Return JSON format: {"sponsors": [{"name": "Company", "source": "logo/text"}], '
                '"speakers": [{"name": "Person", "source": "photo/text"}]}'
            ]

            for url in image_urls[:5]:
                try:
                    prompt_parts.append(Part.from_uri(url, mime_type="image/*"))
                except:
                    continue

            if len(prompt_parts) == 1:
                return {}

            response = self.model.generate_content(prompt_parts)
            response_text = response.text.strip()

            if "{" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_str = response_text[start:end]
                return json.loads(json_str)

            return {}

        except Exception as e:
            logger.error(f"Standard image analysis failed: {e}")
            return {}

    async def _find_external_sites(self, html_content: str, base_url: str) -> List[str]:
        """Find external official websites"""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            external_urls = []

            for link in soup.find_all("a", href=True):
                href = link["href"]
                link_text = link.get_text().lower()

                skip_domains = [
                    "twitter.com",
                    "linkedin.com",
                    "facebook.com",
                    "instagram.com",
                    "lu.ma",
                ]
                if any(domain in href for domain in skip_domains):
                    continue

                website_indicators = [
                    "website",
                    "official",
                    "site",
                    "learn more",
                    "details",
                ]
                if any(indicator in link_text for indicator in website_indicators):
                    full_url = urljoin(base_url, href)
                    if full_url not in external_urls:
                        external_urls.append(full_url)

            return external_urls[:3]

        except Exception as e:
            logger.error(f"External site discovery failed: {e}")
            return []

    def _extract_meta_description(self, soup) -> str:
        """Extract meta description"""
        meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find(
            "meta", attrs={"property": "og:description"}
        )
        return meta_desc.get("content", "") if meta_desc else ""

    def _extract_start_date(self, soup) -> str:
        """Extract event start date"""
        time_elem = soup.find("time")
        if time_elem:
            datetime_attr = time_elem.get("datetime")
            if datetime_attr:
                return datetime_attr
            text_content = time_elem.get_text()
            if text_content:
                return text_content.strip()
        return ""

    def _extract_location(self, soup) -> str:
        """Extract event location"""
        location_keywords = ["location", "venue", "address"]
        for keyword in location_keywords:
            elem = soup.find(
                string=lambda text: text and keyword.lower() in text.lower()
            )
            if elem and isinstance(elem, str):
                return elem.strip()
        return ""

    def _extract_image_urls(self, html_content: str, url: str) -> List[str]:
        """Extract image URLs from HTML content for visual analysis"""
        try:
            import urllib.parse

            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, "html.parser")
            image_urls = []

            # Find all img tags
            img_tags = soup.find_all("img")

            for img in img_tags:
                src = img.get("src") or img.get("data-src") or img.get("data-original")
                if src:
                    # Convert relative URLs to absolute URLs
                    if src.startswith("//"):
                        src = "https:" + src
                    elif src.startswith("/"):
                        src = urllib.parse.urljoin(url, src)
                    elif not src.startswith(("http://", "https://")):
                        src = urllib.parse.urljoin(url, src)

                    # Filter out small icons and ensure reasonable image size
                    if any(
                        skip in src.lower()
                        for skip in ["icon", "favicon", "logo-small", "button"]
                    ):
                        continue

                    # Add valid image URL
                    if src not in image_urls and any(
                        ext in src.lower()
                        for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]
                    ):
                        image_urls.append(src)

            # Limit to first 10 images to avoid processing too many
            return image_urls[:10]

        except Exception as e:
            self.logger.warning(f"⚠️ Image URL extraction failed: {e}")
            return []

    def _is_calendar_page(self, url: str) -> bool:
        """Detect if URL is a calendar/listing page rather than individual event"""
        url_lower = url.lower()

        # Special logic for Luma URLs
        if "lu.ma/" in url_lower:
            # Extract the path after lu.ma/
            path = url_lower.split("lu.ma/")[-1]

            # Calendar pages typically have meaningful names (ethcc, devcon, etc.)
            # Individual events have random IDs (8-12 characters, mix of letters/numbers)
            if len(path) > 12 or not re.match(r"^[a-z0-9]{8,12}$", path):
                return True  # Likely a calendar page
            else:
                return False  # Likely an individual event

        # Additional calendar indicators
        calendar_indicators = [
            "/events",  # Generic events listing
            "/calendar",  # Calendar pages
            "events?",  # Events with query parameters
            "eventbrite.com/o/",  # Eventbrite organizer pages
            "meetup.com/[^/]+/events/?$",  # Meetup group event listings
        ]

        return any(indicator in url_lower for indicator in calendar_indicators)

    async def _extract_multiple_events_from_calendar(
        self, calendar_url: str
    ) -> List[EnhancedExtractionResult]:
        """Extract multiple events directly from a calendar page using browser automation"""
        self.logger.info(f"📅 Extracting multiple events from calendar: {calendar_url}")

        try:
            if not self.mcp_available:
                self.logger.warning(
                    "Browser automation not available for calendar extraction"
                )
                # Fallback to processing as single calendar summary
                return [
                    await self._extract_single_event_enhanced(
                        calendar_url, 0, 120, True, True
                    )
                ]

            # Use browser automation to get the full calendar page content
            browser_result = await self._process_with_browser_automation(calendar_url)

            if not browser_result or not browser_result.success:
                self.logger.warning(
                    f"Browser automation failed for calendar: {calendar_url}"
                )
                # Fallback to processing as single calendar summary
                return [
                    await self._extract_single_event_enhanced(
                        calendar_url, 0, 120, True, True
                    )
                ]

            # Extract multiple events from the calendar page content using AI
            multiple_events = await self._extract_calendar_events_with_ai(
                calendar_url, browser_result.content
            )

            if multiple_events and len(multiple_events) > 1:
                self.logger.info(
                    f"✅ Extracted {len(multiple_events)} events from calendar"
                )
                for i, event in enumerate(multiple_events[:5]):
                    self.logger.info(f"     {i+1}. {event.name}")
                if len(multiple_events) > 5:
                    self.logger.info(f"     ... and {len(multiple_events) - 5} more")
                return multiple_events
            else:
                self.logger.warning(
                    "No multiple events found, processing as calendar summary"
                )
                # Fallback to processing as single calendar summary
                return [
                    await self._extract_single_event_enhanced(
                        calendar_url, 0, 120, True, True
                    )
                ]

        except Exception as e:
            self.logger.error(
                f"Error extracting events from calendar {calendar_url}: {e}"
            )
            # Fallback to processing as single calendar summary
            return [
                await self._extract_single_event_enhanced(
                    calendar_url, 0, 120, True, True
                )
            ]

    async def _extract_calendar_events_with_ai(
        self, calendar_url: str, content: str
    ) -> List[EnhancedExtractionResult]:
        """Extract multiple events from calendar page content using AI"""
        try:
            # Use AI to extract multiple events from the calendar content
            calendar_extraction_prompt = f"""
Extract ALL individual events from this calendar page content. The page shows multiple events in a list format.

For EACH event found, extract:
- title: Event name/title
- description: Event description (if available)
- date_start: Event start date
- time_start: Event start time
- location: Event location/venue
- organizer: Event organizer (if available)
- url: The original calendar URL (since individual URLs may not be available)

Return a JSON array of events, even if some fields are missing. Extract as many events as you can see in the content.

Calendar URL: {calendar_url}
Content: {content[:15000]}...

Return only valid JSON array:
"""

            # Get AI extraction
            ai_result = await self.ai_processor.extract_with_retry(
                calendar_extraction_prompt, calendar_url
            )

            if not ai_result or not ai_result.success:
                self.logger.warning("AI extraction failed for calendar events")
                return []

            # Parse AI result
            import json

            try:
                events_data = json.loads(ai_result.data.get("content", "[]"))
                if not isinstance(events_data, list):
                    events_data = [events_data]
            except:
                self.logger.warning("Failed to parse AI calendar events result")
                return []

            # Convert to EnhancedExtractionResult objects
            extracted_events = []
            for i, event_data in enumerate(events_data):
                if isinstance(event_data, dict) and event_data.get("title"):
                    result = EnhancedExtractionResult(
                        url=calendar_url,
                        name=event_data.get("title", f"Event {i+1}"),
                        description=event_data.get("description", ""),
                        date_start=event_data.get("date_start", ""),
                        time_start=event_data.get("time_start", ""),
                        location=event_data.get("location", ""),
                        organizer=event_data.get("organizer", ""),
                        status="success",
                        completeness_score=0.7,  # Good score for calendar extraction
                        processing_time=1.0,
                        speakers=[],
                        sponsors=[],
                        crypto_industry_matches=0,
                        visual_intelligence=VisualIntelligenceResult(),
                        mcp_browser_used=True,
                        enhanced_data={"source": "calendar_extraction"},
                        error_message="",
                    )
                    extracted_events.append(result)

            return extracted_events

        except Exception as e:
            self.logger.error(f"Error in AI calendar extraction: {e}")
            return []

    async def _process_calendar_urls(
        self, urls: List[str]
    ) -> Tuple[List[EnhancedExtractionResult], List[str]]:
        """Process calendar URLs by extracting multiple events, return calendar results and non-calendar URLs"""
        calendar_results = []
        non_calendar_urls = []

        for url in urls:
            if self.is_calendar_page_simple(url):
                self.logger.info(f"📅 Calendar page detected (simple): {url}")

                # Extract multiple events from calendar using simple method
                calendar_events = await self.extract_calendar_simple(url)

                if calendar_events and len(calendar_events) > 1:
                    # Process database integration if enabled
                    if (
                        self.database_integration_enabled
                        and self.comprehensive_reporting_enabled
                    ):
                        calendar_report = (
                            await self._process_database_integration_for_calendar(
                                calendar_events, url
                            )
                        )
                        # Add report to events
                        for event in calendar_events:
                            event.calendar_extraction_report = calendar_report

                    # Add all calendar events to results
                    calendar_results.extend(calendar_events)
                    self.logger.info(
                        f"✅ Simple extraction found {len(calendar_events)} events from calendar {url}"
                    )

                    if self.database_integration_enabled:
                        total_added = sum(
                            getattr(
                                event.calendar_extraction_report,
                                "events_added_to_db",
                                0,
                            )
                            for event in calendar_events
                            if event.calendar_extraction_report
                        )
                        total_existing = sum(
                            getattr(
                                event.calendar_extraction_report,
                                "events_already_in_db",
                                0,
                            )
                            for event in calendar_events
                            if event.calendar_extraction_report
                        )
                        self.logger.info(
                            f"📊 Database integration: {total_added} added, {total_existing} already existed"
                        )
                else:
                    # Process as single URL if extraction failed
                    non_calendar_urls.append(url)
                    self.logger.warning(
                        f"⚠️ Calendar detected but simple extraction failed, processing as single event: {url}"
                    )
            else:
                # Keep non-calendar URLs for normal processing
                non_calendar_urls.append(url)

        return calendar_results, non_calendar_urls

    def is_calendar_page_simple(self, url: str) -> bool:
        """Simple calendar page detection for staging"""
        url_lower = url.lower()

        # Luma calendar detection
        if "lu.ma/" in url_lower:
            path = url_lower.split("lu.ma/")[-1]
            # Calendar pages have meaningful names, not random IDs
            if len(path) > 12 or not re.match(r"^[a-z0-9]{8,12}$", path):
                return True

        return False

    async def extract_calendar_simple(self, url: str) -> List[EnhancedExtractionResult]:
        """Enhanced calendar extraction using Link Finder Agent"""
        if not self.is_calendar_page_simple(url):
            return [await self._extract_single_event_enhanced(url, 0, 120, True, True)]

        self.logger.info(f"📅 Starting enhanced calendar extraction for: {url}")

        try:
            # Try using the Link Finder Agent first for robust calendar extraction
            try:
                import sys

                sys.path.append(
                    "/Users/eladm/Projects/token/tokenhunter/agents/experimental"
                )
                from link_finder_agent import LinkFinderAgent

                agent = LinkFinderAgent()
                event_links = await agent.run_async(url)

                if event_links and len(event_links) > 1:
                    self.logger.info(
                        f"🔗 Link Finder Agent found {len(event_links)} events"
                    )

                    events = []
                    for event_data in event_links[:50]:  # Limit to first 50 events
                        event_url = event_data.get("url", "")
                        event_name = event_data.get("name", "Unknown Event")

                        if event_url and "lu.ma/" in event_url:
                            result = EnhancedExtractionResult(
                                url=event_url,
                                name=event_name,
                                description=f"Event discovered from calendar: {url}",
                                status="success",
                                completeness_score=0.4,  # Will be improved during individual extraction
                                processing_time=0.5,
                                speakers=[],
                                sponsors=[],
                                crypto_industry_matches=0,
                                error_message="",
                            )
                            result.data_sources = ["link_finder_agent"]
                            events.append(result)

                    self.logger.info(
                        f"✅ Enhanced calendar extraction found {len(events)} individual events"
                    )
                    return events

            except ImportError as e:
                self.logger.warning(f"Link Finder Agent not available: {e}")
            except Exception as e:
                self.logger.warning(f"Link Finder Agent failed: {e}")

            # Fallback to simple HTTP-based extraction
            return await self._fallback_calendar_extraction(url)

        except Exception as e:
            self.logger.error(f"Enhanced calendar extraction failed: {e}")
            return [await self._extract_single_event_enhanced(url, 0, 120, True, True)]

    async def _fallback_calendar_extraction(
        self, url: str
    ) -> List[EnhancedExtractionResult]:
        """Fallback calendar extraction using simple HTTP"""
        try:
            # Fetch calendar page
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    return [
                        await self._extract_single_event_enhanced(
                            url, 0, 120, True, True
                        )
                    ]
                content = await response.text()

            # Simple parsing
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(content, "html.parser")

            events = []

            # Find event links
            event_links = set()
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "/lu.ma/" in href or href.startswith("/"):
                    if href.startswith("/"):
                        href = f"https://lu.ma{href}"

                    if "lu.ma/" in href:
                        path = href.split("lu.ma/")[-1]
                        if re.match(r"^[a-z0-9]{8,12}$", path):
                            event_links.add(href)

            # Add individual event URLs
            for link in list(event_links)[:20]:
                result = EnhancedExtractionResult(
                    url=link,
                    name=f"Event {link.split('/')[-1]}",
                    description="Individual event from calendar (fallback)",
                    status="success",
                    completeness_score=0.3,
                    processing_time=0.5,
                    speakers=[],
                    sponsors=[],
                    crypto_industry_matches=0,
                    error_message="",
                )
                result.data_sources = ["fallback_calendar_extraction"]
                events.append(result)

            self.logger.info(
                f"📅 Fallback calendar extraction found {len(events)} events from {url}"
            )
            return (
                events
                if events
                else [
                    await self._extract_single_event_enhanced(url, 0, 120, True, True)
                ]
            )

        except Exception as e:
            self.logger.error(f"Fallback calendar extraction failed: {e}")
            return [await self._extract_single_event_enhanced(url, 0, 120, True, True)]

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()


# Public interface function for enhanced extraction
async def extract_events_enhanced(
    urls: List[str],
    max_concurrent: int = 8,
    timeout_per_event: int = 120,
    enable_visual_intelligence: bool = True,
    enable_mcp_browser: bool = True,
) -> List[EnhancedExtractionResult]:
    """
    Extract comprehensive data using EventExtractor with agent capabilities
    """
    orchestrator = EventExtractor()

    try:
        if not await orchestrator.initialize():
            logger.error("❌ Failed to initialize event extractor")
            return []

        logger.info(f"🚀 Starting enhanced extraction of {len(urls)} events")

        results = await orchestrator.extract_events_comprehensive(
            urls=urls,
            max_concurrent=max_concurrent,
            timeout_per_event=timeout_per_event,
            enable_visual_intelligence=enable_visual_intelligence,
            enable_mcp_browser=enable_mcp_browser,
        )

        return results

    finally:
        await orchestrator.cleanup()


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    async def test_enhanced_orchestration():
        """Test the enhanced orchestrator"""
        urls = [
            "https://lu.ma/91fw4m6t",
            "https://lu.ma/FOIS_ETHCC",
            "https://lu.ma/dappshub",
        ]

        results = await extract_events_enhanced(
            urls=urls,
            max_concurrent=2,
            timeout_per_event=90,
            enable_visual_intelligence=True,
            enable_mcp_browser=True,
        )

        print("\n🎯 ENHANCED RESULTS SUMMARY:")
        for i, result in enumerate(results):
            print(f"Event {i+1}: {result.name}")
            print(f"  Completeness: {result.completeness_score:.2f}")
            print(f"  Speakers: {len(result.speakers)}")
            print(f"  Sponsors: {len(result.sponsors)}")
            print(f"  Crypto matches: {result.crypto_industry_matches}")
            print(
                f"  Visual intel: {bool(result.visual_intelligence.booth_detections or result.visual_intelligence.agenda_items)}"
            )
            print(f"  MCP used: {result.mcp_browser_used}")

    asyncio.run(test_enhanced_orchestration())
