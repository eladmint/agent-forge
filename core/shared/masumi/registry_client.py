"""
Masumi Registry Client

Client for registering Agent Forge agents with the Masumi Network registry
and discovering other agents in the ecosystem.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging

from .config import MasumiConfig


class MasumiRegistryClient:
    """Client for Masumi agent registry operations."""
    
    def __init__(self, config: Optional[MasumiConfig] = None):
        self.config = config or MasumiConfig.for_testing()
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        # Set base_url immediately for testing compatibility
        self.base_url = f"{self.config.payment_service_url}/registry"
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self):
        """Initialize HTTP session."""
        headers = {
            'X-API-Key': self.config.registry_api_key,
            'Content-Type': 'application/json'
        }
        # Note: Registry endpoint would be determined from Masumi docs
        # Using payment service as base for now
        self.base_url = f"{self.config.payment_service_url}/registry"
        self.session = aiohttp.ClientSession(headers=headers)
    
    async def disconnect(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def register_agent(
        self,
        agent_name: str,
        agent_did: str,
        capabilities: List[str],
        api_endpoint: str,
        price_ada: float,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Register an Agent Forge agent with the Masumi Network.
        
        Args:
            agent_name: Human-readable agent name
            agent_did: Agent's decentralized identifier
            capabilities: List of agent capabilities
            api_endpoint: URL where agent can be accessed
            price_ada: Service price in ADA
            description: Agent description
            metadata: Additional metadata
            
        Returns:
            Registration confirmation data
        """
        if not self.session:
            await self.connect()
        
        registration_data = {
            "name": agent_name,
            "did": agent_did,
            "description": description,
            "capabilities": capabilities,
            "api_endpoint": api_endpoint,
            "pricing": {
                "model": "per_request",
                "amount": price_ada,
                "currency": "ADA"
            },
            "framework": "Agent Forge",
            "version": "1.0.0",
            "network": self.config.network,
            "metadata": metadata or {},
            "registered_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            url = f"{self.base_url}/api/v1/agents/register"
            
            async with self.session.post(url, json=registration_data) as response:
                if response.status == 201:
                    result = await response.json()
                    self.logger.info(f"Agent registered successfully: {agent_name}")
                    return result
                else:
                    self.logger.error(f"Agent registration failed: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error registering agent: {e}")
            return None
    
    async def discover_agents(
        self,
        capabilities: Optional[List[str]] = None,
        max_price_ada: Optional[float] = None,
        framework: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover agents in the Masumi Network.
        
        Args:
            capabilities: Required capabilities filter
            max_price_ada: Maximum price filter
            framework: Framework filter (e.g., "Agent Forge", "CrewAI")
            
        Returns:
            List of matching agents
        """
        if not self.session:
            await self.connect()
        
        params = {}
        if capabilities:
            params['capabilities'] = ','.join(capabilities)
        if max_price_ada:
            params['max_price'] = max_price_ada
        if framework:
            params['framework'] = framework
        
        try:
            url = f"{self.base_url}/api/v1/agents/discover"
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('agents', [])
                else:
                    self.logger.error(f"Agent discovery failed: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error discovering agents: {e}")
            return []
    
    async def get_agent_info(self, agent_did: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific agent.
        
        Args:
            agent_did: Agent's decentralized identifier
            
        Returns:
            Agent information
        """
        if not self.session:
            await self.connect()
        
        try:
            url = f"{self.base_url}/api/v1/agents/{agent_did}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Agent info request failed: {response.status}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting agent info: {e}")
            return None
    
    async def update_agent(
        self,
        agent_did: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update agent registration information.
        
        Args:
            agent_did: Agent's decentralized identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        if not self.session:
            await self.connect()
        
        update_data = {
            **updates,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            url = f"{self.base_url}/api/v1/agents/{agent_did}"
            
            async with self.session.patch(url, json=update_data) as response:
                if response.status == 200:
                    self.logger.info(f"Agent updated successfully: {agent_did}")
                    return True
                else:
                    self.logger.error(f"Agent update failed: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error updating agent: {e}")
            return False
    
    async def unregister_agent(self, agent_did: str) -> bool:
        """
        Remove agent from the registry.
        
        Args:
            agent_did: Agent's decentralized identifier
            
        Returns:
            True if unregistration successful, False otherwise
        """
        if not self.session:
            await self.connect()
        
        try:
            url = f"{self.base_url}/api/v1/agents/{agent_did}"
            
            async with self.session.delete(url) as response:
                if response.status == 204:
                    self.logger.info(f"Agent unregistered successfully: {agent_did}")
                    return True
                else:
                    self.logger.error(f"Agent unregistration failed: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error unregistering agent: {e}")
            return False