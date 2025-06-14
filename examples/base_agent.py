"""
Base Agent Foundation for Rotation-Based Multi-Agent Architecture

This module provides the foundation classes for the Agent Forge framework,
implementing autonomous web agents with advanced coordination capabilities.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

import aiohttp
from playwright.async_api import BrowserContext, Page

if TYPE_CHECKING:
    from .region_manager import RegionManager

logger = logging.getLogger(__name__)


class AgentTaskType(Enum):
    """Types of tasks that agents can perform"""

    SCROLL_CALENDAR = "scroll_calendar"
    DISCOVER_LINKS = "discover_links"
    EXTRACT_TEXT = "extract_text"
    ANALYZE_ORGANIZER = "analyze_organizer"
    PROCESS_IMAGES = "process_images"
    MINE_AGENDA = "mine_agenda"


@dataclass
class AgentTask:
    """Base task definition for agent operations"""

    task_id: str
    task_type: AgentTaskType
    target_url: str
    metadata: Dict[str, Any]
    region_preference: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class AgentResult:
    """Result from agent task execution"""

    task_id: str
    success: bool
    data: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    region_used: str
    execution_time: float
    error_message: Optional[str] = None
    next_task_data: Optional[Dict[str, Any]] = None


@dataclass
class RegionalSession:
    """Regional session container with browser context and metadata"""

    region: str
    session_id: str
    browser_context: Optional[BrowserContext]
    http_session: Optional[aiohttp.ClientSession]
    created_at: datetime
    last_used: datetime
    request_count: int
    rate_limit_remaining: int
    is_active: bool


class PerformanceMonitor:
    """Monitors agent performance and provides metrics"""

    def __init__(self):
        self.metrics = {}
        self.start_times = {}

    def start_operation(self, operation_id: str):
        """Start timing an operation"""
        self.start_times[operation_id] = time.time()

    def end_operation(self, operation_id: str) -> float:
        """End timing an operation and return duration"""
        if operation_id in self.start_times:
            duration = time.time() - self.start_times[operation_id]
            self.metrics[operation_id] = duration
            del self.start_times[operation_id]
            return duration
        return 0.0

    def get_metrics(self) -> Dict[str, Any]:
        """Get all performance metrics"""
        return {
            "operation_metrics": self.metrics.copy(),
            "average_operation_time": (
                sum(self.metrics.values()) / len(self.metrics) if self.metrics else 0
            ),
            "total_operations": len(self.metrics),
        }


class RateLimiter:
    """Rate limiting for agent operations"""

    def __init__(self, max_requests_per_minute: int = 60):
        self.max_requests = max_requests_per_minute
        self.request_times = []

    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        current_time = time.time()

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if current_time - t < 60]

        if len(self.request_times) >= self.max_requests:
            # Wait until the oldest request is outside the window
            wait_time = 60 - (current_time - self.request_times[0])
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)

        self.request_times.append(current_time)

    def get_remaining_quota(self) -> int:
        """Get remaining requests for current minute"""
        current_time = time.time()
        recent_requests = [t for t in self.request_times if current_time - t < 60]
        return max(0, self.max_requests - len(recent_requests))


class BaseAgent(ABC):
    """
    Foundation class for all specialized agents with rotation capabilities

    Provides:
    - Regional rotation and session management
    - Rate limiting and performance monitoring
    - Error handling and recovery
    - Anti-detection pattern integration
    """

    def __init__(self, region_manager: "RegionManager"):
        self.region_manager = region_manager
        self.performance_monitor = PerformanceMonitor()
        self.rate_limiter = RateLimiter()
        self.agent_id = f"{self.__class__.__name__}_{id(self)}"
        logger.info(f"Initialized {self.agent_id}")

    async def execute_with_rotation(self, task: AgentTask) -> AgentResult:
        """
        Execute task with intelligent regional rotation

        This is the main entry point for all agent operations, providing:
        - Regional selection and session management
        - Rate limiting and anti-detection
        - Error handling with fallback
        - Performance monitoring
        """
        operation_id = f"{task.task_id}_{task.task_type.value}"
        self.performance_monitor.start_operation(operation_id)

        try:
            # Get optimal region for this task
            optimal_region = await self.region_manager.get_optimal_region(task)
            logger.info(f"Executing {task.task_type.value} in region {optimal_region}")

            # Get regional session
            session = await self.region_manager.get_regional_session(optimal_region)

            # Apply rate limiting
            await self.rate_limiter.wait_if_needed()

            # Execute core agent logic
            result = await self._execute_core_logic(task, session)

            # Update regional metrics
            await self._update_regional_metrics(optimal_region, result)

            # Add performance metrics
            execution_time = self.performance_monitor.end_operation(operation_id)
            result.execution_time = execution_time
            result.performance_metrics = self.performance_monitor.get_metrics()

            logger.info(
                f"Task {task.task_id} completed successfully in {execution_time:.2f}s"
            )
            return result

        except Exception as e:
            execution_time = self.performance_monitor.end_operation(operation_id)
            logger.error(f"Task {task.task_id} failed: {str(e)}")

            # Try fallback if retries available
            if task.retry_count < task.max_retries:
                return await self._handle_error_with_fallback(task, e)
            else:
                return AgentResult(
                    task_id=task.task_id,
                    success=False,
                    data={},
                    performance_metrics=self.performance_monitor.get_metrics(),
                    region_used=task.region_preference or "unknown",
                    execution_time=execution_time,
                    error_message=str(e),
                )

    @abstractmethod
    async def _execute_core_logic(
        self, task: AgentTask, session: RegionalSession
    ) -> AgentResult:
        """
        Core agent logic to be implemented by specialized agents

        Args:
            task: The task to execute
            session: Regional session with browser context and HTTP session

        Returns:
            AgentResult with task execution results
        """
        raise NotImplementedError("Subclasses must implement core logic")

    async def _handle_error_with_fallback(
        self, task: AgentTask, error: Exception
    ) -> AgentResult:
        """
        Handle errors with regional fallback and retry logic

        Args:
            task: The failed task
            error: The exception that occurred

        Returns:
            AgentResult from retry attempt or final failure
        """
        logger.warning(
            f"Attempting fallback for task {task.task_id}, retry {task.retry_count + 1}"
        )

        # Create retry task with different region preference
        retry_task = AgentTask(
            task_id=task.task_id,
            task_type=task.task_type,
            target_url=task.target_url,
            metadata=task.metadata,
            region_preference=None,  # Let region manager choose different region
            retry_count=task.retry_count + 1,
            max_retries=task.max_retries,
        )

        # Wait before retry (exponential backoff)
        wait_time = 2**task.retry_count
        await asyncio.sleep(wait_time)

        return await self.execute_with_rotation(retry_task)

    async def _update_regional_metrics(self, region: str, result: AgentResult):
        """
        Update regional performance metrics

        Args:
            region: The region where the task was executed
            result: The task execution result
        """
        await self.region_manager.update_regional_metrics(
            region,
            {
                "success": result.success,
                "execution_time": result.execution_time,
                "agent_type": self.__class__.__name__,
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _get_agent_specific_config(self) -> Dict[str, Any]:
        """
        Get agent-specific configuration
        Override in subclasses for specialized settings
        """
        return {
            "user_agent": f"Nuru-AI-{self.__class__.__name__}/1.0",
            "timeout": 30,
            "max_retries": 3,
        }


class AntiDetectionEngine:
    """
    Anti-detection pattern engine for natural behavior simulation
    """

    def __init__(self):
        self.patterns = {
            "scroll_timings": [0.8, 1.2, 1.5, 2.0, 2.3],
            "mouse_movements": ["bezier", "natural", "human-like"],
            "pause_probabilities": [0.1, 0.15, 0.2],
            "typing_speeds": [120, 150, 180, 200],  # WPM
        }

    async def add_natural_delay(
        self, min_seconds: float = 0.5, max_seconds: float = 2.0
    ):
        """Add natural, randomized delay"""
        import random

        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def simulate_human_scroll(self, page: Page, distance: int = 300):
        """Simulate human-like scrolling behavior"""
        import random

        # Random scroll distance variation
        actual_distance = distance + random.randint(-50, 50)

        # Scroll in smaller increments
        increments = random.randint(3, 6)
        scroll_per_increment = actual_distance // increments

        for _ in range(increments):
            await page.evaluate(f"window.scrollBy(0, {scroll_per_increment})")
            await self.add_natural_delay(0.1, 0.3)

    async def simulate_human_typing(self, page: Page, selector: str, text: str):
        """Simulate human-like typing patterns"""
        import random

        # Clear field first
        await page.fill(selector, "")

        # Type character by character with human-like timing
        for char in text:
            await page.type(selector, char)
            delay = random.uniform(0.05, 0.15)
            await asyncio.sleep(delay)


# Export main classes
__all__ = [
    "BaseAgent",
    "AgentTask",
    "AgentResult",
    "AgentTaskType",
    "RegionalSession",
    "PerformanceMonitor",
    "RateLimiter",
    "AntiDetectionEngine",
]
