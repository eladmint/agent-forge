"""
Regional Coordination Manager for Multi-Agent Architecture

This module provides regional session management, rotation logic, and coordination
for the distributed agent system across multiple Cloud Run regions.
"""

import logging
import random
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from playwright.async_api import Browser, async_playwright

from .base_agent import AgentTask, RegionalSession

logger = logging.getLogger(__name__)


class RegionManager:
    """
    Manages regional rotation and coordination across agents

    Provides:
    - Intelligent regional selection based on load and rate limits
    - Session management with browser context isolation
    - Regional performance tracking and optimization
    - Anti-detection coordination across regions
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()

        # Regional configuration
        self.regions = self.config.get("regions", ["us-central1", "europe-west1"])
        self.regional_services = self.config.get("regional_services", {})

        # Session management
        self.regional_sessions: Dict[str, RegionalSession] = {}
        self.session_pools: Dict[str, List[RegionalSession]] = defaultdict(list)

        # Performance tracking
        self.regional_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.regional_load: Dict[str, int] = defaultdict(int)
        self.rate_limits: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # Rotation strategy
        self.rotation_history: deque = deque(maxlen=100)
        self.region_rotation_counter = defaultdict(int)

        # Browser management
        self.playwright = None
        self.browsers: Dict[str, Browser] = {}

        logger.info(f"RegionManager initialized with regions: {self.regions}")

    async def initialize(self):
        """Initialize regional infrastructure and browser contexts"""
        logger.info("Initializing RegionManager infrastructure")

        # Initialize Playwright
        self.playwright = await async_playwright().start()

        # Initialize browsers for each region
        for region in self.regions:
            try:
                browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-blink-features=AutomationControlled",
                    ],
                )
                self.browsers[region] = browser
                logger.info(f"Browser initialized for region {region}")
            except Exception as e:
                logger.error(f"Failed to initialize browser for region {region}: {e}")

        # Initialize regional sessions
        for region in self.regions:
            await self._initialize_regional_sessions(region)

    async def cleanup(self):
        """Cleanup regional resources and browser contexts"""
        logger.info("Cleaning up RegionManager resources")

        # Close all sessions
        for session in self.regional_sessions.values():
            await self._close_session(session)

        # Close browsers
        for browser in self.browsers.values():
            await browser.close()

        # Close playwright
        if self.playwright:
            await self.playwright.stop()

    async def get_optimal_region(self, task: AgentTask) -> str:
        """
        Select optimal region based on task requirements and current conditions

        Args:
            task: The agent task to execute

        Returns:
            str: Selected region identifier
        """
        # If task has region preference, validate and use it
        if task.region_preference and task.region_preference in self.regions:
            if await self._is_region_available(task.region_preference):
                return task.region_preference

        # Apply rotation strategy based on task type
        rotation_strategy = self._get_rotation_strategy(task.task_type.value)

        if rotation_strategy == "round_robin":
            return await self._select_round_robin()
        elif rotation_strategy == "load_balanced":
            return await self._select_load_balanced()
        elif rotation_strategy == "random":
            return await self._select_random()
        else:
            return await self._select_intelligent(task)

    async def get_regional_session(self, region: str) -> RegionalSession:
        """
        Get or create a regional session for the specified region

        Args:
            region: The target region

        Returns:
            RegionalSession: Active session for the region
        """
        # Try to get existing active session
        if region in self.regional_sessions:
            session = self.regional_sessions[region]
            if session.is_active and await self._is_session_healthy(session):
                session.last_used = datetime.now()
                session.request_count += 1
                return session

        # Create new session
        session = await self._create_regional_session(region)
        self.regional_sessions[region] = session

        logger.info(f"Created new regional session for {region}: {session.session_id}")
        return session

    async def rotate_region(self, current_region: str, task_type: str) -> str:
        """
        Intelligent regional rotation based on task type and patterns

        Args:
            current_region: Current region being used
            task_type: Type of task being performed

        Returns:
            str: Next region to use
        """
        available_regions = [r for r in self.regions if r != current_region]

        if not available_regions:
            return current_region

        # Apply anti-pattern rotation
        rotation_pattern = self._get_anti_pattern_rotation(task_type)

        if rotation_pattern == "sequential":
            # Sequential rotation through regions
            current_index = self.regions.index(current_region)
            next_index = (current_index + 1) % len(self.regions)
            return self.regions[next_index]
        elif rotation_pattern == "weighted_random":
            # Weighted random based on performance
            return await self._select_weighted_random(available_regions)
        else:
            # Simple random rotation
            return random.choice(available_regions)

    async def update_regional_metrics(self, region: str, metrics: Dict[str, Any]):
        """
        Update performance metrics for a region

        Args:
            region: The region to update
            metrics: Performance metrics data
        """
        if region not in self.regional_metrics:
            self.regional_metrics[region] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0,
                "last_updated": datetime.now().isoformat(),
            }

        region_metrics = self.regional_metrics[region]
        region_metrics["total_requests"] += 1

        if metrics.get("success", False):
            region_metrics["successful_requests"] += 1
        else:
            region_metrics["failed_requests"] += 1

        # Update average response time
        if "execution_time" in metrics:
            current_avg = region_metrics["average_response_time"]
            total_requests = region_metrics["total_requests"]
            new_avg = (
                (current_avg * (total_requests - 1)) + metrics["execution_time"]
            ) / total_requests
            region_metrics["average_response_time"] = new_avg

        region_metrics["last_updated"] = datetime.now().isoformat()

        # Update regional load
        self.regional_load[region] = region_metrics["total_requests"]

        logger.debug(f"Updated metrics for region {region}: {region_metrics}")

    def get_regional_stats(self) -> Dict[str, Any]:
        """Get comprehensive regional statistics"""
        return {
            "regions": self.regions,
            "active_sessions": len(self.regional_sessions),
            "regional_metrics": dict(self.regional_metrics),
            "regional_load": dict(self.regional_load),
            "rotation_history": list(self.rotation_history)[-10:],  # Last 10 rotations
        }

    # Private methods

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default regional configuration"""
        return {
            "regions": ["us-central1", "europe-west1"],
            "regional_services": {
                "us-central1": "https://enhanced-multi-region-us-central-service-url",
                "europe-west1": "https://enhanced-multi-region-europe-west-service-url",
            },
            "session_timeout": 1800,  # 30 minutes
            "max_requests_per_session": 100,
            "rotation_strategies": {
                "scroll_calendar": "round_robin",
                "discover_links": "load_balanced",
                "extract_text": "random",
                "analyze_organizer": "intelligent",
                "process_images": "load_balanced",
                "mine_agenda": "intelligent",
            },
        }

    async def _initialize_regional_sessions(self, region: str):
        """Initialize session pool for a region"""
        try:
            session = await self._create_regional_session(region)
            self.session_pools[region].append(session)
            logger.info(f"Initialized session pool for region {region}")
        except Exception as e:
            logger.error(f"Failed to initialize session pool for region {region}: {e}")

    async def _create_regional_session(self, region: str) -> RegionalSession:
        """Create a new regional session with browser context"""
        session_id = f"{region}_{uuid.uuid4().hex[:8]}"

        # Create browser context with region-specific fingerprint
        browser_context = None
        if region in self.browsers:
            browser_context = await self.browsers[region].new_context(
                user_agent=self._get_regional_user_agent(region),
                locale=self._get_regional_locale(region),
                timezone_id=self._get_regional_timezone(region),
                extra_http_headers=self._get_regional_headers(region),
            )

        # Create HTTP session
        http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=self._get_regional_headers(region),
        )

        return RegionalSession(
            region=region,
            session_id=session_id,
            browser_context=browser_context,
            http_session=http_session,
            created_at=datetime.now(),
            last_used=datetime.now(),
            request_count=0,
            rate_limit_remaining=100,
            is_active=True,
        )

    async def _close_session(self, session: RegionalSession):
        """Close and cleanup a regional session"""
        session.is_active = False

        if session.browser_context:
            await session.browser_context.close()

        if session.http_session:
            await session.http_session.close()

        logger.debug(f"Closed session {session.session_id}")

    async def _is_region_available(self, region: str) -> bool:
        """Check if region is available and healthy"""
        if region not in self.regions:
            return False

        # Check rate limits
        rate_limit_info = self.rate_limits.get(region, {})
        if rate_limit_info.get("blocked_until", datetime.now()) > datetime.now():
            return False

        return True

    async def _is_session_healthy(self, session: RegionalSession) -> bool:
        """Check if session is healthy and usable"""
        # Check session age
        max_age = timedelta(seconds=self.config.get("session_timeout", 1800))
        if datetime.now() - session.created_at > max_age:
            return False

        # Check request count
        max_requests = self.config.get("max_requests_per_session", 100)
        if session.request_count >= max_requests:
            return False

        return session.is_active

    def _get_rotation_strategy(self, task_type: str) -> str:
        """Get rotation strategy for task type"""
        strategies = self.config.get("rotation_strategies", {})
        return strategies.get(task_type, "intelligent")

    async def _select_round_robin(self) -> str:
        """Round-robin region selection"""
        total_requests = sum(self.regional_load.values())
        region_index = total_requests % len(self.regions)
        return self.regions[region_index]

    async def _select_load_balanced(self) -> str:
        """Load-balanced region selection"""
        # Select region with lowest current load
        min_load = min(self.regional_load.values()) if self.regional_load else 0
        candidates = [r for r in self.regions if self.regional_load[r] == min_load]
        return random.choice(candidates)

    async def _select_random(self) -> str:
        """Random region selection"""
        return random.choice(self.regions)

    async def _select_intelligent(self, task: AgentTask) -> str:
        """Intelligent region selection based on multiple factors"""
        region_scores = {}

        for region in self.regions:
            score = 100  # Base score

            # Factor in current load (lower is better)
            load_penalty = self.regional_load.get(region, 0) * 5
            score -= load_penalty

            # Factor in success rate
            metrics = self.regional_metrics.get(region, {})
            total_requests = metrics.get("total_requests", 1)
            successful_requests = metrics.get("successful_requests", 0)
            success_rate = successful_requests / total_requests
            score += success_rate * 50

            # Factor in response time (lower is better)
            avg_response_time = metrics.get("average_response_time", 0)
            time_penalty = avg_response_time * 10
            score -= time_penalty

            region_scores[region] = max(score, 0)

        # Select region with highest score
        best_region = max(region_scores.keys(), key=lambda r: region_scores[r])
        return best_region

    async def _select_weighted_random(self, regions: List[str]) -> str:
        """Weighted random selection based on performance"""
        weights = []
        for region in regions:
            metrics = self.regional_metrics.get(region, {})
            total_requests = metrics.get("total_requests", 1)
            successful_requests = metrics.get("successful_requests", 0)
            success_rate = successful_requests / total_requests
            weights.append(success_rate)

        if sum(weights) == 0:
            return random.choice(regions)

        return random.choices(regions, weights=weights)[0]

    def _get_anti_pattern_rotation(self, task_type: str) -> str:
        """Get anti-pattern rotation strategy"""
        # Different rotation patterns to avoid detection
        patterns = {
            "scroll_calendar": "sequential",
            "discover_links": "weighted_random",
            "extract_text": "random",
            "analyze_organizer": "sequential",
            "process_images": "weighted_random",
            "mine_agenda": "random",
        }
        return patterns.get(task_type, "random")

    def _get_regional_user_agent(self, region: str) -> str:
        """Get region-appropriate user agent"""
        base_agents = {
            "us-central1": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "europe-west1": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        }
        base = base_agents.get(region, base_agents["us-central1"])
        return f"{base} (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    def _get_regional_locale(self, region: str) -> str:
        """Get region-appropriate locale"""
        locales = {"us-central1": "en-US", "europe-west1": "en-GB"}
        return locales.get(region, "en-US")

    def _get_regional_timezone(self, region: str) -> str:
        """Get region-appropriate timezone"""
        timezones = {"us-central1": "America/Chicago", "europe-west1": "Europe/London"}
        return timezones.get(region, "America/Chicago")

    def _get_regional_headers(self, region: str) -> Dict[str, str]:
        """Get region-appropriate HTTP headers"""
        base_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # Regional customizations
        if region == "europe-west1":
            base_headers["Accept-Language"] = "en-GB,en;q=0.5"

        return base_headers


# Export main class
__all__ = ["RegionManager"]
