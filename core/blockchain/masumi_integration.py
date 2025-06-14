"""
Masumi Network integration for Agent Forge.

Provides AI Agent Economy participation through task rewards
and reputation system integration.
"""

import asyncio
import json
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    REWARDED = "rewarded"


@dataclass
class MasumiTaskReward:
    """
    Represents a task reward from Masumi Network.
    """
    task_id: str
    agent_id: str
    reward_amount: float
    reward_token: str
    completion_time: datetime
    quality_score: float
    transaction_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "reward_amount": self.reward_amount,
            "reward_token": self.reward_token,
            "completion_time": self.completion_time.isoformat(),
            "quality_score": self.quality_score,
            "transaction_hash": self.transaction_hash
        }


class MasumiNetworkClient:
    """
    Masumi Network API client for AI Agent Economy participation.
    
    Handles task registration, completion reporting, and reward claiming
    for blockchain-enabled AI agents.
    """
    
    def __init__(self, 
                 api_key: str,
                 agent_id: str,
                 base_url: str = "https://api.masumi.network"):
        """
        Initialize Masumi Network client.
        
        Args:
            api_key: Masumi Network API key
            agent_id: Unique identifier for this agent
            base_url: Masumi API base URL
        """
        self.api_key = api_key
        self.agent_id = agent_id
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": f"AgentForge-{self.agent_id}"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def register_agent(self, 
                           capabilities: List[str],
                           reputation_score: float = 0.0) -> Dict[str, Any]:
        """
        Register agent with Masumi Network.
        
        Args:
            capabilities: List of agent capabilities
            reputation_score: Initial reputation score
            
        Returns:
            Registration result
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        payload = {
            "agent_id": self.agent_id,
            "capabilities": capabilities,
            "reputation_score": reputation_score,
            "framework": "AgentForge",
            "version": "1.0.0"
        }
        
        async with self.session.post(
            f"{self.base_url}/v1/agents/register",
            json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_available_tasks(self, 
                                task_type: Optional[str] = None,
                                min_reward: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Get available tasks from Masumi Network.
        
        Args:
            task_type: Optional task type filter
            min_reward: Minimum reward amount filter
            
        Returns:
            List of available tasks
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        params = {"agent_id": self.agent_id}
        if task_type:
            params["task_type"] = task_type
        if min_reward:
            params["min_reward"] = min_reward
        
        async with self.session.get(
            f"{self.base_url}/v1/tasks/available",
            params=params
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def claim_task(self, task_id: str) -> Dict[str, Any]:
        """
        Claim a task for execution.
        
        Args:
            task_id: Task identifier to claim
            
        Returns:
            Task claim result
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        payload = {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "claimed_at": datetime.utcnow().isoformat()
        }
        
        async with self.session.post(
            f"{self.base_url}/v1/tasks/{task_id}/claim",
            json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def submit_task_completion(self,
                                   task_id: str,
                                   execution_proof: Dict[str, Any],
                                   quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit task completion with execution proof.
        
        Args:
            task_id: Completed task identifier
            execution_proof: Proof of task execution
            quality_metrics: Quality assessment metrics
            
        Returns:
            Submission result
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        payload = {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "completion_time": datetime.utcnow().isoformat(),
            "execution_proof": execution_proof,
            "quality_metrics": quality_metrics,
            "status": TaskStatus.COMPLETED.value
        }
        
        async with self.session.post(
            f"{self.base_url}/v1/tasks/{task_id}/complete",
            json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_reward_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get reward status for a completed task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Reward status information
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        async with self.session.get(
            f"{self.base_url}/v1/tasks/{task_id}/reward"
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def claim_reward(self, task_id: str) -> MasumiTaskReward:
        """
        Claim reward for completed task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task reward information
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        payload = {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "claim_time": datetime.utcnow().isoformat()
        }
        
        async with self.session.post(
            f"{self.base_url}/v1/rewards/{task_id}/claim",
            json=payload
        ) as response:
            response.raise_for_status()
            reward_data = await response.json()
            
            return MasumiTaskReward(
                task_id=reward_data["task_id"],
                agent_id=reward_data["agent_id"],
                reward_amount=reward_data["reward_amount"],
                reward_token=reward_data["reward_token"],
                completion_time=datetime.fromisoformat(reward_data["completion_time"]),
                quality_score=reward_data["quality_score"],
                transaction_hash=reward_data.get("transaction_hash")
            )
    
    async def get_agent_reputation(self) -> Dict[str, Any]:
        """
        Get current agent reputation metrics.
        
        Returns:
            Reputation information
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        async with self.session.get(
            f"{self.base_url}/v1/agents/{self.agent_id}/reputation"
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_earnings_history(self, 
                                 limit: int = 100,
                                 offset: int = 0) -> List[MasumiTaskReward]:
        """
        Get agent earnings history.
        
        Args:
            limit: Maximum number of records to return
            offset: Offset for pagination
            
        Returns:
            List of task rewards
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        async with self.session.get(
            f"{self.base_url}/v1/agents/{self.agent_id}/earnings",
            params=params
        ) as response:
            response.raise_for_status()
            earnings_data = await response.json()
            
            rewards = []
            for reward_data in earnings_data.get("rewards", []):
                rewards.append(MasumiTaskReward(
                    task_id=reward_data["task_id"],
                    agent_id=reward_data["agent_id"],
                    reward_amount=reward_data["reward_amount"],
                    reward_token=reward_data["reward_token"],
                    completion_time=datetime.fromisoformat(reward_data["completion_time"]),
                    quality_score=reward_data["quality_score"],
                    transaction_hash=reward_data.get("transaction_hash")
                ))
            
            return rewards