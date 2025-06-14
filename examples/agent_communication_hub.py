"""
Agent Communication Hub for Multi-Agent Coordination

This module provides inter-agent communication, task orchestration, and data flow
coordination between specialized agents in the rotation-based architecture.
"""

import asyncio
import json
import logging
import uuid
from collections import defaultdict, deque
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# Legacy compatibility - these classes are deprecated
from enum import Enum
from typing import NamedTuple, Any

class AgentTaskType(Enum):
    """Legacy task type enum - deprecated"""
    SCRAPE = "scrape"
    EXTRACT = "extract"
    VALIDATE = "validate"

class AgentTask(NamedTuple):
    """Legacy task class - deprecated"""
    task_type: AgentTaskType
    data: Any

class AgentResult(NamedTuple):
    """Legacy result class - deprecated""" 
    success: bool
    data: Any

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages that can be sent between agents"""
    
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    DATA_TRANSFER = "data_transfer"
    STATUS_UPDATE = "status_update"
    COORDINATION_REQUEST = "coordination_request"
    ERROR_NOTIFICATION = "error_notification"
    PERFORMANCE_METRIC = "performance_metric"


class MessagePriority(Enum):
    """Message priority levels for agent communication"""
    
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class AgentMessage:
    """Message structure for inter-agent communication"""
    
    def __init__(
        self,
        message_id: str,
        sender: str,
        recipient: str,
        message_type: MessageType,
        priority: MessagePriority,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ):
        self.message_id = message_id
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.priority = priority
        self.payload = payload
        self.correlation_id = correlation_id
        self.timestamp = datetime.now()
        self.processed = False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format"""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "processed": self.processed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary"""
        return cls(
            message_id=data["message_id"],
            sender=data["sender"],
            recipient=data["recipient"],
            message_type=MessageType(data["message_type"]),
            priority=MessagePriority(data["priority"]),
            payload=data["payload"],
            correlation_id=data.get("correlation_id")
        )


class TaskChain:
    """Represents a chain of tasks flowing through multiple agents"""
    
    def __init__(self, chain_id: str, initial_task: AgentTask):
        self.chain_id = chain_id
        self.initial_task = initial_task
        self.task_sequence: List[AgentTaskType] = []
        self.results: List[AgentResult] = []
        self.current_step = 0
        self.started_at = datetime.now()
        self.completed_at: Optional[datetime] = None
        self.status = "active"  # active, completed, failed, cancelled
        
    def add_result(self, result: AgentResult):
        """Add a task result to the chain"""
        self.results.append(result)
        if result.success:
            self.current_step += 1
        else:
            self.status = "failed"
    
    def is_complete(self) -> bool:
        """Check if all tasks in the chain are complete"""
        return self.current_step >= len(self.task_sequence)
    
    def get_next_task_type(self) -> Optional[AgentTaskType]:
        """Get the next task type in the sequence"""
        if self.current_step < len(self.task_sequence):
            return self.task_sequence[self.current_step]
        return None


class AgentCommunicationHub:
    """
    Central communication hub for multi-agent coordination
    
    Provides:
    - Message routing between agents
    - Task chain orchestration
    - Data flow coordination
    - Performance monitoring and metrics
    - Error handling and recovery
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        
        # Message handling
        self.message_queues: Dict[str, deque] = defaultdict(deque)
        self.message_handlers: Dict[MessageType, List[Callable]] = defaultdict(list)
        self.pending_messages: Dict[str, AgentMessage] = {}
        
        # Agent registry
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_capabilities: Dict[str, List[AgentTaskType]] = {}
        self.agent_status: Dict[str, str] = {}
        
        # Task chain management
        self.active_chains: Dict[str, TaskChain] = {}
        self.completed_chains: List[TaskChain] = []
        
        # Performance tracking
        self.communication_metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_processed": 0,
            "average_processing_time": 0,
            "failed_messages": 0
        }
        
        # Message processing
        self.processing_task: Optional[asyncio.Task] = None
        self.shutdown_event = asyncio.Event()
        
        logger.info("AgentCommunicationHub initialized")
    
    async def initialize(self):
        """Initialize the communication hub"""
        logger.info("Starting AgentCommunicationHub")
        
        # Start message processing task
        self.processing_task = asyncio.create_task(self._process_messages())
        
        # Register default message handlers
        self._register_default_handlers()
        
        logger.info("AgentCommunicationHub started")
    
    async def shutdown(self):
        """Shutdown the communication hub"""
        logger.info("Shutting down AgentCommunicationHub")
        
        self.shutdown_event.set()
        
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        logger.info("AgentCommunicationHub shutdown completed")
    
    def register_agent(
        self, 
        agent_id: str, 
        capabilities: List[AgentTaskType],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register an agent with the communication hub
        
        Args:
            agent_id: Unique identifier for the agent
            capabilities: List of task types the agent can handle
            metadata: Additional agent metadata
        """
        self.registered_agents[agent_id] = {
            "capabilities": capabilities,
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "message_count": 0
        }
        self.agent_capabilities[agent_id] = capabilities
        self.agent_status[agent_id] = "active"
        
        logger.info(f"Registered agent {agent_id} with capabilities: {[c.value for c in capabilities]}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the communication hub"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            del self.agent_capabilities[agent_id]
            del self.agent_status[agent_id]
            
            # Clear pending messages for this agent
            if agent_id in self.message_queues:
                del self.message_queues[agent_id]
            
            logger.info(f"Unregistered agent {agent_id}")
    
    async def send_message(
        self, 
        sender: str, 
        recipient: str, 
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Send a message between agents
        
        Args:
            sender: ID of the sending agent
            recipient: ID of the receiving agent
            message_type: Type of message
            payload: Message data
            priority: Message priority
            correlation_id: Optional correlation ID for message tracking
            
        Returns:
            str: Message ID
        """
        message_id = str(uuid.uuid4())
        
        message = AgentMessage(
            message_id=message_id,
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            priority=priority,
            payload=payload,
            correlation_id=correlation_id
        )
        
        # Add to recipient's queue
        self.message_queues[recipient].append(message)
        self.pending_messages[message_id] = message
        
        # Update metrics
        self.communication_metrics["messages_sent"] += 1
        
        logger.debug(f"Message {message_id} sent from {sender} to {recipient}")
        return message_id
    
    async def receive_messages(self, agent_id: str) -> List[AgentMessage]:
        """
        Receive pending messages for an agent
        
        Args:
            agent_id: ID of the receiving agent
            
        Returns:
            List[AgentMessage]: List of pending messages
        """
        messages = []
        queue = self.message_queues[agent_id]
        
        # Sort by priority (lower number = higher priority)
        sorted_messages = sorted(queue, key=lambda m: m.priority.value)
        
        # Get all messages and clear queue
        for message in sorted_messages:
            messages.append(message)
            message.processed = True
        
        queue.clear()
        
        # Update metrics
        self.communication_metrics["messages_received"] += len(messages)
        
        if messages:
            logger.debug(f"Agent {agent_id} received {len(messages)} messages")
        
        return messages
    
    async def create_task_chain(
        self, 
        initial_task: AgentTask, 
        task_sequence: List[AgentTaskType]
    ) -> str:
        """
        Create a task chain that flows through multiple agents
        
        Args:
            initial_task: The starting task
            task_sequence: Sequence of task types to execute
            
        Returns:
            str: Chain ID
        """
        chain_id = str(uuid.uuid4())
        
        chain = TaskChain(chain_id, initial_task)
        chain.task_sequence = task_sequence
        
        self.active_chains[chain_id] = chain
        
        logger.info(f"Created task chain {chain_id} with {len(task_sequence)} steps")
        
        # Send initial task to appropriate agent
        await self._route_task_to_agent(initial_task, chain_id)
        
        return chain_id
    
    async def update_chain_progress(self, chain_id: str, result: AgentResult):
        """
        Update progress of a task chain
        
        Args:
            chain_id: ID of the task chain
            result: Result from the completed task
        """
        if chain_id not in self.active_chains:
            logger.warning(f"Chain {chain_id} not found")
            return
        
        chain = self.active_chains[chain_id]
        chain.add_result(result)
        
        if chain.is_complete():
            # Mark chain as completed
            chain.status = "completed"
            chain.completed_at = datetime.now()
            self.completed_chains.append(chain)
            del self.active_chains[chain_id]
            
            logger.info(f"Task chain {chain_id} completed successfully")
        else:
            # Route next task
            next_task_type = chain.get_next_task_type()
            if next_task_type and result.next_task_data:
                next_task = AgentTask(
                    task_id=str(uuid.uuid4()),
                    task_type=next_task_type,
                    target_url=result.next_task_data.get("target_url", ""),
                    metadata=result.next_task_data
                )
                await self._route_task_to_agent(next_task, chain_id)
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get comprehensive communication statistics"""
        return {
            "metrics": self.communication_metrics,
            "registered_agents": len(self.registered_agents),
            "active_chains": len(self.active_chains),
            "completed_chains": len(self.completed_chains),
            "pending_messages": len(self.pending_messages),
            "agent_status": dict(self.agent_status)
        }
    
    # Private methods
    
    async def _process_messages(self):
        """Background task to process messages"""
        while not self.shutdown_event.is_set():
            try:
                # Process any timeout or cleanup logic here
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message processing: {e}")
    
    def _register_default_handlers(self):
        """Register default message handlers"""
        # Add default handlers for common message types
        pass
    
    async def _route_task_to_agent(self, task: AgentTask, chain_id: str):
        """Route a task to the appropriate agent"""
        # Find agent capable of handling this task type
        capable_agents = [
            agent_id for agent_id, capabilities in self.agent_capabilities.items()
            if task.task_type in capabilities and self.agent_status[agent_id] == "active"
        ]
        
        if not capable_agents:
            logger.error(f"No agents available for task type {task.task_type.value}")
            return
        
        # For now, use simple round-robin selection
        # In production, this would use more sophisticated routing
        selected_agent = capable_agents[0]
        
        # Send task request message
        await self.send_message(
            sender="communication_hub",
            recipient=selected_agent,
            message_type=MessageType.TASK_REQUEST,
            payload={
                "task": task.__dict__,
                "chain_id": chain_id
            },
            priority=MessagePriority.HIGH
        )
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default communication hub configuration"""
        return {
            "max_queue_size": 1000,
            "message_timeout": 300,  # 5 minutes
            "processing_interval": 1,  # 1 second
            "max_retries": 3
        } 