"""
Masumi Bridge Adapter

Bridge that wraps Agent Forge agents to participate in Masumi Network workflows.
This adapter enables seamless integration with CrewAI templates and Masumi services.
"""

import asyncio
import json
import hashlib
import uuid
from typing import Dict, Any, Optional, Type, Union, List
from datetime import datetime, timezone
import logging

from ...agents.base import AsyncContextAgent
from .config import MasumiConfig
from .payment_client import MasumiPaymentClient
from .registry_client import MasumiRegistryClient


class MasumiAgentWrapper:
    """Wrapper that makes any Agent Forge agent compatible with Masumi Network."""
    
    def __init__(
        self,
        agent: AsyncContextAgent,
        config: Optional[MasumiConfig] = None,
        agent_did: Optional[str] = None,
        price_ada: float = 5.0
    ):
        self.agent = agent
        self.config = config or MasumiConfig.for_testing()
        self.agent_did = agent_did or f"did:cardano:agent_{uuid.uuid4().hex[:8]}"
        self.price_ada = price_ada
        self.logger = logging.getLogger(__name__)
        
        # Decision logging for Masumi accountability
        self.decision_log = []
        self.execution_start_time = None
        self.execution_end_time = None
        
    def log_decision(self, decision_type: str, data: Dict[str, Any]):
        """Log decisions for Masumi accountability and audit trails."""
        self.decision_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": decision_type,
            "data": data,
            "agent": self.agent.name,
            "agent_did": self.agent_did
        })
    
    async def execute_with_masumi(
        self,
        job_id: str,
        payment_proof: Optional[str] = None,
        requester_did: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the wrapped agent with Masumi Network integration.
        
        Args:
            job_id: Unique job identifier
            payment_proof: Payment transaction hash (optional for testing)
            requester_did: Requester's DID (optional)
            **kwargs: Additional arguments for the agent
            
        Returns:
            Execution result with Masumi proof and payment info
        """
        self.execution_start_time = datetime.now(timezone.utc)
        
        # Log execution start
        self.log_decision("execution_started", {
            "job_id": job_id,
            "payment_proof": payment_proof,
            "requester_did": requester_did,
            "kwargs": kwargs
        })
        
        # Step 1: Verify payment (if required)
        payment_verified = True
        if payment_proof:
            async with MasumiPaymentClient(self.config) as payment_client:
                payment_verified = await payment_client.verify_payment(payment_proof, job_id)
                
            if not payment_verified:
                self.log_decision("payment_verification_failed", {
                    "payment_proof": payment_proof,
                    "job_id": job_id
                })
                raise ValueError("Payment verification failed")
        
        self.log_decision("payment_verified", {
            "verified": payment_verified,
            "payment_proof": payment_proof
        })
        
        # Step 2: Execute the wrapped agent
        try:
            # Initialize agent if needed
            if not hasattr(self.agent, '_initialized'):
                await self.agent.__aenter__()
                self.agent._initialized = True
            
            # Execute agent task
            result = await self.agent.run(**kwargs)
            
            self.execution_end_time = datetime.now(timezone.utc)
            
            self.log_decision("execution_completed", {
                "success": result is not None,
                "result_type": type(result).__name__,
                "execution_time": (self.execution_end_time - self.execution_start_time).total_seconds()
            })
            
            # Step 3: Generate Masumi-compliant proof
            proof_data = await self.generate_execution_proof(
                input_data=kwargs,
                output_data=result,
                job_id=job_id,
                requester_did=requester_did
            )
            
            # Step 4: Claim payment (if applicable)
            payment_claimed = False
            if payment_proof and payment_verified:
                async with MasumiPaymentClient(self.config) as payment_client:
                    tx_hash = await payment_client.claim_payment(
                        job_id=job_id,
                        proof_hash=proof_data["proof_hash"],
                        execution_proof=proof_data["proof_data"]
                    )
                    payment_claimed = tx_hash is not None
                    
                    self.log_decision("payment_claimed", {
                        "success": payment_claimed,
                        "transaction_hash": tx_hash
                    })
            
            return {
                "job_id": job_id,
                "agent_did": self.agent_did,
                "result": result,
                "proof_hash": proof_data["proof_hash"],
                "proof_data": proof_data["proof_data"],
                "payment_verified": payment_verified,
                "payment_claimed": payment_claimed,
                "execution_time": (self.execution_end_time - self.execution_start_time).total_seconds(),
                "decision_count": len(self.decision_log)
            }
            
        except Exception as e:
            self.execution_end_time = datetime.now(timezone.utc)
            
            self.log_decision("execution_error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            
            raise e
        
        finally:
            # Cleanup agent if needed
            if hasattr(self.agent, '_initialized'):
                try:
                    await self.agent.__aexit__(None, None, None)
                    delattr(self.agent, '_initialized')
                except:
                    pass
    
    async def generate_execution_proof(
        self,
        input_data: Dict[str, Any],
        output_data: Any,
        job_id: str,
        requester_did: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Masumi-compliant proof of execution.
        
        Args:
            input_data: Agent input parameters
            output_data: Agent execution result
            job_id: Unique job identifier
            requester_did: Requester's DID
            
        Returns:
            Proof data with hash and complete audit trail
        """
        proof_data = {
            "job_id": job_id,
            "agent_did": self.agent_did,
            "agent_name": self.agent.name,
            "requester_did": requester_did,
            "input": input_data,
            "output": output_data,
            "decisions": self.decision_log,
            "execution_start": self.execution_start_time.isoformat() if self.execution_start_time else None,
            "execution_end": self.execution_end_time.isoformat() if self.execution_end_time else None,
            "framework": "Agent Forge",
            "masumi_bridge_version": "1.0.0",
            "network": self.config.network
        }
        
        # Generate cryptographic hash
        proof_json = json.dumps(proof_data, sort_keys=True, default=str)
        proof_hash = hashlib.sha256(proof_json.encode()).hexdigest()
        
        return {
            "proof_hash": proof_hash,
            "proof_data": proof_data,
            "masumi_compliant": True,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities for Masumi registry."""
        capabilities = ["web_automation", "data_extraction"]
        
        # Add specific capabilities based on agent type
        agent_class_name = self.agent.__class__.__name__.lower()
        
        if "navigation" in agent_class_name:
            capabilities.extend(["web_navigation", "page_scraping"])
        if "nmkr" in agent_class_name:
            capabilities.extend(["blockchain_verification", "nft_operations"])
        if "data" in agent_class_name:
            capabilities.extend(["data_compilation", "multi_source_extraction"])
        if "text" in agent_class_name:
            capabilities.extend(["text_processing", "content_analysis"])
        
        return capabilities
    
    def get_api_schema(self) -> Dict[str, Any]:
        """Get API schema for this agent for Masumi registry."""
        return {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "Unique job identifier"},
                "payment_proof": {"type": "string", "description": "Payment transaction hash", "required": False},
                "requester_did": {"type": "string", "description": "Requester DID", "required": False}
            },
            "required": ["job_id"],
            "additionalProperties": True  # Allow agent-specific parameters
        }


class MasumiBridgeAdapter:
    """Main adapter for integrating Agent Forge with Masumi Network."""
    
    def __init__(self, config: Optional[MasumiConfig] = None):
        self.config = config or MasumiConfig.for_testing()
        self.logger = logging.getLogger(__name__)
        self.registered_agents: Dict[str, MasumiAgentWrapper] = {}
    
    def wrap_agent(
        self,
        agent: AsyncContextAgent,
        agent_did: Optional[str] = None,
        price_ada: float = 5.0
    ) -> MasumiAgentWrapper:
        """
        Wrap an Agent Forge agent for Masumi Network compatibility.
        
        Args:
            agent: Agent Forge agent to wrap
            agent_did: Agent's decentralized identifier
            price_ada: Service price in ADA
            
        Returns:
            Wrapped agent ready for Masumi integration
        """
        wrapper = MasumiAgentWrapper(
            agent=agent,
            config=self.config,
            agent_did=agent_did,
            price_ada=price_ada
        )
        
        # Register the wrapper
        did = wrapper.agent_did
        self.registered_agents[did] = wrapper
        
        self.logger.info(f"Wrapped agent {agent.name} with DID: {did}")
        
        return wrapper
    
    async def register_agent_with_masumi(
        self,
        wrapper: MasumiAgentWrapper,
        api_endpoint: str,
        description: Optional[str] = None
    ) -> bool:
        """
        Register a wrapped agent with the Masumi Network registry.
        
        Args:
            wrapper: Wrapped Agent Forge agent
            api_endpoint: URL where agent can be accessed
            description: Agent description
            
        Returns:
            True if registration successful, False otherwise
        """
        async with MasumiRegistryClient(self.config) as registry:
            return await registry.register_agent(
                agent_name=wrapper.agent.name,
                agent_did=wrapper.agent_did,
                capabilities=wrapper.get_capabilities(),
                api_endpoint=api_endpoint,
                price_ada=wrapper.price_ada,
                description=description or f"Agent Forge {wrapper.agent.name} wrapped for Masumi Network",
                metadata={
                    "framework": "Agent Forge",
                    "bridge_version": "1.0.0",
                    "api_schema": wrapper.get_api_schema()
                }
            )
    
    async def discover_masumi_agents(
        self,
        capabilities: Optional[List[str]] = None,
        framework: str = "Agent Forge"
    ) -> List[Dict[str, Any]]:
        """
        Discover other Agent Forge agents in the Masumi Network.
        
        Args:
            capabilities: Required capabilities filter
            framework: Framework filter
            
        Returns:
            List of matching agents
        """
        async with MasumiRegistryClient(self.config) as registry:
            return await registry.discover_agents(
                capabilities=capabilities,
                framework=framework
            )
    
    def get_wrapped_agent(self, agent_did: str) -> Optional[MasumiAgentWrapper]:
        """Get a wrapped agent by its DID."""
        return self.registered_agents.get(agent_did)
    
    def list_registered_agents(self) -> List[str]:
        """List all registered agent DIDs."""
        return list(self.registered_agents.keys())
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of Masumi services."""
        results = {}
        
        # Check payment service
        try:
            async with MasumiPaymentClient(self.config) as payment:
                results["payment_service"] = await payment.health_check()
        except Exception as e:
            self.logger.error(f"Payment service health check failed: {e}")
            results["payment_service"] = False
        
        # Registry service would be similar
        results["registry_service"] = True  # Placeholder
        
        return results