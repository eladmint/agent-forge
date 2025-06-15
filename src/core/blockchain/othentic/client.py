"""
Othentic AVS Client for Agent Forge.

Main client for interacting with Othentic's Actively Validated Services (AVS)
infrastructure, providing multi-chain blockchain capabilities for AI agents.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
import aiohttp

from .avs.agent_registry import AgentRegistryAVS
from .avs.payment_processor import UniversalPaymentAVS
from .avs.reputation import ReputationValidationAVS
from .avs.compliance import EnterpriseComplianceAVS
from .avs.cross_chain import CrossChainBridgeAVS


logger = logging.getLogger(__name__)


@dataclass
class OthenticConfig:
    """Configuration for Othentic AVS client."""
    
    # Core configuration
    api_key: str
    agent_id: str
    base_url: str = "https://api.othentic.xyz"
    
    # Network configuration
    eigenlayer_endpoint: str = "https://api.eigenlayer.xyz"
    ethereum_rpc: str = "https://eth-mainnet.g.alchemy.com/v2/"
    cardano_endpoint: str = "https://cardano-mainnet.blockfrost.io/api/v0"
    solana_endpoint: str = "https://api.mainnet-beta.solana.com"
    polygon_endpoint: str = "https://polygon-rpc.com"
    
    # AVS configuration
    agent_registry_address: str = "0x..."
    payment_processor_address: str = "0x..."
    reputation_contract_address: str = "0x..."
    compliance_contract_address: str = "0x..."
    cross_chain_bridge_address: str = "0x..."
    
    # Staking configuration
    min_stake_amount: float = 32.0  # ETH
    slash_threshold: float = 0.1
    reward_rate: float = 0.05
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AVSOperatorInfo:
    """Information about an AVS operator."""
    
    operator_id: str
    stake_amount: float
    reputation_score: float
    validation_count: int
    slash_count: int
    is_active: bool
    supported_chains: List[str]
    last_activity: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.""" 
        data = asdict(self)
        data['last_activity'] = self.last_activity.isoformat()
        return data


class OthenticAVSClient:
    """
    Main client for Othentic AVS integration.
    
    Provides access to all Othentic AVS services including agent registry,
    payment processing, reputation validation, compliance, and cross-chain operations.
    """
    
    def __init__(self, config: Union[OthenticConfig, Dict[str, Any]]):
        """
        Initialize Othentic AVS client.
        
        Args:
            config: Othentic configuration object or dictionary
        """
        if isinstance(config, dict):
            self.config = OthenticConfig(**config)
        else:
            self.config = config
            
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Initialize AVS services
        self.agent_registry = AgentRegistryAVS(self)
        self.payment_processor = UniversalPaymentAVS(self)
        self.reputation = ReputationValidationAVS(self)
        self.compliance = EnterpriseComplianceAVS(self)
        self.cross_chain = CrossChainBridgeAVS(self)
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "User-Agent": f"AgentForge-Othentic/{self.config.agent_id}",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Initialize AVS services
        await self._initialize_avs_services()
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def _initialize_avs_services(self):
        """Initialize all AVS services."""
        try:
            # Initialize each AVS service
            await asyncio.gather(
                self.agent_registry.initialize(),
                self.payment_processor.initialize(),
                self.reputation.initialize(),
                self.compliance.initialize(),
                self.cross_chain.initialize(),
                return_exceptions=True
            )
            logger.info("All AVS services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AVS services: {e}")
            raise
            
    async def register_as_operator(self, 
                                 stake_amount: float,
                                 supported_chains: List[str]) -> Dict[str, Any]:
        """
        Register as an AVS operator.
        
        Args:
            stake_amount: Amount to stake in ETH
            supported_chains: List of supported blockchain networks
            
        Returns:
            Registration result
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
            
        payload = {
            "operator_id": self.config.agent_id,
            "stake_amount": stake_amount,
            "supported_chains": supported_chains,
            "eigenlayer_operator": True,
            "registration_time": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.session.post(
                f"{self.config.base_url}/v1/operators/register",
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Successfully registered as AVS operator: {result}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to register as AVS operator: {e}")
            raise
            
    async def get_operator_status(self) -> AVSOperatorInfo:
        """
        Get current operator status and information.
        
        Returns:
            Operator information
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
            
        try:
            async with self.session.get(
                f"{self.config.base_url}/v1/operators/{self.config.agent_id}/status"
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                return AVSOperatorInfo(
                    operator_id=data["operator_id"],
                    stake_amount=data["stake_amount"],
                    reputation_score=data["reputation_score"],
                    validation_count=data["validation_count"],
                    slash_count=data["slash_count"],
                    is_active=data["is_active"],
                    supported_chains=data["supported_chains"],
                    last_activity=datetime.fromisoformat(data["last_activity"])
                )
                
        except Exception as e:
            logger.error(f"Failed to get operator status: {e}")
            raise
            
    async def validate_task(self, 
                          task_id: str,
                          validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a task as an AVS operator.
        
        Args:
            task_id: Task identifier to validate
            validation_data: Validation proof and data
            
        Returns:
            Validation result
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
            
        payload = {
            "task_id": task_id,
            "operator_id": self.config.agent_id,
            "validation_data": validation_data,
            "validation_time": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.session.post(
                f"{self.config.base_url}/v1/tasks/{task_id}/validate",
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Task validation submitted: {task_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to validate task {task_id}: {e}")
            raise
            
    async def get_validation_rewards(self, 
                                   start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get validation rewards for this operator.
        
        Args:
            start_date: Start date for reward query
            end_date: End date for reward query
            
        Returns:
            List of validation rewards
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
            
        params = {"operator_id": self.config.agent_id}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
            
        try:
            async with self.session.get(
                f"{self.config.base_url}/v1/rewards/validation",
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Failed to get validation rewards: {e}")
            raise
            
    async def submit_fraud_proof(self, 
                               task_id: str,
                               fraud_evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit fraud proof for malicious behavior.
        
        Args:
            task_id: Task identifier with suspected fraud
            fraud_evidence: Evidence of fraudulent behavior
            
        Returns:
            Fraud proof submission result
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
            
        payload = {
            "task_id": task_id,
            "reporter_id": self.config.agent_id,
            "fraud_evidence": fraud_evidence,
            "report_time": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.session.post(
                f"{self.config.base_url}/v1/fraud/report",
                json=payload
            ) as response:
                response.raise_for_status()
                result = await response.json()
                
                logger.info(f"Fraud proof submitted for task: {task_id}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to submit fraud proof: {e}")
            raise
            
    async def get_network_stats(self) -> Dict[str, Any]:
        """
        Get Othentic network statistics.
        
        Returns:
            Network statistics
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
            
        try:
            async with self.session.get(
                f"{self.config.base_url}/v1/network/stats"
            ) as response:
                response.raise_for_status()
                return await response.json()
                
        except Exception as e:
            logger.error(f"Failed to get network stats: {e}")
            raise
            
    def get_supported_chains(self) -> List[str]:
        """
        Get list of supported blockchain networks.
        
        Returns:
            List of supported chains
        """
        return [
            "ethereum",
            "cardano", 
            "solana",
            "polygon",
            "avalanche",
            "fantom",
            "binance-smart-chain",
            "arbitrum"
        ]
        
    def get_config(self) -> OthenticConfig:
        """
        Get current configuration.
        
        Returns:
            Current Othentic configuration
        """
        return self.config