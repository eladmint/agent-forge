"""
Othentic-Enabled Agent Example for Agent Forge.

Demonstrates the integration of Othentic AVS (Actively Validated Services)
for multi-chain blockchain capabilities, payment processing, and reputation management.

This agent showcases:
- Agent registration in Othentic network
- Multi-chain payment processing
- Reputation validation and tracking
- Cross-chain operations
- Enterprise compliance features
"""

import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List

from core.agents.base import AsyncContextAgent
from core.blockchain.othentic.client import OthenticAVSClient, OthenticConfig
from core.blockchain.othentic.avs.agent_registry import (
    AgentRegistration, AgentCapability, AgentStatus, AgentSearchQuery
)
from core.blockchain.othentic.avs.payment_processor import (
    PaymentRequest, PaymentMethod, EscrowContract
)
from core.blockchain.othentic.avs.reputation import (
    ReputationAction, ValidationRequest, ValidationVote
)

logger = logging.getLogger(__name__)


class OthenticEnabledAgent(AsyncContextAgent):
    """
    Example agent with full Othentic AVS integration.
    
    Demonstrates blockchain-enabled AI agent capabilities including:
    - Decentralized agent registry participation
    - Multi-chain payment processing
    - Reputation validation and management
    - Cross-chain asset operations
    - Enterprise compliance tracking
    """
    
    def __init__(self, 
                 task_description: str,
                 target_url: Optional[str] = None,
                 othentic_config: Optional[Dict[str, Any]] = None,
                 payment_config: Optional[Dict[str, Any]] = None,
                 **kwargs):
        """
        Initialize Othentic-enabled agent.
        
        Args:
            task_description: Description of the task to perform
            target_url: Optional target URL for web automation
            othentic_config: Othentic AVS configuration
            payment_config: Payment processing configuration
            **kwargs: Additional agent configuration
        """
        super().__init__(
            name="OthenticEnabledAgent",
            **kwargs
        )
        
        self.task_description = task_description
        self.target_url = target_url
        
        # Generate unique execution ID
        import uuid
        self.execution_id = str(uuid.uuid4())[:8]
        
        # Initialize Othentic configuration
        self.othentic_config = OthenticConfig(
            api_key=othentic_config.get("api_key", "test_api_key"),
            agent_id=othentic_config.get("agent_id", f"agent_{self.execution_id}"),
            base_url=othentic_config.get("base_url", "https://api.othentic.xyz"),
            **{k: v for k, v in othentic_config.items() 
               if k not in ["api_key", "agent_id", "base_url"]}
        ) if othentic_config else OthenticConfig(
            api_key="test_api_key",
            agent_id=f"agent_{self.execution_id}"
        )
        
        self.payment_config = payment_config or {}
        self.othentic_client: Optional[OthenticAVSClient] = None
        self.agent_registration: Optional[AgentRegistration] = None
        self.current_reputation: Optional[Dict[str, Any]] = None
        
    async def __aenter__(self):
        """Enhanced async context manager with Othentic initialization."""
        # Initialize base agent
        await super().__aenter__()
        
        # Initialize Othentic AVS client
        self.othentic_client = OthenticAVSClient(self.othentic_config)
        await self.othentic_client.__aenter__()
        
        # Register agent in Othentic network
        await self._register_in_othentic_network()
        
        # Load current reputation
        await self._load_reputation_data()
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Enhanced cleanup with Othentic deregistration."""
        try:
            # Update final reputation based on execution results
            if hasattr(self, '_execution_results'):
                await self._update_reputation_after_execution()
                
            # Close Othentic client
            if self.othentic_client:
                await self.othentic_client.__aexit__(exc_type, exc_val, exc_tb)
                
        except Exception as e:
            logger.error(f"Error during Othentic cleanup: {e}")
            
        # Cleanup base agent
        await super().__aexit__(exc_type, exc_val, exc_tb)
        
    async def run(self) -> Dict[str, Any]:
        """
        Execute agent task with full Othentic integration.
        
        Returns:
            Comprehensive execution results including blockchain proofs
        """
        try:
            # Start execution tracking
            start_time = datetime.utcnow()
            
            # Step 1: Perform the core task
            task_results = await self._execute_core_task()
            
            # Step 2: Process any payments if configured
            payment_results = await self._handle_payment_processing()
            
            # Step 3: Generate execution proof
            execution_proof = await self._generate_execution_proof(
                task_results, start_time
            )
            
            # Step 4: Submit reputation validation
            reputation_update = await self._submit_reputation_validation(
                task_results, execution_proof
            )
            
            # Step 5: Handle cross-chain operations if needed
            cross_chain_results = await self._handle_cross_chain_operations()
            
            # Compile comprehensive results
            execution_results = {
                "success": True,
                "task_results": task_results,
                "payment_results": payment_results,
                "execution_proof": execution_proof,
                "reputation_update": reputation_update,
                "cross_chain_results": cross_chain_results,
                "othentic_integration": {
                    "agent_id": self.othentic_config.agent_id,
                    "network_status": "connected",
                    "avs_services_used": [
                        "agent_registry",
                        "payment_processor", 
                        "reputation_validation"
                    ]
                },
                "execution_time": (datetime.utcnow() - start_time).total_seconds(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store results for cleanup
            self._execution_results = execution_results
            
            return execution_results
            
        except Exception as e:
            logger.error(f"Error during Othentic-enabled execution: {e}")
            
            # Return error results with Othentic context
            return {
                "success": False,
                "error": str(e),
                "othentic_integration": {
                    "agent_id": self.othentic_config.agent_id,
                    "network_status": "error",
                    "error_context": "execution_failed"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
    async def _register_in_othentic_network(self):
        """Register this agent in the Othentic decentralized registry."""
        try:
            # Create agent registration
            self.agent_registration = AgentRegistration(
                agent_id=self.othentic_config.agent_id,
                owner_address="0x...",  # Would be actual wallet address
                name=f"Agent Forge Agent {self.othentic_config.agent_id}",
                description=self.task_description,
                capabilities=[
                    AgentCapability.WEB_SCRAPING,
                    AgentCapability.DATA_EXTRACTION,
                    AgentCapability.AI_PROCESSING,
                    AgentCapability.BLOCKCHAIN_ANALYSIS
                ],
                supported_chains=["ethereum", "polygon", "cardano"],
                stake_amount=Decimal("1.0"),  # Minimum stake
                reputation_score=0.5,  # Starting reputation
                registration_time=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                status=AgentStatus.ACTIVE
            )
            
            # Register with Othentic
            registration_result = await self.othentic_client.agent_registry.register_agent(
                self.agent_registration
            )
            
            logger.info(f"Agent registered in Othentic network: {registration_result}")
            
        except Exception as e:
            logger.warning(f"Failed to register in Othentic network: {e}")
            
    async def _load_reputation_data(self):
        """Load current reputation data from Othentic."""
        try:
            reputation_score = await self.othentic_client.reputation.get_reputation_score(
                self.othentic_config.agent_id
            )
            
            if reputation_score:
                self.current_reputation = reputation_score.to_dict()
                logger.info(f"Current reputation: {reputation_score.overall_score}")
            else:
                logger.info("No existing reputation found - starting fresh")
                
        except Exception as e:
            logger.warning(f"Failed to load reputation data: {e}")
            
    async def _execute_core_task(self) -> Dict[str, Any]:
        """Execute the core agent task (web automation, data extraction, etc.)."""
        try:
            # Simulate task execution - in real implementation this would
            # use the browser client, AI processing, etc.
            
            if self.target_url:
                # Simulate web automation
                task_results = {
                    "task_type": "web_automation",
                    "target_url": self.target_url,
                    "data_extracted": {
                        "title": "Example Page Title",
                        "content_length": 1500,
                        "links_found": 25
                    },
                    "execution_success": True,
                    "quality_score": 0.85
                }
            else:
                # Simulate AI processing task
                task_results = {
                    "task_type": "ai_processing",
                    "description": self.task_description,
                    "processing_results": {
                        "tokens_processed": 1000,
                        "analysis_confidence": 0.92
                    },
                    "execution_success": True,
                    "quality_score": 0.88
                }
                
            logger.info(f"Core task completed: {task_results['task_type']}")
            return task_results
            
        except Exception as e:
            logger.error(f"Core task execution failed: {e}")
            return {
                "task_type": "unknown",
                "execution_success": False,
                "error": str(e),
                "quality_score": 0.0
            }
            
    async def _handle_payment_processing(self) -> Dict[str, Any]:
        """Handle payment processing through Othentic Universal Payment AVS."""
        try:
            if not self.payment_config.get("enabled", False):
                return {"payment_enabled": False}
                
            # Create payment request
            payment_request = PaymentRequest(
                request_id=f"pay_{self.execution_id}",
                payer_id=self.payment_config.get("payer_id", "client_123"),
                payee_id=self.othentic_config.agent_id,
                amount=Decimal(str(self.payment_config.get("amount", "10.0"))),
                currency=self.payment_config.get("currency", "USD"),
                payment_method=PaymentMethod(self.payment_config.get("method", "usdc")),
                description=f"Payment for task: {self.task_description}",
                task_id=self.execution_id,
                escrow_required=True
            )
            
            # Create payment request
            payment_result = await self.othentic_client.payment_processor.create_payment_request(
                payment_request
            )
            
            # Create escrow if required
            if payment_request.escrow_required:
                escrow = await self.othentic_client.payment_processor.create_escrow(
                    payment_request,
                    release_conditions=["task_completion", "quality_verification"]
                )
                
                payment_result["escrow"] = escrow.to_dict()
                
            logger.info(f"Payment processing completed: {payment_result}")
            return payment_result
            
        except Exception as e:
            logger.warning(f"Payment processing failed: {e}")
            return {
                "payment_enabled": True,
                "payment_success": False,
                "error": str(e)
            }
            
    async def _generate_execution_proof(self, 
                                       task_results: Dict[str, Any],
                                       start_time: datetime) -> Dict[str, Any]:
        """Generate cryptographic proof of execution."""
        try:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            proof_data = {
                "agent_id": self.othentic_config.agent_id,
                "execution_id": self.execution_id,
                "task_description": self.task_description,
                "start_time": start_time.isoformat(),
                "execution_time": execution_time,
                "task_results": task_results,
                "success": task_results.get("execution_success", False),
                "quality_score": task_results.get("quality_score", 0.0)
            }
            
            # In a real implementation, this would generate actual cryptographic proofs
            # using the Othentic proof generation system
            execution_proof = {
                "proof_type": "othentic_avs_execution",
                "proof_data": proof_data,
                "proof_hash": f"0x{hash(str(proof_data)) % (10**16):016x}",
                "validation_status": "pending",
                "blockchain_anchored": False
            }
            
            logger.info(f"Execution proof generated: {execution_proof['proof_hash']}")
            return execution_proof
            
        except Exception as e:
            logger.error(f"Failed to generate execution proof: {e}")
            return {
                "proof_type": "error",
                "error": str(e)
            }
            
    async def _submit_reputation_validation(self,
                                          task_results: Dict[str, Any],
                                          execution_proof: Dict[str, Any]) -> Dict[str, Any]:
        """Submit reputation validation request based on task execution."""
        try:
            # Determine reputation action based on task success
            if task_results.get("execution_success", False):
                action = ReputationAction.TASK_COMPLETION
                evidence = {
                    "execution_proof": execution_proof,
                    "quality_score": task_results.get("quality_score", 0.0),
                    "task_type": task_results.get("task_type", "unknown")
                }
            else:
                action = ReputationAction.VALIDATION_FAILURE
                evidence = {
                    "execution_proof": execution_proof,
                    "failure_reason": task_results.get("error", "unknown_error")
                }
                
            # Create validation request
            validation_request = await self.othentic_client.reputation.create_validation_request(
                agent_id=self.othentic_config.agent_id,
                action=action,
                evidence=evidence,
                stake_requirement=Decimal("0.1"),
                voting_period=3600  # 1 hour
            )
            
            logger.info(f"Reputation validation submitted: {validation_request.request_id}")
            
            return {
                "validation_request_id": validation_request.request_id,
                "action": action.value,
                "status": "submitted",
                "voting_period": 3600
            }
            
        except Exception as e:
            logger.warning(f"Failed to submit reputation validation: {e}")
            return {
                "validation_success": False,
                "error": str(e)
            }
            
    async def _handle_cross_chain_operations(self) -> Dict[str, Any]:
        """Handle any cross-chain operations if configured."""
        try:
            # This would implement actual cross-chain operations
            # For now, just return status
            return {
                "cross_chain_enabled": True,
                "supported_chains": ["ethereum", "polygon", "cardano"],
                "operations_performed": 0
            }
            
        except Exception as e:
            logger.warning(f"Cross-chain operations failed: {e}")
            return {
                "cross_chain_enabled": False,
                "error": str(e)
            }
            
    async def _update_reputation_after_execution(self):
        """Update reputation based on final execution results."""
        try:
            if not hasattr(self, '_execution_results'):
                return
                
            results = self._execution_results
            
            # Update agent activity timestamp
            await self.othentic_client.agent_registry.update_agent(
                self.othentic_config.agent_id,
                {
                    "last_activity": datetime.utcnow().isoformat(),
                    "total_tasks_completed": 1  # Would increment existing count
                }
            )
            
            logger.info("Agent reputation and activity updated")
            
        except Exception as e:
            logger.warning(f"Failed to update reputation after execution: {e}")
            
    # Additional utility methods for advanced Othentic features
    
    async def search_other_agents(self, 
                                 capabilities: Optional[List[AgentCapability]] = None,
                                 min_reputation: Optional[float] = None) -> List[Dict[str, Any]]:
        """Search for other agents in the Othentic network."""
        try:
            query = AgentSearchQuery(
                capabilities=capabilities,
                min_reputation=min_reputation,
                max_results=50
            )
            
            agents = await self.othentic_client.agent_registry.search_agents(query)
            
            return [agent.to_dict() for agent in agents]
            
        except Exception as e:
            logger.error(f"Failed to search agents: {e}")
            return []
            
    async def get_network_reputation_stats(self) -> Dict[str, Any]:
        """Get overall network reputation statistics."""
        try:
            stats = await self.othentic_client.reputation.get_reputation_stats()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get reputation stats: {e}")
            return {}
            
    async def participate_in_validation(self, request_id: str, vote: ValidationVote) -> bool:
        """Participate in validating another agent's reputation."""
        try:
            vote_record = await self.othentic_client.reputation.vote_on_validation(
                request_id=request_id,
                vote=vote,
                stake_amount=Decimal("0.1"),
                justification="Automated validation based on evidence review"
            )
            
            logger.info(f"Participated in validation: {vote_record.vote_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to participate in validation: {e}")
            return False


# Example usage and configuration
if __name__ == "__main__":
    async def main():
        """Example usage of Othentic-enabled agent."""
        
        # Configure Othentic integration
        othentic_config = {
            "api_key": "your_othentic_api_key",
            "agent_id": "example_agent_001",
            "base_url": "https://api.othentic.xyz"
        }
        
        # Configure payment processing
        payment_config = {
            "enabled": True,
            "amount": "25.0",
            "currency": "USD",
            "method": "usdc",
            "payer_id": "client_wallet_123"
        }
        
        # Create and run agent
        async with OthenticEnabledAgent(
            task_description="Extract market data from cryptocurrency exchanges",
            target_url="https://coinmarketcap.com",
            othentic_config=othentic_config,
            payment_config=payment_config
        ) as agent:
            
            # Execute the task with full Othentic integration
            results = await agent.run()
            
            print("Othentic-Enabled Agent Results:")
            print(f"Success: {results['success']}")
            print(f"Execution Time: {results.get('execution_time', 0):.2f}s")
            print(f"Quality Score: {results.get('task_results', {}).get('quality_score', 0)}")
            print(f"Payment Status: {results.get('payment_results', {}).get('payment_success', 'N/A')}")
            print(f"Reputation Update: {results.get('reputation_update', {}).get('status', 'N/A')}")
            
            # Demonstrate additional Othentic features
            print("\nOthentic Network Features:")
            
            # Search for other agents
            other_agents = await agent.search_other_agents(
                capabilities=[AgentCapability.BLOCKCHAIN_ANALYSIS],
                min_reputation=0.7
            )
            print(f"Found {len(other_agents)} high-reputation blockchain agents")
            
            # Get network stats
            network_stats = await agent.get_network_reputation_stats()
            print(f"Network average reputation: {network_stats.get('average_reputation', 'N/A')}")
    
    # Run the example
    asyncio.run(main())