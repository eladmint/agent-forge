"""
Agent Registry AVS for Othentic integration.

Provides decentralized agent discovery and registration services
with reputation staking and multi-chain capabilities.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from dataclasses import dataclass, asdict
from enum import Enum

if TYPE_CHECKING:
    from ..client import OthenticAVSClient

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent registration status enumeration."""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    SLASHED = "slashed"
    DEREGISTERED = "deregistered"


class AgentCapability(Enum):
    """Agent capability enumeration."""
    WEB_SCRAPING = "web_scraping"
    DATA_EXTRACTION = "data_extraction"
    BLOCKCHAIN_ANALYSIS = "blockchain_analysis"
    AI_PROCESSING = "ai_processing"
    DOCUMENT_ANALYSIS = "document_analysis"
    IMAGE_PROCESSING = "image_processing"
    AUTOMATED_TRADING = "automated_trading"
    COMPLIANCE_MONITORING = "compliance_monitoring"
    REPUTATION_VALIDATION = "reputation_validation"
    CROSS_CHAIN_OPERATIONS = "cross_chain_operations"


@dataclass
class AgentRegistration:
    """Agent registration information."""
    
    agent_id: str
    owner_address: str
    name: str
    description: str
    capabilities: List[AgentCapability]
    supported_chains: List[str]
    stake_amount: float
    reputation_score: float
    registration_time: datetime
    last_activity: datetime
    status: AgentStatus
    version: str = "1.0.0"
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['capabilities'] = [cap.value for cap in self.capabilities]
        data['status'] = self.status.value
        data['registration_time'] = self.registration_time.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        return data


@dataclass
class AgentSearchQuery:
    """Agent search query parameters."""
    
    capabilities: Optional[List[AgentCapability]] = None
    supported_chains: Optional[List[str]] = None
    min_reputation: Optional[float] = None
    min_stake: Optional[float] = None
    status: Optional[AgentStatus] = None
    max_results: int = 100
    offset: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API call."""
        data = {}
        if self.capabilities:
            data['capabilities'] = [cap.value for cap in self.capabilities]
        if self.supported_chains:
            data['supported_chains'] = self.supported_chains
        if self.min_reputation is not None:
            data['min_reputation'] = self.min_reputation
        if self.min_stake is not None:
            data['min_stake'] = self.min_stake
        if self.status:
            data['status'] = self.status.value
        data['max_results'] = self.max_results
        data['offset'] = self.offset
        return data


class AgentRegistryAVS:
    """
    Agent Registry AVS service.
    
    Provides decentralized agent discovery and registration with
    reputation staking and validation capabilities.
    """
    
    def __init__(self, client: 'OthenticAVSClient'):
        """
        Initialize Agent Registry AVS.
        
        Args:
            client: Parent Othentic AVS client
        """
        self.client = client
        self._initialized = False
        
    async def initialize(self):
        """Initialize the Agent Registry AVS."""
        try:
            # Verify contract connectivity
            await self._verify_contract_connection()
            self._initialized = True
            logger.info("Agent Registry AVS initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Agent Registry AVS: {e}")
            raise
            
    async def _verify_contract_connection(self):
        """Verify connection to the agent registry contract."""
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/registry/health"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                if not result.get("healthy", False):
                    raise RuntimeError("Agent Registry AVS is not healthy")
                    
        except Exception as e:
            logger.error(f"Agent Registry health check failed: {e}")
            raise
            
    async def register_agent(self, 
                           registration: AgentRegistration) -> Dict[str, Any]:
        """
        Register a new agent in the decentralized registry.
        
        Args:
            registration: Agent registration information
            
        Returns:
            Registration result with transaction details
        """
        if not self._initialized:
            raise RuntimeError("Agent Registry AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        payload = registration.to_dict()
        payload['registration_time'] = datetime.utcnow().isoformat()
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/registry/agents/register",
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Agent registered successfully: {registration.agent_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to register agent {registration.agent_id}: {e}")
            raise
            
    async def update_agent(self, 
                          agent_id: str,
                          updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update agent registration information.
        
        Args:
            agent_id: Agent identifier to update
            updates: Updated fields
            
        Returns:
            Update result
        """
        if not self._initialized:
            raise RuntimeError("Agent Registry AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        updates['last_activity'] = datetime.utcnow().isoformat()
        
        try:
            async with self.client.session.patch(
                f"{self.client.config.base_url}/v1/registry/agents/{agent_id}",
                json=updates
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Agent updated successfully: {agent_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id}: {e}")
            raise
            
    async def deregister_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Deregister an agent from the registry.
        
        Args:
            agent_id: Agent identifier to deregister
            
        Returns:
            Deregistration result
        """
        if not self._initialized:
            raise RuntimeError("Agent Registry AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.delete(
                f"{self.client.config.base_url}/v1/registry/agents/{agent_id}"
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Agent deregistered successfully: {agent_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to deregister agent {agent_id}: {e}")
            raise
            
    async def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        """
        Get agent registration information.
        
        Args:
            agent_id: Agent identifier to lookup
            
        Returns:
            Agent registration or None if not found
        """
        if not self._initialized:
            raise RuntimeError("Agent Registry AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/registry/agents/{agent_id}"
            ) as response:
                if response.status == 404:
                    return None
                    
                response.raise_for_status()
                data = await response.json()
                
                # Convert back to AgentRegistration object
                return AgentRegistration(
                    agent_id=data['agent_id'],
                    owner_address=data['owner_address'],
                    name=data['name'],
                    description=data['description'],
                    capabilities=[AgentCapability(cap) for cap in data['capabilities']],
                    supported_chains=data['supported_chains'],
                    stake_amount=data['stake_amount'],
                    reputation_score=data['reputation_score'],
                    registration_time=datetime.fromisoformat(data['registration_time']),
                    last_activity=datetime.fromisoformat(data['last_activity']),
                    status=AgentStatus(data['status']),
                    version=data.get('version', '1.0.0'),
                    metadata=data.get('metadata')
                )
                
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            raise
            
    async def search_agents(self, query: AgentSearchQuery) -> List[AgentRegistration]:
        """
        Search for agents in the registry.
        
        Args:
            query: Search query parameters
            
        Returns:
            List of matching agent registrations
        """
        if not self._initialized:
            raise RuntimeError("Agent Registry AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/registry/agents/search",
                params=query.to_dict()
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                agents = []
                for agent_data in data.get('agents', []):
                    agents.append(AgentRegistration(
                        agent_id=agent_data['agent_id'],
                        owner_address=agent_data['owner_address'],
                        name=agent_data['name'],
                        description=agent_data['description'],
                        capabilities=[AgentCapability(cap) for cap in agent_data['capabilities']],
                        supported_chains=agent_data['supported_chains'],
                        stake_amount=agent_data['stake_amount'],
                        reputation_score=agent_data['reputation_score'],
                        registration_time=datetime.fromisoformat(agent_data['registration_time']),
                        last_activity=datetime.fromisoformat(agent_data['last_activity']),
                        status=AgentStatus(agent_data['status']),
                        version=agent_data.get('version', '1.0.0'),
                        metadata=agent_data.get('metadata')
                    ))
                
                return agents
                
        except Exception as e:
            logger.error(f"Failed to search agents: {e}")
            raise
            
    async def stake_for_agent(self, 
                            agent_id: str,
                            stake_amount: float) -> Dict[str, Any]:
        """
        Stake tokens for an agent to improve reputation.
        
        Args:
            agent_id: Agent identifier to stake for
            stake_amount: Amount to stake
            
        Returns:
            Staking result
        """
        if not self._initialized:
            raise RuntimeError("Agent Registry AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        payload = {
            "agent_id": agent_id,
            "stake_amount": stake_amount,
            "staker_id": self.client.config.agent_id,
            "stake_time": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.client.session.post(
                f"{self.client.config.base_url}/v1/registry/agents/{agent_id}/stake",
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Staked {stake_amount} for agent {agent_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to stake for agent {agent_id}: {e}")
            raise
            
    async def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent statistics
        """
        if not self._initialized:
            raise RuntimeError("Agent Registry AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/registry/agents/{agent_id}/stats"
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Failed to get agent stats for {agent_id}: {e}")
            raise
            
    async def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get overall registry statistics.
        
        Returns:
            Registry statistics
        """
        if not self._initialized:
            raise RuntimeError("Agent Registry AVS not initialized")
            
        if not self.client.session:
            raise RuntimeError("Client session not available")
            
        try:
            async with self.client.session.get(
                f"{self.client.config.base_url}/v1/registry/stats"
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Failed to get registry stats: {e}")
            raise