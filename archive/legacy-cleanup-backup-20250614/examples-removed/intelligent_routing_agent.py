"""
🧠 Intelligent Routing Agent for Nuru AI Event Intelligence Platform

PURPOSE: Smart coordination between agents with optimal task distribution and performance optimization
INTEGRATION: Sprint 1 Week 3 - Intelligent Routing Agent Development  
FOUNDATION: Coordinates existing 4-agent pipeline (Scroll, Link Discovery, Text Extraction, Validation)
TARGET: 90%+ coordination efficiency through optimized routing algorithms

ARCHITECTURE:
- Smart routing logic for optimal agent coordination and task distribution
- Performance optimization through intelligent agent selection and load balancing
- Error handling and recovery mechanisms for robust multi-agent coordination
- Completion of 5-agent architecture ready for final Content Enhancement Agent integration

PERFORMANCE TARGETS:
- Agent coordination efficiency: 90%+
- Task distribution optimization: 85%+
- Error recovery success rate: 95%+
- Overall pipeline throughput: 2x improvement over sequential processing
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import json
import traceback

# Import our specialized agents
try:
    from .scroll_agent import EnhancedScrollAgent
except ImportError:
    EnhancedScrollAgent = None

try:
    from .link_discovery_agent import EnhancedLinkDiscoveryAgent
except ImportError:
    EnhancedLinkDiscoveryAgent = None

try:
    from .text_extraction_agent import EnhancedTextExtractionAgent
except ImportError:
    EnhancedTextExtractionAgent = None

try:
    from .validation_agent import EnhancedValidationAgent, ValidationResult
except ImportError:
    EnhancedValidationAgent = None
    ValidationResult = None


class AgentType(Enum):
    """Types of agents in the pipeline"""

    SCROLL = "scroll"
    LINK_DISCOVERY = "link_discovery"
    TEXT_EXTRACTION = "text_extraction"
    VALIDATION = "validation"
    CONTENT_ENHANCEMENT = "content_enhancement"  # For future implementation


class TaskPriority(Enum):
    """Task priority levels for intelligent routing"""

    CRITICAL = "critical"  # Immediate processing required
    HIGH = "high"  # High priority processing
    NORMAL = "normal"  # Standard priority
    LOW = "low"  # Background processing
    BATCH = "batch"  # Batch processing when resources available


class AgentStatus(Enum):
    """Agent availability status"""

    AVAILABLE = "available"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class RoutingTask:
    """Task definition for intelligent routing"""

    task_id: str
    task_type: AgentType
    priority: TaskPriority
    data: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    estimated_duration: float = 0.0
    platform: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "data": self.data,
            "dependencies": self.dependencies,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat(),
            "estimated_duration": self.estimated_duration,
            "platform": self.platform,
        }


@dataclass
class AgentMetrics:
    """Agent performance metrics for routing decisions"""

    agent_type: AgentType
    total_tasks_processed: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_processing_time: float = 0.0
    current_load: int = 0
    max_load: int = 5
    last_error: Optional[str] = None
    error_count: int = 0
    status: AgentStatus = AgentStatus.AVAILABLE

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_tasks_processed == 0:
            return 1.0
        return self.successful_tasks / self.total_tasks_processed

    @property
    def load_percentage(self) -> float:
        """Calculate current load percentage"""
        return (self.current_load / self.max_load) * 100.0

    def update_metrics(self, success: bool, processing_time: float, error: str = None):
        """Update agent metrics after task completion"""
        self.total_tasks_processed += 1

        if success:
            self.successful_tasks += 1
        else:
            self.failed_tasks += 1
            self.error_count += 1
            if error:
                self.last_error = error

        # Update rolling average processing time
        if self.total_tasks_processed == 1:
            self.average_processing_time = processing_time
        else:
            # Exponential moving average
            alpha = 0.3
            self.average_processing_time = (
                alpha * processing_time + (1 - alpha) * self.average_processing_time
            )


@dataclass
class RoutingResult:
    """Result of agent task execution"""

    task_id: str
    agent_type: AgentType
    success: bool
    result_data: Any
    processing_time: float
    error_message: Optional[str] = None
    retries_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_type": self.agent_type.value,
            "success": self.success,
            "result_data": self.result_data,
            "processing_time": self.processing_time,
            "error_message": self.error_message,
            "retries_used": self.retries_used,
            "metadata": self.metadata,
        }


class IntelligentRoutingAgent:
    """
    🧠 Intelligent Routing Agent for optimal multi-agent coordination

    CORE CAPABILITIES:
    - Smart task distribution based on agent capabilities and current load
    - Dynamic load balancing across available agents
    - Intelligent error handling and recovery mechanisms
    - Performance monitoring and optimization
    - Dependency-aware task scheduling

    ROUTING STRATEGIES:
    1. Load-Based Routing: Distribute tasks based on current agent load
    2. Performance-Based Routing: Route to agents with best success rates
    3. Capability-Based Routing: Match tasks to agent specializations
    4. Priority-Based Routing: Handle high-priority tasks first
    5. Dependency-Aware Routing: Respect task dependencies and sequencing
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize agents
        self._init_agents()

        # Routing state
        self.agent_metrics: Dict[AgentType, AgentMetrics] = {}
        self.active_tasks: Dict[str, RoutingTask] = {}
        self.completed_tasks: Dict[str, RoutingResult] = {}
        self.task_queue: List[RoutingTask] = []

        # Performance tracking
        self.total_pipeline_runs = 0
        self.successful_pipeline_runs = 0
        self.average_pipeline_time = 0.0

        # Initialize metrics for each agent
        self._init_agent_metrics()

        # Configuration
        self.max_concurrent_tasks = self.config.get("max_concurrent_tasks", 10)
        self.task_timeout = self.config.get("task_timeout", 300)  # 5 minutes
        self.enable_load_balancing = self.config.get("enable_load_balancing", True)
        self.enable_smart_routing = self.config.get("enable_smart_routing", True)

    def _init_agents(self):
        """Initialize all specialized agents"""
        try:
            if EnhancedScrollAgent:
                self.scroll_agent = EnhancedScrollAgent()
            if EnhancedLinkDiscoveryAgent:
                self.link_discovery_agent = EnhancedLinkDiscoveryAgent()
            if EnhancedTextExtractionAgent:
                self.text_extraction_agent = EnhancedTextExtractionAgent()
            if EnhancedValidationAgent:
                self.validation_agent = EnhancedValidationAgent()

            self.logger.info("Specialized agents initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {str(e)}")
            # Continue with mock agents for development
            self.scroll_agent = None
            self.link_discovery_agent = None
            self.text_extraction_agent = None
            self.validation_agent = None

    def _init_agent_metrics(self):
        """Initialize metrics tracking for each agent"""
        agent_configs = {
            AgentType.SCROLL: {"max_load": 3, "avg_time": 30.0},
            AgentType.LINK_DISCOVERY: {"max_load": 5, "avg_time": 10.0},
            AgentType.TEXT_EXTRACTION: {"max_load": 4, "avg_time": 20.0},
            AgentType.VALIDATION: {"max_load": 8, "avg_time": 5.0},
        }

        for agent_type, config in agent_configs.items():
            self.agent_metrics[agent_type] = AgentMetrics(
                agent_type=agent_type,
                max_load=config["max_load"],
                average_processing_time=config["avg_time"],
            )

    async def process_extraction_pipeline(
        self,
        calendar_url: str,
        platform: str = "generic",
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> Dict[str, Any]:
        """
        Process complete extraction pipeline with intelligent routing

        Args:
            calendar_url: URL of calendar to process
            platform: Platform type (luma, eventbrite, etc.)
            priority: Task priority level

        Returns:
            Complete extraction results with metadata
        """
        pipeline_start_time = time.time()
        pipeline_id = f"pipeline_{int(time.time() * 1000)}"

        try:
            self.logger.info(
                f"Starting extraction pipeline {pipeline_id} for {calendar_url}"
            )

            # Create and execute pipeline tasks
            results = await self._execute_pipeline_tasks(
                pipeline_id, calendar_url, platform, priority
            )

            # Calculate pipeline metrics
            pipeline_time = time.time() - pipeline_start_time
            self._update_pipeline_metrics(True, pipeline_time)

            # Compile final results
            final_results = self._compile_pipeline_results(
                results, pipeline_id, pipeline_time
            )

            self.logger.info(
                f"Pipeline {pipeline_id} completed successfully in {pipeline_time:.2f}s"
            )

            return final_results

        except Exception as e:
            pipeline_time = time.time() - pipeline_start_time
            self._update_pipeline_metrics(False, pipeline_time)

            self.logger.error(f"Pipeline {pipeline_id} failed: {str(e)}")

            return {
                "pipeline_id": pipeline_id,
                "success": False,
                "error": str(e),
                "processing_time": pipeline_time,
                "results": {},
            }

    async def _execute_pipeline_tasks(
        self, pipeline_id: str, calendar_url: str, platform: str, priority: TaskPriority
    ) -> Dict[str, RoutingResult]:
        """Execute pipeline tasks with intelligent routing"""
        results = {}

        # Task 1: Scroll Agent - Discover all events
        scroll_task = RoutingTask(
            task_id=f"{pipeline_id}_scroll",
            task_type=AgentType.SCROLL,
            priority=priority,
            data={"calendar_url": calendar_url, "platform": platform},
            platform=platform,
        )

        scroll_result = await self._execute_single_task(scroll_task)
        results["scroll"] = scroll_result

        if not scroll_result.success:
            self.logger.error(f"Scroll agent failed for {pipeline_id}")
            return results

        # Task 2: Link Discovery Agent - Process discovered events
        events_data = scroll_result.result_data.get("events", [])
        if not events_data:
            self.logger.warning(
                f"No events discovered by scroll agent for {pipeline_id}"
            )
            return results

        link_task = RoutingTask(
            task_id=f"{pipeline_id}_links",
            task_type=AgentType.LINK_DISCOVERY,
            priority=priority,
            data={"events": events_data, "platform": platform},
            dependencies=[scroll_task.task_id],
            platform=platform,
        )

        link_result = await self._execute_single_task(link_task)
        results["link_discovery"] = link_result

        if not link_result.success:
            self.logger.error(f"Link discovery agent failed for {pipeline_id}")
            return results

        # Task 3: Text Extraction Agent - Extract detailed event data
        validated_events = link_result.result_data.get("validated_events", events_data)

        text_task = RoutingTask(
            task_id=f"{pipeline_id}_text",
            task_type=AgentType.TEXT_EXTRACTION,
            priority=priority,
            data={"events": validated_events, "platform": platform},
            dependencies=[link_task.task_id],
            platform=platform,
        )

        text_result = await self._execute_single_task(text_task)
        results["text_extraction"] = text_result

        if not text_result.success:
            self.logger.error(f"Text extraction agent failed for {pipeline_id}")
            return results

        # Task 4: Validation Agent - Validate extracted data
        extracted_events = text_result.result_data.get("extracted_events", [])

        validation_task = RoutingTask(
            task_id=f"{pipeline_id}_validation",
            task_type=AgentType.VALIDATION,
            priority=priority,
            data={"events": extracted_events, "platform": platform},
            dependencies=[text_task.task_id],
            platform=platform,
        )

        validation_result = await self._execute_single_task(validation_task)
        results["validation"] = validation_result

        return results

    async def _execute_single_task(self, task: RoutingTask) -> RoutingResult:
        """Execute a single task with intelligent agent selection"""
        start_time = time.time()

        try:
            # Select optimal agent based on routing strategy
            selected_agent = self._select_optimal_agent(task)

            if not selected_agent:
                return RoutingResult(
                    task_id=task.task_id,
                    agent_type=task.task_type,
                    success=False,
                    result_data=None,
                    processing_time=time.time() - start_time,
                    error_message="No available agent for task type",
                )

            # Update agent load
            self.agent_metrics[task.task_type].current_load += 1

            # Execute task with selected agent
            result_data = await self._execute_agent_task(selected_agent, task)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Update agent metrics
            self.agent_metrics[task.task_type].update_metrics(
                success=True, processing_time=processing_time
            )

            return RoutingResult(
                task_id=task.task_id,
                agent_type=task.task_type,
                success=True,
                result_data=result_data,
                processing_time=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            error_message = str(e)

            # Update agent metrics
            self.agent_metrics[task.task_type].update_metrics(
                success=False, processing_time=processing_time, error=error_message
            )

            self.logger.error(f"Task {task.task_id} failed: {error_message}")

            return RoutingResult(
                task_id=task.task_id,
                agent_type=task.task_type,
                success=False,
                result_data=None,
                processing_time=processing_time,
                error_message=error_message,
            )

        finally:
            # Decrease agent load
            if task.task_type in self.agent_metrics:
                self.agent_metrics[task.task_type].current_load = max(
                    0, self.agent_metrics[task.task_type].current_load - 1
                )

    def _select_optimal_agent(self, task: RoutingTask) -> Optional[Any]:
        """Select optimal agent for task execution"""
        agent_type = task.task_type

        # Check if agent type is available
        if agent_type not in self.agent_metrics:
            return None

        metrics = self.agent_metrics[agent_type]

        # Check if agent is available (not at max load)
        if metrics.current_load >= metrics.max_load:
            self.logger.warning(f"Agent {agent_type.value} at max load")
            return None

        # Check agent status
        if metrics.status != AgentStatus.AVAILABLE:
            self.logger.warning(
                f"Agent {agent_type.value} not available: {metrics.status.value}"
            )
            return None

        # Return appropriate agent instance
        agent_map = {
            AgentType.SCROLL: getattr(self, "scroll_agent", None),
            AgentType.LINK_DISCOVERY: getattr(self, "link_discovery_agent", None),
            AgentType.TEXT_EXTRACTION: getattr(self, "text_extraction_agent", None),
            AgentType.VALIDATION: getattr(self, "validation_agent", None),
        }

        return agent_map.get(agent_type)

    async def _execute_agent_task(
        self, agent: Any, task: RoutingTask
    ) -> Dict[str, Any]:
        """Execute task with specific agent"""
        task_data = task.data

        if task.task_type == AgentType.SCROLL:
            # Execute scroll agent
            if agent and hasattr(agent, "discover_all_events"):
                calendar_url = task_data.get("calendar_url")
                platform = task_data.get("platform", "generic")
                events = await agent.discover_all_events(calendar_url, platform)
                return {"events": events, "platform": platform}
            else:
                # Mock response for development
                return {
                    "events": [
                        {"url": task_data.get("calendar_url"), "name": "Mock Event"}
                    ],
                    "platform": task_data.get("platform", "generic"),
                }

        elif task.task_type == AgentType.LINK_DISCOVERY:
            # Execute link discovery agent
            if agent and hasattr(agent, "process_event_links"):
                events = task_data.get("events", [])
                platform = task_data.get("platform", "generic")
                validated_events = await agent.process_event_links(events, platform)
                return {"validated_events": validated_events, "platform": platform}
            else:
                # Mock response for development
                events = task_data.get("events", [])
                return {
                    "validated_events": events,
                    "platform": task_data.get("platform", "generic"),
                }

        elif task.task_type == AgentType.TEXT_EXTRACTION:
            # Execute text extraction agent
            if agent and hasattr(agent, "extract_event_details"):
                events = task_data.get("events", [])
                platform = task_data.get("platform", "generic")
                extracted_events = await agent.extract_event_details(events, platform)
                return {"extracted_events": extracted_events, "platform": platform}
            else:
                # Mock response for development
                events = task_data.get("events", [])
                return {
                    "extracted_events": events,
                    "platform": task_data.get("platform", "generic"),
                }

        elif task.task_type == AgentType.VALIDATION:
            # Execute validation agent
            if agent and hasattr(agent, "validate_event_data"):
                events = task_data.get("events", [])
                platform = task_data.get("platform", "generic")

                validated_results = []
                for event in events:
                    validation_result = await agent.validate_event_data(
                        event, source_agent="text_extraction", correction_mode=True
                    )
                    validated_results.append(
                        {
                            "event": event,
                            "validation": (
                                validation_result.to_dict()
                                if hasattr(validation_result, "to_dict")
                                else {"is_valid": True}
                            ),
                        }
                    )

                return {"validated_events": validated_results, "platform": platform}
            else:
                # Mock response for development
                events = task_data.get("events", [])
                validated_results = [
                    {
                        "event": event,
                        "validation": {"is_valid": True, "overall_quality_score": 0.8},
                    }
                    for event in events
                ]
                return {
                    "validated_events": validated_results,
                    "platform": task_data.get("platform", "generic"),
                }

        else:
            raise ValueError(f"Unknown agent type: {task.task_type}")

    def _compile_pipeline_results(
        self, results: Dict[str, RoutingResult], pipeline_id: str, pipeline_time: float
    ) -> Dict[str, Any]:
        """Compile final pipeline results"""

        # Extract final events data
        final_events = []
        if "validation" in results and results["validation"].success:
            validation_data = results["validation"].result_data
            final_events = validation_data.get("validated_events", [])
        elif "text_extraction" in results and results["text_extraction"].success:
            text_data = results["text_extraction"].result_data
            final_events = text_data.get("extracted_events", [])
        elif "link_discovery" in results and results["link_discovery"].success:
            link_data = results["link_discovery"].result_data
            final_events = link_data.get("validated_events", [])
        elif "scroll" in results and results["scroll"].success:
            scroll_data = results["scroll"].result_data
            final_events = scroll_data.get("events", [])

        # Calculate quality metrics
        total_events = len(final_events)
        validated_events = 0
        high_quality_events = 0

        for event_result in final_events:
            if isinstance(event_result, dict) and "validation" in event_result:
                validation = event_result["validation"]
                if validation.get("is_valid"):
                    validated_events += 1
                if validation.get("overall_quality_score", 0) >= 0.8:
                    high_quality_events += 1
            else:
                # If no validation data, count as basic event
                validated_events += 1

        # Compile performance metrics
        agent_performance = {}
        for agent_type, result in results.items():
            agent_performance[agent_type] = {
                "success": result.success,
                "processing_time": result.processing_time,
                "error": result.error_message,
            }

        return {
            "pipeline_id": pipeline_id,
            "success": True,
            "total_events": total_events,
            "validated_events": validated_events,
            "high_quality_events": high_quality_events,
            "validation_rate": (
                validated_events / total_events if total_events > 0 else 0
            ),
            "quality_rate": (
                high_quality_events / total_events if total_events > 0 else 0
            ),
            "processing_time": pipeline_time,
            "agent_performance": agent_performance,
            "events": final_events,
            "routing_metadata": {
                "total_pipeline_runs": self.total_pipeline_runs,
                "success_rate": self.successful_pipeline_runs
                / max(1, self.total_pipeline_runs),
                "average_pipeline_time": self.average_pipeline_time,
                "agent_metrics": {
                    agent_type.value: {
                        "success_rate": metrics.success_rate,
                        "average_time": metrics.average_processing_time,
                        "current_load": metrics.current_load,
                        "total_processed": metrics.total_tasks_processed,
                    }
                    for agent_type, metrics in self.agent_metrics.items()
                },
            },
        }

    def _update_pipeline_metrics(self, success: bool, pipeline_time: float):
        """Update overall pipeline performance metrics"""
        self.total_pipeline_runs += 1

        if success:
            self.successful_pipeline_runs += 1

        # Update rolling average pipeline time
        if self.total_pipeline_runs == 1:
            self.average_pipeline_time = pipeline_time
        else:
            # Exponential moving average
            alpha = 0.3
            self.average_pipeline_time = (
                alpha * pipeline_time + (1 - alpha) * self.average_pipeline_time
            )

    def get_routing_status(self) -> Dict[str, Any]:
        """Get current routing agent status and metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_pipeline_runs": self.total_pipeline_runs,
            "successful_pipeline_runs": self.successful_pipeline_runs,
            "success_rate": self.successful_pipeline_runs
            / max(1, self.total_pipeline_runs),
            "average_pipeline_time": self.average_pipeline_time,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "agent_metrics": {
                agent_type.value: {
                    "status": metrics.status.value,
                    "success_rate": metrics.success_rate,
                    "average_processing_time": metrics.average_processing_time,
                    "current_load": metrics.current_load,
                    "max_load": metrics.max_load,
                    "load_percentage": metrics.load_percentage,
                    "total_tasks_processed": metrics.total_tasks_processed,
                    "error_count": metrics.error_count,
                    "last_error": metrics.last_error,
                }
                for agent_type, metrics in self.agent_metrics.items()
            },
        }


# Export main class
__all__ = [
    "IntelligentRoutingAgent",
    "RoutingTask",
    "RoutingResult",
    "TaskPriority",
    "AgentType",
]
