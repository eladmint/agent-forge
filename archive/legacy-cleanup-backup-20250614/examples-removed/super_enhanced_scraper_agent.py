#!/usr/bin/env python3

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# from swarms import Agent  # REMOVED - Framework migration complete

# Import existing components
try:
    from .page_scraper_agent import PageScraperAgent
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent.parent))
    from extraction.agents.experimental.page_scraper_agent import PageScraperAgent

# Import our Steel Browser client - corrected path
try:
    from ....mcp_tools.steel_enhanced_client import SteelEnhancedScrapingManager
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from mcp_tools.steel_enhanced_client import SteelEnhancedScrapingManager

# Import anti-bot evasion manager - corrected path
try:
    from ....shared.anti_bot_evasion_manager import EvasionLevel
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    from agent_forge.core.shared.anti_bot_evasion_manager import EvasionLevel

logger = logging.getLogger(__name__)


@dataclass
class SiteAnalysis:
    """Analysis of website complexity and protection mechanisms"""

    complexity: str  # 'simple', 'moderate', 'high'
    has_captcha: bool
    has_anti_bot: bool
    recommended_tier: int
    confidence: float
    detection_methods: List[str]
    estimated_response_time: float


@dataclass
class ScrapingResult:
    """Result of scraping operation"""

    status: str  # 'Success', 'Failed', 'Partial'
    data: Optional[Dict[str, Any]]
    tier_used: int
    tier_name: str
    response_time: float
    error: Optional[str]
    analysis: Optional[SiteAnalysis]
    metadata: Optional[Dict[str, Any]]


class IntelligentRouter:
    """Analyzes sites and routes to optimal scraping tier"""

    def __init__(self):
        self.site_history: Dict[str, SiteAnalysis] = {}
        self.success_rates: Dict[int, List[bool]] = {1: [], 2: [], 3: []}

    async def analyze_site(self, url: str) -> SiteAnalysis:
        """Analyze site complexity and protection mechanisms"""

        # Check cache first
        domain = self._extract_domain(url)
        if domain in self.site_history:
            cached = self.site_history[domain]
            logger.info(
                f"Using cached analysis for {domain}: tier {cached.recommended_tier}"
            )
            return cached

        analysis = SiteAnalysis(
            complexity="moderate",
            has_captcha=False,
            has_anti_bot=False,
            recommended_tier=2,
            confidence=0.6,
            detection_methods=[],
            estimated_response_time=3.0,
        )

        # URL-based analysis
        if any(
            known in url.lower()
            for known in ["luma.co", "eventbrite.com", "meetup.com"]
        ):
            analysis.complexity = "simple"
            analysis.recommended_tier = 1
            analysis.confidence = 0.95
            analysis.detection_methods.append("known_simple_site")
            analysis.estimated_response_time = 2.0

        elif any(
            protected in url.lower()
            for protected in [
                "facebook.com",
                "instagram.com",
                "linkedin.com",
                "twitter.com",
                "x.com",
                "discord.com",
                "telegram.org",
            ]
        ):
            analysis.complexity = "high"
            analysis.has_anti_bot = True
            analysis.recommended_tier = 3
            analysis.confidence = 0.9
            analysis.detection_methods.append("known_protected_site")
            analysis.estimated_response_time = 8.0

        elif any(
            moderate in url.lower()
            for moderate in [
                "github.com",
                "stackoverflow.com",
                "medium.com",
                "substack.com",
            ]
        ):
            analysis.complexity = "moderate"
            analysis.recommended_tier = 2
            analysis.confidence = 0.8
            analysis.detection_methods.append("known_moderate_site")
            analysis.estimated_response_time = 4.0

        # Advanced analysis based on URL patterns
        if any(
            captcha_indicator in url.lower()
            for captcha_indicator in ["captcha", "verify", "security", "challenge"]
        ):
            analysis.has_captcha = True
            analysis.recommended_tier = max(analysis.recommended_tier, 2)
            analysis.detection_methods.append("captcha_url_pattern")

        # Check for dynamic content indicators
        if any(
            dynamic in url.lower()
            for dynamic in ["api.", "app.", "secure.", "auth.", "login.", "dashboard."]
        ):
            analysis.complexity = "moderate"
            analysis.recommended_tier = max(analysis.recommended_tier, 2)
            analysis.detection_methods.append("dynamic_subdomain")

        # Cache the analysis
        self.site_history[domain] = analysis

        logger.info(
            f"Site analysis for {url}: {analysis.complexity} complexity, tier {analysis.recommended_tier}"
        )
        return analysis

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for caching"""
        try:
            from urllib.parse import urlparse

            return urlparse(url).netloc.lower()
        except Exception:
            return url.lower()

    def update_success_rate(self, tier: int, success: bool):
        """Update success rate tracking for tier optimization"""
        self.success_rates[tier].append(success)

        # Keep only last 100 attempts
        if len(self.success_rates[tier]) > 100:
            self.success_rates[tier] = self.success_rates[tier][-100:]

    def get_tier_performance(self) -> Dict[int, float]:
        """Get current performance metrics for each tier"""
        performance = {}
        for tier, results in self.success_rates.items():
            if results:
                performance[tier] = sum(results) / len(results)
            else:
                performance[tier] = 0.0
        return performance


class SuperEnhancedScraperAgent:
    """Framework-free three-tier scraping agent with intelligent routing"""

    def __init__(
        self,
        name: str = "SuperEnhancedScraperAgent",
        logger: Optional[logging.Logger] = None,
        evasion_level: EvasionLevel = EvasionLevel.STEALTH,
    ):
        """Initialize the SuperEnhancedScraperAgent.

        Args:
            name: Name of the agent.
            logger: Optional logger instance.
            evasion_level: Level of anti-bot evasion to apply.
            logger: Optional logger instance. If None, a default logger is created.
        """
        self.name = name
        self.logger = logger if logger else logging.getLogger(self.__class__.__name__)
        self.logger.info("[%s] initialized framework-free agent", self.name)

        # Initialize tier handlers
        self.tier1_playwright = PageScraperAgent(logger=self.logger)
        self.tier2_steel = None  # Will be initialized lazily
        self.tier3_bright_data = None  # Future implementation

        # Initialize intelligent router
        self.router = IntelligentRouter()

        # Performance tracking
        self.stats = {
            "total_requests": 0,
            "tier_usage": {1: 0, 2: 0, 3: 0},
            "success_rates": {1: [], 2: [], 3: []},
            "average_response_times": {1: [], 2: [], 3: []},
        }

    async def run_async(
        self, website_url: str, existing_event_data: Optional[Dict] = None
    ) -> Tuple[str, Optional[Dict]]:
        """Main entry point for enhanced scraping with intelligent routing"""

        start_time = time.time()
        self.stats["total_requests"] += 1

        try:
            logger.info(f"SuperEnhancedScraperAgent processing: {website_url}")

            # Step 1: Analyze site complexity
            analysis = await self.router.analyze_site(website_url)
            logger.info(
                f"Site analysis: {analysis.complexity} complexity, recommended tier {analysis.recommended_tier}"
            )

            # Step 2: Execute scraping based on analysis
            result = await self._execute_intelligent_scraping(
                website_url, analysis, existing_event_data
            )

            # Step 3: Update performance tracking
            self._update_stats(result, time.time() - start_time)

            # Step 4: Return result in expected format
            if result.status == "Success":
                return ("Success", result.data)
            else:
                logger.warning(f"Scraping failed: {result.error}")
                return (
                    "Failed",
                    {"error": result.error, "analysis": analysis.__dict__},
                )

        except Exception as e:
            logger.error(f"SuperEnhancedScraperAgent error: {e}")
            return ("Failed", {"error": str(e)})

    async def _execute_intelligent_scraping(
        self,
        url: str,
        analysis: SiteAnalysis,
        existing_event_data: Optional[Dict] = None,
    ) -> ScrapingResult:
        """Execute scraping with intelligent tier selection and fallback"""

        # Determine tier order based on analysis
        tier_order = self._determine_tier_order(analysis)
        logger.info(f"Tier execution order: {tier_order}")

        last_error = None

        for tier in tier_order:
            try:
                start_time = time.time()
                result = await self._execute_tier(tier, url, existing_event_data)
                response_time = time.time() - start_time

                # Update performance tracking
                self.router.update_success_rate(tier, result.status == "Success")
                self.stats["tier_usage"][tier] += 1
                self.stats["average_response_times"][tier].append(response_time)

                if result.status == "Success":
                    result.tier_used = tier
                    result.response_time = response_time
                    result.analysis = analysis
                    logger.info(f"Tier {tier} succeeded in {response_time:.2f}s")
                    return result
                else:
                    last_error = result.error
                    logger.warning(f"Tier {tier} failed: {result.error}")

            except Exception as e:
                last_error = str(e)
                logger.error(f"Tier {tier} exception: {e}")
                continue

        # All tiers failed
        return ScrapingResult(
            status="Failed",
            data=None,
            tier_used=0,
            tier_name="None",
            response_time=0.0,
            error=f"All tiers failed. Last error: {last_error}",
            analysis=analysis,
            metadata=None,
        )

    def _determine_tier_order(self, analysis: SiteAnalysis) -> List[int]:
        """Determine optimal tier execution order based on analysis"""

        # Start with recommended tier
        primary_tier = analysis.recommended_tier

        # Build tier order
        if primary_tier == 1:
            # Simple sites: try Playwright first, then Steel if needed
            return [1, 2]
        elif primary_tier == 2:
            # Moderate sites: try Steel first (it's free!), fallback to Playwright
            return [2, 1]
        elif primary_tier == 3:
            # Complex sites: Steel first (free), then premium if really needed
            return [2, 3]
        else:
            # Default: Steel -> Playwright -> Premium
            return [2, 1, 3]

    async def _execute_tier(
        self, tier: int, url: str, existing_event_data: Optional[Dict] = None
    ) -> ScrapingResult:
        """Execute scraping for specific tier"""

        if tier == 1:
            return await self._tier1_playwright(url, existing_event_data)
        elif tier == 2:
            return await self._tier2_steel(url, existing_event_data)
        elif tier == 3:
            return await self._tier3_bright_data(url, existing_event_data)
        else:
            raise ValueError(f"Unknown tier: {tier}")

    async def _tier1_playwright(
        self, url: str, context: Optional[Dict] = None
    ) -> ScrapingResult:
        """Tier 1: Fast Playwright scraping"""

        try:
            # Use existing Playwright-based scraper
            status, data = await self._run_playwright_scraper(url, context)

            return ScrapingResult(
                status=status,
                data=data,
                tier_used=1,
                tier_name="Playwright",
                response_time=0.0,  # Will be set by caller
                error=None if status == "Success" else "Playwright scraping failed",
                analysis=None,
                metadata={"method": "playwright", "fast": True},
            )

        except Exception as e:
            return ScrapingResult(
                status="Failed",
                data=None,
                tier_used=1,
                tier_name="Playwright",
                response_time=0.0,
                error=str(e),
                analysis=None,
                metadata=None,
            )

    async def _tier2_steel(
        self, url: str, context: Optional[Dict] = None
    ) -> ScrapingResult:
        """Tier 2: Steel Browser enhanced scraping (FREE!)"""

        try:
            # Initialize Steel Browser client if needed
            if self.tier2_steel is None:
                self.tier2_steel = SteelEnhancedScrapingManager()
                await self.tier2_steel.__aenter__()

            # Use Steel Browser for enhanced scraping
            result = await self.tier2_steel.scrape_with_intelligence(url)

            if result.get("status") == "Success":
                return ScrapingResult(
                    status="Success",
                    data=result.get("data"),
                    tier_used=2,
                    tier_name="Steel Browser",
                    response_time=0.0,  # Will be set by caller
                    error=None,
                    analysis=None,
                    metadata={
                        "method": "steel_browser",
                        "anti_bot": True,
                        "captcha_solving": True,
                        "enhanced": True,
                    },
                )
            else:
                return ScrapingResult(
                    status="Failed",
                    data=None,
                    tier_used=2,
                    tier_name="Steel Browser",
                    response_time=0.0,
                    error=result.get("error", "Steel Browser scraping failed"),
                    analysis=None,
                    metadata=None,
                )

        except Exception as e:
            return ScrapingResult(
                status="Failed",
                data=None,
                tier_used=2,
                tier_name="Steel Browser",
                response_time=0.0,
                error=str(e),
                analysis=None,
                metadata=None,
            )

    async def _tier3_bright_data(
        self, url: str, context: Optional[Dict] = None
    ) -> ScrapingResult:
        """Tier 3: Bright Data premium scraping (Future implementation)"""

        # For now, return not implemented
        return ScrapingResult(
            status="Failed",
            data=None,
            tier_used=3,
            tier_name="Bright Data (Not Implemented)",
            response_time=0.0,
            error="Bright Data tier not yet implemented",
            analysis=None,
            metadata=None,
        )

    async def _run_playwright_scraper(
        self, url: str, context: Optional[Dict] = None
    ) -> Tuple[str, Optional[Dict]]:
        """Run existing Playwright-based scraper"""

        try:
            # Use the existing PageScraperAgent
            result = await self.tier1_playwright.run_async(url)

            if isinstance(result, tuple):
                return result
            else:
                # Handle different return format
                return ("Success", result)

        except Exception as e:
            logger.error(f"Playwright scraper error: {e}")
            return ("Failed", {"error": str(e)})

    def _update_stats(self, result: ScrapingResult, total_time: float):
        """Update performance statistics"""

        tier = result.tier_used
        success = result.status == "Success"

        self.stats["success_rates"][tier].append(success)

        # Keep only last 100 results
        for tier_key in self.stats["success_rates"]:
            if len(self.stats["success_rates"][tier_key]) > 100:
                self.stats["success_rates"][tier_key] = self.stats["success_rates"][
                    tier_key
                ][-100:]

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""

        stats = {
            "total_requests": self.stats["total_requests"],
            "tier_usage": dict(self.stats["tier_usage"]),
            "tier_success_rates": {},
            "tier_avg_response_times": {},
        }

        # Calculate success rates
        for tier, results in self.stats["success_rates"].items():
            if results:
                stats["tier_success_rates"][tier] = sum(results) / len(results)
            else:
                stats["tier_success_rates"][tier] = 0.0

        # Calculate average response times
        for tier, times in self.stats["average_response_times"].items():
            if times:
                stats["tier_avg_response_times"][tier] = sum(times) / len(times)
            else:
                stats["tier_avg_response_times"][tier] = 0.0

        return stats

    async def cleanup(self):
        """Clean up resources"""

        if self.tier2_steel:
            await self.tier2_steel.__aexit__(None, None, None)
            self.tier2_steel = None

        logger.info("SuperEnhancedScraperAgent cleanup completed")


# Test function
async def test_super_enhanced_scraper():
    """Test the SuperEnhancedScraperAgent"""

    logger.info("Testing SuperEnhancedScraperAgent...")

    agent = SuperEnhancedScraperAgent()

    test_urls = [
        "https://luma.co/event/test",  # Should use Tier 1
        "https://github.com/test",  # Should use Tier 2
        # "https://facebook.com/test"   # Would use Tier 3 (not implemented)
    ]

    try:
        for url in test_urls:
            logger.info(f"Testing URL: {url}")

            status, data = await agent.run_async(url)
            logger.info(f"Result: {status}")

            if data:
                logger.info(
                    f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}"
                )

        # Log performance stats
        stats = agent.get_performance_stats()
        logger.info("Performance Stats:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")

    finally:
        await agent.cleanup()

    logger.info("SuperEnhancedScraperAgent test completed!")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_super_enhanced_scraper())
